import praw, argparse, sys, json, re, os, time, traceback
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
reddit.login(config[0], config[1])

db = MySQLDatabase(database='stunbot', host='localhost', user='root', passwd=config[2])
db.connect()

learn_types = { 'M': 'a TM', 'L': 'Level Up', 'T': 'a Move Tutor', 'S': 'an Event', 'E': "an Egg Move"}
stats = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
rotom_forms = { 'w' : 'wash', 'h':'heat', 'c':'mow', 's':'fan', 'f':'frost'}
dex_suffixes = { 'b':'black', 'w':'white', 't':'therian', 'm':'mega', 'd':'defense', 'a':'attack', 's':'speed', 'mega':'mega'}
gens = [range(1, 152), range(152, 252), range(252, 387), range(387, 494), range(494, 650), range(650, 720)]

base_string = '***\n\n'
suffix = '\n\n^[help](http://www.reddit.com/r/Stunfisk/wiki/stunfiskbot) ^^created ^^by ^^/u/0ffkilter \n***'

class Comment(Model):
    sub_id = CharField()
    class Meta:
        database = db

Comment.create_table(True)

def main():

    print('Subreddits: %s', ', '.join(config[3:]))
    while True:
        try:
            comments = praw.helpers.comment_stream(reddit, '+'.join(config[2:]), limit=None, verbosity=0)
            for comment in comments:
                if not already_processed(comment.id):
                    Comment.create(sub_id=comment.id)
                    comment_string = base_string
                    parent_string = base_string
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

                    if comment_string is not base_string:
                        comment_string = comment_string + suffix
                        reply(comment_string, comment, False, False)
                    if parent_string is not base_string:
                        parent_string = parent_string + suffix
                        reply(parent_string, comment, True, '-parent' in comment.body and '-confirm' in comment.body)


        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(traceback.format_exc())

def get_learn(pokemon, move):
    move = move.replace(' ', '')
    if 'mega' in pokemon and (not 'yanmega' in pokemon and not 'meganium' in pokemon):
        pokemon = pokemon[:pokemon.index('mega')]

    print('%s -> %s' %(pokemon, move))

    if move in learnsets[pokemon]['learnset']:
        return learnsets[pokemon]['learnset'][move]
    else:
        if 'prevo' in pokedex[pokemon]:
            return get_learn(pokedex[pokemon]['prevo'], move)
        else:
            return []

def can_learn(pokemon, move):
    move = move.replace(' ', '')
    if 'mega' in pokemon and (not 'yanmega' in pokemon and not 'meganium' in pokemon):
        pokemon = pokemon[:pokemon.index('mega')]

    if move in learnsets[pokemon]['learnset']:
        return True
    else:
        if 'prevo' in pokedex[pokemon]:
            return can_learn(pokedex[pokemon]['prevo'].lower(), move)
        else:
            return False

def set_learns(pokemon, moves):
    if moves == []:
        return True
    return all(any(can_learn(pokemon, sub) for sub in move.split('/')) for move in moves)

def set_abilities(pokemon, abilities):
    if abilities == []:
        return True
    return all(any(abil.lower().title() in pokedex[pokemon]['abilities'].values() for abil in ability.split('/')) for ability in abilities)

def set_types(pokemon, poke_types):
    if poke_types == []:
        return True
    return all(any(poke_typ.lower().title() in pokedex[pokemon]['types'] for poke_typ in poke_type.split('/')) for poke_type in poke_types)

def set_gens(pokemon, gens):
    if gens == []:
        return True
    return get_gen(pokemon) in list(map(int, gens.split('/')))

def get_prevo(pokemon):
    return str(pokedex[pokemon]['prevo']) if 'prevo' in pokedex[pokemon] else 'None'

def get_evo(pokemon):
    return str(pokedex[pokemon]['evos'][0]) if 'evos' in pokedex[pokemon] else 'None'

def get_gen(pokemon):
    num = pokedex[pokemon]['num']
    for index, gen in enumerate(gens):
        if num in gen:
            return (index + 1)
    return 0


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

