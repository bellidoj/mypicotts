#!/usr/bin/env python3

from gi.repository import Gtk
from contextlib import closing

import subprocess
import wave
import os

mediaEncoders = {
'mp3': 'lame',
'ogg': 'oggenc',
}


class myMain:

    def __init__(self):
        self.gladefile = "mypicotts.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.handlers = {
            "on_menuFileOpen_activate": self.menuOpenActivate,
            "on_menuFileSave_activate": self.menuSaveActivate,
            "on_menuFileSaveAs_activate": self.menuSaveAsActivate,
            "on_menuFileQuit_activate": self.menuQuitActivate,
            "on_RunButton_clicked": self.process_file,
            "on_menuHelpAbout_activate": self.menuAboutActivate,
            }
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("window1")
        self.window.set_default_size(640, 480)
        self.statusBar = self.builder.get_object("statusbar")
        self.context_id = self.statusBar.get_context_id("status")
        self.checkEncoders()
        self.mytextview = self.builder.get_object("textview")
        self.mytextview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.mybuffer = self.mytextview.get_buffer()
        self.mybuffer.connect("changed", self.contentChanged)

        self.window.show()
        self.fileList = []
        self.modified = False
        self.statusBarMessage("Please, load a document")
        self.documentName = 'Untitled document'
        self.window.set_title("mypicotts: " + self.documentName)
        self.language = self.activeLanguage()
        self.encoder = self.activeEncoder()

    def statusBarMessage(self, message):
        self.statusBar.pop(self.context_id)
        self.statusBar.push(self.context_id, message)

    def contentChanged(self, textbuffer):
        self.modified = True
        self.updateTitle()

    def updateTitle(self):
        if self.modified:
            appendix = '*'
        else:
            appendix = ''
        window_title = "mypicotts: {0}{1}".format(os.path.basename(self.documentName), appendix)
        self.window.set_title(window_title)

    def checkEncoders(self):
        group = self.builder.get_object("radiobutton4").get_group()
        for i in group:
            if i.get_label() != 'none':
                if not self.is_tool(mediaEncoders[i.get_label()]):
                    i.set_sensitive(0)

    def activeEncoder(self):
        group = self.builder.get_object("radiobutton4").get_group()
        for i in group:
            if i.get_active():
                return i.get_label()

    def activeLanguage(self):
        group = self.builder.get_object("radiobutton1").get_group()
        for i in group:
            if i.get_active():
                return i.get_label()

    def loadFile(self):
        with closing(open(self.documentName)) as text_file:
            self.mybuffer.set_text(text_file.read())
            self.mytextview.set_buffer(self.mybuffer)
            start_iter = self.mybuffer.get_start_iter()
            end_iter = self.mybuffer.get_end_iter()

            mytext = self.mybuffer.get_text(start_iter, end_iter, True)
            message = "File loaded: {0}".format(self.documentName)
            self.statusBarMessage(message)
            self.updateTitle()

    def saveFile(self):
        
        start_iter = self.mybuffer.get_start_iter()
        end_iter = self.mybuffer.get_end_iter()
        mytext = self.mybuffer.get_text(start_iter, end_iter, True)
            
        with closing(open(self.documentName, "w")) as text_file:
            print(mytext, file=text_file)
            self.modified = False
            self.updateTitle()
            message = "File saved: {0}".format(self.documentName)
            self.statusBarMessage(message)

    def process_file(self, widget):
        self.language = self.activeLanguage()
        self.encoder = self.activeEncoder()
        message = "Language: {0}, encoder: {1}".format(self.language,
            self.activeEncoder())
        self.statusBarMessage(message)
        start_iter = self.mybuffer.get_start_iter()
        end_iter = self.mybuffer.get_end_iter()

        mytext = self.mybuffer.get_text(start_iter, end_iter, True)

        for index, mytext_line in enumerate(mytext.split("\n")):
            self.tts(mytext_line, index)


        splitedDocumentName = os.path.splitext(self.documentName)    
        with closing(wave.open(self.getName() + ".wav", 'wb')) as output:
            # find sample rate from first file
            with closing(wave.open(self.fileList[0])) as w:
                output.setparams(w.getparams())
            # write each file to output
            for infile in sorted(self.fileList):
                with closing(wave.open(infile)) as w:
                    output.writeframes(w.readframes(w.getnframes()))

        for i in self.fileList:
            os.remove(i)

        self.statusBarMessage("Cleaning temporary files")
        self.encoder = self.activeEncoder()

        if self.encoder != 'none':
            message = "Encoding to {0}.".format(self.encoder)
            self.statusBarMessage(message)
            self.encode()

        message = "Process finished."
        self.statusBarMessage(message)
        del self.fileList[:]

    def tts(self, text, number):
        fileout = "{1}{0:04d}.wav".format(number, self.getName())
        self.fileList.append(fileout)
        command = 'pico2wave|--lang={2}|--wave={0}|--|{1}'.format(fileout, text,
            self.language)
        subprocess.call(command.split('|'), shell=False)

    def encode(self):
        filein = self.getName() + ".wav"
        fileout = self.getName() + ".{0}".format(self.encoder)

        if self.encoder == 'mp3':
            command = 'lame|{0}|{1}'.format(filein, fileout)
        elif self.encoder == 'ogg':
            command = 'oggenc|-o|{1}|{0}'.format(filein, fileout)
            print(command)
        else:
            return True

        subprocess.call(command.split("|"), shell=False)

        return True

    def is_tool(self, encoder):
        '''
            Credit to stackoverflow user sorin
        '''

        if not encoder == 'none':
            try:
                devnull = open(os.devnull)
                subprocess.Popen([encoder], stdout=devnull,
                    stderr=devnull).communicate()
            except OSError as e:
                if e.errno == os.errno.ENOENT:
                    return False
            return True

    def menuOpenActivate(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
            Gtk.FileChooserAction.OPEN)
        dialog.add_button("Abrir", Gtk.ResponseType.OK)
        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)

        self.add_filters(dialog)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.documentName = dialog.get_filename()
            self.loadFile()
        elif response == Gtk.ResponseType.CANCEL:
            pass
            
        dialog.destroy()
        
        self.modified = False

    def menuSaveAsActivate(self, widget):
        dialog = Gtk.FileChooserDialog("Save file", self.window,
            Gtk.FileChooserAction.SAVE)

        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        dialog.add_button("Guardar", Gtk.ResponseType.ACCEPT)

        dialog.set_current_name(self.documentName)
        dialog.set_do_overwrite_confirmation(True)
        
        self.add_filters(dialog)

        response = dialog.run()

        if response == Gtk.ResponseType.ACCEPT:
            self.documentName = dialog.get_filename()
            self.saveFile()
            
        elif response == Gtk.ResponseType.CANCEL:
            pass
            
        dialog.destroy()
        self.updateTitle()

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        filter_all = Gtk.FileFilter()
        filter_all.set_name("All files")
        filter_all.add_pattern("*.*")
        dialog.add_filter(filter_text)
        dialog.add_filter(filter_all)

    def menuSaveActivate(self, widget):
        self.saveFile()

    def menuQuitActivate(self, widget):
        if self.modified:
            message = "Save {0} before exit?".format(self.documentName) 
            dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL, 
                Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, message)
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                self.saveFile()
            elif response == Gtk.ResponseType.NO:
                pass
            dialog.destroy()
        Gtk.main_quit()

    def menuAboutActivate(self, widget):
        dialog = Gtk.AboutDialog(None, self.window, None)
        dialog.set_program_name("Mypicotts")
        dialog.set_version("0.3")
        dialog.set_comments("A TTS wrapper around pico2wave")
        dialog.set_website("http://peregilllica.com") 
        dialog.set_website_label("Peregilllica.com") 
        response = dialog.run()
        dialog.destroy()

    def getName(self):
        splitedName = os.path.splitext(self.documentName)
        return splitedName[0]

if __name__ == "__main__":
    main = myMain()
    Gtk.main()
