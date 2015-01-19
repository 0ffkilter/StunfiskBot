
learn_types = { 'M': 'a TM', 'L': 'Level Up', 'T': 'a Move Tutor', 'S': 'an Event', 'E': "an Egg Move"}
stats = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
rotom_forms = { 'w' : 'wash', 'h':'heat', 'c':'mow', 's':'fan', 'f':'frost'}
dex_suffixes = { 'b':'black', 'w':'white', 't':'therian', 'm':'mega', 'd':'defense', 'a':'attack', 's':'speed', 'mega':'mega', 'mega-y':'megay', 'mega-x':'megax', 'i':''}
gens = [range(1, 152), range(152, 252), range(252, 387), range(387, 494), range(494, 650), range(650, 720)]

base_string = '***\n\n'
suffix = '\n\n^[help](http://www.reddit.com/r/Stunfisk/wiki/stunfiskbot) ^^created ^^by ^^/u/0ffkilter \n***'

rmt_tags = ['rmt', 'hmf', 'hms', 'rmt', 'help me finish', 'help me start', 'my team', 'my first team']
tag_tiers = ['ou', 'uu', 'ru', 'nu', 'pu', 'fu', 'overused', 'underused', 'rarelyused', 'neverused', 'vgc', 'doubles', 'triples']
min_length = 1000
day = 86400

rmt_standard = """

Hello there!  It seems you've posted a request for an analysis on your team!

Here's a few things to remember when you make your post:

  * Remember to playtest your team!  Replays help people know how your team functions and what your general strategy is.

  * Try to analyze the team yourself.  Play with the team and try to find out what gives your team problems.  If you can figure this out, it's easier for people to help you.

  * Formatting.  Reddit formatting is different, and having a poorly formatted post makes it harder for users to help you out.

    * The most common mistake is spacing.  To make a new space on reddit, you need to enter TWO (2) new lines instead of just one.

  * Use online resources to help you!

    * Calculate your team's weaknesses [here](http://www.teammagma.net/teambuilder/)

    * See what walls and stalls your team [here](http://sweepercalc.com/swc/)

"""

rmt_doubles = """

It seems you've made a doubles team!  Try posting it to /r/doublade instead since it's a subreddit made specifically for doubles posts.  If this is already in doublade, then you don't have to do anything (the programmer who made me was too lazy to check).

"""

rmt_short = """

Unfortunately, it seems that your rmt post is kind of short.  This means that there probably isn't enough critical information in the post regarding your team.

The post doesn't have to be exceptionally long, but you should include at least a sentence or two about each pokemon.

Check to make sure you have the following information:

  * A full, complete set for each pokemon.  If you can't come up with something, check smogon's pokedex or the subreddit's pokedex instead!  The most important thing is that you have information for each pokemon, even if it isn't the best set.

  * A bit of explanation for each pokemon.

    *  What does each pokemon do?

    *  What is its specific role on the team?

    *  If it has unusual or custom built evs, what is the purpose of the evs?
"""

rmt_tiers = """

I couldn't detect a tier in your post.  Remember to put the tier that the team performs in in the title of the post, or make it visible in the actual post.

"""

rmt_suffix = """

This is an automatic bot set up to help people format their RMTS (and other teambuilding posts).

Want to delete this post?

Too bad, that's not happening.

Questions? Comments? Missing something?

Send it to someone who cares.


^^^Send ^^^it ^^^to ^^^/u/0ffkilter
"""
