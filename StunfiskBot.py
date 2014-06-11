import praw, argparse, sys, json, re

parser = argparse.ArgumentParser()

parser.add_argument('-u', '--username', help='username')
parser.add_argument('-p', '--password', help='password')

args = parser.parse_args()

user_agent = "StunfiskHelperBot v0.1 by /u/0ffkilter"

reddit = praw.Reddit(user_agent = user_agent)
reddit.login('StunfiskHelperBot', 'ratchet')

learn_types = { 'M': 'a TM', 'L': 'Level Up', 'T': 'a Move Tutor', 'S': 'an Event', 'E': "an Egg Move"}
stats = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
approved_users = ['StunfiskDexter', '0ffkilter', 'veeveearnh']


approved_regex = re.compile('###.*?###', re.DOTALL|re.MULTILINE )
other_regex = re.compile('##Sets.*?##Nature', re.DOTALL|re.MULTILINE)

def main():

    comments = praw.helpers.comment_stream(reddit, 'KilterBots', limit=None, verbosity=0)
    for comment in comments:
        for line in comment.body.strip().split('\n'):
            if '+stunfiskhelp' in line:
                print('comment found! %s' %(comment.id))
             #   process_comment(line.replace('+stunfiskhelp', '').lower(), comment)

def can_learn(pokemon, move):
    move = move.replace(' ', '')
    if move in learnsets[pokemon]['learnset']:
        return learnsets[pokemon]['learnset'][move]
    else:
        if 'prevo' in pokedex[pokemon]:
            return can_learn(pokedex[pokemon]['prevo'], move)
        else:
            return []

def get_prevo(pokemon):
    return str(pokedex[pokemon]['prevo']) if 'prevo' in pokedex[pokemon] else 'None'

def get_evo(pokemon):
    return str(pokedex[pokemon]['evos'][0]) if 'evos' in pokedex[pokemon] else 'None'

def keys_to_string(keys):
    if keys:
        result = ''
        for key in keys:
            result = result + gen_string(key) + '\n\n'
        return result
    else:
        return 'No Results Found'

def gen_string(key):
    string = '* Generation ' + key[0] + ' through ' + learn_types[key[1]]
    if key[1] == 'l':
        string = string + ' at Level ' + key[2:]
    return string

def stats_to_string(pokemon):
    string = ''
    for stat in stats:
        string += '>>' + stat + ': ' + str(pokedex[pokemon]['baseStats'][stat]) + '\n\n'
    return string

def process_comment(line, comment):
    parent = '-parent' in line
    line = line.replace('-parent', '')
    confirm = '-confirm' in line and parent
    line = line.replace('-confirm', '')

    line.strip()
    sections = line.split(' ')
    pokemon = sections[0]
    mode = sections[1]
    args = sections[2:]
    comment_string = ''
    if pokemon.replace('-', '').replace(' ', '') in pokedex:
        if mode == 'learnset':
            comment_string = learnset_comment(pokemon, args)
        elif mode == 'data' or mode == 'info':
            comment_string = data_comment(pokemon)
        elif mode == 'set' or 'moveset':
            comment_string = set_comment(pokemon)

        if parent:
            comment_to_parent(comment_string, comment, confirm )
    else:
        comment.reply('Pokemon not found!  Sorry about that.')

def comment_to_parent(string, comment, confirm):
    parent = reddit.get_info(thing_id = 't1_%s' %(comment))
    if type(parent) is praw.Objects.Submission:
        parent.add_comment(string)
    else:
        parent.reply(string)

    if confirm:
        comment.reply('Confirmation Reply!')

def learnset_comment(pokemon, moves):
    comment = ''
    for move in moves:
        comment = '%s%s - %s\n\n' %(comment, pokemon, move)
        comment = '%s%s' %(comment, keys_to_string(can_learn(pokemon, move)))
    return comment

def data_comment(pokemon):
    pokemon = pokemon.replace('-', '').replace(' ', '')
    comment = ('>%s\n\n>Pokedex Number: %s\n\n>Types: %s\n\n>Abilities: %s\n\n>BaseStats:\n\n%s>Egg Groups: %s\n\n>Evolution: %s\n\n>PreEvolution: %s'
        %(pokemon.capitalize(),
        str(pokedex[pokemon]['num']),
        ', '.join(pokedex[pokemon]['types']),
        ', '.join(pokedex[pokemon]['abilities'].values()),
        stats_to_string(pokemon),
        ', '.join(pokedex[pokemon]['eggGroups']),
        get_evo(pokemon).capitalize(),
        get_prevo(pokemon).capitalize()))
    return comment

def set_comment(pokemon):
    page = reddit.get_wiki_page('stunfisk', pokemon)
    sections = page.content_md.split('##')

    if sections[3].index('Nature') == 0: return sections[2] if sections[2].len() > 10 else 'No Sets Found'

    return section[3]


file = open('Learnsets.json', 'r')
learnsets = json.load(file)
file.close()

file = open('Pokedex.json', 'r')
pokedex = json.load(file)
file.close()

main()
