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
from multiprocessing import *
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

def run_catalog_search(channel, sender, board, string, all_posts=False):
    """Search 4chan posts for a search string and return
    the matching post numbers"""
    # Strip unyieldly characters
    board = sanitise(board)
    message = ""
    try:
        posts = search_catalog(string, board, all_posts)
        posts = list(set(posts))
    except Exception as e:
        log.error(e)
        raise
    if len(posts) <= 0:
        sendMessage(channel, "{0}: No results for {1}".format(sender, string))
    else:
        # Turn the post numbers into fully-fledged URLs
        post_template = "https://boards.4chan.org/{0}/res/{1}"
        urls = [post_template.format(board, post_num) for post_num in posts]
        if len(urls) > 3:
            # If the number of posts is more than 3,
            # then send it to sprunge.us
            message = output_to_sprunge('\n'.join(urls))
        else:
            message = " ".join(urls[:3])
        sendMessage(channel, "{0}: {1}".format(sender, message))

def run_board_search(channel, sender, board, string):
    """Wrapper for catalog search to make it search
    the entire board"""
    run_catalog_search(channel, sender, board, string, True)

def get_json_data(url, sleep_time=1):
    """Returns a json data object from a given url."""
    # Respect 4chan's rule of at most 1 JSON request per second
    # but only if searching the catalog
    sleep(sleep_time)
    try:
        open_url = urllib2.urlopen(url)
        json_data = simplejson.load(open_url.fp)
        open_url.close()
        return json_data
    except urllib2.HTTPError as e:
        # Handle if a thread has 404'd
        if e.getcode() == 404:
            pass
        else:
            raise
    except Exception as e:
        log.error(e)
        raise

def search_thread(mutex, thread_num, process_data, found_list):
    """
    Searches every post in thread thread_num on board board for the
    string provided. Returns a list of matching post numbers.
    """
    json_url = "https://api.4chan.org/{0}/res/{1}.json".format(process_data["board"], thread_num)
    thread_json = get_json_data(json_url, process_data["request_delay"])
    re_search = None
    for post in thread_json["posts"]:
        user_text = "".join([post[s] for s in process_data["sections"] if s in post.keys()])
        re_search = re.search(process_data["string"], user_text, re.UNICODE)
        if re_search is not None:
            mutex.acquire()
            found_list.append("{0}#p{1}".format(thread_num, post["no"]))
            mutex.release()

def search_page(mutex, process_count, page, process_data, found_list):
    """Will be run by the multiprocessing module. Searches all the 
    threads on a page and stores any matching results in an array"""
    # Process count is used as a counting semaphore to 
    # keep track of how many processes are currently active
    process_count.value += 1
    for thread in page['threads']:
        user_text = "".join([thread[s] for s in process_data["sections"] if s in thread.keys()])
        if re.search(process_data["string"], user_text, re.UNICODE) is not None:
            mutex.acquire()
            found_list.append(thread["no"])
            mutex.release()
        if process_data["all_posts"]:
            search_thread(mutex, thread['no'], process_data, found_list)
    process_count.value -= 1

def search_catalog(string, board, all_posts):
    """
    Searches through every thread on a board. Sets the sleep limit as 
    the base 2 logarithm of    how many posts there are on a board
    """
    manager = Manager()
    mutex = manager.Lock()
    process_count = Value('i', 0)
    json_url = "https://api.4chan.org/{0}/catalog.json".format(board)
    sections = ["com", "name", "trip", "email", "sub", "filename"]
    found_list = manager.list()
    catalog_json = get_json_data(json_url)
    # Add in an artificial delay of the log base 2 of the number of posts on that board.
    # Moot requests that there be at least 1 second between 4chan API requests
    # This will create at least some form of delay
    #thread_count = sum([len(page['threads']) for page in catalog_json])
    #request_delay = float(math.log(thread_count, 2)) / thread_count
    request_delay = 0
    process_data = {"sections" : sections, "request_delay" : request_delay,
            "board" : board, "string" : string, "all_posts" : all_posts} 
    timeout_value = 60

    for page in catalog_json:
        p = Process(target=search_page, args=(mutex, process_count, page, process_data, found_list))
        # Make sure that the child process is teriminated once this parent process is
        p.daemon = True
        p.start()
    
    timeout_timer = time.clock()
    # Wait until all processes have completed
    while process_count.value > 0:
        # Have a timer running in case one of the child processes doesn't finish 
        if (time.clock() - timeout_timer) > timeout_value:
            log.error("Timed out")
            break
    return found_list


