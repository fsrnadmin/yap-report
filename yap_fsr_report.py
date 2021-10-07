import json
import re
import csv

from datetime import *
from urllib.request import urlopen
import mysql.connector
import yapReportCalendar  
import calendar
    

shifts = [['Monday',0,7.5],['Monday',7.5,13],['Monday',13,17],['Monday',17,23],['Tuesday',0,7.5],['Tuesday',7.5,13],['Tuesday',13,17],['Tuesday',17,23],['Tuesday',0,7], \
          ['Wednesday',0,7.5],['Wednesday',7.5,13],['Wednesday',13,17],['Wednesday',17,23],['Thursday',0,7.5],['Thursday',7.5,13],['Thursday',13,17],['Thursday',17,23], \
          ['Friday',0,7.5],['Friday',7.5,13],['Friday',13,17],['Friday',17,23],['Saturday',0,7.5],['Saturday',7.5,13],['Saturday',13,17],['Saturday',17,23], \
          ['Sunday',0,7.5],['Sunday',7.5,13],['Sunday',13,17],['Sunday',17,23]]
row = []
vol_no_answer = []
vol_rej = []
shifts_missing_call = []
str_status = ""
str_comment = ""
num_meta = []
meta_str = []
#yap_json_file = open('yap.json')
#yap_report_rile = open('yap_report.csv',"a+")


#day stuff

weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

url = "https://freestatena.org/yap/admin/cdr_api.php?service_body_id=31&page=1&size=20000"
response = urlopen(url)
calls = json.loads(response.read())
#monthToReport = '10/27/21'
monthToReport = yapReportCalendar.getDate()
rec_start_date = monthToReport + "-" + "01"
edate = datetime.strptime(rec_start_date,"%Y-%m-%d")
d = edate.replace(day = calendar.monthrange(edate.year, edate.month)[1])
rec_end_date = d.strftime("%Y") + "-" + d.strftime("%m") + "-" + d.strftime("%d")
number_of_calls = 0
with open('yap_report.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    header = ['id','Start Time','End Time','Duration (seconds)','From','To','Call Events','Comment']
    writer.writerow(header)
    
    num_calls = len(calls)
    row = ["Number of calls:",num_calls]
    writer.writerow(row)
    #num_calls = 0
    for call in reversed(calls['data']):
        date_str = call['start_time'][0:10]
        date_str_ms = int(round(datetime.strptime(date_str, '%Y-%m-%d').timestamp() * 1000))
        rec_start_ms = int(round(datetime.strptime(rec_start_date, '%Y-%m-%d').timestamp() * 1000))
        if (date_str_ms >= rec_start_ms):
           continue
        if (datetime.strptime(date_str, '%Y-%m-%d') <= datetime.strptime(rec_end_date,'%Y-%m-%d')):
            break
        num_events = len(call['call_events'])
        i=1
        real_call=0
        for event in reversed(call['call_events']):
            meta_str = json.loads(event['meta'])
            to_number = ""
            str_comment = ""
            if 'to_number' in meta_str:
                to_number = meta_str['to_number']
            if (event['event_id'] == 'Volunteer No Answer'):
                vol_no_answer.append(to_number)
                str_comment = "NOAN"
            elif (event['event_id'] == "Volunteer Rejected Call"):
                vol_rej.append(to_number)
                str_comment = "VOLREJ"
            elif (event['event_id'] == "Volunteer Connected To Caller"):
                real_call = 1
                #num_calls += 1
            elif (event['event_id'] == "Caller Hungup"):
                if real_call == 0:
                   str_comment = "CALHUNG"
                   continue

            row = [call['id'],call['start_time'],call['end_time'],call['duration'],  \
                    call['from_number'],to_number,event['event_id'],str_comment]
            writer.writerow(row)
    row = ["Number of calls:",num_calls]
    writer.writerow(row)
    num_ignored_calls = len(vol_no_answer)
    uniqueVolNoAnswer = []
    for vol in vol_no_answer:
        if vol not in uniqueVolNoAnswer:
           uniqueVolNoAnswer.append(vol)
    row = ['Volunteers who didn\'t answer','Count','','','','','','','']
    writer.writerow(row)
    row = ['----------------------------','-----','','','','','','','']
    writer.writerow(row)
    for vol in uniqueVolNoAnswer:
        row = [vol,vol_no_answer.count(vol),'','','','','','','']
        writer.writerow(row)
    row = ['Volunteers who rejected calls','Count','','','','','','','']
    writer.writerow(row)
    row = ['----------------------------','-----','','','','','','','']
    uniqueVolRejected = []
    for vol in vol_rej:
        if vol not in uniqueVolRejected:
           uniqueVolRejected.append(vol)
    for vol in uniqueVolRejected:
       row = [vol,vol_rej.count(vol),'','','','','','','']
       writer.writerow(row)
    
    row = ['total calls','','','','','','','','']
    writer.writerow(row)
    row = ['----------------------------','-----','','','','','','','']
    row = [num_calls,'','','','','','','','']
    writer.writerow(row)

    row = ['rejected calls','','','','','','','','']
    writer.writerow(row)
    row = ['----------------------------','-----','','','','','','','']
    row = [len(vol_rej),'','','','','','','','']
    writer.writerow(row)


    row = ['rej/total calls','','','','','','','','']
    writer.writerow(row)
    
    floatInString = round(len(uniqueVolRejected)/num_calls,3)
    format_float = "{:.2f}".format(floatInString)
    row = [str(format_float),'','','','','','','']

    writer.writerow(row)
yap_json_file.close()
