import discord
from discord.ext import commands
from discord.utils import get
#from discord.utils import find

# for configuration parsing
import configparser

# for exit and envs etc
import sys

# for db
import json

def config_has_option(object, section, option, path):
    if not object.has_option(section, option):
        print("No attribute \"%s\" in \"%s\"" % (option, path))
        sys.exit(1)


### improve this with error handling etc
myconfig = configparser.ConfigParser()
myconfig.read('bot.conf')
if not myconfig.has_section('main'):
    print("No section [\"main\"] in \"%s\"" % 'bot.conf')
    sys.exit(1)

config_has_option(myconfig, 'main', 'token', 'bot.conf')
config_has_option(myconfig, 'main', 'prefix', 'bot.conf')
config_has_option(myconfig, 'main', 'guild', 'bot.conf')
config_has_option(myconfig, 'main', 'category', 'bot.conf')
config_has_option(myconfig, 'main', 'archive_category', 'bot.conf')
config_has_option(myconfig, 'main', 'role', 'bot.conf')

# set token and category and prefix
bot_token = myconfig.get('main', 'token')
bot_category = myconfig.get('main', 'category')
bot_archive_category = myconfig.get('main', 'archive_category')
bot_guild = myconfig.get('main', 'guild')
bot_command_prefix = myconfig.get('main', 'prefix')
bot_supporter_role = myconfig.get('main', 'role')


# define write function for case
async def write_db(db, file):
    with open(file, 'w') as f:
        json.dump(db, f, indent=2, sort_keys=True)

#load json at the beginning
try:
    with open('db.json') as f:
        db = json.load(f)
except FileNotFoundError:
    db = {'case': 1, 'users': {}}
    with open('db.json', 'w') as f:
        json.dump(db, f, indent=2, sort_keys=True)

# set command prefix for bot
bot = commands.Bot(command_prefix=bot_command_prefix)

# add listener on startup
@bot.event
async def on_ready():
    # at first check if guild in config is available
    if not get(bot.guilds, name=bot_guild):
        print("ERROR: Cannot find guild \"%s\"" % bot_guild)
        sys.exit(1)
    else:
        op_guild = get(bot.guilds, name=bot_guild)

    # check if role in guild exists
    if not get(op_guild.roles, name=bot_supporter_role):
        print("ERROR: Cannot find role for supporters")
        sys.exit(1)

    # check if channel categories exist in guild
    for guild_category in [bot_category, bot_archive_category]:
        if not get(op_guild.categories, name=guild_category):
            print('ERROR: Cannot find channel category "%s" to create support channels' % guild_category)
            sys.exit(1)

@bot.command()
async def create(ctx):
    author_id = ctx.author.id
    guild = get(bot.guilds, name=bot_guild)

    # not sure if this is really neccessary. But better safe than sorry
    if not get(guild.members, id=author_id):
        await ctx.send('ERROR: You are no member of server/guild "%s"' % bot_guild)
    else:
        # only one room should be open at one time
        if str(author_id) in db['users'].keys():
            await ctx.send('ERROR: You have already opened a case which is not closed. Please ask a supporter')
        else:
            role_object = get(guild.roles, name=bot_supporter_role)
            category_object = get(guild.categories, name=bot_category)

            # set permissions so the requester and the supporter wrote have write access and the bot can manage the channel.
            channel_overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                role_object: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                bot.user: discord.PermissionOverwrite(read_messages=True, manage_permissions=True),
            }

            # create the channel and message to the channel/user
            await guild.create_text_channel('case'+ str(db['case']), reason='case' + str(case_id) + ' created', category=category_object, overwrites=channel_overwrites)

            # add user to open case list
            db['users'][str(author_id)] = db['case']
            # update case number afterwards
            db['case'] = db['case'] + 1
            # write updates to db file
            await write_db(db, 'db.json')
            # send information to user
            await ctx.send('Channel "#%s" created. Please check for the channel in the "%s" category' % ('case' + str(db['case']), bot_category))


@bot.command()
async def close(ctx,case_id: int):
    # initialize needed objects
    guild = get(bot.guilds, name=bot_guild)
    role_object = get(guild.roles, name=bot_supporter_role)
    # check if user is a member of configured group
    if not ctx.author in role_object.members:
        await ctx.send('ERROR: You are not a member of role "%s" or the opener of this case. Sorry' % str(role_object))
    else:
        # check if there is a open case
        if case_id not in db['users'].values():
            await ctx.send('No open case available. Please check your case id')
        else:
            # get the channel fitting to case id mentioned
            text_channel = get(guild.text_channels, name='case' + str(case_id))
            category_object = get(guild.categories, id=text_channel.category_id)
            # check if channel is in the correct directory
            if str(category_object.name) != bot_category:
                await ctx.send('Channel is already archived. Manual intervention neccessary (move channel "#%s" into category %s' % ('case' + str(case_id), str(bot_category)))
            else:
                # get category object of destiation/archive category by name
                archive_category_object = get(guild.categories, name=bot_archive_category)

                # craft permission overrides. Only mods should able to read/write. And bot needs to have manage permissions
                channel_overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    role_object: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    bot.user: discord.PermissionOverwrite(read_messages=True, manage_permissions=True),
                }
                # sync permissions first and the overwrite them so supporter group and bot has still access
                await text_channel.edit(reason='case' + str(case_id) + ' closed', category=archive_category_object, sync_permissions=True)

                # remove case from db thanks stackoverflow
                # https://stackoverflow.com/questions/29218750/what-is-the-best-way-to-remove-a-dictionary-item-by-value-in-python
                db['users'] = {key:val for key, val in db['users'].items() if val != case_id}

                # write updates to db file
                await write_db(db, 'db.json')
                # send success information to user
                await ctx.send('Case #%s successfully closed.' % str(case_id) )

bot.run(bot_token)
