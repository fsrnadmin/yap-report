import json
import re
import csv
import phonenumbers

from datetime import *
from urllib.request import urlopen
import mysql.connector
import yapReportCalendar  
import calendar
import os

shifts = [['Monday',0,7.5],['Monday',7.5,13],['Monday',13,17],['Monday',17,23],['Tuesday',0,7.5],['Tuesday',7.5,13],['Tuesday',13,17],['Tuesday',17,23],['Tuesday',0,7], \
          ['Wednesday',0,7.5],['Wednesday',7.5,13],['Wednesday',13,17],['Wednesday',17,23],['Thursday',0,7.5],['Thursday',7.5,13],['Thursday',13,17],['Thursday',17,23], \
          ['Friday',0,7.5],['Friday',7.5,13],['Friday',13,17],['Friday',17,23],['Saturday',0,7.5],['Saturday',7.5,13],['Saturday',13,17],['Saturday',17,23], \
          ['Sunday',0,7.5],['Sunday',7.5,13],['Sunday',13,17],['Sunday',17,23]]
chairmans_list = ['4109004821','4438269387','14109004821','14438269387','+14109004821','+14438269387']
row = []
vol_no_answer = []
vol_rej = []
vol_missed = []
vol_answered = []
voicemails = []
str_status = ""
str_comment = ""
num_meta = []
meta_str = []
is_missed_call = 0
#yap_json_file = open('yap.json')
#yap_report_rile = open('yap_report.csv',"a+")

#day stuff

#states
call_connected = False
call_missed=False
call_noanswer = False

state=""

num_calls_missed = 0

weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")

url = "https://freestatena.org/yap/admin/cdr_api.php?service_body_id=31&page=1&size=20000"
response = urlopen(url)
calls = json.loads(response.read())
#monthToReport = '2021-10'
monthToReport = yapReportCalendar.getDate()
rec_start_date = monthToReport + "-" + "01"
edate = datetime.strptime(rec_start_date,"%Y-%m-%d")
d = edate.replace(day = calendar.monthrange(edate.year, edate.month)[1])
rec_end_date = d.strftime("%Y") + "-" + d.strftime("%m") + "-" + d.strftime("%d")
number_of_calls = 0
if not os.path.exists('C:\\temp\\yap'):
   os.mkdir("C:\\temp\\yap")
