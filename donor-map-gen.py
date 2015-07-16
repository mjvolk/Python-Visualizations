import pandas as pd
import json
import vincent
from vincent.legends import LegendProperties
from vincent.properties import PropertySet
from vincent.values import ValueRef
import urllib2
from progressbar import ProgressBar
import os
import sys

# with open('http://raw.githubusercontent.com/wrobstory/vincent_map_data/master/world-countries.topo.json', 'r') as f:
#     get_id = json.load(f)

def getProjectData(index, organization, years):
    url = 'http://api.aiddata.org/aid/project?size=50&fo=' + str(organization) + '&from=' + str(index) + '&y=' + str(years)
    result = json.load(urllib2.urlopen(url))
    return result

def addNonDonatedCountries(donor_dict, world):
    for country in world['objects']['world-countries']['geometries']:
        if country['id'] not in donor_dict:
            donor_dict[country['id']] = 0.0
    return donor_dict

def getYearString(start_year, finish_year):
    result = ''
    while start_year < finish_year:
        result += str(start_year)
        result += ','
        start_year += 1
    result += str(finish_year)
    return result

request = urllib2.urlopen('https://raw.githubusercontent.com/wrobstory/vincent_map_data/master/world-countries.topo.json')
get_id = json.load(request)

geometries = get_id['objects']['world-countries']['geometries']
iso_codes = [x['id'] for x in geometries]
country_df = pd.DataFrame({'iso_a3': iso_codes}, dtype=str)

# First cmd line parameter is the organization id as specified by the organization id numbers on
# the AidData API
organization_id = int(sys.argv[1])
# Second cmd line parameter is the start year for the project data
start_year = int(sys.argv[2])
# Third cmd line parameter is the end year for the project data
end_year = int(sys.argv[3])

# Used for testing
# organization_id = 6
# start_year = 2004
# end_year = 2013


url = 'http://api.aiddata.org/aid/project?size=50&fo=' + str(organization_id)
organizations_url = 'http://api.aiddata.org/data/origin/organizations?'
json_orgs = json.load(urllib2.urlopen(organizations_url))
donating_org = ''

for org in json_orgs['hits']:
    if org['id'] == organization_id:
        donating_org = org['name']
        break

print 'Creating map for ' + donating_org

json_result = json.load(urllib2.urlopen(url))
num_projects = json_result['project_count']
year_range = getYearString(start_year, end_year)
count = 0
country_dict = {}
pbar = ProgressBar(maxval=num_projects).start()

# print str(num_projects)
while (count < num_projects):
    project_info = getProjectData(count, organization_id, year_range)
    for project in project_info['items']:
        if 'transactions' in project:
            for transactions in project['transactions']:
                if 'tr_receiver_country' in transactions and transactions['tr_receiver_country']['iso3'] != '':
                    donor = transactions['tr_funding_org']['name']
                    receiver = transactions['tr_receiver_country']['iso3']
                    amount = transactions['tr_constant_value']
                    if donor not in country_dict:
                        country_dict[donor] = {}
                    if receiver not in country_dict[donor]:
                        country_dict[donor][receiver] = amount
                    else:
                        country_dict[donor][receiver] += amount
    count += 50
    if(count < num_projects):
        pbar.update(count)
    else:
        to_add = num_projects - (count - 50)
        pbar.update(to_add)

# print country_dict[donating_org]
pbar.finish()

geo_data = [{'name': 'countries',
             'url': 'https://raw.githubusercontent.com/wrobstory/vincent_map_data/master/world-countries.topo.json',
             'feature': 'world-countries'}]

country_dict[donating_org] = addNonDonatedCountries(country_dict[donating_org], get_id)

receiving_df = pd.DataFrame(list(country_dict[donating_org].iteritems()), columns=['iso_a3', 'total_received'])

merged = pd.merge(receiving_df, country_df, on='iso_a3', how='inner')

vis = vincent.Map(data=merged, geo_data=geo_data, scale=1000, projection='patterson',
          data_bind='total_received', data_key='iso_a3',
          map_key={'countries': 'id'})

vis.legend(title="Donation Amount")
json_file_name = donating_org.replace(' ', '_') + '_donations.json'
png_file_name = donating_org.replace(' ', '_') + '_donations.png'
vis.to_json(json_file_name)
os.system("vg2png " + json_file_name + " " + png_file_name)

