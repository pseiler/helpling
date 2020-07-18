import discord
from discord.ext import commands

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
config_has_option(myconfig, 'main', 'category', 'bot.conf')
config_has_option(myconfig, 'main', 'prefix', 'bot.conf')


# set token and category and prefix
bot_token = myconfig.get('main', 'token')
bot_category = myconfig.get('main', 'category')
bot_command_prefix = myconfig.get('main', 'prefix')

# set command prefix for bot
bot = commands.Bot(command_prefix=bot_command_prefix)

@bot.command()
async def create(ctx,arg):
    # only one room should be open at one time
    # print(ctx.author)
    guild = ctx.message.guild

    # get categeory object ( don't hardcode anymore in the future
    category_object = discord.utils.get(ctx.guild.categories, name=bot_category)

    await guild.create_text_channel(arg,category=category_object)
    await ctx.send(arg)

@bot.command()
async def close(ctx,arg):
    # only one room should be open at one time
    # print(ctx.author)
    await ctx.send(arg)


bot.run(bot_token)
