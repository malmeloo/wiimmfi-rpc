# wiimmfi-rpc
A Discord rich presence implementation for Wiimmfi.

## Installing
For normal usage, you should head over to the [releases section](https://github.com/DismissedGuy/wiimmfi-rpc/releases) and download the latest release. You can then just run `start.py` using the latest python 3 version (3.6.5 atm).
For Windows systems, I've packed the scripts with the python executable, so having python installed isn't a requirement and you can simply run `start.exe` to start the script.

Once you're ready to run the program, you're done! Well, almost. To make this program recognize you when you're playing a game, you will have to add your friend code(s). Let's go to the next section, shall we?

## Configuring
I've tried to make this program as configurable as possible. Just want to start off right away? No problem! I've filled the config files in with default values, so you don't _have_ to configure everything. The only thing you'll have to do is input your games and friend codes.

Inside the config/ folder, you'll see 3 configuration files:
* friend_codes.json
* rpc_config.json
* status_codes.json

The first file is required for this program to work, so let's begin with that first. Oh and by the way, you can edit these files with any text editor you like. If you don't understand how these file formats work, try reading up on a website [like this one](https://www.tutorialspoint.com/json/json_syntax.htm).

### friend_codes.json
This is the most important file. When you open it up, its contents should look like this:
```json
{
  "samplegame": "1234-5678-9012"
}
```
where "samplegame" is the Game ID and the code, well.. your friend code.
An example file:
```json
{
  "mariokartwii": "1234-4321-1234",
  "smashbrosxwii": "0987-7890-0987"
}
```
And that brings us to the following sub-sub-subsection:

#### Getting your Game ID
This is actually not too hard. Just go to [this page](https://wiimmfi.de/stat?m=25) and look for your game in that huuuuugge list. In this list, you can do a quick `Ctrl+F` (Cmd+F??) to find your game. Its ID will be on the left.

### rpc_config.json
**rpc_id**
ID of the Discord rich presence application. Should not be changed, except for rare cases.

**show_game**
This parameter controls whether the game icon will be shown in your presence.
As every icon has to be added manually, turning this off can often fix problems where your presence isn't updating.
1 means on, 0 means off.

**timeout**
This parameter controls your presence refresh rate in seconds.
Lowering this will make your presence update more often, but also increases the amount of web requests that are sent.

**show_mkwii_room_data**
This parameter controls whether the rpc should show more detailed data when you're playing Mario Kart Wii (the room hoster).

### status_codes.json
This file stores the text corresponding to Wiimmfi's status codes (1-6).
Should be pretty straightforward, however when you notice your status being off, you can change the shown text in this file.

## Troubleshooting
There is a chance that the program crashes or just refuses to work. To read the error the program gives you, please run it in the terminal instead of executing it by double-clicking. I've listed a few common problems and their solutions here.

### It says my config files are invalid. What do I do now?
This probably means that you edited one of the files incorrectly. Please reinstall this program and refer to a page [like this](https://www.tutorialspoint.com/json/json_syntax.htm) to read up on JSON and its syntax, and try again.

### The rich presence doesn't show.
This problem can have multiple causes, so I'll go through them here.
- Does the program say that it's found you online? If not, check your friend code and try again.
- Does the program say that it couldn't find a specific game ID? If so, double check your ID(s) and try again.
- Make sure to have the Discord desktop client running and "display currently running game" turned on (settings -> games).
- For some games, the presence doesn't work because I haven't uploaded its images yet. To fix this, please read on.

### Fixing unsupported games
If a game doesn't seem to work, it might be because there is no image for it. Please check the list below to check whether that's the case. There are three ways to fix this:
1. Edit the `config/rpc_config.json` file and set `show_game` to 0. This will disable images for all of your games.
2. Open an issue and tell me your game ID + an image of at least 512x512 so I can add your game.
3. Create your own RPC Application (undocumented).

## Visually supported games
I've made a list below that contains all the games with rich presence artwork.

| Game ID | Platform | Full Game Name            |
|---------|----------|---------------------------|
| AMCJ    | NDS      | Mario Kart DS             |
| AMHE    | NDS      | Metroid Prime Hunters     |
| ATDE    | NDS      | Club House Games          |
| B4TE    | NDS      | Tetris Party Deluxe       |
| HCFA    | Wii      | Wii Speak Channel         |
| KUNV    | DSi      | UNO                       |
| RB6J    | Wii      | Bomberman Blast           |
| RMCJ    | Wii      | Mario Kart Wii            |
| RPBJ    | Wii      | Pokemon Battle Revolution |
| RSBJ    | Wii      | Super Smash Bros. Brawl   |
| RUUJ    | Wii      | Animal Crossing Wii       |
| WDMJ    | Wii      | Dr. Mario                 |
| WTKE    | Wii      | TV Show King 2            |
| WTPJ    | DSi/Wii  | Tetris Party Deluxe       |
