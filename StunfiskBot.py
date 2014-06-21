import praw, argparse, sys, json, re, os, time
from peewee import *

parser = argparse.ArgumentParser()

parser.add_argument('-u', '--username', help='username')
parser.add_argument('-p', '--password', help='password')

args = parser.parse_args()

user_agent = "StunfiskHelperBot v0.1.1 by /u/0ffkilter"

config_file =  open('%s%s' %(os.getcwd(), '/Config.txt'), 'r')
config = config_file.read().split('\n')
config_file.close()

reddit = praw.Reddit(user_agent = user_agent)
reddit.login('StunfiskHelperBot', config[0])

db = MySQLDatabase(database='stunbot', host='localhost', user='root', passwd=config[1])
db.connect()

learn_types = { 'M': 'a TM', 'L': 'Level Up', 'T': 'a Move Tutor', 'S': 'an Event', 'E': "an Egg Move"}
stats = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
rotom_forms = { 'w' : 'wash', 'h':'heat', 'c':'mow', 's':'fan', 'f':'frost'}
dex_suffixes = { 'b':'black', 'w':'white', 't':'therian', 'm':'mega'}

class Comment(Model):
    sub_id = CharField()
    class Meta:
        database = db

Comment.create_table(True)

def main():

    print('Subreddits: %s', ', '.join(config[2:]))
    while True:
        try:
            comments = praw.helpers.comment_stream(reddit, '+'.join(config[2:]), limit=None, verbosity=0)
            for comment in comments:
                if not already_processed(comment.id):
                    Comment.create(sub_id=comment.id)
                    comment_string = '***\n\n'
                    parent_string = '***\n\n'
                    for line in comment.body.strip().split('\n'):
                        if '+stunfiskhelp' in line:
                            print('comment found! %s' %(comment.id))
                            parent = '-parent' in line
                            line = line.replace('-parent', '')
                            line = line.replace('-confirm', '')
                            if (parent):
                                parent_string = parent_string + process_comment(line.replace('+stunfiskhelp', '').lower(), comment) + '\n\n***\n\n'
                            else:
                                comment_string = comment_string + process_comment(line.replace('+stunfiskhelp', '').lower(), comment) + '\n\n***\n\n'
                    if comment_string is not '***\n\n':
                        reply(comment_string, comment, False, False)
                    if parent_string is not '***\n\n':
                        reply(parent_string, comment, True, '-parent' in comment.body and '-confirm' in comment.body)


        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print(sys.exc_info()[0])

def can_learn(pokemon, move):
    move = move.replace(' ', '')
    if 'mega' in pokemon and (not 'yanmega' in pokemon and not 'meganium' in pokemon):
        pokemon = pokemon[:pokemon.index('mega')]

    print('%s -> %s' %(pokemon, move))

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
        return 'No Results Found\n\n'

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
    if 'moveset' in line:
        line = line.replace('moveset', '')
        moves = ''.join(line.split(' ')).split(',')
        return moveset_comment(moves)
    else:
        line.strip()
        sections = line.strip().split(' ')
        pokemon = sections[0]
        mode = sections[1]
        args = ''.join(sections[2:]).split(',')
        comment_string = ''
        print('Pokemon: %s Mode: %s Args: %s' %(pokemon, mode, args))
        if '-' in pokemon:
            temp_poke = ''
            if 'rotom' in pokemon:
                temp_poke = pokemon[:pokemon.index('-')] + rotom_forms[pokemon[pokemon.index('-')+1:]]
            else:
                temp_poke = pokemon[:pokemon.index('-')] + dex_suffixes[pokemon[pokemon.index('-')+1:]]

            if  temp_poke in pokedex:
                if mode == 'learnset':
                    comment_string = learnset_comment(pokemon, args)

                elif mode == 'data' or mode == 'info':
                    comment_string = data_comment(pokemon)
                elif mode == 'set':
                    comment_string = set_comment(pokemon)

                return comment_string
            else:
                return 'I couldn\'t find %s in the pokedex.  If this is an error, let /u/0ffkilter know' %(pokemon)

        else:
            if  pokemon.replace('-', '').replace(' ', '').strip() in pokedex:
                if mode == 'learnset':
                    comment_string = learnset_comment(pokemon, args)

                elif mode == 'data' or mode == 'info':
                    comment_string = data_comment(pokemon)
                elif mode == 'set':
                    comment_string = set_comment(pokemon)

                return comment_string
            else:
                return 'I couldn\'t find %s in the pokedex.  If this is an error, let /u/0ffkilter know' %(pokemon)

        print("Successful Comment! (Probably)\n")


