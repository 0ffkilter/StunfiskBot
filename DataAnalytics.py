import praw, os, json, re
from collections import OrderedDict
from peewee import *


config_file = open('%s%s' %(os.getcwd(), '/Config.txt'), 'r')
config = config_file.read()
config_file.close
config = config.split('\n')

db = MySQLDatabase(database='stunbot', host='localhost', user='root', passwd=config[1])
db.connect()

rotom_forms = { 'w' : 'wash', 'h':'heat', 'c':'mow', 's':'fan', 'f':'frost'}
dex_suffixes = { 'b':'black', 'w':'white', 't':'therian', 'm':'mega', 'd':'defense', 'a':'attack', 's':'speed', 'mega':'mega'}
text_replace = { '\n':'', ',':'', ';':'', '.':'', '?':'', '!':'', '\'':'', '\"':''}


class Comment(Model):
    sub_id = CharField()
    class Meta:
        database = db

def main():
    stun_count = 0
    words = {}
    poke_dict = {}
    users = {}
    word_count = 0
    char_count = 0
    no_mention = 0
    comments = 0
    reddit = praw.Reddit(user_agent='/u/0ffkilter Data Analytics')
    poke_dict = { poke:0 for poke in pokedex}
    count = Comment.select().count()
    for comment in Comment.select():
        comments += 1
        print('Starting comment %s/%s' %(str(comments), str(count)))
        try:
            cur = reddit.get_info(thing_id='t1_' + comment.sub_id)
            text = cur.body
            text = re.sub('|'.join([',', '\.', ';', '\?', '\!', '\:', '&gt;' ]), ' ', text )
            sections = text.split(' ')
            word_count = word_count + len(sections)
            char_count = char_count + len(text)

            if str(cur.author) in users:
                users[str(cur.author)] += 1
            else:
                users[str(cur.author)] = 1
            for section in sections:
                section = section.strip().lower()
                if '-' in section:
                    if 'rotom' in section:
                        section = section[:section.index('-')] + rotom_forms[section[section.index('-') + 1:]]
                    else:
                        try:
                            section = section[:section.index('-')] + dex_suffixes[section[section.index('-')+1:]]
                        except: pass
                if section in pokedex:
                    poke_dict[section] = poke_dict[section] + 1
                if sections == '+stunfiskhelp':
                    stun_count += 1

                if section in words:
                    words[section] = words[section] + 1
                else:
                    words[section] = 1


            print('Finished Processing Comment -> %s' %comment.sub_id)
        except Exception as e:
            print(e)

    data_string = ''

    data_string = data_string + 'Total Comments Parsed : %s\n' %str(comments)
    data_string = data_string + 'Total Word Count: %s\n' %str(word_count)
    data_string = data_string + 'Total Char Count: %s\n' %str(char_count)
    data_string = data_string + 'Total User Count: %s\n' %str(len(users))
    data_string = data_string + 'Total Summons: %s\n' %str(stun_count)



    for poke in poke_dict:
        if poke_dict[poke] == 0:
            no_mention +=1

    data_string = data_string + 'Num Pokes not Mentioned: %s\n' %str(no_mention)

    file = open('Stats.txt', 'r+')
    file.write(data_string)
    file.close()

    print('finished data file')

    pokemon_string = ''

    poke_dict = OrderedDict([(k,v) for v,k in sorted([(v,k) for k,v in poke_dict.items()], reverse=True)])
    for poke in poke_dict:
        pokemon_string = pokemon_string + '%s : %s\n' %(poke, str(poke_dict[poke]))

    file = open('Pokemon.txt', 'r+')
    file.write(pokemon_string)
    file.close()

    print('finished Pokemon file')

    user_string = ''

    users = OrderedDict([(k,v) for v,k in sorted([(v,k) for k,v in users.items()], reverse=True)])
    for user in users:
        user_string = user_string + '%s : %s\n' %(user, str(users[user]))

    file = open('Users.txt', 'r+')
    file.write(user_string)
    file.close()

    print('finished user file')

    word_string = ''

    words = OrderedDict([(k,v) for v,k in sorted([(v,k) for k,v in words.items()], reverse=True)])

    for word in words:
        word_string = word_string + '%s : %s\n' %(word, str(words[word]))

    file = open('Words.txt', 'r+')
    file.write(word_string)
    file.close()

    print('finished word file')


file = open('Learnsets.json', 'r')
learnsets = json.load(file)
file.close()

file = open('Pokedex.json', 'r')
pokedex = json.load(file)
file.close()

main()