def get_last_set(sections):
    for i in range(len(sections)):
        try:
            if sections[i].index('Nature') == 0:
                return i
        except ValueError:
            pass

    return 3

def get_set_names(pokemon):
    page = reddit.get_wiki_page('Stunfisk', pokemon)
    sections = page.content_md.split('##')
    if is_format_correct(page):
        names = sections[3:get_last_set(sections)]
        for index, name in enumerate(names):
            if '#' in name:
                name = name.replace('#', '')[:name.index('\n')]
                names[index] = name
        print('Sets found -> %s', names)
        return names
    else:
        print('Incorrectly formatted page for: %s' %pokemon)
        return []

def is_format_correct(wiki_page):
    sections = wiki_page.content_md.split('##')
    return not sections[3][:7] == 'Nature'

def format_poke(pokemon):
    if '-' in pokemon:
        if 'rotom' in pokemon:
            pokemon = pokemon[:pokemon.index('-')] + rotom_forms[pokemon[pokemon.index('-') + 1:]]
        else:
            pokemon = pokemon[:pokemon.index('-')] + dex_suffixes[pokemon[pokemon.index('-')+1:]]
    return pokemon

def format_poke_set(pokemon):
    if '-' in pokemon:
        if 'rotom' in pokemon:
            pokemon = pokemon[:pokemon.index('-')+1] + rotom_forms[pokemon[pokemon.index('-')+1:]]
            print('rotom form!  -> %s' %pokemon)
        else:
            pokemon =  pokemon[:pokemon.index('-')+1] + dex_suffixes[pokemon[pokemon.index('-')+1:]]
    return pokemon

def sort_by_bst(pokemon):

    poke_dict = {poke:sum(pokedex[poke]['baseStats'].values()) for poke in pokemon}
    return sorted(poke_dict, key=poke_dict.get, reverse=True)


def process_comment(line, comment):

    if 'tell me a joke' in line:
        return 'Your Life'
    parent = '-parent' in line
    line = line.replace('-parent', '')
    confirm = '-confirm' in line and parent
    line = line.replace('-confirm', '')
    if 'moveset' in line:
        number = 30
        numbers = [int(s) for s in line.split() if s.isdigit()]
        if numbers == []:
            number = 30
        else:
            if (number > 100):
                number = 100
            else:
                number = numbers[0]
        for number in numbers:
            line = line.replace(str(number), '')
        line = line.replace('moveset', '')
        moves = line.replace(' ', '').split(',')

        return moveset_comment(moves, number)
    elif 'search' in line:


        line = line.replace('search', '')
        moves = []
        types = []
        abilities = []
        gens = []

        sections = line.split('|')
        for section in sections:
            if 'move:' in section or 'moves:' in section:
                moves = section[section.index(':')+1:].replace(' ', '').split(',')
            elif 'ability:' in section or 'abilities:' in section:
                abilities = section[section.index(':')+1:].strip().split(',')
            elif 'type:' in section or 'types:' in section:
                types = section[section.index(':')+1:].strip().split(',')
            elif 'gen:' in section or 'gens:' in section:
                gens = section[section.index(':')+ 1:].strip()

        return search_comment(moves, abilities, types, gens)

    else:
        line.strip()
        sections = line.strip().split(' ')
        pokemon = sections[0]
        mode = sections[1]
        args = ''.join(sections[2:]).split(',')
        comment_string = ''
        print('Pokemon: %s Mode: %s Args: %s' %(pokemon, mode, args))
        if '-' in pokemon:
            temp_poke = format_poke(pokemon)
            if  temp_poke in pokedex:
                if mode == 'learnset':
                    comment_string = learnset_comment(pokemon, args)

                elif mode == 'data' or mode == 'info':
                    comment_string = data_comment(pokemon)
                elif mode == 'set':
                    if 'list' in line:
                        comment_string = set_name_comment(pokemon)
                    else:
                        comment_string = set_comment(pokemon, args)

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
                    if 'list' in line:
                        comment_string = set_name_comment(pokemon)
                    else:
                        comment_string = set_comment(pokemon, args)

                return comment_string
            else:
                return 'I couldn\'t find %s in the pokedex.  If this is an error, let /u/0ffkilter know' %(pokemon)



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
    print('%s -> learnset' %pokemon)
    pokemon = format_poke(pokemon)
    comment = ''
    for move in moves:
        comment = '%s%s - %s\n\n' %(comment, pokemon, move)
        comment = '%s%s' %(comment, keys_to_string(get_learn(pokemon.replace('-', '').replace(' ', ''), move)))
    return comment

