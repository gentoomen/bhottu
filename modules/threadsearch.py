"""
Searches posts on 4chan using the 4chan JSON API and returns the post
url of any matching post
"""
import regex as re
import ujson as json
import time
import requests
import traceback
from api import *
from utils.pastebins import paste
from time import sleep
from threading import *
from collections import deque
import time

def load():
    """Load the module"""
    registerFunction("catalog %s %S", catalog_search_handler, "catalog <board> <regex>")
    registerFunction("board %s %S", board_search_handler, "board <board> <regex>")
registerModule("ThreadSearch", load)

def sanitise(string):
    """Strips a string of all non-alphanumeric characters"""
    return re.sub(r"[^a-zA-Z0-9 ]", "", string)

def catalog_search_handler(channel, sender, board, user_regex):
    """Handler for initiating catalog search"""
    def do(channel, sender, board, user_regex):
        results_data = perform_concurrent_4chan_search(board, user_regex, catalog_search=True)
        process_results(channel, sender, results_data)
    Thread(target=do, args=(channel, sender, board, user_regex)).start()

def board_search_handler(channel, sender, board, user_regex):
    """Handler for initiating full board search"""
    def do(channel, sender, board, user_regex):
        results_data = perform_concurrent_4chan_search(board, user_regex, catalog_search=False)
        process_results(channel, sender, results_data)
    Thread(target=do, args=(channel, sender, board, user_regex)).start()

def process_results(channel, sender, results_data):
    """Process the resulting data of a search and present it"""
    max_num_urls_displayed = 1
    search_parameters = results_data["search_parameters"]
    post_numbers = results_data["post_numbers"]
    total_time = results_data["total_time"]

    if len(post_numbers) <= 0:
        sendMessage(channel, "{0}: No results for {1} on {2}".format(sender, search_parameters["string"],
                                                                     search_parameters["user_board"]))
    else:
        post_template = "https://boards.4chan.org/{0}/thread/{1}"
        urls = [post_template.format(search_parameters["board"], post_num) for post_num in post_numbers]
        if len(urls) > max_num_urls_displayed:
            message = paste('\n'.join(urls))
        else:
            message = " ".join(urls[:max_num_urls_displayed])
        sendMessage(channel, "{0}: {1} | Search time {2:.2f}s | {3} matches".format(sender, message, total_time, len(urls)))

def get_json_data(url):
    """Returns a json data object from a given url."""
    response = None
    try:
        response = requests.get(url)
        if response.status_code == 404:
            log.error("url {}: 404".format(url))
            return None
        json_data = json.loads(response.text.encode())
        return json_data
    except Exception as e:
        if response is None:
            exception_string = "url: {0}\n{1}".format(url, traceback.format_exc())
        else:
            exception_string = "url: {0} status_code: {1}\n{2}".format(
                    url, response.status_code, traceback.format_exc())
        log.error(exception_string)
        print(exception_string)
        raise

def search_thread(results_deque, thread_num, search_parameters):
    """
    Searches every post in thread thread_num on a board for the
    string provided. Returns a list of matching post numbers.
    """
    json_url = "https://a.4cdn.org/%s/thread/%s.json" % (search_parameters["board"], thread_num)
    thread_json = get_json_data(json_url)
    if thread_json is None:
        return

    regex_search = search_parameters["compiled_regex"].search
    sections = search_parameters["sections"]
    deque_append = results_deque.append
    for post in thread_json["posts"]:
        for item in map(post.__getitem__, filter(post.has_key, sections)):
            if regex_search(item):
                deque_append("%s#p%s" % (thread_num, post.__getitem__("no")))
                break


def search_catalog_page(results_deque, page, search_parameters):
    """Will be run by the threading module. Searches all the 
    4chan threads on a page and adds matching results to synchronised queue"""
    regex_search = search_parameters["compiled_regex"].search
    sections = search_parameters["sections"]
    deque_append = results_deque.append
    for thread in page["threads"]:
        for item in map(thread.__getitem__, filter(thread.has_key, sections)):
            if regex_search(item):
                deque_append(thread.__getitem__("no"))
                break

def perform_concurrent_4chan_search(board, user_regex, catalog_search=False):
    """Search a thread or catalog on 4chan using several threads concurrently, then return relevant data"""
    thread_join_timeout_seconds = 10
    results_deque = deque()
    json_url = "https://a.4cdn.org/{0}/{1}.json".format(board, "catalog" if catalog_search else "threads")
    # Note that "tim" is used for the timestamp that is used to name files on 4chan
    sections = ["com", "name", "filename", "sub", "ext", "tim"] 
    json_data = get_json_data(json_url)
    search_regex = re.compile(user_regex, re.UNICODE + re.IGNORECASE)
    search_parameters = {"sections": sections, "board": sanitise(board), "string": user_regex,
            "compiled_regex": search_regex, "user_board": board}
    results_data = {"post_numbers": results_deque, "search_parameters": search_parameters, "total_time": 0}
    thread_pool = []

    start = time.time()

    if json_data is None:
        return results_data

    for page in json_data:
        if catalog_search:
            t = Thread(None, target=search_catalog_page, args=(results_deque, page, search_parameters))
            t.start()
            thread_pool.append(t)
        else:
            for thread in page["threads"]:
                t = Thread(None, target=search_thread, args=(results_deque, thread["no"], search_parameters))
                t.start()
                thread_pool.append(t)

    for _thread in thread_pool:
        if _thread.is_alive():
            _thread.join(float(thread_join_timeout_seconds))
    end = time.time()
    results_data['total_time'] = end - start
    return results_data


