# Mypicotts

Mypicotts is a wrapper around picotts. picotts lacks of file to wave mode, makes it pretty hard to use as a TTS software.

## Overview

Mypicotts is a command line python3 based software with a limited functionality. Indeed, you only can pass a filename as an argument.
In the end you will get an mp3 file with the read aloud text.


Mypicotts-gtk is a GUI frontend of picotts. You can select enconding to ogg or mp3 if the enconders are available in your system.

## Usage

Cli

    mypicotts.py [--lang LANG] file.txt

`--lang` supports the same languages as picotts does. If not specified it defaults to spanish ('es-ES').  

GUI

    mypicotts-gtk.py

Write some text or open a file. Select the language and enconder a fire it. 


