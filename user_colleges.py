#!/bin/python

# Create a bar graph of the number of users on Mt Moran for each college.
# The information comes from ARCC's ldap server and UWyo's AD server.
# Requires ldap, matplotlib, numpy

import uwyoldap
import getpass
import matplotlib.pyplot as plt
import numpy as np
import ldap
from sys import exit


# Whether or not colleges with no users are displayed or not.
includeZeros = False

# Servers
arcc_ldap = 'ldaps://arccidm1.arcc.uwyo.edu'

# Prompt for username and password. Username should be domain\user format
username = raw_input("Username for UWyo AD Server: ")
password = getpass.getpass()

# Init ldap
arcc_d = ldap.initialize(arcc_ldap)

# Connect to UWyo first, because if it fails the script fails
try:
    uwyo_d = uwyoldap.UWyoLDAP(username, password)
    del password
except ldap.INVALID_CREDENTIALS:
    del password
    print "Invalid Credentials"
    exit()

# Connect to ARCC ldap server, it supports anonymous searches,
# so no need for credentials.
arcc_d.simple_bind_s()

# Perform the search
base = 'dc=arcc,dc=uwyo,dc=edu'
filt = 'cn=mountmoran'
mtmoran = arcc_d.search_s(base, ldap.SCOPE_SUBTREE, filt)
arcc_d.unbind()

# Pull users out
users = mtmoran[0][1]['memberUid']
print mtmoran
# Get the user information from the UWyo AD server in one request.
uw_users = uwyo_d.searchByCN(users, uwyoldap.USER)
l = [user.cn for user in uw_users]

collegeCount = {'Ag & Nat Resources': 0,
                'Arts & Sciences': 0,
                'Business': 0,
                'Education': 0,
                'Engineering': 0,
                'Health Sciences': 0,
                'Law': 0,
                'Undergraduate': 0}
total = 0

for user in uw_users:
    # Skip ARCC and retired employees 
    if user.isARCCEmployee or user.isRetired:
        continue

    # If the entry in the dictionary doesn't exist, create it
    col = user.getCollege()
    if len(set(col)) > 1:
        print user.cn + " belongs to multiple colleges. Only one of them has\
        been counted."

    try:
        collegeCount[col[0]] += 1
        total += 1
    except:
        if user.isFaculty:
            "Something else needs to be done here."
        if user.isStudent:
            collegeCount['Undergraduate'] += 1
            total += 1


if not includeZeros:
    collegeCount = {k: v for k, v in collegeCount.iteritems() if v != 0}


# Plot the data
plt.figure(figsize=(12,12))
x = np.arange(len(collegeCount))
rects = plt.bar(x, collegeCount.values(), width=0.5, align='center')
plt.title('Number of Mt. Moran Users per College')
plt.xlabel('College')
plt.ylabel('Number of Users')
plt.xticks(x, collegeCount.keys(), rotation=80,)
plt.tick_params(axis='x', top='off')
plt.subplots_adjust(bottom=0.35)
# Add the values to the top of the bars
for rect in rects:
    h = rect.get_height()
    plt.text(rect.get_x() + rect.get_width()/2.,
             .25 + h,
             '%d' % int(h),
             ha='center',
             va='bottom')
plt.savefig('User_colleges.eps', format='eps', dpi=1000)
plt.show()

print collegeCount
print total

uwyo_d.unbind()
