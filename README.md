Email 2 Gotify
========

Email to [Gotify](https://github.com/gotify/server) notification

A fork of [email2pb](https://github.com/side2k/email2pb)


This simple script allows to redirect mail input(from postfix, for example) from a certain mail address to a Gotify notification. Useful to send pushes from sources which are able to send email only.


### Example usage

Let's imagine that we want to redirect all emails sent to push@example.com to your Gotify account (and therefore to your mobile devices).
These instructions below were tested on Ubuntu 16.04, with Python 2.7.12.

#### Step zero: setup and configure postfix for domain example.com and other prerequisites

Bla-bla-bla

#### Step 1: create shell script

First, create shell script which will contain email2gotify call and an API key. If you will directly specify python script with a API key in aliases file - this'll be a major security hole.
So our script will be something like this:

```
#!/bin/sh
/usr/bin/python /var/spool/postfix/email2gotify/gotify --key YOUR_GOTIFY_TOKEN
```

Let's name it...umm... `/var/spool/postfix/email2gotifyemail2gotify`
And make it executable:

```
chmod +x /var/spool/postfix/email2gotify/email2gotify
```

Why there? My example was tested in Debian, and postfix's home dir on Ubuntu 16.04 is /var/spool/postfix
Remember, postfix should be able to acces your script.


#### Step 2: add mail alias

Open /etc/aliases file and append a line there:

```
push: |/var/spool/postfix/email2gotify/email2gotify
```
Save the file and execute `newaliases` command.

#### Step 3: test it

Send email to push@example.com and, if it didn't work, check /var/log/mail.log


Thats it.
