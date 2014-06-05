import praw, argparse, sys, json, re

parser = argparse.ArgumentParser()

parser.add_argument('-u', '--username', help='username')
parser.add_argument('-p', '--password', help='password')

args = parser.parse_args()

user_agent = "StunfiskHelperBot v0.1 by /u/0ffkilter"

reddit = praw.Reddit(user_agent = user_agent)

learn_types = { 'M': 'A TM', 'L': 'Level Up', 'T': 'A Move Tutor', 'S': 'An Event', 'E': "an Egg Move"}

learn_regex = re.compile('(?<=can )\w+|(?= learn)\w+')

def main():

    comments = praw.helpers.comment_stream(reddit, 'KilterBots', limit=None, verbosity=0)
    for comment in comments:
        if '+stunfiskhelp' in comment.body:
            print(keys_to_string(can_learn(comment.body.split()[1], comment.body.split()[2])))


def can_learn(pokemon, move):
    if move in learnsets[pokemon]['learnset']:
        return learnsets[pokemon]['learnset'][move]
    else:
        if 'prevo' in pokedex[pokemon]:
            return can_learn(pokedex[pokemon]['prevo'], move)
        else:
            return null

def keys_to_string(keys):
    if keys:
        result = ''
        for key in keys:
            result = result + gen_string(key) + '\n'
        return result
    else:
        return 'No Results Found'

def gen_string(key):
    string = 'Generation ' + key[0] + ' through ' + learn_types[key[1]]
    if key[1] == 'l':
        string = string + ' at Level ' + key[2::w]
    return string

file = open('Learnsets.json', 'r')
learnsets = json.load(file)
file.close()

file = open('Pokedex.json', 'r')
pokedex = json.load(file)
file.close()


main()


