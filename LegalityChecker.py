import praw, os, sys, time

def main():
    while True:
        try:
            messages = list(reddit.get_unread())
            if len(messages) >= 1:
                for message in messages:
                    message.mark_as_read()
                    if message.subject.lower() == 'rmt':
                        print('Message from /u/%s', str(message.author))
                        pokemon = message.body.replace(' ', '').lower().split(',')
                        print('Pokemon: %s' %pokemon)
                        if is_legal(pokemon):
                            message.reply('Your Team is **LEGAL** for Round 1 of Bucket O\' Mons!  Go Fight!')
                        else:
                            message.reply('Your Team is **ILLEGAL** for Round 1 of Bucket O\' Mons.  Sorry about that, try again and make sure to review the rules.')

            time.sleep(10)
        except Exception as e:
            print(e)

def is_legal(pokemon):
    if len(pokemon) != 6:
        print('Failed Party Number Length')
        return false

    if len(list(set(pokemon).intersection(set(required)))) == 1:
        pokemon.remove(list(set(pokemon).intersection(set(required)))[0])
    else:
        print('Failed Required Pokemon Check')
        return False

    if any(wildcard in pokemon for wildcard in wildcards):
        for poke in list(set(pokemon).intersection(set(wildcards))):
            pokemon.remove(poke)

    if any(all(poke in bucket for poke in pokemon) for bucket in buckets):
        return True
    else:
        print('Failed Bucket Check')
        return False

    return False



user_agent = 'Team Legality Checker by /u/0ffkilter'

config_file =  open('%s%s' %(os.getcwd(), '/Config.txt'), 'r')
config = config_file.read().split('\n')
config_file.close()

reddit = praw.Reddit(user_agent = user_agent)
reddit.login(config[0], config[1])

bucket_file = open('%s%s' %(os.getcwd(), '/Buckets.txt'), 'r')
bucket_text = bucket_file.read().split('\n')
bucket_file.close()

required = bucket_text[0].replace(' ', '').lower().split(',')
print('Required Pokemon -> %s' %required)
wildcards = bucket_text[1].replace(' ', '').lower().split(',')
print('WildCard Pokemon -> %s' %wildcards)
buckets = bucket_text[2:]

for index, bucket in enumerate(buckets):
        buckets[index] = bucket.replace(' ', '').lower().split(',')
        print('Bucket %s -> %s' %(index, buckets[index]))

try:
    print('Starting Legality Checker')
    main()
except KeyboardInterrupt:
    sys.exit(0)
