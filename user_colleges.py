#!/bin/python


# Create a bar graph of the number of users on Mt Moran for each college. The information comes from ARCC's ldap server and UWyo's AD server.
# Requires ldap, matplotlib, numpy

import ldap
import getpass
import re
import matplotlib.pyplot as plt
import numpy as np
from sys import exit


# Whether or not college with no users are displayed or not.
includeZeros = False


# Servers
arcc_ldap = 'ldaps://arccidm1.arcc.uwyo.edu'
uwyo_ldap = 'ldaps://windows.uwyo.edu'


# Prompt for username and password
username = raw_input("Username for UWyo AD Server: ")
password = getpass.getpass()

# Init ldap
arcc_d = ldap.initialize(arcc_ldap)
uwyo_d = ldap.initialize(uwyo_ldap)

# The UWyo AD server has a self-signed cert (I think), which throws an error without this option.
uwyo_d.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

# Connect to UWyo first, because if it fails the script fails
try:
    uwyo_d.simple_bind_s(username, password)
    del password
except ldap.INVALID_CREDENTIALS:
    uwyo_d.unbind()
    print "Invalid Credentials"
    exit()

# Connect to ARCC ldap server, it supports anonymous searches, so no need for credentials. Also, it seems to not have a self-signed cert, because it doesn't need the option that was set for the UWyo AD server.
arcc_d.simple_bind_s()

# Perfrom the search
base = 'dc=arcc,dc=uwyo,dc=edu'
filt = 'cn=mountmoran'
mtmoran = arcc_d.search_s(base, ldap.SCOPE_SUBTREE, filt)
arcc_d.unbind()

# Pull users out
users = mtmoran[0][1]['memberUid']

# Get the user information from the UWyo AD server in one request.
base = 'cn=Users,dc=windows,dc=uwyo,dc=edu'
filt = '(|(cn=' + '(cn='.join("{})".format(user) for user in users) + ')' 
userinfo = uwyo_d.search_s(base, ldap.SCOPE_SUBTREE, filt)

collegeCount = {'Ag & Nat Resources' : 0, 'Arts & Sciences' : 0, 'Business' : 0, 'Education' : 0, 'Engineering' : 0, 'Health Sciences' : 0, 'Law' : 0, 'Undergraduate' : 0}

colleges = {}
colleges['Undergraduate'] = set()
base = 'dc=windows,dc=uwyo,dc=edu'
attr = ['memberOf']

# Filter out ARCC users by their department. I probably shouldn't have done this in one line, it's messy
userinfo = filter(lambda x: 'department' not in x[1] or ('IT-Research Support' not in x[1]['department'][0]) and ('IT/Research Support' not in x[1]['department'][0]), userinfo)

for user in userinfo:
    memberOf = user[1]['memberOf']
    # Get a list of just the group names that the member belongs too
    #groups = [re.search('CN=(.*?),', member).group(1) for member in memberOf]
    username = re.search('CN=(.*?),',user[0]).group(1)
    foundCol = False
    for member in memberOf:
        # Get just the cn of the group
        group = re.search('CN=(.*?),', member).group(1)
        # The groups that indicate what department they are in begin with DEPT_
        if group.startswith("DEPT_"):
            # Create a filter to query the info for the group with
            filt = 'cn=' + group
            groupinfo = uwyo_d.search_s(base, ldap.SCOPE_SUBTREE, filt, attr)
            # Get just the cn of the group (this group is the college)
            col = re.search('CN=(.*?),',groupinfo[0][1]['memberOf'][0]).group(1)
            # All of the college groups have DIV_ in front of them, so remove it.
            col = col[4:]
            if col.startswith('College of '):
                col = col[len('College of '):]
            # If the entry in the dictionary doesn't exist, create it
            if col not in colleges:
                colleges[col] = set()
            colleges[col].add(username)
            foundCol = True
    
    # Can't get the users's college, this means they are probably undergrad students
    if not foundCol:
        colleges['Undergraduate'].add(username)

# Put the number of users in each college in collegeCount, also get a total number of user's
total = 0
for college in colleges:
    if college in collegeCount:
        collegeCount[college] = len(colleges.get(college))
        total += len(colleges.get(college))

if not includeZeros:
    collegeCount = {k:v for k,v in collegeCount.iteritems() if v != 0}

# This fixes the fact that some people don't show up in an actual college, but they are in other things that are in the colleges dictionary. They need to be added to undergrads.
collegeCount['Undergraduate'] = collegeCount.get('Undergraduate') + (len(userinfo) - total)

x = np.arange(len(collegeCount))
rects = plt.bar(x, collegeCount.values(), width = 0.5, align = 'center')
plt.title('Number of Mt. Moran Users per College')
plt.xlabel('College')
plt.ylabel('Number of Users')
plt.xticks(x, collegeCount.keys(), rotation=80)
plt.subplots_adjust(bottom=0.35)
# Add the values to the top of the bars
for rect in rects:
    h = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2., 1 + h, '%d' % int(h), ha = 'center', va = 'bottom')


plt.show()

print collegeCount
print total
uwyo_d.unbind()


