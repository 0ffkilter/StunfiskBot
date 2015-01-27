import praw, argparse, sys, json, re, os, time, traceback
from peewee import *
from logins import *
from var_dicts import *
import HTMLParser

user_agent = "RMTBot 1.0 by /u/0ffkilter"

reddit = praw.Reddit(user_agent=user_agent)

reddit.login(rmt_name, rmt_password)

me = praw.objects.Redditor(reddit, 'RMTformatting')

db = MySQLDatabase(database='rmtbot', host='localhost', user='root', passwd=sql_password)
db.connect()

h = HTMLParser.HTMLParser()

subs = reddit.get_subreddit('stunfisk+doublade')

reg = re.compile('<[^>]+>')

class Post(Model):
    sub_id = CharField()
    class Meta:
        database = db

Post.create_table(True)

def main():
    print "starting RMT BOT!"

    while True:
        print('starting loop check')
        post_gen = subs.get_new(limit=10)
        posts = [post for post in post_gen]
        for post in posts:
            try:
                if not submission_read(post.id):
                    print('unread post -> %s' %post.title)
                    Post.create(sub_id=post.id)
                    if is_elligible(post):
                        if is_rmt(post.selftext_html, post.title):
                            print "found rmt post -> %s, %s" %(post.title, str(post.subreddit))
                            if post.title == None or post.selftext_html == None:
                                print "NoneType Post Found o.o"
                                reply_text = build_post(post.selftext_html, post.title)
                                post.add_comment(reply_text)
                            else:
                                print('previously read post -> %s' %post.title)

                comments = [x for x in me.get_comments(limit = 10)]
                for c in comments:
                    if c.ups < 0:
                        c.delete()
                time.sleep(480)
            except TypeError as e:
                print "Type Error Generated -> %s,  %s" %(post.title, str(post.subreddit))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(traceback.format_exc())

            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(traceback.format_exc())

def is_elligible(post):
    if post.is_self == True:
        if time.time() - post.created_utc < day:
            if post.selftext_html is not None:
                return True
    return False
def is_rmt(post, title):
    return any(tag in post or tag in title for tag in rmt_tags)
def is_doubles(post, title):
    return any(tag in post or tag in title for tag in tag_tiers[10:12])
def has_tier(post, title):
    return any(tag in post or tag in title for tag in tag_tiers)
def build_post(post, title):
    text = rmt_standard
    body = h.unescape(post)
    body = re.sub(reg, '', body)
    if body is None:
        print("body is none :( ")
    if not has_tier(post, title):
        text = rmt_tiers + text
    if len(body) < min_length:
        text = rmt_short + text
    if is_doubles(post, title):
        text = text + rmt_doubles
    return text + rmt_suffix

def submission_read(sub_id):
    try:
        Post.get(Post.sub_id==sub_id)
        return True
    except:
        return False

while True:
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())


