import praw, argparse, sys, json, pprint

parser = argparse.ArgumentParser()

parser.add_argument('-u', '--username', help='username')
parser.add_argument('-p', '--password', help='password')

args = parser.parse_args()

user_agent = "StunfiskHelperBot v0.1 by /u/0ffkilter"

reddit = praw.Reddit(user_agent = user_agent)

def main():

    file = open('Learnsets.json', 'r')
    learnsets = json.load(file)
    file.close()

    learnsets['bulbasaur']['learnset']

    comments = praw.helpers.comment_stream(reddit, 'KilterBots', limit=None, verbosity=0)
    for comment in comments:
        print(comment.body)
    print("Done")


main()


