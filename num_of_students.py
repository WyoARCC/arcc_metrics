import uwyoldap
import getpass
import subprocess

users = subprocess.Popen('ipa group-show mountmoran', stdout=subprocess.PIPE, shell=True)


users = users.communicate()[0]
users = [u.strip() for u in users.split(':')[-1].split(',')]

username = raw_input('Username: ')
password = getpass.getpass()

srv = uwyoldap.UWyoLDAP(username, password)
u = srv.search(users, uwyoldap.USERS, uwyoldap.CN)
students = [user.cn for user in u if user.isStudent]

g = srv.search("Enrolled Students", uwyoldap.GROUPS, uwyoldap.CN)
print "Number of Students that are users of Mount Moran: " + str(len(students))
print "Number of Students total: " + str(len(g[0].members))
print "Percentage of students that are Mount Moran users: " + str(len(students)/float(len(g[0].members))*100)
