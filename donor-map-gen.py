import pandas as pd
import json
import vincent
import urllib2
import socket
import os
import sys


timeout = 0.5
socket.setdefaulttimeout(timeout)

# Gets project data from AidData project api for an organization indicated by its AidData api id
def getProjectData(index, organization, years):
    url = 'http://api.aiddata.org/aid/project?size=50&fo=' + str(organization) + '&from=' + str(index) + '&y=' + str(years)
    while (True):
        try:
            result = json.load(urllib2.urlopen(url))
            break
        except:
            pass
    return result

# Adds countries that have not received donations to the list so that they can be displayed on the map
def addNonDonatedCountries(donor_dict, world):
    for country in world['objects']['world-countries']['geometries']:
        if country['id'] not in donor_dict:
            donor_dict[country['id']] = 0.0
    return donor_dict

# Creates a string of years to search in the api
def getYearString(start_year, finish_year):
    result = ''
    while start_year < finish_year:
        result += str(start_year)
        result += ','
        start_year += 1
    result += str(finish_year)
    return result

# A base map to be used by the map creator
request = urllib2.urlopen('https://raw.githubusercontent.com/mjvolk/Python-Visualizations/master/world-countries.topo.json')
get_id = json.load(request)

# create a dataframe of iso-3 codes in for use in builiding the map
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
# organization_id = 28
# start_year = 2003
# end_year = 2016

# Retrieves list of donor organizations and their IDs from AidData API
organizations_url = 'http://api.aiddata.org/data/origin/organizations?'
json_orgs = json.load(urllib2.urlopen(organizations_url))
donating_org = ''

# Finds the donating organization based on the id
for org in json_orgs['hits']:
    if org['id'] == organization_id:
        donating_org = org['name']
        break

print 'Creating map for ' + donating_org

# Gets total number of projects for a donor in the given time frame
json_result = getProjectData(0, organization_id, getYearString(start_year, end_year))
num_projects = json_result['project_count']
print 'Evaluating ' + str(num_projects) + ' projects'
year_range = getYearString(start_year, end_year)
count = 0
country_dict = {}

# Iterates over the projects from the AidData api in chunks of 50, the max size allowed by the api
while (count < num_projects):
    project_info = getProjectData(count, organization_id, year_range)
    for project in project_info['items']:
        # Only looks at projects that have transaction values
        if 'transactions' in project:
            for transactions in project['transactions']:
                # Ignores projects that don't indicate a recipient country
                if 'tr_receiver_country' in transactions and transactions['tr_receiver_country']['iso3'] != '':
                    donor = transactions['tr_funding_org']['name']
                    receiver = transactions['tr_receiver_country']['iso3']
                    amount = transactions['tr_constant_value']
                    # Adds donor to dictionary if it isn't there yet
                    if donor not in country_dict:
                        country_dict[donor] = {}
                    # Adds receiver to donors dictionary with amount if it has not appeared yet
                    if receiver not in country_dict[donor]:
                        country_dict[donor][receiver] = amount
                    # If the donor and receiver already exist, the receiver has the new project cost added
                    # to it's running total
                    else:
                        country_dict[donor][receiver] += amount
    count += 50
    print '{}/{}\r'.format(count, num_projects),

# Creates geo-data outline for vincent/vega operations
geo_data = [{'name': 'countries',
             'url': 'https://raw.githubusercontent.com/mjvolk/Python-Visualizations/master/world-countries.topo.json',
             'feature': 'world-countries'}]

# Adds countries to dictionary that were not donated to so they still appear on map
country_dict[donating_org] = addNonDonatedCountries(country_dict[donating_org], get_id)

# A dataframe of all iso3 codes with their associated recipient totals
receiving_df = pd.DataFrame(list(country_dict[donating_org].iteritems()), columns=['iso_a3', 'total_received'])

# Merges receiving_df with country_df for use with vincent/vega
merged = pd.merge(receiving_df, country_df, on='iso_a3', how='inner')

# Uses vincent to create a map in vega format
vis = vincent.Map(data=merged, geo_data=geo_data, scale=1000, projection='patterson',
          data_bind='total_received', data_key='iso_a3',
          map_key={'countries': 'id'})

vis.legend(title="Donation Amount")
# Creates file names to seperate different countries
json_file_name = donating_org.replace(' ', '_') + '_donations.json'
png_file_name = donating_org.replace(' ', '_') + '_donations.png'
vis.to_json(json_file_name)
# Transforms the vega json into a donor map image using the vg2png command line function
# Must have vega installed to work
os.system("vg2png " + json_file_name + " " + png_file_name)

