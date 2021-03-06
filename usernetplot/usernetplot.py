#!/bin/python

# Creates two csv files for Gephi of groups and their users.
# One contains data for the nodes, the other for the edges.
# An input file needs to be given as an argument.
# This file should be generated with the following command:
# sacct --starttime MMDDYY -a -P -n -s CD -o User,Account,CPUTimeRAW > input_f
# Replace MMDDYY with the date of when you want data collected back to.
# This currently doesn't support nested groups.
import ldap
import csv
import sys
import uwyoldap
import getpass


# Options
groupsToSkip = ['arcc', 'arccinterns', 'bc-201606']

# ARCC employees are members of other projects/groups. If you want them
# displayed, set this to True.
includeARCCUsers = False

# If true, include username label's on username nodes.
# Even with them off, their ID's are still set to their username.
# These can be displayed in overview. but not preview.
# If you want them in preview, set this to True.
# This is off by default, because the plot is messy with them on.
usernamelabels = False


def getMemberCN(member):
    uidi = member.find("uid=")
    return (member[uidi+4:member.find(",", uidi)])


# LDAP Server
srv = 'ldap://arccidm1.arcc.uwyo.edu'


# Get cputime per user and account
# Assume that only argument will be the file with the cpu time data.
try:
    with open(sys.argv[1], 'r') as data:
        lines = data.readlines()
except:
    print "No input file given or file doesn't exist, exiting..."
    sys.exit()

users = {}
accts = {}
total = 0

# Read input file
for line in lines:
    line = line.strip().split('|')
    if line[0]:
        acct = line[1]
        user = line[0]
        cput = int(line[2])
        total += cput
        accts[acct] = accts.get(acct, 0) + cput
        users[user] = users.get(user, 0) + cput

username = raw_input('Username: ')
password = getpass.getpass()

try:
    uw_srv = uwyoldap.UWyoLDAP(username, password)
    del password
except ldap.INVALID_CREDENTIALS:
    print "Invalid Credientials"
    sys.exit()
except ldap.SERVER_DOWN:
    print "Server can't be reached."
    sys.exit()
except:
    print "An error has occurred."
    sys.exit()


max_users = float(max(users.values()))
max_accts = float(max(accts.values()))


# Setup connection to ldap server.
ad = ldap.initialize(srv)

# Make TLS connection to LDAP server.
# best practice is probably to try/except this.
ad.start_tls_s()
ad.simple_bind_s()

# Open up edges CSV file.
edgesf = open('edges.csv', 'wb')
edges = csv.writer(edgesf, delimiter=',')

# Edge files must have Target and Source as their header.
# The way this is set up, users will be the source, groups will be the target.
# To reverse this, simply switch Target and Source Below.
edges.writerow(["Target", "Source"])

# Open up nodes CSV file.
nodesf = open('nodes.csv', 'wb')
nodes = csv.writer(nodesf, delimiter=',')

# The nodes file holds the info on each node
# The ID can be anything, I've made it the group name/username
# The Label is the label of the node, it's what get displayed on the node
# Color is float between 0 or 1, used to make a heatmap
# The Size is just an integer that is used to set the size of the node
# The type distinguishes between group and user. Users are 0, groups are 1
nodes.writerow(["ID", "Label", "Color", "SizeN", "Type", "College"])

# Perform a search on the server to get subgroups of Mt Moran
# This returns a lot of information on the groups, including the users
base_dn = 'dc=arcc,dc=uwyo,dc=edu'
filt = 'memberOf=cn=mountmoran,cn=groups,cn=accounts,dc=arcc,dc=uwyo,dc=edu'
groups = ad.search_s(base_dn, ldap.SCOPE_SUBTREE, filt)

# Get a list of ARCC users from the ARCC Interns and ARCC groups.
# This is a really messy way of doing it with list comprehension.
#skip = [member for members in [group[1]['member'] for group in groups
#        if group[1]['cn'][0] == 'arcc' or group[1]['cn'][0] == 'arccinterns']
#        for member in members]
print len(groups)
for group in groups:
    # get the group name
    g_name = group[1]['cn'][0]

    collegeCount = {'Ag & Nat Resources': 0,
                    'Arts & Sciences': 0,
                    'Business': 0,
                    'Education': 0,
                    'Engineering': 0,
                    'Health Sciences': 0,
                    'Law': 0}

    # get a list of members of group (users and subgroups)
    # there's at least one group with no members, write it's row
    # and skip doing the member stuff for it.
    try:
        members = group[1]['member']
    except:
        row = [g_name, g_name, accts.get(g_name, 0)/max_accts, len(members) + 2, 1, '']
        continue

    # Skip groups in groupsToSkip.
    if g_name in groupsToSkip:
        continue

    # Write the info for the group in the node file.
    # The group name goes twice, because it's the label and ID.
    # Then goes the 'Color' field, which contains the CPU time used on Mt Moran
    # Last, there is the size field. It is the number of members in the group
    # plus 2 to make group nodes always larger then user nodes.
    members_cn = [getMemberCN(member) for member in members]
    uw_users = uw_srv.search(members_cn, uwyoldap.USER, uwyoldap.CN)
    rows = []
    #uw_users = uwyoldap.createLDAPObjDict(uw_users)
    # Go through the members, add them to the data file.
    for member in uw_users:
        # Skip ARCC Users if includeARCCUsers is False.
        if not includeARCCUsers and member.isARCCEmployee:
            continue
        col = member.getCollege()
        try:
            col = col[0]
        except:
            col = ''
        try:
            collegeCount[col] += 1
        except:
            pass
        # Write the edge from user to group.
        edges.writerow([g_name, member.cn])

        # Write the node info for the users
        row = [member.cn,
               member.cn if usernamelabels else " ",
               users.get(member.cn, 0)/max_users,
               1, 0]
        rows.append(row)
        #nodes.writerow(row)
    if len(set(collegeCount.values())) == 1:
        group_col = ''
    else:
        group_col = max(collegeCount, key=collegeCount.get)

    for row in rows:
        row.append(group_col)
        nodes.writerow(row)

    row = [g_name, g_name, accts.get(g_name, 0)/max_accts, len(members) + 2, 1, group_col]
    nodes.writerow(row)


# Close the CSV files
nodesf.close()
edgesf.close()

# Disconnect from the server
ad.unbind()
