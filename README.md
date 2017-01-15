Multitag
========

A simple tool for adding metadata to multiple audio files in different formats.
Metadata is read from a yaml file and an additional jpg (for coverart)
and can be applied to multiple files at once.
It was developed with linux in mind, but might work on other platforms as well.


**Warning:** This is tool is a quick and dirty one day hack and has only been tested using mpv.
Expect bugs and other random weirdness.


Features
---------

Support audio formats:
* mp3
* mp4
* ogg vorbis
* ogg opus

Supported metadata entries:
* Title
* Artist
* Date
* Language
* Coverart (only jpg format supported)
* Chapters


Usage
-----
`multitag.py metadatafile audiofile1 audiofile2 ... audiofileN`


Dependencies
------------
* python3
* pyyaml
* mutagen
* libm4v2 (for the m4chaps utility)
