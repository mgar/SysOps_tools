#!/usr/bin/python
import sys
import mysql.connector
from time import gmtime, strftime

def usage():
  print """
          usage: add_domains.py [file] [type] (type must be support or corp)
          """
  exit()

if len(sys.argv) == 3:
    script = sys.argv[0]
    filename = sys.argv[1]
    siteType = sys.argv[2]
elif len(sys.argv) < 3:
    usage()
    sys.exit(1)
else:
    sys.exit(1)

if siteType.lower()  == 'support':
    description = 'Support Site'
    targetDomain = 'supportsite.com'
elif siteType.lower() == 'corp':
    description = 'Corporation Site'
    targetDomain = 'corpsite.com'
else:
    print "You have entered an invalid type\n"
    usage()

timeNow = strftime("%Y-%m-%d %H:%M:%S", gmtime())
connection = mysql.connector.connect(user='$user', password='$password', database='$database')
cursor = connection.cursor()

with open(filename, 'r') as domains:
    for line in domains:
        line = line.rstrip()
        add_domain = ("INSERT INTO domain "
                     "(domain, description, aliases, mailboxes, maxquota, quota, transport, backupmx, created, modified, active) "
                     "VALUES ('%s', '%s', 0, 0, 0, 0, 'virtual', 0, '%s', '%s', 1)") % (line, description, timeNow, timeNow)
        add_alias = ("INSERT INTO alias_domain "
                    "(alias_domain, target_domain, created, modified, active) "
                    "VALUES ('%s', '%s', '%s', '%s', 1)") % (line, targetDomain, timeNow, timeNow)
        cursor.execute(add_domain)
        cursor.execute(add_alias)

cursor.close()
connection.close()
