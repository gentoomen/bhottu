"""
Searches posts on 4chan using the 4chan JSON API and returns the post
url of any matching post

:author Cody Harrington:
"""
import simplejson
import urllib
import urllib2
from api import *
from time import sleep
import re
import math
from threading import *
from Queue import *
import time

def load():
    """Load the module"""
    registerFunction("catalog %s %S", run_catalog_search, "catalog <board> <regex>")
    registerFunction("board %s %S", run_board_search, "board <board> <regex>")
registerModule("ThreadSearch", load)

def sanitise(string):
    """Strips a string of all non-alphanumeric characters"""
    return re.sub(r"[^a-zA-Z0-9 ]", "", string)

def output_to_sprunge(string):
    """Takes a string of data, sends it to http://sprunge.us 
    as a POST request, and returns the URL that sprunge returns"""
    data = urllib.urlencode({"sprunge": string})
    request = urllib2.Request("http://sprunge.us", data)
    response = urllib2.urlopen(request) 
    message = response.read().strip('\n')
    response.close()
    return message

def process_results(channel, sender, board, string, posts):
    """Process the resulting data of a search and present it"""
    max_num_urls_displayed = 3
    board = sanitise(board)
    message = ""
    if len(posts) <= 0:
        sendMessage(channel, "{0}: No results for {1}".format(sender, string))
    else:
        post_template = "https://boards.4chan.org/{0}/res/{1}"
        urls = [post_template.format(board, post_num) for post_num in posts]
        if len(urls) > max_num_urls_displayed:
            message = output_to_sprunge('\n'.join(urls))
        else:
            message = " ".join(urls[:max_num_urls_displayed])
        sendMessage(channel, "{0}: {1}".format(sender, message))

def get_json_data(url, sleep_time=0):
    """Returns a json data object from a given url."""
    # Respect 4chan's rule of at most 1 JSON request per second
    sleep(sleep_time)
    try:
        open_url = urllib2.urlopen(url)
        json_data = simplejson.load(open_url.fp)
        open_url.close()
        return json_data
    except urllib2.HTTPError as e:
        if e.getcode() == 404:
            pass
        else:
            raise
    except Exception as e:
        log.error(e)
        raise

def search_thread(mutex, results_queue, thread_num, search_specifics):
    """
    Searches every post in thread thread_num on board board for the
    string provided. Returns a list of matching post numbers.
    """
    json_url = "https://a.4cdn.org/{0}/res/{1}.json".format(search_specifics["board"], thread_num)
    thread_json = get_json_data(json_url)
    re_search = None
    for post in thread_json["posts"]:
        user_text = "".join([post[s] for s in search_specifics["sections"] if s in post.keys()])
        re_search = re.search(search_specifics["string"], user_text, re.UNICODE)
        if re_search is not None:
            mutex.acquire()
            found_list.append("{0}#p{1}".format(thread_num, post["no"]))
            mutex.release()

def search_page(mutex, results_queue, page, search_specifics):
    """Will be run by the threading module. Searches all the 
    4chan threads on a page and adds matching results to synchronised queue"""
    for thread in page['threads']:
        user_text = "".join([thread[s] for s in search_specifics["sections"] if s in thread.keys()])
        if re.search(search_specifics["string"], user_text, re.UNICODE) is not None:
            mutex.acquire()
            results_queue.put(thread["no"])
            mutex.release()
        
def search_catalog(channel, sender, board, string):
    """Search all OP posts on the catalog of a board, and return matching results"""
    results_queue = Queue()
    mutex = RLock()
    json_url = "https://a.4cdn.org/{0}/catalog.json".format(board)
    sections = ["com", "name", "trip", "email", "sub", "filename"]
    catalog_json = get_json_data(json_url)
    search_specifics = {"sections" : sections, "board" : board, "string" : string}
    thread_pool = []

    for page in catalog_json:
        t = Thread(None, target=search_page, args=(mutex, results_queue, page, search_specifics, search_all_threads))
        t.start()
        thread_pool.append(t)

    for _thread in thread_pool:
        if _thread.is_alive():
            _thread.join()
    
    process_results(channel, sender, board, string, posts)

def search_board(channel, sender, board, string):
    """Search all the posts on a board and return matching results"""
    results_queue = Queue()
    mutex = RLock()
    json_url = "https://a.4cdn.org/{0}/threads.json".format(board)
    sections = ["com", "name", "trip", "email", "sub", "filename"]
    threads_json = get_json_data(json_url)
    search_specifics = {"sections" : sections, "board" : board, "string" : string}
    thread_pool = []

    for page in threads_json:
        for thread in page["threads"]:
            t = Thread(None, target=search_thread, args=(mutex, results_queue, thread["no"], search_specifics))
            t.start()
            thread_pool.append(t)
    
    for _thread in thread_pool:
        if _thread.is_alive():
            _thread.join()

    process_results(channel, sender, board, string, posts)









