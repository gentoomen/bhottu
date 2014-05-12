# bhottu
_A modular IRC bot_

## Installation
Clone the github repo:
    git clone https://github.com/gentoomen/bhottu.git

Install MySQL and python-pip if you haven't already.

## Requirements
A list of the required python packages is provided in requirements.txt. You can load these into a virtualenv.

## Setting up
Make a new copy of `config_example.py` and name it config.py.

Editing config.py`to your liking. The comments in that file are very helpful.

## Configuring the MySQL Database
The majority of the modules in this bot make use of a central MySQL database in some way. Therefore, it is strongly recommended to set up a database. The bot does NOT do this automatically.

Use the following commands:

    mysqladmin create bhottu

If you cannot remember your MySQL root password (this is **different** from your system root password), here are some [instructions on how to reset it that are Ubuntu-specific but that should work anywhere.](https://help.ubuntu.com/community/MysqlPasswordReset)

## Running
To run bhottu just open a shell, navigate it to the cloned git repo and run `python bhottu.py` or just `./bhottu.py` if you're on \*nux/\*BSD. In order to keep the bot running after you close your shell, you might want to use screen or tmux. We currently do not supply init scripts.

### Default modules and their usage
_All of the following commands have to be preceeded by bhottu's current name. E.g. 'bhottu, list admins'._

#### admins.py
Takes care of admin-related stuff. Users in the `GODS` list are automatically admins.

```
# Admin-only commands:
add admin [nick]               # gives [nick] admin priviliges
remove admin [nick]            # takes [nick]'s admin priviliges

