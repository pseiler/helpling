# ToDo list
1. add support for closing the case by the requester
1. implement reopen command (!reopen 14 @user)
1. implement add command (!add 14 @user) add @user to case
1. implement remove command (!remove 14 @user) removes @user from case
1. add language support via config file
1. add support for a specific channel to post bot logs such as case creation, closing, reactions, etc
1. add support to configure the channel prefix (default is *case*)
1. categorize commands using [cogs](https://discordpy.readthedocs.io/en/latest/ext/commands/cogs.html#quick-example)
1. Consider using the guild id instead of name in config file to make sure it is mapped to the correct guild
1. Consider moving channel tests to [check](https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#checks) section
1. Grab also a few message before and after for better context (thanks KenDeep)
1. implement (!hi) command easter egg to check for server\_owner or suppoter or a funny message for unworthy users
1. implement check if user is administrator to skip role checks
1. optionally ping the supporter role in the newly created channel
1. add support for more than one guild (change db layout to add guild before case dict and remove guild from config file)
