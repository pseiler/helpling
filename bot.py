import discord
from discord.ext import commands

from discord.utils import get, find as ds_find

# for configuration parsing
import configparser

# for exit and envs etc
import sys

# for json parsing and writing support. a simple json file is used as a "db" backend.
import json

# used to determine timezone
from pytz import timezone, exceptions as tz_exceptions
import datetime

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
config_has_option(myconfig, 'main', 'timezone', 'bot.conf')
config_has_option(myconfig, 'main', 'emoji', 'bot.conf')

# set token and category and prefix
bot_token = myconfig.get('main', 'token')
bot_category = myconfig.get('main', 'category')
bot_archive_category = myconfig.get('main', 'archive_category')
bot_guild = myconfig.get('main', 'guild')
bot_command_prefix = myconfig.get('main', 'prefix')
bot_supporter_role = myconfig.get('main', 'role')
bot_timezone = myconfig.get('main', 'timezone')
bot_emoji = myconfig.get('main', 'emoji')

# set local timezone and check for validity
try:
    my_timezone = timezone(bot_timezone)
except tz_exceptions.UnknownTimeZoneError:
    print('ERROR: Timezone "%s" not found. Please check your configuration' % bot_timezone)
    print('\nA table with TZ database names can be found on wikipedia')
    print('https://en.wikipedia.org/wiki/List_of_tz_database_time_zones')
    sys.exit(1)

# set also static UTC timezone
utc_timezone = timezone('UTC')

#################
### functions ###
#################
async def channel_exists(name, channel_list):
    if ds_find(lambda m: m.name == str(name), channel_list) != None:
        return True
    else:
        return False

async def create_dm(member):
    if member.dm_channel == None:
        await member.create_dm()

# define write function for cases
async def write_db(db, file):
    with open(file, 'w') as f:
        json.dump(db, f, indent=2, sort_keys=True)

async def update_channel(channel, id, new_category, overwrites):
    await channel.edit(reason='case' + str(id) + ' closed', category=new_category, overwrites=overwrites, sync_permissions=True)

# returns dict without the mentioned value (id). Thanks stackoverflow
# https://stackoverflow.com/questions/29218750/what-is-the-best-way-to-remove-a-dictionary-item-by-value-in-python
async def remove_key_by_val(dict, id):
    return {key:val for key, val in dict.items() if val != id}

async def check_if_user_has_role(member):
    guild = get(bot.guilds, name=bot_guild)
    author_id = member.id
    role_object = get(guild.roles, name=bot_supporter_role)
    if member in role_object.members:
        return True
    else:
        return False

###################################
### here starts the actual code ###
###################################

#load json at the beginning. Create new file when missing
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
    print('Login complete')
    print('Timezone: ' + str(bot_timezone))
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


