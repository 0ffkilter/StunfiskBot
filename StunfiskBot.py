import praw, argparse, sys, json

parser = argparse.ArgumentParser()

parser.add_argument('-u', '--username', help='username')
parser.add_argument('-p', '--password', help='password')

args = parser.parse_args()

user_agent = "StunfiskHelperBot v0.1 by /u/0ffkilter"

reddit = praw.Reddit(user_agent = user_agent)

def main():

    learnsets = json.loads(open('Learnsets.txt', 'r').read())

    comments = praw.helpers.comment_stream(reddit, 'KilterBots', limit=None, verbosity=0)
    for comment in comments:
        print(comment.body)
    print("Done")


main()


