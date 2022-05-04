# aTasteProgram
Program for upcoming piece. Creates scores measure by measure using data obtained from a chat interface. To attempt a high relationship between 
audience activity and resulting music, the data obtained is limited to command frequency (``volume``) and subjective continuity of each command (`direction`).

## Requirements
* Python 3.7 or newer.
* PyQt5 installed
* [twitchio](https://twitchio.dev/en/latest/) python library installed
* Lilypond Music Notation Software (can be downloaded [here](https://lilypond.org/doc/v2.23/Documentation/web/download))
* Pypond: library created for this project. Repository can be found [here](https://github.com/tqmbanados/pypond). The library must be in the same folder as this program, in a folder called `pypond`. 

Additionally:
* A folder titled `ly_files` must be created in the same directory as the `main.py` or `main.exe` files.
* In the same directory as above, a file must be created called `private_parameters.py`. These hold the parameters `channel_name` and `url`. `channel_name` is for the Twitch channel the bot will connect to, while `url` is the url of the API, and can be set to `localhost` by default. 
* In the folder `twitch_bot`, a file must be created containing the bots AUTH information, called `token_data.py`. This must contain three parameters: `OAUTH_TOKEN`, `CLIENT_TOKEN` and `ADMIN`. Information on what the first two should contain can be found in the above link and in [this](https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8) tutorial. `ADMIN` is the name of the twitch account allowed to send commands to the bot; this can be left empty for testing. 

## Executable
For those who don't have Python or Git installed, an executable version can be found [here](https://drive.google.com/drive/folders/1QBPYQZZcQzIF3kKNgpHF70ut7ll_NNAc?usp=sharing). 

## How to run

For the executable version, simply run the file "main.exe". For the code version, run the file by entering "python main.py" in your command line. This command may change depending on your python version. 
For testing without an API, it is important to set the parameter `USE_API` in `parameters.py` to `False`.

On the window, you will have access to different options:
 * **Next**: Ask the program to generate one measure of music.
 * **Advance**: Ask the program to advance the piece, causing the material to be used differently.
 * **End**: Save all generated measures as one lilypond file.
 * **Auto-generate**: Cause the program to atomatically advance the piece. Next option must still be clicked manually. 

For the executable, and older version of the programm is used, that requires less dependencies and is better for testing. Here only the options `Next` and `End` and `Run` are available, run being equivalent to `Autogenerate`, but not requiring the `Next` button to be clicked manually.  

## Interface for performers

Performence use a separate program to connect to an API where the Lilypond code is saved. This program is founde [here](https://github.com/tqmbanados/PuppetInterface).