@bot.event
async def on_raw_reaction_add(payload):
    emoji = payload.emoji

    # check if emoji is a unicode emoji
    if emoji.is_unicode_emoji():
        # check if its fit the emoji from the configuration
        if emoji.name == bot_emoji:
            reporter_id = payload.member.id
            guild = get(bot.guilds, id=payload.guild_id)
            channel = get(guild.text_channels, id=payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            message_author = message.author

            # add missing timezone information (stupid discord)
            utc_timestamp = message.created_at.replace(tzinfo=utc_timezone)

            formatted_timestamp = utc_timestamp.strftime("%a, %Y-%m-%d, %H:%M %Z")
            # this time object is used to create the timestamp for the channel message
            formatted_local_timestamp = utc_timestamp.astimezone(my_timezone).strftime("%a, %Y-%m-%d, %H:%M %Z")

            # get the support channel for a emoji report
            if str(reporter_id) in (db['users'].keys()):
                if not await channel_exists('case'+str(db['users'][str(reporter_id)]), guild.text_channels):
                    # make sure direct message channel is create before messaging to it
                    await create_dm(payload.member)
                    # send emoji responses as a direct messsage
                    await payload.member.dm_channel.send('Channel *#%s* missing. Please ask a **%s** for help.' % ('case' + str(db['case']),bot_supporter_role))
                else:
                    case_channel = ds_find(lambda m: m.name == 'case'+str(db['users'][str(reporter_id)]), guild.text_channels)
                    # craft messeage
                    message_content = '```\n%s\n```\n*Message link*: %s\n\n>>> **%s**: %s' % (str(formatted_local_timestamp), message.jump_url, str(message_author), message.content)
                    await case_channel.send(message_content)
            else:
                role_object = get(guild.roles, name=bot_supporter_role)
                category_object = get(guild.categories, name=bot_category)
                channel_overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    payload.member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    role_object: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    bot.user: discord.PermissionOverwrite(read_messages=True, manage_permissions=True),
                }
                # create the channel and message to the channel/user
                await guild.create_text_channel('case'+ str(db['case']), reason='case' + str(db['case']) + ' created', category=category_object, overwrites=channel_overwrites)
                # add user to open case list
                db['users'][str(reporter_id)] = db['case']
                # get created object by name
                case_channel = ds_find(lambda m: m.name == 'case'+str(db['users'][str(reporter_id)]), guild.text_channels)

                # make sure direct message channel is create before messaging to it
                await create_dm(payload.member)

                # send emoji responses as a direct messsage
                await payload.member.dm_channel.send('Channel *#%s* created. Please check for the channel in the **%s** category' % ('case' + str(db['case']), bot_category))

                # craft message response
                message_content = '```\n%s\n```\n*Message link*: %s\n\n>>> **%s**: %s' % (str(formatted_local_timestamp), message.jump_url, str(message_author), message.content)
                
                # send copied message into case channel
                await case_channel.send(message_content)

                # update case number afterwards
                db['case'] = db['case'] + 1
                # write updates to db file
                await write_db(db, 'db.json')
                # send information to user

            # delete reaction with this remove after handling report
            for reaction in message.reactions:
                if reaction.emoji == bot_emoji:
                    await reaction.remove(payload.member)

# create a new case manually
@bot.command(description="Create a new support case", brief='Create/open a new support case')
async def create(ctx):
    author_id = ctx.author.id
    guild = get(bot.guilds, name=bot_guild)

    # not sure if this is really neccessary. But better safe than sorry
    if not get(guild.members, id=author_id):
        await ctx.send('ERROR: You are no member of server/guild **%s**' % bot_guild)
    else:
        # only one room should be open at one time
        if str(author_id) in db['users'].keys():
            await ctx.send('ERROR: You have already opened a case (*#%s*) which is not closed.\nPlease ask a member of role **%s**.' % (str(db['users'][str(author_id)]), bot_supporter_role))
        else:
            role_object = get(guild.roles, name=bot_supporter_role)
            category_object = get(guild.categories, name=bot_category)

            # check if channel already exists
            if await channel_exists('case'+str(db['case']), guild.text_channels):
                await ctx.send('Cannot create channel "#%s". It already exists. Ask a member of "%s" for help' % ('case' + str(db['case']), bot_supporter_role))
            else:

                # set permissions so the requester and the supporter wrote have write access and the bot can manage the channel.
                channel_overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    role_object: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    bot.user: discord.PermissionOverwrite(read_messages=True, manage_permissions=True),
                }
                # create the channel and message to the channel/user
                await guild.create_text_channel('case'+ str(db['case']), reason='case' + str(db['case']) + ' created', category=category_object, overwrites=channel_overwrites)
                await ctx.send('Channel *#%s* created. Please check for the channel in the "%s" category' % ('case' + str(db['case']), bot_category))
                # add user to open case list
                db['users'][str(author_id)] = db['case']
                # update case number afterwards
                db['case'] = db['case'] + 1
                # write updates to db file
                await write_db(db, 'db.json')
                # send information to user


@bot.command(description="Close a specified case", brief=bot_supporter_role +' only. Close an open case.', usage='<CASE ID>')

# this line works. But I can't send a message. in a check TODO
#@commands.check(check_if_user_has_role)

