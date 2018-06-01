# wiimmfi-rpc
A Discord rich presence implementation for Wiimmfi, made as user friendly as possible

## Installing
### For Windows Users
If you're using Windows, the easiest way would be to go over to the releases section and download the latest release. It contains a pre-compiled .exe, so there's no need to install additional programs and stuff. However, if you want to receive "beta" updates and stuff, you can follow the instructions for Unix systems below.

### For Unix Users
Unfortunately, I don't compile this program for OSX/Linux systems, so this'll require some more work.
First off, let's clone this repository.
```
git clone https://github.com/DismissedGuy/wiimmfi-rpc.git
```
That wasn't too hard, right? Good. Let's proceed then.
You'll have to have the latest **python 3** version installed (not py2). At the time of this writing, it's [3.6.5](https://www.python.org/downloads/release/python-365/), so head over to [the download page](https://www.python.org/downloads/) and install the correct release according to your system.

Once you've finished these instructions, you're done! Well, almost. To make this program recognize you when you're playing a game, you will have to add your friend code(s). Let's go to the next section, shall we?

## Configuring
I've tried to make this program as configurable as possible. Just want to start off right away? No problem! I've filled the config files in with default values, so you don't _have_ to configure everything. The only thing you'll have to do is input your games and friend codes. Nice, huh?

Inside the config/ folder, you'll see 3 configuration files:
* friend_codes.json
* rpc_config.json
* status_codes.json

The first file is required for this program to work, so let's begin with that first. Oh and by the way, you can edit these files with any text editor you like.

### friend_codes.json
This is the most important file. When you open it up, its contents should look like this:
```json
{
  "samplegame": "1234-5678-9012"
}
```
where "samplegame" is your Wiimfi Game ID© (yes, i made that name up) and the code, well.. your friend code.
And that brings us to the following sub-sub-subsection:

#### Getting your Wiimfi Game ID©
This is actually not too hard. Just go to [this page](https://wiimmfi.de/stat?m=25) and look for your game in that huuuuugge list. After you've found it, click on the status of your game and you'll be brought to the game history list.
Now, just look at your address bar and copy the line after the slash. That's it!