def reply(comment_string, comment, parent, confirm):
    if parent:
        comment_to_parent(comment_string, comment, confirm )
    else:
        comment.reply(comment_string)



def comment_to_parent(string, comment, confirm):
    parent = reddit.get_info(thing_id=comment.parent_id)
    if type(parent) is praw.objects.Submission:
        parent.add_comment(string)
    elif type(parent) is praw.objects.Comment:
        parent.reply(string)

    if confirm:
        comment.reply('Confirmation Reply!')

def learnset_comment(pokemon, moves):

    if '-' in pokemon:
        if 'rotom' in pokemon:
            pokemon = pokemon[:pokemon.index('-')] + rotom_forms[pokemon[pokemon.index('-') + 1:]]
        else:
            pokemon[:pokemon.index('-')] + dex_suffixes[pokemon[pokemon.index('-')+1:]]


    comment = ''
    for move in moves:
        comment = '%s%s - %s\n\n' %(comment, pokemon, move)
        comment = '%s%s' %(comment, keys_to_string(can_learn(pokemon.replace('-', '').replace(' ', ''), move)))
    return comment

def data_comment(pokemon):
    if '-' in pokemon:
        if 'rotom' in pokemon:
            pokemon = pokemon[:pokemon.index('-')] + rotom_forms[pokemon[pokemon.index('-') + 1:]]
        else:
            pokemon = pokemon[:pokemon.index('-')] + dex_suffixes[pokemon[pokemon.index('-')+1:]]

    print('%s -> data' %(pokemon))
    name= pokemon
    pokemon = pokemon.replace('-', '').replace(' ', '')
    comment = ('>%s\n\n>Pokedex Number: %s\n\n>Types: %s\n\n>Abilities: %s\n\n>BaseStats:\n\n%s>Egg Groups: %s\n\n>Evolution: %s\n\n>PreEvolution: %s'
        %(name.capitalize(),
        str(pokedex[pokemon]['num']),
        '/'.join(pokedex[pokemon]['types']),
        ', '.join(pokedex[pokemon]['abilities'].values()),
        stats_to_string(pokemon),
        ', '.join(pokedex[pokemon]['eggGroups']),
        get_evo(pokemon).capitalize(),
        get_prevo(pokemon).capitalize()))
    return comment

def set_comment(pokemon):
    print('%s -> set' %(pokemon))
    if '-' in pokemon:
        if 'rotom' in pokemon:
            pokemon = pokemon[:pokemon.index('-')+1] + rotom_forms[pokemon[pokemon.index('-')+1:]]
            print('rotom form!  -> %s' %pokemon)
        else:
            pokemon =  pokemon[:pokemon.index('-')] + dex_suffixes[pokemon[pokemon.index('-')+1:]]



    page = reddit.get_wiki_page('stunfisk', pokemon)
    sections = page.content_md.split('##')

    if sections[3].index('Nature') == 0: return sections[2].replace('&gt;', '>') if len(sections[2]) > 10 else (
        'I couldn\'t find a set for %s in the pokedex.  I\'m sorry.' %pokemon)

    return ('##%s' % sections[3]).replace('&gt;', '>')

def moveset_comment(moves):
    print('Moveset -> %s' %(', '.join(moves)))
    pokes = []
    for pokemon in learnsets:
        if all(move in learnsets[pokemon]['learnset'] for move in moves):
            pokes.append(pokemon)

    comment_string = 'Here are the pokemon that can learn %s: \n\n* %s' %(', '.join(moves), '\n\n* '.join(pokes))
    return comment_string

def already_processed(sub_id):
    try:
        Comment.get(Comment.sub_id==sub_id)
        return True
    except:
        return False

file = open('Learnsets.json', 'r')
learnsets = json.load(file)
file.close()

file = open('Pokedex.json', 'r')
pokedex = json.load(file)
file.close()

try:
    print('Starting Bot...')
    main()
except KeyboardInterrupt:
    print('Force Quit the Bot')
    sys.exit(0)
