#!/bin/python

# Script that returns the number of interns working for ARCC.
# Depending on what is done with intern accounts when they leave ARCC,
# this script may also give the number total number of interns ever hired.
# This is done by querying ARCC's LDAP server to get the number of
# of members in the arccinterns group.

import ldap

ldap_srv = 'ldaps://arccidm1.arcc.uwyo.edu'

arcc_d = ldap.initialize(ldap_srv)

arcc_d.simple_bind_s()

base = 'dc=arcc,dc=uwyo,dc=edu'
filt = 'cn=arccinterns'
arccinterns = arcc_d.search_s(base, ldap.SCOPE_SUBTREE, filt)
arcc_d.unbind()

users = arccinterns[0][1]['memberUid']

print len(users)
