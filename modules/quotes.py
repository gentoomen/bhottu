from api import *

def load():
    dbExecute('''create table if not exists quote (
              quoteID int auto_increment primary key,
              name varchar(255),
              quotation text,
              index(name) )''')
    registerFunction("quote %s %S", addQuote, "quote <nick> citation")
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
    quote = dbQuery('SELECT quotation, name FROM quote WHERE name=%s ORDER BY RAND() LIMIT 1', [target])
    if len(quote) > 0:
        sendMessage(channel, "%s - %s" % quote[0][0], [0][1])
    else:
        sendMessage(channel, "No quotes for %s" % target)

def allQuotes(channel, sender, target):
    """Fetches all quotes for target, uploads them to ompload and echoes link to channel"""
    quotes = dbQuery('SELECT quotation FROM quote WHERE name=%s', [target])
    if len(quotes) < 1:
        sendMessage(channel, "No quotes for %s" % target)
        return
    return_list = []
    for row in quotes:
        return_list.append(row[0])
    return_list = "\n".join(return_list)
    f = open('./quotelist','w')
    f.write(return_list)
    f.close()
    url = os.popen('./ompload quotelist')
    sendMessage(channel, url.read())
