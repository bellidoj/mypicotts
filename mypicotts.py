#!/usr/bin/env python3


import sys
import os
import subprocess
import glob
import wave
import argparse

from contextlib import closing


DEBUG = False
parser = argparse.ArgumentParser(prog='mypicotts.py')
langsAvailable = ['es-ES', 'en-EU', 'en-GB']
parser.add_argument('-l', '--lang', choices=langsAvailable,
    help='Specify the language used')
parser.add_argument('file', help='File to read from')
args = parser.parse_args()


def getdoc():
    myfile = args.file
    if not os.path.exists(myfile):
        sys.exit("file " + myfile + " not found")
    else:
        with open(myfile) as doc:
            documentname = os.path.basename(doc.name).split('.')[0]
            if  os.path.exists(documentname + '.wav'):
                print(("File", documentname + ".wav already exist."))
                if DEBUG:
                    what_to_do = 'y'
                else:
                    what_to_do = input("Process anyway? (y/n) ")
                if what_to_do == 'y':
                    os.remove(documentname + ".wav")
                    return doc.readlines(), documentname
                else:
                    print("Nothing done.")
                    doc.close()
                    sys.exit(0)
            else:
                return doc.readlines(), documentname


def processdoc(document, documentname):
    print(("Processing", documentname))
    linenumber = 1
    steps = len(document) / 20
    for line in document:
        tts(". " + line, linenumber, documentname)
        linenumber += 1
        if linenumber % steps == 0:
            print('-')
    print("\bDone.")


def tts(text, number, documentname):
    fileout = documentname + "{0:04d}".format(number) + ".wav"
    if not args.lang:
        language = 'es-ES'
    else:
        language = args.lang
    command = 'pico2wave|--lang={2}|--wave={0}|{1}'.format(fileout, text,
    language)
    subprocess.call(command.split('|'), shell=False)


def clean(filelist):
    print("Removing temp files...")
    for i in filelist:
        os.remove(i)
    print("Done.")


def makewave(filelist, docname):
    print("Creating wav file...")
    with closing(wave.open(docname + ".wav", 'wb')) as output:
        # find sample rate from first file
        with closing(wave.open(filelist[0])) as w:
            output.setparams(w.getparams())
        # write each file to output
        for infile in sorted(filelist):
            with closing(wave.open(infile)) as w:
                output.writeframes(w.readframes(w.getnframes()))
    print("Done.")


def encode(docname):
    filein = docname + ".wav"
    fileout = docname + ".mp3"
    command = 'lame {0} {1}'.format(filein, fileout)
    subprocess.call(command.split(), shell=False)


def main():

    my_doc, my_docname = getdoc()
    if my_doc:
        processdoc(my_doc, my_docname)
        projectfiles = glob.glob(my_docname + '*.wav')
        makewave(projectfiles, my_docname)
        clean(projectfiles)
        encodefile = input("Encode to mp3 file? (y/n) ")
        if encodefile == 'y':
            encode(my_docname)
        else:
            print("Job done. Everything went OK.")
            sys.exit(0)
        print("Job done. Everything went OK.")
    else:
        print("Something went wrong.")
        sys.exit(1)


if __name__ == "__main__":
    main()
