#!/usr/bin/python

# Creates a pie chart of active vs inactive users.
# Config file must contain group to get users from and opionally contain a list
# of users to ignore (which is recommended so things like root, unknown,
# reboot, etc. are ignored)

import matplotlib.pyplot as plt
import subprocess
import datetime
import sys
import argparse
import os.path


# Parse arguments, trying to follow PEP8 line width here,
# but I feel like it just made the code harder to read.
parser = argparse.ArgumentParser(
    description='Create pie chart of active users versus inactive users.')

parser.add_argument('-d', '--days',
                    type=int, default=31,
                    help='The number of days back to be \
                    considered active (default : 31)')

parser.add_argument('-f', '--file', default='wtmp',
                    help='wtmp file to use (default: ./wtmp)')

parser.add_argument('-c', '--config', default='userutil.conf',
                    help='Configuration file to use \
                    (default: ./userutil.conf)')

args = parser.parse_args()

history = args.days

# Check if the specified file exists, if not print an error and exit.
if os.path.isfile(args.file):
    wtmp_loc = args.file
else:
    print "Specified wtmp file doesn't exist, use -h for help."
    sys.exit()


last_day = datetime.datetime.today()


# Parse the config file
if os.path.isfile(args.config):
    with open(args.config, 'r') as config:
        lines = config.readlines()
else:
    print "Config file doesn't exist, use -h for help."
    sys.exit()

for line in lines:
    line = line.strip()
    if not line.startswith('#'):  # if not a comment
        # find ignored users.
        if line.startswith('ignore'):
            # Remove all whitespace
            line = ''.join(line.split())
            # Get the list of users to ignore
            ignorenames = line[7:].split(",")

        # get the group to pull a list of users from
        if line.startswith('group'):
            line = ''.join(line.split())
            # Get the name of the group
            group = line[6:]


# Get the initial data.
# -i displays IP
# -f specifies file
# -F prints full login dates
searchresult = subprocess.Popen('last -i -F -f' + wtmp_loc,
                                stdout=subprocess.PIPE, shell=True)

searchresult = searchresult.communicate()[0]

m = searchresult.split('\n')


# get all of the users currently in the mountmoran group
users = subprocess.Popen('getent group ' + group,
                         stdout=subprocess.PIPE, shell=True)

users = users.communicate()[0]

# Getent group is colon seperated with the 4th item being the list of users,
# so, get that, strip trailing whitespace (there's a newline), and then
# create a list of users.
users = users.split(':')[3].strip().split(',')

# Remove users that are in ignorenames from the list of users.
for name in ignorenames:
    if name in users:
        users.remove(name)

active_users = []
inactive_users = []

for entry in m:
    username = entry.split(" ")[0]

    # Check if username exists and that it's not in ignorenames,
    # and that is's in the list users (so in the group from the config)
    if username and username in users and username not in ignorenames:
        entry = ' '.join(entry.split())
        ent_year = entry.split(' ')[7]
        ent_month = entry.split(' ')[4]
        ent_day = entry.split(' ')[5]

        ent_date = datetime.datetime.strptime((ent_month
                                               + " " + ent_day
                                               + " " + ent_year), '%b %d %Y')

        days_since_login = (last_day - ent_date).days
        if (days_since_login < history):
            active_users.append(username)

# All the users that aren't active are inactive
for user in users:
    if user not in active_users:
        inactive_users.append(user)

# Turn the list of active users into a set of active users to remove duplicates
active_users = set(active_users)

print "Number of Users: " + str(len(users))
print "Number of Active Users " + str(len(active_users))
print "Number of Inactive Users: " + str(len(inactive_users))


fig_size = plt.rcParams["figure.figsize"]

# Prints: [8.0, 6.0]

# Set figure width to 9 and height to 9
fig_size[0] = 9
fig_size[1] = 9

plt.rcParams["figure.figsize"] = fig_size


# Generate the pi chart, with labels. autopct can take a function
# as an argument and it passes the percent to it, and the percent
# needs to be turned back into the actual data
plt.pie([len(active_users), len(inactive_users)],
        labels=["Active", "Inactive"], colors=["b", "g"],
        autopct=lambda(a): '{:g}'.format(a * len(users) / 100))


#plt.tight_layout()
plt.legend()
plt.show()
