# ToDo list
* prevent spamming (only allow one room per user)
* setup configuration file for guild id, category id and token
* test for channel category and exit if it's not found
* test for every permission neccesarry
* check if a user is in the guild mentioned in the config file
* add json or similiar to track the case id/number (starts with one)
* implement case close command with id/number as first and only argument (!close 14). This removes user from db
* implement reopen command (!reopen 14) (but supporter needs to be informed that user must added manually
* implement add command (!add 14 @user) add @user to case
* implement remove command (!remove 14 @user) removes @user from case
* add language support via config file
* add list command (!list)  to show open cases and the user who opened it.
* add support for a specific channel to post a message when a new case was opened
* add support to configure the channel prefix (default is *case*)
