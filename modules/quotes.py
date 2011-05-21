from api import *
from utils.ompload import *

def load():
    dbExecute('''create table if not exists quote (
              quoteID int auto_increment primary key,
              name varchar(255),
              quotation text,
              index(name) )''')
    registerFunction("quote <%s> %S", addQuote, "quote <nick> citation")
    registerFunction("cite %s", echoQuote, "cite <nick>")
    registerFunction("quotes from %s", allQuotes, "quotes from <nick>", restricted = True)
registerModule('Quotes', load)

def addQuote(channel, sender, target, quotation):
    """Quotes a nick on the channel and stores it to the DB"""
    target = target.lstrip('~&@%+')
    if sender == target:
        sendMessage(channel, "%s, you shouldn't quote your lonely self." % sender)
        return
    log.info('Trying to insert quote: %s' % quotation)
    dbExecute('INSERT INTO quote (name, quotation) VALUES (%s, %s)', [target, quotation])
    sendMessage(channel, "Quote recorded")

def echoQuote(channel, sender, target):
    """Fetches a random quote from DB for target and echoes it to channel"""
    quote = dbQuery('SELECT quotation FROM quote WHERE name=%s ORDER BY RAND() LIMIT 1', [target])
    if len(quote) == 0:
        sendMessage(channel, "No quotes for %s" % target)
        return
    sendMessage(channel, '"%s" -- %s' % (quote[0][0], target))

def allQuotes(channel, sender, target):
    """Fetches all quotes for target, uploads them to ompload and echoes link to channel"""
    quotes = dbQuery('SELECT quotation FROM quote WHERE name=%s', [target])
    if len(quotes) == 0:
        sendMessage(channel, "No quotes for %s" % target)
        return
    quoteList = ''
    for quote in quotes:
        quoteList += '"%s" -- %s\n' % (quote[0], target)
    try:
        url = omploadData(quoteList)
    except Exception:
        url = None
    if url == None:
        sendMessage(channel, "Uploading quotes for %s failed." % target)
        return
    sendMessage(channel, "Quotes for %s: %s" % (target, url))
