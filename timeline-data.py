import urllib2
import json
import pandas as pd
import progressbar as pbar


def getDonorData(donor, yearlist, index):
    url = 'http://api.aiddata.org/aid/project?fo=' + str(donor) + '&size=50&y=' + yearlist + '&from=' + str(index)
    result = json.load(urllib2.urlopen(url))
    return result

def getYearString(start_year, finish_year):
    result = ''
    while start_year < finish_year:
        result += str(start_year)
        result += ','
        start_year += 1
    result += str(finish_year)
    return result

organization_id = 6
start_year = 2000
end_year = 2010
yearlist = getYearString(start_year, end_year)

num_projects = getDonorData(organization_id, yearlist, 0)['project_count']
count = 0
year_dict = {}

while(count < num_projects):
    source_info = getDonorData(organization_id, yearlist, count)
    for source in source_info['items']:
        if 'transactions' in source and int(source['transactions'][0]['tr_year']) >= start_year:
            if int(source['transactions'][0]['tr_year']) not in year_dict:
                year_dict[int(source['transactions'][0]['tr_year'])] = list()
            if source['source']['label'] not in year_dict[int(source['transactions'][0]['tr_year'])]:
                year_dict[int(source['transactions'][0]['tr_year'])].append(source['source']['label'])
    count += 50

print year_dict
max_sources = 0
for year in year_dict:
    if len(year_dict[year]) > max_sources:
        max_sources = len(year_dict[year])
for year in year_dict:
    if len(year_dict[year]) < max_sources:
        while len(year_dict[year]) < max_sources:
            year_dict[year].append(None)
dates_and_sources = pd.DataFrame(year_dict)
dates_and_sources.to_csv('dates_and_sources.csv')
# dates_and_sources.to_csv('dates_and_sources.csv')

# year_dict = {}
# index = 0
# for year in dates_and_sources['Years']:
#     if year not in year_dict:
#         year_dict[year] = list()
#     if dates_and_sources['Sources'][index] not in year_dict[year]:
#         year_dict[year].append(dates_and_sources['Sources'][index])
#     index += 1




# dates_and_sources = list()
# source = [datetime(2012, 1, 1), 'OECD']
# source2 = [datetime(2011, 1, 1), 'OECD']
# dates_and_sources.append(source)
# dates_and_sources.append(source2)
# dates_and_sources.sort()
# # print dates_and_sources
# df = pd.DataFrame(dates_and_sources, columns=['Date', 'Source'])
# print df