def data_comment(pokemon):
    pokemon = format_poke(pokemon)
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

def set_name_comment(pokemon):
    print('%s -> set list' %pokemon)
    names = get_set_names(pokemon)
    if names == []:
        return 'No defined sets found for %s' %pokemon
    else:
        comment_string = ''
        for name in names:
            comment_string = comment_string + '\n\n* %s \n\n' %name
        return comment_string

def set_comment(pokemon, set_names):
    pokemon = format_poke_set(pokemon)
    page = reddit.get_wiki_page('stunfisk', pokemon)
    sections = page.content_md.split('##')
    print('%s -> set' %(pokemon))
    comment_string = ''
    if is_format_correct(page):
        sets = sections[3:get_last_set(sections)]
        if set_names == []:
            print('No Sets Quested -> Giving First One')
            return '##%s' %sets[0].replace('&gt;', '>')
        else:
            print('Sets Requested -> %s' %set_names)
            for name in set_names:
                for set in sets:
                    if name.strip().lower() in set[:set.index('\n')].replace(' ', '').lower():
                        comment_string = comment_string + '##%s \n\n' %set.replace('&gt;', '>')
        return comment_string
    else:
        if sections[3].index('Nature') == 0:
            if len(sections[2]) > 10:
                return sections[2].replace('&gt;', '>')
            else:
                return 'No Sets Found, Sorry!'

    return ('Something happened - an error I think.  Here, have something that I think is a set.\n\n##%s' % sections[3]).replace('&gt;', '>')

def search_comment(moves, abilities, types, gens):
    print ('Moves     -> %s' %(', '.join(moves)))
    print ('Abilities -> %s' %(', '.join(abilities)))
    print ('Types     -> %s' %(', '.join(types)))
    print ('Gens      -> %s' %(', '.join(gens)))
    pokes1 = []
    pokes2 = []
    for pokemon in learnsets:
        if set_learns(pokemon, moves):
            pokes1.append(pokemon)
    for pokemon in pokedex:
        if set_abilities(pokemon, abilities) and set_types(pokemon, types) and set_gens(pokemon, gens):
            pokes2.append(pokemon)
    pokes = list(set(pokes1).intersection(set(pokes2)))

    if moves == []:
        moves = ['anything']

    if abilities == []:
        abilities = ['anything']

    if types == []:
        types = ['anything']

    if gens ==[]:
        gens = ['any gen']

    if len(pokes) > 0:

        if len(pokes) > 30:
            pokes = pokes[:30]
        pokes = sort_by_bst(pokes)
        comment_string = 'Here are the strongest %s pokemon that: \n\n> %s \n\n> %s \n\n> %s \n\n> %s \n\n* %s' %(
                    str(len(pokes)),
                    ('learn: %s' % ', '.join(moves)),
                    ('have %s as abilities' %', '.join(abilities)),
                    ('have %s as types'  %', '.join(types)),
                    ('and are in gen: %s' %', '.join(gens)),
                    '\n\n* '.join(pokes))
    else:
        comment_string = 'No pokemon found, sorry'

    return comment_string

def moveset_comment(moves, number):
    print('Moveset -> %s' %(', '.join(moves)))
    pokes = []
    for pokemon in learnsets:
        if set_learns(pokemon, moves):
            pokes.append(pokemon)

    if len(pokes) > 0:
        pokes = sort_by_bst(pokes)
        pokes = pokes[:number]
        comment_string = 'Here are the strongest %s pokemon out of  %s total that can learn %s: \n\n* %s' %(
            str(number),
            str(max(len(pokes), number)),
            ', '.join(moves),
            '\n\n* '.join(pokes))
    else:
        comment_string = 'No pokemon found, sorry'

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
