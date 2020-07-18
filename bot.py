import discord
from discord.ext import commands
from discord.utils import get
#from discord.utils import find

# for configuration parsing
import configparser

# for exit and envs etc
import sys

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
config_has_option(myconfig, 'main', 'role', 'bot.conf')

# set token and category and prefix
bot_token = myconfig.get('main', 'token')
bot_category = myconfig.get('main', 'category')
bot_guild = myconfig.get('main', 'guild')
bot_command_prefix = myconfig.get('main', 'prefix')
bot_supporter_role = myconfig.get('main', 'role')

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

    # check if channel category exists in guild
    if not get(op_guild.categories, name=bot_category):
        print("ERROR: Cannot find channel category to create support channels")
        sys.exit(1)

@bot.command()
async def create(ctx,arg):
    # only one room should be open at one time
    # print(ctx.author)
    author_id = ctx.author.id
    guild = get(bot.guilds, name=bot_guild)

    # not sure if this is really neccessary. But better safe than sorry
    if not get(guild.members, id=author_id):
        await ctx.send('ERROR: You are no member of server/guild "%s"' % bot_guild)
    else:
        role_object = get(guild.roles, name=bot_supporter_role)
        category_object = get(guild.categories, name=bot_category)

        channel_overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            role_object: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        await guild.create_text_channel(arg,category=category_object, overwrites=channel_overwrites)
        await ctx.send('Channel "#%s" created. Please check for the channel in the "%s" category' % arg, bot_category)

@bot.command()
async def close(ctx,arg):
    # only one room should be open at one time
    # print(ctx.author)
    await ctx.send(arg)

bot.run(bot_token)
