# ToDo list
1. test for every permission neccesarry
1. add support for closing the case by the requester
1. implement reopen command (!reopen 14) (but supporter needs to be informed that user must be added manually
1. implement add command (!add 14 @user) add @user to case
1. implement remove command (!remove 14 @user) removes @user from case
1. add language support via config file
1. add list command (!list)  to show open cases and the user who opened it.
1. add support for a specific channel to post a message when a new case was opened
1. add support to configure the channel prefix (default is *case*)
1. categorize commands (not sure how to do that yet)
1. Use guild id instead of name in config to make sure it is mapped to the correct guild
1. handle close command error when no argument is given
1. check if channel already exists before creating.
1. add command to show next ticket number (!next)
1. move channel checks to future check section
1. add react watch and react on a specific emoji. create a case for it and paste the problematic message into the channel. (thanks KenDeep)
1. Grab also a few message before and after for better context (thanks KenDeep)
1. If a case is already open, add new reacts to an already open case instead of creating a new one (thanks KenDeep)
1. check for channel id/name and close with argument when in a support case channel (thanks KenDeep)
