#!/usr/bin/python
from distutils.util import strtobool
from termcolor import colored
import sys, os, pxssh

#VARIABLES
servers = ['162.250.78.93', 'cs2412.mojohost.com', 'cs2413.mojohost.com']

# FUNCTIONS
# answer the user for yes/no
def yesNoQuery(question):
    sys.stdout.write('%s [y/n]\n' % question)
    while True:
        try:
            return strtobool(raw_input().lower())
        except ValueError:
            sys.stdout.write('Please respond with \'y\' or \'n\'.\n')
# set user depending of the host
def getSSHuser(host):
    global user
    if host == '162.250.78.93':
        user = 'root'
    else:
        user = 'whdeployer'
# answer the yser for d/r
def deployQuery(question):
    while True:
        action = raw_input(question)
        if action is 'd':
            return 'Deployment'
        elif action is 'r':
            return 'Rollback'
        else:
            sys.stdout.write('Please respond with \'d\' or \'r\'.\n')
# establish SSH connection with host and send command
def ssh(user, server, command):
    try:
        s = pxssh.pxssh()
        if not s.login (server, user, ssh_key='/root/.ssh/whwebservers'):
            sys.exit(1)
        else:
            s.sendline(command)
            s.prompt()
            print s.before
            s.logout()
    except pxssh.ExceptionPxssh, e:
        error_ssh = "Error %r:" % (e)
        sys.exit(1)
        return
#cURL to create the new release in NR and Datadog
def createRelease(release):
    newrelicUrl = 'https://api.newrelic.com/deployments.xml'
    datadogURL = 'https://app.datadoghq.com/api/v1/events?api_key=90170ee4b01fedefe9ccfd8c4cbac265&application_key=3642271163337a5c8e76128f328719100d22e17c'

    newRelicQuery = ("""
    curl -H \"x-api-key:06661dfce75a8a7a6e3ec83e522a74cb80672ce65fd8745\" \
    -d \"deployment[application_id]=3572263\" \
    -d \"deployment[description]=https://teamcmp.atlassian.net/issues/?jql=fixVersion%%3D%s\" \
    -d \"deployment[revision]=%s\" \
    -d \"deployment[user]=Samuel Yellin\" \
    %s
    """) % (release, release, newrelicUrl )

    datadogQuery = ("""
    curl  -X POST -H \"Content-type: application/json\" -d '{ \
    \"title\": \"Deployment\", \
    \"text\": \"%s\", \
    \"priority\": \"normal\", \
    \"tags\": [\"env:prod\", \"deployment\"], \
    \"alert_type\": \"info\" \
    %s
    """) % (release, datadogURL)

    os.system(newRelicQuery)
    os.system(datadogQuery)

# MAIN EXECUTION
os.system('clear')
print colored("""
================================================================
#   _       ____  __    __           __                        #
#  | |     / / / / /___/ /__  ____  / /___  __  _____  _____   #
#  | | /| / / /_/ / __  / _ \/ __ \/ / __ \/ / / / _ \/ ___/   #
#  | |/ |/ / __  / /_/ /  __/ /_/ / / /_/ / /_/ /  __/ /       #
#  |__/|__/_/ /_/\__,_/\___/ .___/_/\____/\__, /\___/_/        #
#                         /_/            /____/                #
================================================================
""", 'cyan')

action = deployQuery('Is this a Deployment or a Rollback? [(d)eploy/(r)ollback]: ')
release = raw_input("Enter Release: ")
phinx = raw_input("Enter Phinx Release: ")

print colored('         You are about to perform: ', 'blue', attrs=['bold'])
print colored('         Action: ', 'blue', attrs=['bold']),
print colored('%s', 'green') % action
print colored('         Release: ', 'blue', attrs=['bold']),
print colored('%s', 'green') % release
print colored('         Phinx: ', 'blue', attrs=['bold']),
print colored('%s', 'green') % phinx

print colored('         Are you sure?: ', 'red', attrs=['bold']),
confirm1 = yesNoQuery('')

if confirm1 is 1:
    for server in servers:
        getSSHuser(server)
        cmd = """
        sudo /etc/init.d/nginx stop;
        cd /var/www/wellhello.com/vendor;
        find -type f -name config | xargs sed -i -e \"s/filemode = true/filemode = false/\";
        cd ..;
		git checkout .;
		git fetch origin;

        git checkout $release;
		composer install --no-dev --no-interaction;
		php bin/generate-parameters.php --targetEnv=prod;
		rm -f data/cache/*;
		grunt;
		composer dumpautoload --optimize;"

        sudo /etc/init.d/nginx start

        """
        #Connect to each server and deploy the code
        ssh(user, server, cmd)
    #Clear Redis cache
    os.system('redis-cli -h wh-prod-redis-a.cmpservers.com flushall;')
    createRelease(release)
    #Restart crons
    ssh('root','162.250.78.93', 'restart wh-daemon; restart wh-task-runner;')
else:
    print('Exiting...')
