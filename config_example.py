#Config file for bhottu
#filename: ./config.py

#Connection options
SERVER = 'irc.lolipower.org'
PORT = 6667
NICK ='SICPBot'
REALNAME = 'bhottu'
IDENT = 'bhottu'
CHANNEL = '#/g/sicp'
MODE = 0 #This is a bitmask for user mode
NICK_PASS = None
#Authed users
GODS = []

#Logging options
# Set either of the loglevels to None for no logging to that channel
# Verbose enables printing the calling function with each log message
STDOUT_LOGLEVEL = 'DEBUG'
STDOUT_VERBOSE = False
LOG_FILE = 'bhottu_log'
LOG_LEVEL = 'INFO'
LOG_VERBOSE = True

#Database connection
DB_HOSTNAME = ''
DB_USERNAME = ''
DB_PASSWORD = ''
DB_DATABASE = ''

ENABLED_MODULES = [
    'Quit',
    'Echo',
    'Help',
    'FloodControl',
    
    'NickScore',
    'LinkTitle',
    'Quotes',
    'Reply',
    'Spew',
    'Greetings',
    'Colors',
    'Commits',
    'AutoUpdate',
    'Poll',
    'Statistics',
    'Roulette',
    'LoadAverage',
    'Admins',
    'Ignore',
]
