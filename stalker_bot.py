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
    for username in USER_LIST:
        user_list_file = POST_LIST + "/" + start_time + "/" + username + ".csv"
        if not os.path.exists(user_list_file):
            with open(user_list_file, 'w'):
                pass
            out_files[username] = open(user_list_file, 'a')

    def close():
        for username in USER_LIST:
            out_files[username].close()

    atexit.register(close)

    last_checked = {}
    while(True):
        for username in USER_LIST:
            print("[bot] checking %s on %s" % (username, time.asctime()))
            user = API.get_redditor(username)
            submissions = None
            if user in last_checked and len(last_checked[user]) > 0:
                last = last_checked[user][-1]
                while (API.get_submission(submission_id=last[3:]).author is None or len(last_checked[user]) > 0):
                    last_checked[user].pop()
                    last = last_checked[user][-1]

                print("last: " + last)
                submissions = user.get_submitted(sort='new', params={"before": last})
            else:
                submissions = user.get_submitted(sort='new')

            submissions = list(submissions)
            submissions.reverse()
            for s in submissions:
                if s.subreddit.display_name != SUBREDDIT:
                    continue

                if s.is_self or "livecap" not in s.url:
                    continue

                print("[bot] new post: %s" % s.permalink)
                out_files[username].write("%s,%s,%s\n" % (datetime.datetime.fromtimestamp(s.created), s.permalink, s.url))


                if user in last_checked:
                    last_checked[user].append(s.fullname)
                else:
                    last_checked[user] = [s.fullname]

            out_files[username].flush()

        time.sleep(WAIT_TIME)


if __name__ == '__main__':
    main()
