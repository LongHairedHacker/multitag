#!/usr/bin/env python3

import sys
import os
import subprocess

import yaml

import mutagen
from mutagen.id3 import ID3, CTOC, CHAP, TIT2, CTOCFlags
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4

YAML_KEYS = ["title", "artist", "date", "comment", "cover", "language", "chapters"]

def time_to_milliseconds(time_str):
    time_parts = list(map(lambda t: float(t), time_str.split(':')))
    time = 0
    for part in time_parts[:-1]:
        time = part + time * 60

    time = int((time_parts[-1] + time) * 1000)

    return time

def read_tag_file(chapter_file):
    if not os.path.isfile(chapter_file):
        raise RuntimeError("Chapter file %s does not exist" % chapter_file)

    tags = yaml.load(open(chapter_file, 'r'))

    for key in YAML_KEYS:
        if not key in tags:
            raise RuntimeError("Expected key %s not found in yaml" % key)


    tags['chapters'] = sorted(tags['chapters'].items(), key=lambda x: x[0])

    return tags


def make_mp3_tags(tags, path):
    id3 = EasyID3(path)

    id3['title'] = tags['title']
    id3['artist'] = tags['artist']
    id3['date'] = tags['date']
    id3['language'] = tags['language']

    id3.save()


def make_mp3_chapters(chapters, path):
    audio = mutagen.File(path)

    file_length = int(audio.info.length * 1000)

    element_ids = [(u"ch%d" % i) for i in range(0, len(chapters))]

    audio.tags.add(CTOC(element_id = u"toc",
                    flags = CTOCFlags.TOP_LEVEL | CTOCFlags.ORDERED,
                    child_element_ids = element_ids,
                    sub_frames = [
                        TIT2(text = [u"TOC"]),
                    ]))

    for i in range(0, len(chapters)):
        start_time, name = chapters[i]
        start_time = time_to_milliseconds(start_time)

        end_time = file_length - 1
        if i < len(chapters) - 1:
            end_time = time_to_milliseconds(chapters[i+1][0])

        audio.tags.add(CHAP(element_id = u"chp%d" % i, start_time = start_time, end_time = end_time,
                        sub_frames = [
                            TIT2(text = [name]),
                        ]))



def make_mp4_tags(tags, path):
    mp4 = EasyMP4(path)

    mp4['title'] = tags['title']
    mp4['artist'] = tags['artist']
    mp4['date'] = tags['date']

    mp4.save()

def make_mp4_chapters(chapters, path):
    chap_path = "%s.chapters.txt" % os.path.splitext(path)[0]
    chapter_file = open(chap_path, 'w')
    lines = [u"%s %s\n" % (start_time, name) for start_time, name in chapters]
    chapter_file.writelines(lines)
    chapter_file.close()

    popen = subprocess.Popen(["mp4chaps", "-i", path])
    popen.wait()

    os.remove(chap_path)

def make_ogg_tags(tags, audio):
    audio.tags['TITLE'] = tags['title']
    audio.tags['ARTIST'] = tags['artist']
    audio.tags['DATE'] = tags['date']
    audio.tags['LANGUAGE'] = tags['language']
    audio.tags['COMMENT'] = tags['comment']

    audio.save()

def make_ogg_chapters(chapters, audio):

    for i in range(0, len(chapters)):
        num = str(i).zfill(3)
        audio.tags['CHAPTER%s' % num] = chapters[i][0]
        audio.tags['CHAPTER%sNAME' % num] = chapters[i][1]

    audio.save()


def main():

    if len(sys.argv) < 3:
        print("Usage: %s tagfile mediafile1 mediafile2 mediafile3 ..." % sys.argv[0])
        sys.exit(0)

    tag_file_path = sys.argv[1]
    media_files = sys.argv[2:]

    tags = read_tag_file(tag_file_path)

    for path in media_files:
        print("Adding chapters to: %s" % path)

        audio = mutagen.File(path)

        if isinstance(audio, mutagen.mp3.MP3):
            make_mp3_tags(tags, path)
            make_mp3_chapters(tags['chapters'], path)
        elif isinstance(audio, mutagen.mp4.MP4):
            make_mp4_tags(tags, path)
            make_mp4_chapters(tags['chapters'], path)
        elif isinstance(audio, mutagen.oggvorbis.OggVorbis) or isinstance(audio, mutagen.oggopus.OggOpus):
            make_ogg_tags(tags, audio)
            make_ogg_chapters(tags['chapters'], audio)
        else:
            print("Skipping unsupported file: %s" % path)




if __name__ == '__main__':
    main()
