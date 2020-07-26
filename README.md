# Helpling
A supportive bot for bigger discord servers/guilds.

![helpling log](https://github.com/pseiler/hilfebot/raw/master/img/helpling.png)

This bot helps users reporting abuse, rule breaks and other delicts to a defined role / the moderators.
Users can create new cases via direct/channel message or reacting to a message in the guild.
This opens a new channel where a configured discord role and the requester can read and write messages.
The configured role can close the case via message command. This removes the requester from accessing
the channel and moves the channel to an archive channel category

## Features
* bot commands such as create and close with a configurable prefix
* configurable discord role
* automatic channel creating with defined permissions in a configurable channel category
* configurable channel category where channels will be moved into when a case is closed
* by reacting to a message with a configurable emoji a copy of the message with some meta information will be send into an open case channel
* * if there is no open case available a new one will be created
* * the reaction gets removed so no traces will be left
* only one case per discord user
* list all open cases
* consecutive case number
* configurable timezone for timestamps when messages will be copied into a case channel
* json file to store persistent data. It is used as a tiny database

## Requirements
* python3
* python3-pytz python3-configparser
* [discord.py](https://pypi.org/project/discord.py/)

## Installation
### Install requirements
You need to have python3 installed. On unix-based operation systems this can be done with the corresponding package manager. On Windows [download](https://www.python.org/downloads/windows/) and install python3 manually. After that, install the discord.py and pytz modules via pip or manually. For unix-based operating systems a dedicated user account to run the bot is prefered.
##### Install discord.py via pip
If ```pip3``` isn't available use ```pip``` instead. Make sure ```pip``` uses *python3* not *python2*
```sh
pip3 install --user discord.py pytz
```
##### Download the Bot
Clone the bot sourcecode with from github and change into that directory.
```sh
git clone https://github.com/pseiler/helpling.git && cd helpling
```
### Configuration
the configuration is quite simple. A few bot configurations are neccessary and additionally some guild preperations need to be done.
##### Discord guild configuration
Create two new channel category with a name you define. Reasonable names are *support* for active cases and *archive* for closed/archived cases. Also create a role to control the bot. Add the created role to both channel categories and explicitly add the *Read Text Channels & See Voice Channels* and *Send Messages* permissions to the role. Explicitly disallow everyone to *Read Text Channels & See Voice Channels* and *Send Messages* in both categories.
##### Bot configuration
At first you need to create an discord application and the corresponding bot. discord.py itself has a good documentation [for this](https://discordpy.readthedocs.io/en/latest/discord.html#). There you can get the bot token.
On the filesystem where the bot code is located, there is an example configuration named *bot.conf.example*. Just copy it and name the new file *bot.conf*. Adjust at least the *token*. Also change the *category* and *archive_category* parameter to the values from your server/guild. Feel free to change every parameter mentioned in the example file. Make sure the file *bot.conf* is in the same directory as *bot.py*

## Run the bot
### Temporary
To check if the bot is working correctly, run it from the command line as user
```sh
python3 bot.py
```
If the bot prints his name and the used timezone into stdout it should work properly. To test it, send commands to a channel or a direct message to the bot (f.e. !help). It should respond as expected.
### Run as a systemd service
to run your bot as a systemd service, simply create a service for it. This can by done by this command (replace the *$EDITOR* your with your favorite editor):
```sh
EDITOR=vim sudo -E systemctl edit --force --full helpling.service
```
Then copy the contents of *bot.service.example* into the editor.
Alternatively place the file directly to ```/etc/systemd/system/helpling.service``` and reload systemd with ```systemctl daemon-reload```.
Of course the name of the service can be changed too.
Please change the following parameters:
* **WorkingDirectory** - The path to the directory where your bot is located
* **ExecStart** - Change the path to the bot.py according to the files location
* **User** - Change the username to the user which executes the bot

### Other methods to run the bot permanently
The bot can also be executed via detached screen session. Also a simple bsd-style init script should work as expected. You can even write your own little management script with ```pgrep``` or similiar.

## ToDos
All todos can be found [here](./ToDo.md)

## Credits
* my girlfriend for the project name
* [Joanna Ambroziak](https://www.iconfinder.com/Nielubiewatrobki) for the awesome logo
* [KenDeep](https://twitter.com/kendeep_fgc) for a lot of input
