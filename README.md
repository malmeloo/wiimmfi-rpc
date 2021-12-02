# Wiimmfi-RPC
Show your Discord friends what you're playing on Wiimmfi!

![AppVeyor](https://img.shields.io/appveyor/build/DismissedGuy/wiimmfi-rpc/gui-rewrite)
![Release](https://img.shields.io/github/v/release/DismissedGuy/wiimmfi-rpc)
![GitHub All Releases](https://img.shields.io/github/downloads/DismissedGuy/wiimmfi-rpc/total)
![GitHub](https://img.shields.io/github/license/DismissedGuy/wiimmfi-rpc)
![Python Version](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue)

## ⚠️ Due to recent attacks on Wiimmfi's server, Wiimmfi has deployed a DDoS protection system which unfortunately breaks automated tools such as this one. I am aware of the issue but it is impossible to fix, so please do not use this program until this is changed (if ever). You *will* run into errors.
#### Update: There is possibly a way to get around this limitation, but it would require refactoring most of the internal code, as well as dropping some features such as the online user tab. I am currently investigating possible solutions.

![Discord Preview](https://github.com/DismissedGuy/wiimmfi-rpc/raw/master/assets/discord_preview.png)

## Features
* Works for all games on all Wiimmfi-capable consoles (Wii, WiiWare, NDS and DSiWare)
* Python is not a requirement; download, unzip and go!
* Cross-platform: works on both Windows and Linux! (Mac OSX under testing)
* Easy to use friendcode manager
* Shows game art for popular games
* Support for 2-player games
* Shows Mario Kart Wii room info (if possible)
* Adaptive timeout logic allows for accurate presences while keeping bandwidth and server stress low
* Built-in updater so you'll always be on the latest version!

### Planned Features
Nothing yet! If you know something you'd like to see, please open an issue or [contact me](#contact) on Discord.

## Screenshots
See the [assets](assets) directory for screenshots!

## Installation
There are two "editions" of this program. Both of these have their pros and cons, so I'll list them below.

### "Packaged" edition
This is for the people who just want things to work without too much of a hassle. There's no additional programs to download which allows you to get the program up and running in no time!

You can download it over at the [releases](https://github.com/DismissedGuy/wiimmfi-rpc/releases/) page. Simply extract the zip into a directory and run the executable!

#### Pros
- Extremely easy to set up

#### Cons
- **Updates might require manual work.** Although the updater seems to be decently robust, it will not remove the old program for you. Make sure to always run the latest executable so you don't run into any errors.
- You can only update to the latest stable release. This should be fine for the majority of the users.
- The file size is rather large, so it takes longer for updates to download. The reason for this is that all of the program's dependencies are packed into a single file.
- For Linux users: You'll have to (re)mark the program as executable after an update.

### "Live" edition
This is for those that are not afraid to get their hands dirty. Although it requires some knowledge on how to set it up, it does allow you to update to the latest prerelease version, which, although it might be a bit unstable at times, includes the newest and hottest features available.

#### Pros
- Fully automatic updater, requiring no extra work (unless you've renamed the main file, in which case you will have to remove it)
- Updates are blazing fast and file sizes are small
- Updates to the latest prerelease

#### Cons
- Requires basic knowledge of how to use Python features, such as how to install dependencies using pip.

## Game art requests
In order for this program to show game art in your rich presence, I will have to add it manually. If you notice that the program is not showing an image for a game you'd like to see, please create an [issue](https://github.com/DismissedGuy/wiimmfi-rpc/issues/) and select "Game Art Request". Simply fill out the fields and I'll add it if possible!

## FAQ
**It's not showing my presence.**

This can be caused by multiple things. Try making your way through this checklist first, but if you still can't get it to work, please [contact me](#contact). It might be a bug.

- [ ] Make sure that the program is currently running.
- [ ] Make sure that your Discord client is currently running (the local client, not in your web browser!)
- [ ] Turn on "Display currently running game as status message" under Settings -> Game Activity in your Discord client.
- [ ] Make sure that no other program is using the rich presence at this time. If multiple programs are trying to use the rich presence, Discord will pick only one of them based on some (unknown to me) factors.
- [ ] If you know what to look for, check the logs in the log directory. It might show useful information.

**I can't get it to work.**

No problem! Contact me using one of [these methods](#contact) and I'll help you out.

**I think I've found a bug.**

That sucks. It would be nice if you could create an issue so I can look into it. You can also contact me in one of the ways linked to above if that's what you prefer.

**You're not replying to my issue or messages!**

I must've either missed it or am unavailable at the moment. GitHub notifications are kinda wonky for me sometimes. You could shoot me a Discord DM if I don't reply within a day or so.

## Contact
Are you stuck somewhere during the installation process, have you found a bug, do you have a question or are you simply up for a chat? You can contact me anytime using one of these methods:

- Discord (preferred): DismissedGuy#2118
- [GitHub Issues](https://github.com/DismissedGuy/wiimmfi-rpc/issues/)
- Email: dismissed.is.a.guy \[at] gmail \[dot] com
