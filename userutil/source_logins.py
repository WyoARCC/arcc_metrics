#!/usr/bin/python

# Creates a pie chart of where users are logging in from (on campus and other.)

import matplotlib.pyplot as plt
import subprocess
import datetime
import sys
import argparse
import os.path


# Parse arguments
parser = argparse.ArgumentParser(
    description='Create pie chart of logins from campus versus otherwise \
                 using a specified wtmp file.')

parser.add_argument('-d', '--days', type=int, default=31,
                    help='The number of days in the past to collect data \
                    from (default: 31)')

parser.add_argument('-f', '--file', default='wtmp',
                    help='Location of wtmp file (default: ./wtmp)')

parser.add_argument('-l', '--last',
                    help='The last day for data to be collected in\
                          dd-mm-yyyy format (default: today)')

parser.add_argument('-c', '--config', default='userutil.conf',
                    help='Configuration file to use \
                          (default: ./userutil.conf)')

args = parser.parse_args()

history = args.days

# Check if the specified file exists, if not print an error and exit.
if os.path.isfile(args.file):
    wtmp_loc = args.file
else:
    print "File doesn't exist, use -h for help."
    sys.exit()


# Check if -l was given, if it wasn't, set last_day to today. If it was, use it
# to create a datetime object, throw an error if it doesn't work.
if args.last:
    try:
        last_day = datetime.datetime.strptime(args.last, '%d-%m-%Y')
    except:
        print "Day must be in dd-mm-yyyy format, use -h for help."
        sys.exit()
else:
    last_day = datetime.datetime.today()

# Parse the config file
if os.path.isfile(args.config):
    with open(args.config, 'r') as config:
        lines = config.readlines()
else:
    print "Config file doesn't exist, use -h for help."


for line in lines:
    line = line.strip()
    if not line.startswith('#'):  # if not a comment
         # find ignored users.
        if line.startswith('ignore'):
            # Delete all whitespace
            line = ''.join(line.split())
            # Get the list of users to ignore
            ignorenames = line[7:].split(",")


# Get the initial data.
# -i displays IP
# -f specifies file
# -F prints full login dates
searchresult = subprocess.Popen("last -i -F -f" + wtmp_loc,
                                stdout=subprocess.PIPE, shell=True)
searchresult = searchresult.communicate()[0]
m = searchresult.split('\n')

logins_from_campus = 0
logins_from_home = 0
total_logins = 0

for entry in m:
    username = entry.split(" ")[0]

    # Check if username exists and that it's not in ignorenames.
    if username and username not in ignorenames:
        entry = ' '.join(entry.split())

        ent_year = entry.split(' ')[7]
        ent_month = entry.split(' ')[4]
        ent_day = entry.split(' ')[5]
        ent_ip = entry.split(' ')[2]

        #print ent_year + " " + ent_month + " " + ent_day

        ent_date = datetime.datetime.strptime((ent_month
                                               + " " + ent_day
                                               + " " + ent_year),
                                              '%b %d %Y')

        days_since_login = (last_day - ent_date).days
        # Ignore local logins.
        if ((days_since_login < history) and ent_ip != "0.0.0.0"):
            # Logins coming from an IP with a first octet of 10 are considered
            # as coming from campus
            if ent_ip.startswith("10."):
                logins_from_campus += 1
            else:
                logins_from_home += 1
            total_logins += 1


print "Logins from Campus: " + str(logins_from_campus)
print "Logins from off Campus: " + str(logins_from_home)
print "Total Logins: " + str(total_logins)

fig_size = plt.rcParams["figure.figsize"]

# Set figure width to 9 and height to 9
fig_size[0] = 9
fig_size[1] = 9

plt.rcParams["figure.figsize"] = fig_size


# Generate the pi chart, with labels.
# Autopct can take a function as an argument and it passes the percent to it,
# and the percent needs to be turned back into the actual data
plt.pie([logins_from_campus, logins_from_home],
        labels=["Campus", "Other"],
        colors=["b", "g"],
        autopct=lambda(a): '{:g}'.format(a * total_logins / 100))


#plt.tight_layout()
plt.legend()
plt.show()