# Public commands:
list admins                    # gives a list of current admins
```

#### autoupdate.py
Takes care of updating the bhottu source by pulling the up-to-date sources from github.

```
# Admin-only commands:
it's your birthday             # fetches most recent bhottu sources and restarts the bot
```

#### colors.py
Does stuff with colors. Like listing them when somebody says a known color and stuff...

```
# Public commands:
color [#hexvalue] [name]       # saves a color with the value [#hexvalue] under [name]
```

#### echo.py
Makes the bot say stuff (useful through private messages).

```
# Public commands:
say [message]                  # makes bhottu say [message]
shout [message]                # -//- but capitalized in bold font
```

#### feeds.py
Remembers RSS feeds and checks for updates everytime the server sends a 'PING' command.

```
# Admin-only commands:
add feed [name] [link]         # saves the feed at [link] under [name]
remove feed [name]             # removes a feed with called [name]
```

#### floodcontrol.py
Checks whether somebody is spamming and if somebody IS spamming sets the channel mode to 'moderated'.

Works without any specific commands.

#### greetings.py
Greets users when they connect or change their nickname.

```
# Admin-only commands:
greet [nick] [message]         # greets [nick] with [message] when he joins the channel
don't greet [nick]             # stops greeting [nick] and removes the greeting from the database
```

#### help.py
Kinda self-explanatory, isn't it?

```
# Public commands:
help [command]                 # gives info on [command]
```

#### ignore.py
Makes bhottu ignore a user's messages. That user will not be able to trigger any bhottu commands/module functions.

```
# Admin-only commands:
ignore [nick]                  # makes bhottu ignore [nick]
stop ignoring [nick]           # stops bhottu from ignoring [nick] again

# Public commands:
list ignores                   # gives a list of currently ignored nicknames (this can be triggered also by a nickname that is being ignored at the moment)
```

#### interjection.py
Whenever somebody says 'linux' instead of 'GNU/linux' (or a similar version) bhottu spams the legendary RMS copypasta.

Works without any specific commands.

#### kana.py
Romanizes kana and turns romaji into kana.

```
Public commands:
romanize [kana]                # turn kana string to romaji
kana [syllabary] [romaji]      # turn romaji into katakana / hirgana
```

#### linktitle.py
If somebody mentions a link, bhottu fetches that webpage and prints out _a)_ its title or _b)_ its mime-type. Bhottu also saves those links and gives them if someone asks for them.

```
# Admin-only commands:
all links [search pattern]     # see the 'links' command below
show blacklist                 # gives a domain blacklist
blacklist [domain]             # adds a domain to the blacklist
remove blacklist [domain]      # removes a domain from the blacklist

# Public commands:
links [search pattern]         # searches for [search pattern] in all the links titles - if more than 3 search results nothing gets returned (to avoid link spamming and short search terms such as 'a') and an admin must run the 'all links' command
```

#### loadaverage.py
Gives the current system load on bhottu's host machine.

```
# Public commands:
load average                   # pretty much what the description above says
```

#### nickscore.py
Users can give other users 'points' for doing cool stuff. This module takes care of that...

```
# Public commands:
[nick]++                       # gives [nick] one point (increments [user]'s points by 1)
[nick]--                       # takes [nick] one point (decrements [user]'s points by 1)
tell me about [nick]           # shows how many points [nick] has
show me the top [number]       # shows the top [number] users with the most points
```

#### poll.py
A module for creating polls and voting for stuff and stuff.

```
# Admin-only commands:
open poll [question]           # creates a new poll with [question]
close poll [question]          # closes a poll with matching [question]
delete poll [question]         # deletes a poll with matching [question]

# Public commands:
show poll [poll ID]            # shows info about a poll with [ID] containing answer IDs
vote for [answer ID]           # adds a vote to [answer ID]
vote new [answer]              # creates a new possible answer
search poll [search query]     # searches through all the polls for a matching query
```

#### quit.py
This module makes bhottu kill itself. Nothing special here.

```
# Admin-only commands:
gtfo                           # makes bhottu leave
```

#### quotes.py
A module for saving memorable quotes.

```
# Admin-only commands:
quotes from [nick]             # returns all the citations/quotes from [nick]

# Public commands:
quote <[nick]> [citation]      # saves [citation] with author [nick]
cite [nick]                    # returns a citation/quote by [nick]
```

#### reply.py
A module for automatically replying to things that are said in the channel. Also provides suggestions from channel-contributed lists.

```
# Admin-only commands:
list replies                   # lists replies and uploads them to sprunge.us for easy viewing
stop that                      # stops the bot from triggering 
yes, stop that                 # really stops the bot from triggering (can only be used after stop that)
remove reply to [trigger]      # stops the bot from triggering without asking for confirmation
assign [term] to [variable]    # assigns a new possible suggestion to a variable
don't reply to [trigger]       # kicks users who try add a reply for this trigger
reply to [trigger]             # makes it okay to add a reply for this trigger again

#Public commands:
[term] <reply> [term]          # makes the bot say the term on the right when the term on the left is said in the channel
what was that?                 # makes the bot tell you what triggered a certain event
suggest a [variable]           # suggests a random entry from one of the predefined lists
```

#### roulette.py
A module for the users to play Russian Roulette.

```
# Public commands:
roulette                       # plays a turn of russian roulette
```

#### spew.py
Records all messages everyone has said ever (into a table called `lines`) and gives them back at random if someone asks for them.

```
# Public commands:
spew like [nick]               # gives a citation of what [nick] has said sometime in the past
spew improv                    # gives 3-5 citations of what somebody has said sometime in the past
```

#### statistics.py
Gives some commands for statistics and stuff.

```
# Public commands:
top10ever                      # returns a list of the 10 most talkative people
mpm                            # returns how many messages per minute are said
line average of [nick]         # returns how long a message by [nick] is by average
```

#### threadsearch.py
Used for searching for threads on 4chan containing certain text.

```
# Public commands:
catalog [board] [regex]        # searches the 4chan catalog on board [board] for matching regex [regex]
board [board] [regex]          # searches every post on 4chan board [board] for matching regex [regex]
```
#### weather.py
```
# Public commands:
what's the weather in [city]   # returns current conditions in city
```
## Extending
Bhottu is very extendable and it's quite simple to do that:

### Creating a module
To create a module just create a blank `.py` file in the `/modules` folder. This part will go through the creation of the `modules/greetings.py` file/module thing.

Now first I will need to define a`load()` method, which will set up whatever the module needs on it's initialization. Essential bhottu commands are located in the `/api` folder so you should import that:

```python
from api import *
```

Now that you have access to the most important functions you can use them. Most (all) modules have a `load()` function which prepares whatever the module needs. In this case the load function should: create a table in the MySQL database which will hold the greetings and the nicknames of people to which will trigger them. Also, I need to tell bhottu to use `load()` function on start, so write there something something like:

```python
def load():
    dbExecute('''create table if not exists greetings (
              greetingID int auto_increment primary key,
              nick varchar(255),
              greeting text,
              index(nick) )''')
registerModule('Greetings', load) # add this after defining "load()" and don't place it inside "load()"
```

Now let's make functions which will add a greeting to the table and remove a greeting from the table:

```python
def addGreet(channel, sender, target, message):
    if sender == target: # setting a greeting for yourself is kinda selfish
        sendMessage(channel, "%s, u silly poophead" % sender)
        return
    currentGreeting = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [target])
    if len(currentGreeting) > 0: # target nickname already has a greeting
        sendMessage("I already greet %s with %s" % (target, currentGreeting[0][0]))
        return
    dbExecute("INSERT INTO greetings (nick, greeting) VALUES (%s, %s)", [target, message]) # insert a new greeting
