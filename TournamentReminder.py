import praw, sys, os

user_agent = "Tournament Reminder by /u/0ffkilter"

config_file =  open('%s%s' %(os.getcwd(), '/Config.txt'), 'r')
config = config_file.read().split('\n')
config_file.close()

reddit = praw.Reddit(user_agent = user_agent)
reddit.login('stunfiskhelperbot', config[1])

part_file = open('%s%s' %(os.getcwd(), '/Participants.txt'), 'r')
parts = part_file.read().split('\n')
part_file.close()

message = ("Hello!  You are receiving this message because you are "
        "signed up for /r/stunfisk's Bucket O' Mons Tournament!  If you "
        "did not sign up for the tournament, that means that /u/0ffkilter "
        "typed in someone's name wrong.  You should probably let him know. \n\n"

        "In Any case, this is a reminder that Round 1 of the Tournament is out! \n\n"

        "The Theme is 'power pokes', and the post can be found "
        "[here](http://www.reddit.com/r/stunfisk/comments/2cejgl/tournament_bucket_o_mons_round_1_announcement/)\n\n "

        "You have until Tuesday, August 5th 12:00 PST to complete your match! \n\n"

        "Additional rules and regulations can be found on the aforementioned post. \n\n"

        "Send Questions or comments to /u/0ffkilter!")

subject = "Reminder for Bucket O' Mons Tournament!"

parts = ['bigyeIIowtaxi']

for participant in parts:
    try:

        reddit.send_message(participant, subject, message)
        print('Sent -> %s' %participant)
    except:
        print('Failed -> %s' %participant)

