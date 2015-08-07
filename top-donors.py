import pandas as pd
import json
import urllib2
import socket
import csv
import sys


timeout = 1
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

# Creates a string of years to search in the api
def getYearString(start_year, finish_year):
    result = ''
    while start_year < finish_year:
        result += str(start_year)
        result += ','
        start_year += 1
    result += str(finish_year)
    return result



# First cmd line parameter is the organization id as specified by the organization id numbers on
# the AidData API
# topX = int(sys.argv[1])
# # Second cmd line parameter is the start year for the project data
# start_year = int(sys.argv[2])
# # Third cmd line parameter is the end year for the project data
# end_year = int(sys.argv[3])

# Used for testing
topX = 10
start_year = 2005
end_year = 2010

result = list()
header = list()
header.append('Donor')
for x in range(topX):
    header.append('Receiver ' + str(x+1))
    header.append('Amount ' + str(x+1))
result.append(header)
file_name = 'Top' + str(topX) + 'DonorsFor' + str(start_year) + '-' + str(end_year) + '.csv'
file = open(file_name, 'wb')
csv_file = csv.writer(file)


organizations_url = 'http://api.aiddata.org/data/origin/organizations?'
while(True):
    try:
        json_orgs = json.load(urllib2.urlopen(organizations_url))
        break
    except:
        pass

# Finds the donating organization based on the id
for org in json_orgs['hits']:
    donating_org = org['name']
    url = 'http://api.aiddata.org/aid/project?size=50&fo=' + str(org['id'])
    print 'Evaluating projects for ' + donating_org

    while(True):
        try:
            json_result = getProjectData(0, org['id'], getYearString(start_year, end_year))
            break
        except:
            pass
    num_projects = json_result['project_count']
    print str(num_projects) + ' projects'
    year_range = getYearString(start_year, end_year)
    count = 0
    country_dict = {}

    if num_projects > 0:

        # Iterates over the projects from the AidData api in chunks of 50, the max size allowed by the api
        while (count < num_projects):
            project_info = getProjectData(count, org['id'], year_range)
            for project in project_info['items']:
                # Only looks at projects that have transaction values
                if 'transactions' in project:
                    for transactions in project['transactions']:
                        # Ignores projects that don't indicate a recipient country
                        if 'tr_receiver_country' in transactions and 'iso3' in transactions['tr_receiver_country'] and transactions['tr_receiver_country']['iso3'] != '':
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
            print '{}/{}\r'.format(count, num_projects),

        # Double check to make sure the donor has donated in the given years
        if donating_org in country_dict:
            # Puts donor data into a pandas dataframe and sorts it by amount donated
            receiving_df = pd.DataFrame(country_dict[donating_org].items(), columns=['recipient', 'amount'])
            receiving_df = receiving_df.sort(columns=['amount'], ascending=False)

            temp = list()
            temp.append(donating_org)

            # Adds in the topX donors into a new row of the result list
            for row in receiving_df[:topX].index:
                temp.append(receiving_df.ix[row]['recipient'])
                temp.append(receiving_df.ix[row]['amount'])

            result.append(temp)

# Writes each row of the result list as a new row of a csv
csv_file.writerows(result)
