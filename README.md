# bhottu
_A modular IRC bot_

## Installation
Just clone the git repo and you're ready. Also you will need `MySQL` if you want to use all of the modules.

## Setting up
Set up a configuration by editing the `config_example.py` file to your liking and rename it to `config.py`. The comments in that file are very helpful.

## Running
To run bhottu just open a shell, navigate it to the cloned git repo and run `python bhottu.py` or just `./bhottu.py` if you're on \*nux/\*BSD.

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

Now I have to alter `load()` again and hook these new functions to the "JOIN" and "NICK" IRC:

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

Alright! Seems about right. Now let's make sure bhottu loads the module itself. To do that I'll need to edit `config.py` and under `ENABLED_MODULES` add `"greetings"`, so it should look something like this:

```python
ENABLED_MODULES = [
	'Greetings'
]
# if you're adding the 'Greetings' entry to the last line, add a comma on the line before that
# if you're adding that entry inbetween other entries add a comma at the end of it
# just make sure it's proper python syntax
```

Now bhottu is ready to go! Just do the steps written in the `Running` section.