def removeGreet(channel, sender, target):
    dbExecute("DELETE FROM greetings WHERE nick=%s", [target]) # just deletes a greeting
```

Now I have to alter the `load()` function so that bhottu knows when to run these new functions:

```python
def load():
    """Greets people when joining the channel."""
    dbExecute('''create table if not exists greetings (
              greetingID int auto_increment primary key,
              nick varchar(255),
              greeting text,
              index(nick) )''')
    registerFunction("greet %s %S", addGreet, "greet <target> <message>", restricted = True) # restricted means that only people who have admin authorization can run this command
    registerFunction("don't greet %s", removeGreet, "don't greet <target>", restricted = True)
```

Now I will create functions that get called when a user has joined the channel and/or changed his name and greet him:

```python
def checkGreetJoin(arguments, sender):
    (nick, ident, hostname) = parseSender(sender)
    greetings = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [nick])
    channel = arguments[0]
    if len(greetings) > 0:
        time.sleep(2) # wait for him/her to acoomodate him/herself in the channel (NOTE: I'll need to "import time" if I want to use this)
        sendMessage(channel, "%s, %s" % (nick, greetings[0][0])) # greet him/her
def checkGreetNick(arguments, sender):
    (nick, ident, hostname) = parseSender(sender)
    newNick = arguments[0]
    greetings = dbQuery("SELECT greeting FROM greetings WHERE nick=%s", [newNick])
    if len(greetings) > 0:
        time.sleep(2)
        for channel in joinedChannels():
            if newNick in channelUserList(channel):
                sendMessage(channel, "%s, %s" % (newNick, greetings[0][0]))
```

Now I have to alter `load()` again and hook these new functions to the "JOIN" and "NICK" IRC commands:

```python
def load():
    dbExecute('''create table if not exists greetings (
              greetingID int auto_increment primary key,
              nick varchar(255),
              greeting text,
              index(nick) )''')
    registerFunction("greet %s %S", addGreet, "greet <target> <message>", restricted = True)
    registerFunction("don't greet %s", removeGreet, "don't greet <target>", restricted = True)
    registerCommandHandler("JOIN", checkGreetJoin)
    registerCommandHandler("NICK", checkGreetNick)
```

Alright! Seems about right. Now let's make sure bhottu loads the module itself. To do that I'll need to edit `config.py` and add `Greetings` into `ENABLED_MODULES`.

And there you go!

Now the module is ready to go! To test it, just do the steps written in the `Running` section.
