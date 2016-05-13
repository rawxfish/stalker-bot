import praw
import time
import datetime
import os
import atexit
from config import *

API = praw.Reddit('reddit stalker tool monitoring {}'.format(SUBREDDIT))

POST_LIST = "post_list"
WAIT_TIME = 60

def main():
    start_time = time.asctime()
    if not os.path.exists(POST_LIST):
        os.makedirs(POST_LIST)
    if not os.path.exists(POST_LIST + "/" + start_time):
        os.makedirs(POST_LIST + "/" + start_time)

    out_files = {}
    checked = {}
    for username in USER_LIST:
        user_list_file = POST_LIST + "/" + start_time + "/" + username + ".csv"
        if not os.path.exists(user_list_file):
            with open(user_list_file, 'w'):
                pass
            out_files[username] = open(user_list_file, 'a')
        checked[username] = set()

    def close():
        for username in USER_LIST:
            out_files[username].close()

    atexit.register(close)

    while(True):
        for username in USER_LIST:
            print("[bot] checking %s on %s" % (username, time.asctime()))
            user = API.get_redditor(username)
            submissions = user.get_submitted(sort='new')

            for s in submissions:
                if s.subreddit.display_name != SUBREDDIT:
                    continue

                if s.is_self or "livecap" not in s.url:
                    continue

                if s.name not in checked[username]:
                    print("[bot] new post: %s" % s.permalink)
                    checked[username].add(s.name)
                    out_files[username].write("%s,%s,%s\n" % (datetime.datetime.fromtimestamp(s.created), s.permalink, s.url))
                break

            out_files[username].flush()

        time.sleep(WAIT_TIME)


if __name__ == '__main__':
    main()
