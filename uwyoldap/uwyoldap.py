#!/bin/python

# Classes to make it easier to deal with Uwyo LDAP server
# Originally was going to work with ARCC LDAP too,
# but the two servers are very different.
import ldap
import re


def extractCN(dn):
    """Given the dn on an object, this extracts the cn."""
    return re.findall('CN=(.*?),', dn)[0]


def createLDAPObj(info, ldap_srv):
    """info is the information on the object. This uses the info to
    figure out what type of object it is (computer, user, group) and
    then creates the coresponding LDAPObj."""
    types = {'Person': LDAPUser, 'Group': LDAPGroup,
             'Computer': LDAPComputer}

    objectCat = re.findall('CN=(.*?),', info[1]['objectCategory'][0])

    return types[objectCat[0]](info, ldap_srv)


def createLDAPObjDict(objs):
    """Creates a dictionary from a list of LDAP Obj's. The keys are the cn
    of the object, the value is the object."""
    return {obj.cn: obj for obj in objs}


class UWyoLDAP(object):
    """Uwyo LDAP object. Connects to the ldap server and is used for
    searching."""
    URL = 'ldaps://windows.uwyo.edu'
    BASE = 'dc=windows,dc=uwyo,dc=edu'
    USER = 'Person'
    USERS = USER
    PERSON = USER
    PERSONS = PERSON
    GROUP = 'Group'
    GROUPS = GROUP
    COMPUTER = 'Computer'
    COMPUTERS = COMPUTER
    LDAPObjs = {}

    def __init__(self, username, password):
        self.srv = ldap.initialize(self.URL)
        self.srv.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        self.srv.simple_bind_s(username, password)
        del password

    def unbind(self):
        self.srv.unbind()

    def searchByCN(self, cns, cn_type):
        """Search for stuff by given cn's. Result is a list of LDAPObj objects.
        Type must be UWyoLDAP.USERS or UWyoLDAP.GROUPS. Computers aren't
        currently supported. The objects returned will be of the corresponding
        subtype of LDAPObj objects."""

        if type(cns) is not list:
            cns = [cns]

        cn = cns[:]

        objs = []
        for n in cn:
            h = '@' + cn_type + '@' + n
            if h in self.LDAPObjs.keys():
                cn.remove(n)
                objs.append(self.LDAPObjs[h])

        if cn == []:
            return objs
        else:
            base = self.BASE
            filt = '(|' + ''.join('{})'.format('(CN=' + n) for n in cn) + ')'
            filt = '(&(objectCategory=' + cn_type + ')' + filt + ')'
            results = self.srv.search_s(base, ldap.SCOPE_SUBTREE, filt)

            for result in results:
                if result[0] is not None:
                    obj = createLDAPObj(result, self)
                    self.LDAPObjs['@' + cn_type + '@' + obj.cn] = obj
                    objs.append(obj)
        return objs


class LDAPObj(object):
    """Base class for ldap objects. The subclasses are LDAPUser, LDAPGroup, and
    LDAPComputer."""
    def __init__(self, info, ldap_srv):
        self.cn = extractCN(info[0])
        self.cn = self.cn
        self.memberOf = {}
        self.info = info

        if self.info[1]['gidNumber'][0]:
            self.gid = self.info[1]['gidNumber'][0]
        if self.info[1]['description'][0]:
            self.description = self.info[1]['description'][0]

        # Just a list of CN's.
        if 'memberOf' in info[1]:
            for obj in info[1]['memberOf']:
                self.memberOf[extractCN(obj)] = obj


class LDAPUser(LDAPObj):
    """User object"""
    def __init__(self, info, ldap_srv):
        super(LDAPUser, self).__init__(info, ldap_srv)
        if 'department' in info[1]:
            self.departments = info[1]['department'][0].split('|')
        else:
            self.departments = None

        self._ldap_srv = ldap_srv
        self.isFaculty = False
        self.isEmployee = False
        self.isStudent = False
        self.isARCCEmployee = False
        self.isRetired = False
        if 'UW Employees' in self.memberOf:
            self.isEmployee = True
            if self.departments and ('IT-Research Support' in self.departments
                                or 'IT/Research Support' in self.departments):
                self.isARCCEmployee = True
        if 'UW Faculty' in self.memberOf \
                or 'UW Academic Professionals' in self.memberOf:
            self.isFaculty = True
        if 'UWSTUDENTS' in self.memberOf:
            self.isStudent = True
        if 'Retired' in self.memberOf:
            self.isRetired = True

    def getCollege(self):
        """Attempts to get the college(s) that the user belongs to. Doesn't
        currently work on undergraduate students (it's possible to identify
        some undergrad's colleges but not all.) It will return an empty list
        for them. This will also return an empty list for non-undergrads who
        don't work for a specific college. Some users seem to belong
        to multiple colleges, so this returns a list of colleges."""
        self.college = []
        for group in self.memberOf.keys():
            if group.startswith("DEPT_"):
                groupObj = self._ldap_srv.searchByCN([group], self._ldap_srv.GROUP)
                for member in groupObj[0].memberOf.keys():
                    if member.startswith('DIV_College of '):
                        self.college.append(member[len('DIV_College of '):])
        return self.college


class LDAPGroup(LDAPObj):
    """LDAP group. Currently doesn't handle very large groups, because the
    member attribute gets split up automatically by the AD server, and multiple
    requests have to be made to the server to get all of the members"""
    def __init__(self, info, ldap_srv):
        super(LDAPGroup, self).__init__(info, ldap_srv)
        self.members = {}
        # Just a list of CN's.
        if 'member' in info[1]:
            for obj in info[1]['member']:
                self.members[extractCN(obj)] = obj


class LDAPComputer(LDAPObj):
    """Nothing is done here currently."""
    def __init__(self, info, ldap_srv):
        super(LDAPComputer, self).__init__(info, ldap_srv)
       # Not finished. I don't think ARCC will need this, anyway
