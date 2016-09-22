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
faculty = [user.cn for user in u if user.isFaculty]

g = srv.search(['UW Faculty', 'UW Academic Professionals'], uwyoldap.GROUPS, uwyoldap.CN)
all_faculty = g[0].members.keys() + g[1].members.keys()

print "Number of Faculty that uses Mt. Moran: ", len(faculty)
print "Number of Faculty Total: ", len(all_faculty)
print "Percentage of faculty that are Mt. Moran Users: ", len(faculty)/float(len(all_faculty)) * 100
