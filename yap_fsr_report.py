import json
import re
import csv
import datetime

yap_json_file = open('yap.json')
#yap_report_rile = open('yap_report.csv',"a+")

rec_start_date = datetime.datetime.strptime('2021-08-27', '%Y-%m-%d')

calls = json.load(yap_json_file)
number_of_calls = 0
length = len(calls)
with open('yap_report.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    header = ['id','Start Time','End Time','Duration (seconds)','From','To','Call Events']
    writer.writerow(header)
    num_calls = len(calls)
    for call in reversed(calls):
        date_str = call['start_time'][0:10]
        if (datetime.datetime.strptime(date_str, '%Y-%m-%d') < rec_start_date):
           continue
        num_events = len(call['call_events'])
        i=1
        for event in call['call_events']:
            meta_str = event['meta']
            to_number = ""
            if re.match(r"^{\"to_number",meta_str):
                to_number = event['meta'][14:len(event['meta'])-2]  
                if(to_number[0] == '1' or to_number[0] == '+'):
                    to_number = to_number[1:]
                    if(to_number[0] == '1'):
                        to_number = to_number[1:]
            to_number = re.sub(r"[^0-9a-z\+]", "", to_number.lower())
            
            row = [call['id'],call['start_time'],call['end_time'],call['duration'],  \
                    call['from_number'],call['duration'],to_number,event['event_id']]
            writer.writerow(row)
            to_number = re.sub
yap_json_file.close()