async def close(ctx,case_id: int):
    # initialize needed objects
    guild = get(bot.guilds, name=bot_guild)
    role_object = get(guild.roles, name=bot_supporter_role)
    # TODO check if a channel is in the right category

    # check if channel exists
    if not await channel_exists('case' + str(case_id), guild.text_channels):
        await ctx.send('ERROR: channel *%s* is missing. Create it manually to proceed.' % ('case' + str(case_id)))
    else:
        # check if user is a member of configured group
        if not await check_if_user_has_role(ctx.author):
            await ctx.send('ERROR: You are not a member of role **%s**. Sorry' % str(role_object))
        else:
            # check if there is a open case
            if case_id not in db['users'].values():
                await ctx.send('No open case with id *%s* available.\nPlease check your case id' % str(case_id))
            else:
                # get the channel fitting to case id mentioned
                text_channel = get(guild.text_channels, name='case' + str(case_id))
                category_object = get(guild.categories, id=text_channel.category_id)
                # check if channel is in the correct directory
                if str(category_object.name) != bot_category:
                    await ctx.send('ERROR: Channel is already archived. Manual intervention neccessary.\nMove channel *#%s* into category *%s*' % ('case' + str(case_id), str(bot_category)))
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
                    await update_channel(text_channel, case_id, archive_category_object, channel_overwrites)

                    db['users'] = await remove_key_by_val(db['users'], case_id)

                    # write updates to db file
                    await write_db(db, 'db.json')
                    # send success information to user
                    await ctx.send('Case *#%s* successfully closed.' % str(case_id) )
@close.error
async def close_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        # set variables as usual
        guild = get(bot.guilds, name=bot_guild)
        role_object = get(guild.roles, name=bot_supporter_role)
        if not await check_if_user_has_role(ctx.author):
            await ctx.send('ERROR: You are not a member of role **%s**. Sorry' % str(role_object))
        else:
            # let channels be closed without id when in a case channel
            if not "case" in ctx.message.channel.name:
                message = '```\nERROR: No case number given\n\nUsage:\n%sclose <ID>\n\n<ID> can be ommited if you are in a %s channel\n```' % (bot_command_prefix, 'case')
                await ctx.send(message)
            else:
                    # set variables as usual
                    guild = get(bot.guilds, name=bot_guild)
                    role_object = get(guild.roles, name=bot_supporter_role)
                    case_id = int(str(ctx.message.channel).replace('case', ''))
                    archive_category_object = get(guild.categories, name=bot_archive_category)

                    channel_overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        role_object: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                        bot.user: discord.PermissionOverwrite(read_messages=True, manage_permissions=True),
                    }
                    # sync permissions first and the overwrite them so supporter group and bot has still access
                    await update_channel(ctx.message.channel, case_id, archive_category_object, channel_overwrites)

                    # remove a user determined by case id. thanks stackoverflow
                    # https://stackoverflow.com/questions/29218750/what-is-the-best-way-to-remove-a-dictionary-item-by-value-in-python
                    db['users'] = await remove_key_by_val(db['users'], case_id)

                    # write updates to db file
                    await write_db(db, 'db.json')
                    # send success information to user
                    await ctx.send('Case *#%s* successfully closed.' % str(case_id) )

@bot.command(description=str(bot_supporter_role) +' only: List all open cases.', brief=bot_supporter_role +' only: List all open cases.')
async def list(ctx):
    guild = get(bot.guilds, name=bot_guild)
    role_object = get(guild.roles, name=bot_supporter_role)
    # check if user is a member of configured group
    if not ctx.author in role_object.members:
        await ctx.send('ERROR: You are not a member of role "%s" or the opener of this case. Sorry' % str(role_object))
    else:
        # check if db['users'] is empty. If yes print that there is no open case
        if bool(db['users']):
            formatted_text = "__All open cases__:\n------"
            for i in db['users'].items():
                user = bot.get_user(int(i[0]))
                formatted_text += "\n{key}#{disc}: *#{value}*".format(key=user.name, disc=user.discriminator, value=i[1])
            # send the generated message
            await ctx.send(formatted_text)
        else:
            await ctx.send('No open cases available')

bot.run(bot_token)
