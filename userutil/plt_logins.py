#!/usr/bin/python

# Plots the user logins for the past 30 days

import numpy as np
import matplotlib.pyplot as plt
import subprocess
import datetime

from collections import Counter

wtmp_loc = './'
# number of days since today
history = 31
ignorenames = '[root,(unknown,system,reboot,wtmp]'
MonthMapping = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

# calculate the furthest date we would like to see records from
today =  datetime.date.today()
today_date = datetime.datetime(today.year, today.month, today.day)
#hist_date = hist_date.strftime('%Y:%m:%d')

#hist_year = int(hist_date.split(':')[0])
#hist_month = int(hist_date.split(':')[1])
#hist_day = int(hist_date.split(':')[2])

#print hist_year
#print hist_month
#print hist_day

# get the initial data
searchresult = subprocess.Popen("last -FRf " + wtmp_loc + "wtmp*", stdout=subprocess.PIPE, shell=True)

searchresult = searchresult.communicate()[0]

login_list = []

# print searchresult
m = searchresult.split('\n')

def create_list_sequential(n):
    "create a sequence of size n"
    new_list = []
    for i in range(n):
        new_list.append(i);
    return new_list 

def create_list_zeros(n):
    "create a list of n zeros"
    new_list = []
    for i in range(n):
        new_list.append(0)
    return new_list

def create_list_dates(start_date, n):
    "creates a list of n dates before and including start date"
    one_day = datetime.timedelta(days=1)
    current_day = start_date
    date_list = []
    for i in range(n):
        date_list.insert(0, (current_day))
        current_day = current_day - one_day
    return date_list

def create_user_map(n):
    "create a map from indices (0 to n-1) to a set of user names"
    user_map = {}
    for i in range (n):
        user_map[i] = set()
    return user_map

def unique_logins_perday(user_map):
     "computes the number of unique users per day from a map returned \
      by create_user_map(n)"
     days_list = create_list_zeros(len(user_map.keys()))
     for key in user_map.keys():
         days_list[key] = len(user_map[key])
     days_list.reverse()
     return days_list

def pad_list_zeros(lst, n):
    "appends n zeros to the list lst"
    for i in range(pad):
        lst.append(0)

# creates a map from indices (0 to history-1) to a set of user names 
user_map = create_user_map(history)

num_logins = create_list_zeros(history)
max_logins = 0;
number_of_logins = 0

for entry in m:
    username = entry.split(" ")[0]

    if username and username not in ignorenames:
        isuser = subprocess.Popen("getent passwd " + username,\
                  stdout=subprocess.PIPE, shell=True).communicate()[0]
        
        #print username + " " + isuser
        
        if isuser.count(':') == 6:
            #print username
            entry = ' '.join(entry.split())
        
            #print entry
            
            ent_year = entry.split(' ')[6] 
            ent_month = entry.split(' ')[3] 
            ent_day = entry.split(' ')[4] 

            #print ent_year + " " + ent_month + " " + ent_day

            ent_date = datetime.datetime.strptime(ent_month + " " + ent_day + " " + ent_year , '%b %d %Y')

            #print ent_date
            days_since_login = (today_date - ent_date).days
            if (days_since_login < history):
               login_list.append(username)
               number_of_logins += 1
               user_map[days_since_login].add(username)
               num_logins[days_since_login] = num_logins[days_since_login] + 1
               max_logins = max(max_logins, num_logins[days_since_login])
pad = 1
print number_of_logins
max_logins = max_logins + pad
num_unique_logins = unique_logins_perday(user_map)
dates_list = create_list_dates(datetime.date.today(), history)

num_logins.reverse()
N = len(Counter(login_list).keys())

#print datetime.date.today()
#width = 1/1.5
#plt.bar(range(len(Counter(login_list).keys())), Counter(login_list).values(), width, color='black', align='center')
xAxis = create_list_sequential(history)
#plt.plot(xAxis, num_logins,
#         xAxis,num_unique_logins)

# Get current size
fig_size = plt.rcParams["figure.figsize"]
 
# Prints: [8.0, 6.0]
print "Current size:", fig_size
 
# Set figure width to 12 and height to 9
fig_size[0] = 12
fig_size[1] = 9
plt.rcParams["figure.figsize"] = fig_size

fig, ax = plt.subplots()
index = np.arange(history)
bar_width = 0.35
opacity = 0.8
 
rects1 = plt.bar(index, num_logins, bar_width,
                 alpha=opacity,
                 color='b',
                 label='total logins')
 
rects2 = plt.bar(index + bar_width, num_unique_logins, bar_width,
                 alpha=opacity,
                 color='g',
                 label='unique logins')
 
plt.xlabel('date')
plt.ylabel('number of logins')
plt.title('logins')
plt.ylim((0,max_logins))
plt.xticks(index + bar_width, dates_list)
plt.legend()

# Make the date readable
fig.autofmt_xdate()

plt.tight_layout()
plt.show()
