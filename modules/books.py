from api import *
from utils.pastebins import *

def load():
    """Records books for the gentoolib v2."""
    dbExecute('''create table if not exists books (
              book_id int auto_increment primary key,
              title text, 
              added_by varchar(255) )
              ''')
registerModule('Books', load)

@register("addbook %S", syntax="addbook booktitle")
def addBook(channel, sender, booktitle):
    """Store the book in the database"""
    if booktitle == "":
        sendMessage(sender, "Enter a proper book title. syntax: addbook booktitle")
        return
    else:
        log.info('Trying to insert book: %s' % booktitle)
        dbExecute('INSERT INTO books (title, added_by) VALUES (%s, %s)', [booktitle, sender])
        sendMessage(channel, "Book recorded")

@register("dumpbooks", syntax="dumpbooks")
def allBooks(channel, sender):
    """Fetches all books in database, upload them on nnmml or whatever, not featured not scalable fuckyou"""
    books = dbQuery('SELECT title, added_by FROM books')
    bookList = ''
    for (title, added_by) in books:
        bookList += '\"%s\" inserted by \"%s\"\n' % (title, added_by)
    try:
        url = nnmm(bookList)
    except Exception:
        sendMessage(channel, "Uploading book list failed.")
        return
    sendMessage(sender, "Books: %s" % url)
