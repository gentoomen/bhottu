from api import *
from utils.pastebins import *

def load():
    """Records memorable quotes and cites them."""
    dbExecute('''create table if not exists quote (
              quoteID int auto_increment primary key,
              name varchar(255),
              quotation text,
              index(name) )''')
registerModule('Quotes', load)

_lastAddAttempt = None

@register("quote <%s> %S", syntax="quote <nick> citation")
def addQuote(channel, sender, target, quotation):
    """Quotes a nick on the channel and stores it to the DB"""
    global _lastAddAttempt
    target = target.lstrip('~&@%+')
    if sender == target:
        sendMessage(channel, "%s, you shouldn't quote yourself." % sender)
        return
    result = dbQuery('SELECT message FROM `lines` WHERE message = %s AND name = %s', [quotation, target])
    if len(result) == 0:
        sendMessage(channel, "%s, %s never said that, dude..." % (sender, target))
        _lastAddAttempt = target, quotation
        return
    else:
        log.info('Trying to insert quote: %s' % quotation)
        dbExecute('INSERT INTO quote (name, quotation) VALUES (%s, %s)', [target, quotation])
        sendMessage(channel, "Quote recorded")

@register("yes they did", restricted=True)
def yesTheyDid(channel, sender):
    """Force-adds a quote to the DB"""
    global _lastAddAttempt
    if _lastAddAttempt:
        target, quotation = _lastAddAttempt 
        log.info('Trying to insert quote: %s' % quotation)
        dbExecute('INSERT INTO quote (name, quotation) VALUES (%s, %s)', [target, quotation])
        sendMessage(channel, "Quote recorded")
        _lastAddAttempt = None

@register("cite %s")
def echoQuote(channel, sender, target):
    """Fetches a random quote from DB for target and echoes it to channel"""
    quote = dbQuery('SELECT quotation FROM quote WHERE name=%s ORDER BY RAND() LIMIT 1', [target])
    if len(quote) == 0:
        sendMessage(channel, "No quotes for %s" % target)
        return
    sendMessage(channel, '<%s> %s' % (target, quote[0][0]))

@register("cite %s %S")
def searchQuote(channel, sender, target, keyword):
    """Fetches a quote from target containing the keyword(s) from the DB and echoes it to the channel"""
    quote = dbQuery('SELECT quotation FROM quote WHERE name=%s AND quotation LIKE %s ORDER BY RAND() LIMIT 1',
                    [target, '%'+keyword+'%'])
    if len(quote) == 0:
        sendMessage(channel, "No quotes for %s matching %s" % (target, keyword))
        return
    sendMessage(channel, '<%s> %s' % (target, quote[0][0]))

@register("quotes from %s", syntax="quotes from <nick>", restricted=True)
def allQuotes(channel, sender, target):
    """Fetches all quotes for target, uploads them to a pastebin and echoes link to channel"""
    quotes = dbQuery('SELECT quotation FROM quote WHERE name=%s', [target])
    if len(quotes) == 0:
        sendMessage(channel, "No quotes for %s" % target)
        return
    quoteList = ''
    for quote in quotes:
        quoteList += '<%s> %s\n' % (target, quote[0])
    try:
        url = nnmm(quoteList)
    except Exception:
        sendMessage(channel, "Uploading quotes for %s failed." % target)
        return
    sendMessage(channel, "Quotes for %s: %s" % (target, url))
