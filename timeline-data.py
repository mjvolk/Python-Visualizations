import urllib2
import json
import pandas as pd
import socket
from progressbar import ProgressBar


timeout = 4
socket.setdefaulttimeout(timeout)

def getDonorData(donor, yearlist, index):
    url = 'http://api.aiddata.org/aid/project?fo=' + str(donor) + '&size=50&y=' + yearlist + '&from=' + str(index) + '&src=1,2,3,4,5,6,7,3249668'
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

def getStartYears(year_list):
    result = list()
    current_start = year_list[0]
    previous_year = year_list[0]
    for year in year_list:
        if year != year_list[0]:
            if year == previous_year+1:
                previous_year = year
            else:
                result.append(current_start)
                current_start = year
                previous_year = year
    result.append(current_start)
    return result

def getEndYears(year_list):
    result = list()
    current_end = year_list[0]
    previous_year = year_list[0]
    for year in year_list:
        if year != year_list[0]:
            if year == previous_year+1:
                previous_year = year
                current_end = year
            else:
                result.append(current_end)
                current_end = year
                previous_year = year
    result.append(year_list[len(year_list)-1])
    return result

start_year = 1900
end_year = 2020
yearlist = getYearString(start_year, end_year)
json_orgs = json.load(urllib2.urlopen('http://api.aiddata.org/data/origin/organizations?'))
index = 0

for org in json_orgs['hits']:
    organization_id = org['id']
    donating_org = org['name']
    print 'Creating Timeline for ' + donating_org
    num_projects = getDonorData(organization_id, yearlist, 0)['project_count']
    print 'Processing ' + str(num_projects) + ' projects'
    count = 0
    year_dict = {}


    while(count < num_projects):
        while (True):
            try:
                source_info = getDonorData(organization_id, yearlist, count)
                break
            except socket.timeout:
                print 'Timeout: retrying API call'
        for source in source_info['items']:
            if 'transactions' in source and int(source['transactions'][0]['tr_year']) >= start_year:
                year = int(source['transactions'][0]['tr_year'])
                current_source = source['source']['label']
                if current_source not in year_dict:
                    year_dict[current_source] = list()
                if year not in year_dict[current_source]:
                    year_dict[current_source].append(year)
                    year_dict[current_source].sort()
        count += 50
        print str(count)


    # print year_dict
    timeline_dict = {}
    for source in year_dict:
        timeline_dict[source] = {}
        timeline_dict[source]['Start'] = getStartYears(year_dict[source])
        timeline_dict[source]['End'] = getEndYears(year_dict[source])


    dates_and_sources = pd.DataFrame(timeline_dict)
    file_name = 'src_timelines/' + donating_org.replace(' ', '_') + '_source_timeline.json'
    dates_and_sources.to_json(file_name)
    index += 1
    print str(index) + ' out of 100 completed'