os.chdir("C:\\temp\\yap")
filename = 'yap_' + str(monthToReport) +"_report.csv"
with open(filename, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    header = ['id','Start Time','End Time','Duration (seconds)','From','To','Call Events','Comment']
    writer.writerow(header)
    
    num_calls = 0
    for call in reversed(calls['data']):
        date_str = call['start_time'][0:10]
        date_str_ms = int(round(datetime.strptime(date_str, '%Y-%m-%d').timestamp() * 1000))
        rec_start_ms = int(round(datetime.strptime(rec_start_date, '%Y-%m-%d').timestamp() * 1000))
        if (date_str_ms < rec_start_ms):
           continue
        if (datetime.strptime(date_str, '%Y-%m-%d') > datetime.strptime(rec_end_date,'%Y-%m-%d')):
            break
        num_events = len(call['call_events'])
        i=1
        call_connected = False
        call_missed = False
        num_calls += 1
        event_ph_numbers = []
        to_number = ""
        str_comment = ""
        event_no = 0
        for event in reversed(call['call_events']):
            event_no+=1
            meta_str = json.loads(event['meta'])
            if 'to_number' in meta_str:
                to_number = meta_str['to_number']
                to_number = str(phonenumbers.parse(to_number,"US").national_number)
                if to_number == '':
                    continue
            if to_number in chairmans_list:
                continue
            if call['from_number'] in chairmans_list:
                continue
            event_ph_numbers.append(to_number)
            str_comment = ""
            if (event['event_id'] == 'Volunteer No Answer'):
                vol_no_answer.append(to_number)
                state = "Volunteer No Answer"
            elif (event['event_id'] == "Volunteer Answered"):
                call_answered=True
            elif (event['event_id'] == "Volunteer Connected To Caller"):
                call_connected=True
                state = "Volunteer Connected To Caller"
                vol_answered.append(to_number)
            elif (event['event_id'] == "Volunteer Answered but Caller Hungup"):
                state = "Volunteer Answered but Caller Hungup"
            elif (event['event_id'] == "Volunteer Rejected Call"):
                state = "Volunteer Rejected Call"
                vol_rej.append(to_number)
                str_comment = "VOLREJ"
            elif (event['event_id'] == "Volunteer Hungup"):
                   state = "Volunteer Hungup"
            elif (event['event_id'] == "Caller Hungup"):
                   state = "Caller Hungup"
            elif (event['event_id'] == "Voicemail"):
                # add all numbers to missed call list, cuz they all missed the calls
                voicemails.append(meta_str['url'])
                call_missed = True
            
            if (event_no == len(call['call_events'])):
                if (call_missed == True): 
                    event_ph_numbers = list(dict.fromkeys(event_ph_numbers))
                    vol_missed.extend(event_ph_numbers)
                    str_comment = "MISSED_CALL"
                    num_calls_missed+=1
                elif state == "Volunteer Answered but Caller Hungup":
                    str_comment = "CALLER HUNG UP"
                elif state == "Caller Hungup":
                    if (call_connected == False):
                           if(call['call_events'][1]['event_id'] == "Volunteer Dialed"):
                                str_comment = "CALLER HUNG UP"
                    elif call_connected == True:
                           str_comment = "CONNECTED CALL"
                    else:
                           str_comment = "MISSED CALL"
                           num_calls_missed+=1
                elif state == "Volunteer Hungup":
                    if call_connected == True:
                            str_comment = "CONNECTED CALL"
                elif state == "Voicemail":
                    str_comment = "MISSED_CALL"
                    num_calls_missed+=1
                        
            row = [call['id'],call['start_time'],call['end_time'],call['duration'],  \
                    call['from_number'],to_number,event['event_id'],str_comment]
            writer.writerow(row)        
            #if (call_missed == True): 
            #        vol_missed.extend(event_ph_numbers)
    #row = ["number of calls:",num_calls]
    #writer.writerow(row)
    #vol_no_answer = list(dict.fromkeys(vol_no_answer))
    #num_ignored_calls = len(vol_no_answer)
    ##for vol in vol_no_answer:
    #    if vol not in uniqueVolNoAnswer:
    #       uniqueVolNoAnswer.append(vol)
    #row = ['Volunteers(no answer)','Count','','','','','','','']
    #writer.writerow(row)
    #row = ['-----','------','-----','','','','','','','']
    #writer.writerow(row)
    #for vol in uniqueVolNoAnswer:
    #    row = [vol,vol_no_answer.count(vol),'','','','','','','']
    #    writer.writerow(row)
    row = ['Volunteers(rejected calls)','Count','','','','','','','']
    writer.writerow(row)
    row = ['-----','------','-----','','','','','','','']
    writer.writerow(row)
    uniqueVolRejected = []
    for vol in vol_rej:
        if vol not in uniqueVolRejected:
           uniqueVolRejected.append(vol)
    for vol in uniqueVolRejected:
       row = [vol,vol_rej.count(vol),'','','','','','','']
       writer.writerow(row)
    
    row = ['total calls','','','','','','','','']
    writer.writerow(row)
    row = ['-----','------','-----','','','','','','','']
    writer.writerow(row)
    row = [num_calls,'','','','','','','','']
    writer.writerow(row)

    row = ['missed calls','','','','','','','','']
    writer.writerow(row)
    row = ['-----','------','-----','','','','','','','']
    writer.writerow(row)
    row = [num_calls_missed,'','','','','','','','']
    writer.writerow(row)
    row = ['missed/total calls','','','','','','','','']
    writer.writerow(row)
    floatInString = round(num_calls_missed*100/num_calls,3)
    format_float = "{:.2f}".format(floatInString)
    row = [str(format_float) +"%",'','','','','','','']
    writer.writerow(row)
    row = ['rejected calls','','','','','','','','']
    writer.writerow(row)
    row = ['-----','------','-----','','','','','','','']
    writer.writerow(row)
    row = [len(vol_rej),'','','','','','','','']
    writer.writerow(row)
    row = ['rej/total calls','','','','','','','','']
    writer.writerow(row)
    
    floatInString = round(len(uniqueVolRejected)*100/num_calls,3)
    format_float = "{:.2f}".format(floatInString)
    row = [str(format_float) + "%",'','','','','','','']

    writer.writerow(row)

    row = ['Voicemails','','','','','','','','']
    writer.writerow(row)
    row = ['-----','------','-----','','','','','','','']
    writer.writerow(row)
    for vm in voicemails:
        row = ['','','','','','',vm]
        writer.writerow(row)


f.close()
