#___.   .__            __    __         
#\_ |__ |  |__   _____/  |__/  |_ __ __ 
# | __ \|  |  \ /  _ \   __\   __|  |  \
# | \_\ |   Y  (  <_> |  |  |  | |  |  /
# |___  |___|  /\____/|__|  |__| |____/ 
#     \/     \/                         
#
#
SERVER = "irc.rizon.net" #server you wish for the bot to connect to
PORT = 6667 #port that you want the bot to connect on. Note that 6697 is usually SSL, but not always. If in doubt leave default
IS_SSL = False #whether or not to use SSL. If in doubt leave default, else set True
NICK = "bhottu" #nick you want the bot to use
IDENT = "bot" #ident you want the bot to send to the IRC server. note this value will be ignored if you have an identd installed
MODE = 0 #numerical IRC mode. see section 3.1.3 of RFC2812. Common values are "0" and "8" (invisible)
REALNAME = "bot" #real name sent to the server. Displayed in /whois
CHANNEL = "" #channel you want the bot to join on start
NICK_PASS = None #enter a string here to have the bot auto-auth to nickserv

#Logging information
STDOUT_LOGLEVEL = "DEBUG"
STDOUT_VERBOSE = True

LOG_FILE = "log"
LOG_LEVEL = "INFO"
LOG_VERBOSE = True

#These users are allowed to use all privileged commands regardless of if they're loaded in the Admin module or not
GODS = [""]

#See the section in README.md for more information 
DB_HOSTNAME = "localhost"
DB_USERNAME = "root"
DB_PASSWORD = ""
DB_DATABASE = "bhottu"

#recommended modules. For more, browse modules/. There is documentation about writing them in the README and the default ones serve as good examples
ENABLED_MODULES = [
    'Admins',
    'Colors',
    'CTCP',
    'Echo',
    'FloodControl',
    'Greetings',
    'Help',
    'Ignore',
    'LinkTitle',
    'LoadAverage',
    'NickScore',
    'Poll',
    'Quit',
    'Quotes',
    'Reply',
    'Spew',
    'Statistics',
    'ThreadSearch',
    'Weather',
]
