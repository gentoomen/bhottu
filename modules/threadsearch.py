"""
Searches posts on 4chan using the 4chan JSON API and returns the post
url of any matching post

:author chchjesus:
"""
import simplejson
import urllib2
from api import *
from time import sleep
import re

def load():
    """Load the module"""
    sql = """CREATE TABLE IF NOT EXISTS chan_search (
             search_id INT auto_increment NOT NULL,
             nick VARCHAR(255),
             search_string TEXT,
             board VARCHAR(255),
             PRIMARY KEY (search_id)
             );"""

    dbExecute(sql)
    registerFunction("search %s for %s", run_catalog_search, "search <board> for <string>")
    registerFunction("show searches by %s", show_searches_by_nick, "show searches by <nick>", restricted=True)
    registerFunction("show who searched %s", show_who_searched, "show who searched <string>", restricted=True)
registerModule("ThreadSearch", load)

def sanitise(string):
    """Strips a string of all non-alphanumeric characters"""
    return re.sub(r"[^a-zA-Z0-9 ]", "", string)

def run_catalog_search(channel, sender, board, string):
    """Search 4chan posts for a search string and return
    the matching post numbers"""
    # Strip unyieldly characters
    board = sanitise(board)

    posts = search_catalog(string, board)
    posts = list(set(posts))
    insert_in_db(string, sender, board)

    if len(posts) <= 0:
        sendMessage(channel, "{0}: No results for {1}".format(sender, string))
    else:
        # Turn the post numbers into fully-fledged URLs
        post_template = "https://boards.4chan.org/{0}/res/{1}"
        urls = [post_template.format(board, post_num) for post_num in posts]
        sendMessage(channel, "{0}: {1}".format(sender, " ".join(urls[:3])))

def show_who_searched(channel, sender, string):
    """Gets a list of the users who executed a particular search"""
    results = select_db_values("nick", "search_string", string)
    if not results:
        sendMessage(channel, "No-one has searched for {0}".format(string))
    else:
        sendMessage(channel, "{0} searched by: {1}".format(string, " ".join(results)))

def show_searches_by_nick(channel, sender, nick):
    """Gets the searches executed by a certain user"""
    results = select_db_values("search_string", "nick", nick)
    if not results:
        sendMessage(channel, "{0} hasn't searched anything".format(nick))
    else:
        sendMessage(channel, "{0}'s searches: {1}".format(nick, " ".join(results)))

def insert_in_db(search_string, nick, board):
    """
    Stores a search string in the database under the nick
    who searched for it
    """
    sql = """INSERT INTO chan_search (search_string, nick, board)
             VALUES (%s, %s, %s);"""
    dbExecute(sql, [search_string, nick, board])
    db().commit()

def select_db_values(col_name, match_col, match_val):
    """Get column col_name values where match_col == match_val"""
    sql = """SELECT {0}
             FROM chan_search
             WHERE {1} = %s
             GROUP BY {0};"""
    result = dbQuery(sql.format(col_name, match_col), [match_val])
    if len(result) <= 0:
        return False
    else:
        return [val[0] for val in result]

def get_json_data(url):
    """Returns a json data object from a given url."""
    # Respect 4chan's rule of at most 1 JSON request per second
    sleep(1)
    try:
        open_url = urllib2.urlopen(url)
        json_data = simplejson.load(open_url.fp)
        open_url.close()
        return json_data
    except Exception as e:
        log.error(e)
        raise

def search_thread(string, board, thread_num):
    """
    Searches every post in thread thread_num on board board for the
    string provided. Returns a list of matching post numbers.
    """
    json_url = "http://api.4chan.org/{0}/res/{1}.json".format(board, thread_num)
    sections = ["com", "name", "trip", "email", "sub", "filename"]
    found_list = []
    thread_json = get_json_data(json_url)
    string = string.lower()

    for post in thread_json["posts"]:
        user_text = "".join([post[s] for s in sections if s in post.keys()]).lower()
        if re.search(string.lower()) is not None:
            found_list.append("{0}#p{1}".format(thread_num, user_text))
        return found_list

def search_catalog(string, board):
    """
    Searches through the user-editable fields of each OP post
    in the 4chan catalog on a particular board for the string provided.
    Returns a list of matching OP post numbers.
    """
    json_url = "http://api.4chan.org/{0}/catalog.json".format(board)
    sections = ["com", "name", "trip", "email", "sub", "filename"]
    found_list = []
    catalog_json = get_json_data(json_url)
    string = string.lower()

    for page in catalog_json:
        for thread in page['threads']:
            user_text = "".join([thread[s] for s in sections if s in thread.keys()]).lower()
            if re.search(string, user_text) is not None:
                found_list.append(thread["no"])

    return found_list

def search_board(string, board):
    """
    Searches through user-editable fields of every post on a
    particular board for the string provided. Returns a list of
    matching post numbers. Uses a separate process to run because
    the search set would be larger than usual.
    """

    # Not that important at this stage...
    raise NotImplemented
