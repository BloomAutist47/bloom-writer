# -*- coding: utf-8 -*-
# Copyright (c) Bloom Autist 2021
# For license see LICENSE

import os
import glob
import string
import ctypes
import configparser
import json

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.messagebox import askyesno
from tkinter.filedialog import askopenfilename
from ttkwidgets import ScrolledListbox, AutoHideScrollbar
from ttkwidgets.frames import ScrolledFrame, ToggledFrame
from ttkwidgets.autocomplete import AutocompleteCombobox

from PIL import Image, ImageDraw, ImageTk, ImageOps
from random import randrange
from pprintpp import pprint
from threading import Thread
from psutil import process_iter

from lib.Widgets import rClicker, ButtonBM, LabelEntryBM, MessageBM, TextBM, Tip, WindowEntryBM, ComboboxBM
from lib.Style import s
from lib.Parser import ImageParser
from lib.Viewer import CanvasImage

os.chdir(os.path.dirname(os.path.abspath(__file__)))
ctypes.windll.shcore.SetProcessDpiAwareness(1)

class CharacterDoesNotExists(Exception):
    pass


class HandWriter(tk.Frame):
    """The main program code that contains UI and converter code"""

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.version = "v.1.0.0"
        self.delete_cache()
        self.folder_integrity_check()

        # Master configs
        self.master.geometry("800x400")
        self.master.title("Bloom Writer v.1.0.0")
        self.config(bg = s.bg)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variable declaration
        self.handstyle_selected = ""
        self.page_width = 6000      # page config
        self.page_height = 6000
        self.border_left = 100

        self.line_height = 120      # letter config
        self.letter_spacing = 5
        self.word_spacing = 50

        self.size = 1

        self.tempImg = ""
        self.previous_section = ""

        self.charconfigs = {}

        self.profile_list = []
        self.handstyle_list = []
        self.sectionlist = []

        settings_default = {"settings": {"Image": 0, "Selected": ""}, "profiles": {}}
        # Setups
        # self.style_ini = configparser.ConfigParser()
        self.style_ini = configparser.ConfigParser(comment_prefixes=';', allow_no_value=True)

        if not os.path.exists("settings.json"):
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings_default, f, ensure_ascii=False, indent=4)

        with open('./settings.json', 'r', encoding="utf-8") as f:
            self.settings = json.load(f)

            # Checks if the selected profil still exists
        if self.settings["settings"]["Selected"] not in self.settings["profiles"]:
            self.settings["settings"]["Selected"] = ""
            self.save_settings()

        # Checks if profiles are empty or not
        self.parser = ImageParser()
        valid = self.parser.update_data(self.settings)

        # Loads selected profile
        self.profile_use(True)

        # Loads the generic texts
        with open('./lib/texts/generic_text.txt') as f:
            self.genertic_texts = f.read().replace(",", "").replace(".", "")

        # Loads needed lists
        self.profile_get()
        self.handstyle_get()

        # Styles
        self.style = ttk.Style(self)
        self.style.theme_create( "yummy", parent="alt", settings={
                "TNotebook": {"configure": {
                        "tabposition": 'wn', "background":s.bg}},
                "TNotebook.Tab": {
                    "configure": {"padding": [10, 1], "borderwidth": 0, 
                                  "background": "white", "focuscolor": "red"},
                    "map":       {"background": [("selected", s.sub)],
                                  "foreground": [("selected", "WhiteSmoke")]
                                  },
                } 
            } 
        )
        self.style.theme_use("yummy")
     
        # Debug Text
        # scroll_bar1 = tk.Scrollbar(self)
        # scroll_bar1.grid(row=1, column=3, sticky="NS")
        # self.debug_log = tk.Text(self, bg=s.fg, fg=s.bg, bd=0,
        #                         relief=tk.FLAT, undo=True, font=s.font,
        #                         yscrollcommand=scroll_bar1.set)
        # self.debug_log.grid(row=1, column=0, columnspan=3, sticky="nswe")
        # scroll_bar1.config(command=self.debug_log.yview)
        # self.debug_log.bind('<Button-3>', rClicker, add='')

        # Function Calls

        self.ui()
        # self.master.iconify()
        # self.settings_window()


    def on_closing(self):
        self.master.destroy()
        self.delete_cache()

    def delete_cache(self):
        if os.path.exists('./lib/cache/temp.png'):
            try:
                os.remove('./lib/cache/temp.png')
                print("> Deleted Cache")
            except:
                pass

    def folder_integrity_check(self):
        folders = ["Data", "Input", "Output", "Style", "lib"]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def ui(self):
        frametop = tk.Frame(self, bg=s.bg)
        frametop.grid(row=0, column=0, sticky="W", padx=10)
        tk.Label(frametop, bg=s.bg, fg=s.fg,
                  text="Bloom Writer", font=(s.fstyle, s.fsize)).grid(row=0, column=0, sticky="W")
        # self.status = tk.Label(frametop, text="[none]", bg=s.bg, fg="whitesmoke",
        #                        font=("Consolas", 10))
        # self.status.pack(side="right")
        btn_insert = ButtonBM(frametop, text="Insert",
                              command=self.insert_generic)
        btn_insert.grid(row=0, column=1, padx=5, sticky="W")


        # Button top
        buttonframe = tk.Frame(self, bg=s.bg)
        buttonframe.grid(row=0, column=1, columnspan=2, padx=5, sticky="E")

        self.btn_print = ButtonBM(buttonframe, text="Print", command=self.start_printing)
        self.btn_print.grid(row=0, column=1, sticky="E")

        self.btn_clear = ButtonBM(buttonframe, text="Clear", command=self.clear_textlog)
        self.btn_clear.grid(row=0, column=2, padx=5, sticky="E")

        self.btn_output = ButtonBM(buttonframe, text="Output",
                              command=lambda: os.startfile(os.path.relpath("./Output/")))
        self.btn_output.grid(row=0, column=3, sticky="E")




        self.btn_setting = ButtonBM(buttonframe, text="Settings",
                               command=self.open_setting)
        self.btn_setting.grid(row=0, column=5, padx=(5,0), sticky="E")

        # Tooltips
        Tip(self.btn_print, text="Print's the good stuff.")
        Tip(self.btn_output, text="Opens output folder.")
        Tip(self.btn_setting, text="Opens settings window.")

        # Input Area bottom
        scroll_bar = tk.Scrollbar(self)
        scroll_bar.grid(row=1, column=3, sticky="NS")
        
        self.text_log = TextBM(self, bg=s.fg, fg=s.bg, bd=0,
                                relief=tk.FLAT, undo=True, font=s.font,
                                yscrollcommand=scroll_bar.set)
        self.text_log.grid(row=1, column=0, columnspan=3, sticky="nswe")
        scroll_bar.config(command=self.text_log.yview)
        self.text_log.bind('<Button-3>', rClicker, add='')
    

    def settings_window(self):
        """Creates the Settings window"""

        bg = 'WhiteSmoke'

        self.sett = tk.Toplevel()
        self.sett.geometry("650x450")
        self.sett.title("Settings")
        self.sett.focus_set()
        self.sett['bg'] = bg

        notebook = ttk.Notebook(self.sett, style='lefttab.TNotebook')
        notebook.pack(expand=True, fill=tk.BOTH)

        pageframe = tk.Frame(notebook, bg='WhiteSmoke', width=200, height=200)
        sysframe = tk.Frame(notebook, bg='WhiteSmoke', width=200, height=200)
        output = tk.Frame(notebook, bg='WhiteSmoke', width=200, height=200)

        notebook.add(pageframe, text='Page')
        notebook.add(sysframe, text='Style')
        notebook.add(output, text='Print')

        pageframe.columnconfigure(2, weight=1)
        pageframe.rowconfigure(3, weight=1)

        # sysframe.columnconfigure(0, weight=1)
        sysframe.columnconfigure(2, weight=1)
        # sysframe.columnconfigure(2, weight=1)
        # sysframe.rowconfigure(1, weight=1)


        # notebook.select(sysframe)

        self.settings_pageframe(pageframe, bg)
        self.settings_styleframe(sysframe, bg)

    def settings_pageframe(self, pageframe, bg):

        """Pageframe"""
        # Profile Buttons
        btn_preframe = tk.LabelFrame(pageframe, text="Preview", bg=bg)
        btn_preframe.grid(row=0, column=0, padx=5, ipady=3,
                         sticky="nw")
        self.btn_preview = ButtonBM(btn_preframe, text="Preview", w=10,
                               command=self.profile_preview)
        self.btn_preview.grid(row=0, column=0, padx=10,  sticky="w")


        # Command Buttons
        btn_proframe = tk.LabelFrame(pageframe, text="Command", bg=bg)
        btn_proframe.grid(row=1, column=0, rowspan=2, padx=5, ipady=2,
                         sticky="nw")

        self.btn_use = ButtonBM(btn_proframe, text="Use", w=10, command=self.profile_use)
        self.btn_use.grid(row=1, column=0, padx=10, sticky="w")
        self.btn_save = ButtonBM(btn_proframe, text="Save", w=10,
                            command=self.profile_save)
        self.btn_save.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        btn_new = ButtonBM(btn_proframe, text="New", w=10,
                           command=self.profile_windownew)
        btn_new.grid(row=3, column=0, padx=10, sticky="w")
        self.btn_rem = ButtonBM(btn_proframe, text="Delete", w=10,
                           command=self.profile_delete)
        self.btn_rem.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        # Folder buttons
        btn_fileframe = tk.LabelFrame(pageframe, text="File", bg=bg)
        btn_fileframe.grid(row=3, column=0, padx=5, ipady=3,
                         sticky="nw")
        btn_file = ButtonBM(btn_fileframe, text="Settings", w=10,
                               command=lambda: self.file_settings('settings.json'))
        btn_file.grid(row=0, column=0, padx=10,  sticky="w")
        btn_gentext = ButtonBM(btn_fileframe, text="Preview Text", w=10,
                               f=(s.fstyle, 9),
                               command=lambda: self.file_settings('lib\\texts\\generic_text.txt'))
        btn_gentext.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Profile Buttons - Tips
        Tip(self.btn_preview, text="Prints and opens a test image for the profile.")
        Tip(self.btn_use, text="Activates current profile as the one to use.")
        Tip(self.btn_save, text="Saves profile. Remember to use the `Use` button to activate it.")
        Tip(btn_new, text="Creates new profile.")
        Tip(self.btn_rem, text="Delete Selected Profile.")

        if not self.profile_list:
            self.btn_use['state'] = tk.DISABLED
            self.btn_save['state'] = tk.DISABLED
            self.btn_rem['state'] = tk.DISABLED
            self.btn_preview['state'] = tk.DISABLED

        # Page Profiles
        pagelistframe = tk.LabelFrame(pageframe, text="Page Profiles", bg=bg)
        pagelistframe.grid(row=0, column=1, padx=10, ipady=3, sticky="nw")

        self.pagelistbox = AutocompleteCombobox(pagelistframe, width=22,
                                                state="readonly", 
                                                completevalues=self.profile_list)
        self.pagelistbox.bind("<<ComboboxSelected>>", self.profile_insert)
        self.pagelistbox.grid(row=0, column=1, padx=5, sticky="we")
        self.pagelistbox.set(self.settings["settings"]["Selected"])


        # Handwritign Style
        handframe = tk.LabelFrame(pageframe, text="Handwritting Style", bg=bg)           
        handframe.grid(row=1, column=1, padx=10, ipady=4, sticky="nw")
                       
        self.handstyle = AutocompleteCombobox(handframe, width=22,
                                                state="readonly", 
                                                completevalues=self.handstyle_list)
        self.handstyle.grid(row=0, column=0, padx=5, sticky="we")

        # Size
        lettersizeframe = tk.LabelFrame(pageframe, text="In decimal percent",
                                        bg=bg, width=50)
        lettersizeframe.grid(row=1, column=2, ipady=3, sticky="nw")
        eny_lettersize = LabelEntryBM(lettersizeframe, text="      Letter Size",
                                        bg=bg, tip="Percentage size of the "\
                                        "Letters. Example -> 0.5 or 0.2 or 1.0")
        eny_lettersize.grid(row=0, column=0, padx=10, sticky="w")


        # Page Settings
        pagesettingframe = tk.LabelFrame(pageframe, text="Page Settings",
                                         bg=bg)
        pagesettingframe.grid(row=2, column=1, padx=10, ipady=3, sticky="w")

        eny_pagewidth = LabelEntryBM(pagesettingframe, text="Width", bg=bg)
        eny_pagewidth.grid(row=0, column=0, padx=10, sticky="e")
        eny_pageheight = LabelEntryBM(pagesettingframe, text="Height",
                                        bg=bg)
        eny_pageheight.grid(row=1, column=0, padx=10, pady=3, sticky="e")
        eny_leftborder = LabelEntryBM(pagesettingframe,
                                        text="    Left-Border", bg=bg)
        eny_leftborder.grid(row=2, column=0, padx=10, sticky="e")


        # Letter Settings
        lettersettingframe = tk.LabelFrame(pageframe, text="Letter Settings", bg=bg)
        lettersettingframe.grid(row=2, column=2, ipady=3, sticky="w")

        eny_lineheight = LabelEntryBM(lettersettingframe, text="Line Height",
                                      bg=bg, tip="Space in px between each "\
                                      "line.")
        eny_lineheight.grid(row=0, column=0, padx=10, sticky="e")
        eny_letterspacing = LabelEntryBM(lettersettingframe, bg=bg,
                                         text="Letter Spacing",
                                         tip="Space in px between each "\
                                         "characters.")
        eny_letterspacing.grid(row=1, column=0, padx=10, pady=3, sticky="e")
        eny_wordspacing = LabelEntryBM(lettersettingframe, text="Word Spacing",
                                       bg=bg, tip="Space in px between "\
                                       "each word.")
        eny_wordspacing.grid(row=2, column=0, padx=10, sticky="e")

        # Letter Config
        charconfigframe = tk.LabelFrame(pageframe, text="Letter Config",
                                          bg=bg, width=50)
        charconfigframe.columnconfigure(0, weight=1)
        charconfigframe.rowconfigure(0, weight=1)
        charconfigframe.grid(row=3, column=1, columnspan=2, padx=10,
                               ipady=3, sticky="nswe", pady=(0,10))

        scroll_bar2 = AutoHideScrollbar(charconfigframe)
        scroll_bar2.grid(row=0, column=1, sticky="NS")
        
        self.charconfig = tk.Text(charconfigframe, bd=0,
                                  bg=charconfigframe['bg'],
                                  relief=tk.FLAT, undo=True,
                                  font=(s.fstyle, 9),
                                  yscrollcommand=scroll_bar2.set)
        self.charconfig.grid(row=0, column=0, sticky="nswe")
        scroll_bar2.config(command=self.charconfig.yview)
        self.charconfig.bind('<Button-3>', rClicker, add='')
        

        self.pageentries = {
            "lineHeight": eny_lineheight,
            "letterSpacing": eny_letterspacing,
            "wordSpacing": eny_wordspacing,

            "width": eny_pagewidth,
            "height": eny_pageheight,
            "leftBorder": eny_leftborder,

            "size": eny_lettersize

        }
        try:
            self.profile_insert(self.settings["settings"]["Selected"])
        except:
            self.pagelistbox.current(0)
            self.profile_insert(self.profile_list[0])
        

    def settings_styleframe(self, sysframe, bg):

        """SysFrame"""
        # Splice Buttons
        btn_splitframe = tk.LabelFrame(sysframe, text="Image", bg=bg)
        btn_splitframe.grid(row=0, column=0, padx=5, ipady=3,
                         sticky="nw")
        self.btn_splice = ButtonBM(btn_splitframe, text="Splice", w=10,
                              command=self.splice_image)
        self.btn_splice.grid(row=0, column=0, padx=10,  sticky="w")


        # Command Buttons
        btn_cmdframe = tk.LabelFrame(sysframe, text="Command", bg=bg)
        btn_cmdframe.grid(row=1, column=0, rowspan=2, padx=5, ipady=2,
                         sticky="nw")

        btn_save2 = ButtonBM(btn_cmdframe, text="Save", w=10, command=self.style_save)
        btn_save2.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        btn_new2 = ButtonBM(btn_cmdframe, text="New", w=10, command=self.style_windownew)
        btn_new2.grid(row=3, column=0, padx=10, sticky="w")
        btn_rem2 = ButtonBM(btn_cmdframe, text="Delete", w=10,
                            command=self.style_delete)
        btn_rem2.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        # Folder buttons
        btn_foldername = tk.LabelFrame(sysframe, text="Folder", bg=bg)
        btn_foldername.grid(row=3, column=0, rowspan=3, padx=5, ipady=3,
                         sticky="nw")
        btn_data = ButtonBM(btn_foldername, text="Data", w=10,
                               command=lambda: os.startfile("Data\\"))
        btn_data.grid(row=0, column=0, padx=10,  sticky="w")
        btn_style = ButtonBM(btn_foldername, text="Style", w=10,
                              tip="Opens the .inis folder",
                              command=lambda: os.startfile("Style\\"))
        btn_style.grid(row=1, column=0, padx=10,  pady=5,  sticky="w")



        # Hand style
        handframe = tk.LabelFrame(sysframe, text="Handwritting Style", bg=bg)           
        handframe.grid(row=0, column=1, columnspan=2, padx=10, ipady=4, sticky="nw")
        self.handstyle2 = ComboboxBM(handframe, width=22,
                                                state="readonly", 
                                                completevalues=self.handstyle_list)
        self.handstyle2.grid(row=0, column=0, padx=5, sticky="we")
        self.handstyle2.bind("<<ComboboxSelected>>", self.style_insert)

        # Section Frame
        sctn_frame = tk.LabelFrame(sysframe, text="Section", bg=bg)           
        sctn_frame.grid(row=1, column=1, columnspan=2, padx=10, ipady=4, sticky="nw")
                       
        self.sctn_header = ComboboxBM(sctn_frame, width=22,
                                                state="sectionframe", 
                                                completevalues=[])
        self.sctn_header.grid(row=0, column=0, padx=(5,0), sticky="nw")
        self.sctn_header.bind("<<ComboboxSelected>>", self.style_section_insert)
        sctn_btn_new = ButtonBM(sctn_frame, text="New", w=10, f=(s.fstyle, 7),
                                command=self.style_windowsection)
        sctn_btn_new.grid(row=0, column=1, padx=(5,0), sticky="nw")
        sctn_btn_del = ButtonBM(sctn_frame, text="Delete", w=11, f=(s.fstyle, 7),
                                command=self.style_section_delete)
        sctn_btn_del.grid(row=0, column=2, padx=(5,5), sticky="nw")

        # Widget Row 1
        textframe = tk.LabelFrame(sysframe, text="Data list", bg=bg, fg=s.bg, font=s.font)
        textframe.grid(row=2, column=1, columnspan=2, rowspan=2,  padx=10, sticky="nw")
        textframe.columnconfigure(0, weight=1)
        textframe.rowconfigure(0, weight=1)

        textdata = TextBM(textframe, bind=False, fg="black", width=40, height=3, font=(s.fstyle, 9), undo=True)
        textdata.grid(row=0, column=0, padx=5, pady=5, sticky="nsw")
        textdata.bind('<Button-3>', rClicker, add='')

        # Widget Row 2
        dimensionframe = tk.LabelFrame(sysframe, text="Dimensions", bg=bg, fg=s.bg, font=s.font)
        dimensionframe.grid(row=5, column=1, columnspan=1, padx=(10,5), sticky="w")
        dimensionframe.columnconfigure(0, weight=1)

        eny_row = LabelEntryBM(dimensionframe, bg=bg, width=6, text="Row")
        eny_row.grid(row=0, column=1, padx=5,  pady=5, ipady=3)
        eny_clm = LabelEntryBM(dimensionframe, bg=bg, width=6, text="Column")
        eny_clm.grid(row=0, column=2, padx=5,  pady=5, ipady=3)

        # Auxilliary buttons
        btn_aux = tk.LabelFrame(sysframe, text="Buttons", bg=bg, fg=s.bg, font=s.font)
        btn_aux.grid(row=5, column=2, columnspan=1, padx=12, pady=5, sticky="nw")
        btn_browse = ButtonBM(btn_aux, text="Browse", w=10, f=(s.fstyle, 9),
                              height=1,
                              command=lambda: self.style_askfile(t="Select input image path"))
        btn_browse.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
        

        # Widget Row 3
        imgfile = tk.LabelFrame(sysframe, text="Image File", bg=bg, fg=s.bg, font=s.font)
        imgfile.grid(row=4, column=1, columnspan=2, padx=10, sticky="w")
        imgfile.columnconfigure(0, weight=1)
        self.eny_file = LabelEntryBM(imgfile, bg=bg, width=35, text="Path")
        self.eny_file.grid(row=0, column=0, padx=5,  pady=5, ipady=3)


        self.styleentries = {
            "row": eny_row,
            "column": eny_clm,
            "path": self.eny_file,
            "datalist": textdata,
            "section": self.sctn_header
        }

        self.stylebuttons = {
            "save": btn_save2,
            "new": btn_new2 ,
            "delete": btn_rem2
        }

        self.sectionbuttons = {
            "new": sctn_btn_new,
            "delete": sctn_btn_del
        }

        if self.handstyle_list:
            self.handstyle2.current(0)
            self.style_insert(self.handstyle2.get())

    def profile_windownew(self):

        self.styleentries

        WindowEntryBM(title="New Profile", stat_func=self.profile_new)
        self.sett.attributes('-topmost',1)



    def profile_preview(self):
        # Value Check
        if not self.profile_check():
            return

        char_config = self.parse_charsetting()
        if char_config == "Cancel":
            return

        def _end_preview():
            print("WHATTT")
            self.btn_preview.config(state=tk.NORMAL)
            self.sett.title("Settings - Preview complete...")

        self.btn_preview.config(state=tk.DISABLED)
        self.sett.title("Settings - Generating preview...")
        self.master.title("Bloom Writer v.1.0.0")

        thread = Thread(target=self.converter,
                        args=[
                            self.pageentries["width"].getint(),
                            self.pageentries["height"].getint(),
                            self.pageentries["leftBorder"].getint(),
                            self.pageentries["lineHeight"].getint(),
                            self.pageentries["letterSpacing"].getint(),
                            self.pageentries["wordSpacing"].getint(),
                            self.pageentries["size"].getfloat(),
                            _end_preview,
                            char_config,
                            True
                        ])
        thread.start()

    def profile_viewer(self):
        try:
            if not tk.Toplevel.winfo_exists(self.topwindow):
                self.create_topviewer()
        except:
            self.create_topviewer()

        self.canvasview = CanvasImage(self.topwindow, path="./lib/cache/temp.png")  # create widget
        self.canvasview.grid(row=0, column=0)  # show widget


    def profile_use(self, start=False):
        """Gets the current values and uses it"""

        if not start:
            # Entries Validation Check
            if not self.profile_check():
                return

            current = self.pagelistbox.get()
            self.settings["settings"]["Selected"] = current 
            self.save_settings()
        else:
            current = self.settings["settings"]["Selected"].strip()
            if not current or current not in self.settings["profiles"]:
                return

        profile = self.settings["profiles"][current]

        self.page_width = profile["pageSettings"]["width"]
        self.page_height = profile["pageSettings"]["height"]
        self.border_left = profile["pageSettings"]["leftBorder"]

        self.line_height = profile["letterSettings"]["lineHeight"]
        self.letter_spacing = profile["letterSettings"]["letterSpacing"]
        self.word_spacing = profile["letterSettings"]["wordSpacing"]

        self.size = profile["size"]
        self.handstyle_selected = profile["style"]

        self.charconfigs = profile["config"]
        print("this: ", self.charconfigs)
        self.parser.update_data(self.settings)

    def profile_save(self):
        """Gathers the page frame setting values"""
        
        # Value Check
        if not self.profile_check():
            return

        current = self.pagelistbox.get()
        profile = self.settings["profiles"][current]

        profile["pageSettings"]["width"] = self.pageentries["width"].getint()
        profile["pageSettings"]["height"] = self.pageentries["height"].getint()
        profile["pageSettings"]["leftBorder"] = self.pageentries["leftBorder"].getint()

        profile["letterSettings"]["lineHeight"] = self.pageentries["lineHeight"].getint()
        profile["letterSettings"]["letterSpacing"] = self.pageentries["letterSpacing"].getint()
        profile["letterSettings"]["wordSpacing"] = self.pageentries["wordSpacing"].getint()

        profile["size"] = self.pageentries["size"].getfloat()
        profile["style"] = self.handstyle.get()
        
        char_config = self.parse_charsetting()
        if char_config == "Cancel":
            return

        profile["config"] = char_config
        self.save_settings()
        MessageBM("Saved Successfully", f"\tDone saving profile {current}. lol\t")


    def profile_new(self, get):
        """creates new profile entry"""
        item = get().strip()
        if not item:
            MessageBM("Invalid Profile name", "Please enter atleast a single character")
            return "Nope."

        if item in self.settings["profiles"]:
            MessageBM("Invalid Profile name", f"\tThe name {item} already "\
                      "exists.\t\nPlease pick a unique name.")
            return "Nope."

        self.settings["profiles"][item] = {
            "style": "",
            "size": "",
            "pageSettings": {
                "width": "",
                "height": "",
                "leftBorder": ""
            },
            "letterSettings": {
                "lineHeight": "",
                "letterSpacing": "",
                "wordSpacing": "",
            },
            "config": {}
        }
        self.save_settings()
        self.pagelistbox['completevalues'] = self.profile_get()
        self.pagelistbox.set(item)
        for item in self.pageentries:
            self.pageentries[item].clear()
        self.charconfig.delete("1.0", tk.END)

        if self.profile_list:
            self.btn_use['state'] = tk.NORMAL
            self.btn_save['state'] = tk.NORMAL
            self.btn_rem['state'] = tk.NORMAL
            self.btn_preview['state'] = tk.NORMAL
            self.pagelistbox.current(0)

        return True

    def profile_delete(self):
        """deletes the current profile"""
        current = self.pagelistbox.get()

        answer = askyesno(title='Confirmation',
                          message=f'Are you sure that you want to delete "{current}"?')
        if not answer:
            return
        if not current:
            MessageBM("Can't delete", "Nothing to delete, pal.")
            return
        self.settings["profiles"].pop(current, None)
        self.save_settings()

        self.profile_get()
        if self.profile_list:
            self.pagelistbox.current(0)
            self.profile_insert(self.profile_list[0])
        else:
            self.profile_clear()
            self.pagelistbox.set("")
            self.btn_use['state'] = tk.DISABLED
            self.btn_save['state'] = tk.DISABLED
            self.btn_rem['state'] = tk.DISABLED
            self.btn_preview['state'] = tk.DISABLED

    def profile_insert(self, event):
        """inserts current profile data
            :event:
                eventObj -> if the combobox is changed into a different profile
                string -> manual invocation
        """
        if type(event) == str:
            try:
                profile = self.settings["profiles"][event]
            except:
                # There are no profiles
                return
        else:
            profile = self.settings["profiles"][event.widget.get()]

        self.pageentries["lineHeight"].insert(profile["letterSettings"]["lineHeight"])
        self.pageentries["letterSpacing"].insert(profile["letterSettings"]["letterSpacing"])
        self.pageentries["wordSpacing"].insert(profile["letterSettings"]["wordSpacing"])

        self.pageentries["width"].insert(profile["pageSettings"]["width"])
        self.pageentries["height"].insert(profile["pageSettings"]["height"])
        self.pageentries["leftBorder"].insert(profile["pageSettings"]["leftBorder"])

        self.pageentries["size"].insert(profile["size"])
        self.handstyle.set(profile["style"])

        self.charconfig.delete('1.0', tk.END)

        if not profile["config"]:
            return

        for item in profile["config"]:
            self.charconfig.insert(tk.END, f"{item}: ")
            if not profile["config"][item]:
                continue
            for char in profile["config"][item]:
                self.charconfig.insert(tk.END, f"{char}{profile['config'][item][char]}, ")
            self.charconfig.insert(tk.END, "\n")
        

    def profile_clear(self):
        """clears the profile entry widget"""
        for widget in self.pageentries:
            self.pageentries[widget].clear()

    def profile_get(self):
        """returns list of profile names"""
        self.profile_list = list(self.settings["profiles"].keys())
        if hasattr(self, 'pagelistbox'):
            self.pagelistbox['completevalues'] = self.profile_list
        return self.profile_list

    def profile_check(self):
        # Value Check
        for entry in self.pageentries:
            if entry == "size":
                if not self.pageentries[entry].getfloat():
                    MessageBM("Invalid Value", f"Please enter only integer in the {entry} entry.")
                    self.sett.lift()
                    return False
                else: continue
            if not self.pageentries[entry].getint():
                MessageBM("Invalid Value", f"Please enter only integer in the {entry} entry.")
                self.sett.lift()
                return False
        return True

    def parse_charsetting(self):
        charconfig = self.charconfig.get("1.0", "end").strip()
        print(f"CHAR: {charconfig}")
        if not charconfig:
            return {}

        table = {}
        charconfig = charconfig.split("\n")
        
        for char_ in charconfig:
            x = char_.strip()
            if not x:
                continue

            x = x.split(":", 1)
            print(f"x: {x}")
            table[x[0]] = {}
            for i in x[1].split(","):
                j = i.strip()
                if not j: continue
                if "l" in j:
                    if "l" in table[x[0]]:
                        MessageBM("Invalid Char Value", f"\tThe char config {j} is a duplicate.\t")
                        return "Cancel"
                    table[x[0]]["l"] = int(j.replace("l", ""))
                    continue 
                if "r" in j:
                    if "r" in table[x[0]]:
                        MessageBM("Invalid Char Value", f"\tThe char config {j} is a duplicate.\t")
                        return "Cancel"
                    table[x[0]]["r"] = int(j.replace("r", ""))
                    continue
                if "v" in j:
                    if "v" in table[x[0]]:
                        MessageBM("Invalid Char Value", f"\tThe char config {j} is a duplicate.\t")
                        return "Cancel"
                    table[x[0]]["v"] = int(j.replace("v", ""))
                    continue
                MessageBM("Invalid Char Value", f"The value \"{j}\" is not valid. Please only use l, r, or v.")
                return "Cancel"

        return table

    def clear_textlog(self):
        log = self.text_log.get("1.0", tk.END)
        if log == "Type Something here....":
            return
        self.text_log.delete('1.0', tk.END)

    def create_topviewer(self):
        self.topwindow = tk.Toplevel()
        self.topwindow.title('Print Preview - Advanced Zoom v3.0')
        self.topwindow.geometry('1000x600')  # size of the main window
        self.topwindow.rowconfigure(0, weight=1)  # make the CanvasImage widget expandable
        self.topwindow.columnconfigure(0, weight=1)

    def style_askfile(self, t):
        """asks for image file path"""
        filename = askopenfilename(parent=self, title=t, initialdir="./Input/").strip()
        if not filename:
            return
        self.eny_file.insert(os.path.relpath(filename))

    def style_windownew(self):

        for widget in self.stylebuttons:
            self.stylebuttons[widget].disable()

        def _style_enable_buttons():
            self.sett.attributes('-topmost',1)
            for widget in self.stylebuttons:
                self.stylebuttons[widget].enable()

        WindowEntryBM(title="New Style", stat_func=self.style_new, end_func=_style_enable_buttons)
        




    def style_save(self):
        current = self.handstyle2.get()
        try:
            self.style_section_save(self.sctn_header.get())
        except: pass

        if not self.style_ini.has_section("METADATA"):
            self.style_ini["METADATA"] = {"version": self.version}
        with open(f'Style/{current}', 'w') as configfile:    # save
            self.style_ini.write(configfile)

        MessageBM("Saved ini", f"\tSuccessfully saved {current}.\t")
        return

    def style_new(self, get):
        """creates new profile entry"""
        item = get().strip()
        if not item:
            MessageBM("Invalid Profile name", "Please enter atleast a single character")
            return "Nope."
        inis = [x.lower() for x in glob.glob("./Style/*.ini")]
        item_test = f'./style\\{item}.ini'.lower()

        if item_test in inis:
            MessageBM("Invalid Profile name", f"The name {item} already "\
                      "exists. Please pick a unique name.\t")
            return "Nope."

        self.style_ini = configparser.ConfigParser()
        self.style_ini["METADATA"] = {"version": self.version}

        with open(f'Style\\{item}.ini', 'w') as configfile:
            self.style_ini.write(configfile)

        self.handstyle_get()

        self.handstyle2.set(f'{item}.ini')
        for item in self.styleentries:
            if item == "section": continue
            self.styleentries[item].clear()
        self.styleentries["section"]["completevalues"] = []
        self.styleentries["section"].set("")

        self.previous_section = ""

        return True

    def style_windowsection(self):

        for widget in self.sectionbuttons:
            self.stylebuttons[widget].disable()

        def _style_enable_buttons():
            for widget in self.sectionbuttons:
                self.stylebuttons[widget].enable()

        WindowEntryBM(title="New Section", stat_func=self.style_section_new, end_func=_style_enable_buttons)



    def style_insert(self, e):
        """inserts style ini main data on the widgets"""
        current = self.widget_check(e)
        if not current:
            return

        print(f"Cur: {current}")
        self.style_ini = configparser.ConfigParser()
        self.style_ini.read(f'./Style/{current}', encoding="utf-8")
        print("what")


        for widget in self.styleentries:
            if widget == "section": continue
            self.styleentries[widget].clear()
            print(widget)

        self.section_get()

        self.styleentries["section"].set("")
        if len(self.style_ini.sections()) >= 2:
            self.styleentries["section"].current(0)

        self.style_section_insert(self.styleentries["section"].get(), True)
        


    def style_delete(self):
        current = self.handstyle2.get()
        answer = askyesno(title='Confirmation',
                          message=f'Are you sure that you want to delete "{current}"?')
        if answer:
            try:
                os.remove(f"Style/{current}")
            except:
                pass

            self.handstyle_get()
            self.handstyle2.current(0)
            self.style_insert(self.handstyle2.get())
        return


    def style_section_insert(self, e, switch=False):
        """insert the section data of the style inis"""

        current = self.widget_check(e)
        if not current or current not in self.style_ini.sections():
            return 
        print("yes??")
        if not switch:
            self.style_section_save()

        try: self.styleentries["row"].insert(self.style_ini[current]["row"])
        except: self.styleentries["row"].insert("")
            
        try: self.styleentries["column"].insert(self.style_ini[current]["column"])
        except: self.styleentries["column"].insert("")

        try: self.styleentries["path"].insert(self.style_ini[current]["path"])
        except: self.styleentries["path"].insert("")

        self.styleentries["datalist"].delete("1.0", tk.END)
        try:
            self.styleentries["datalist"].insert("1.0", self.style_ini[current]["data"])
        except: 
            pass
        
        
        self.previous_section = current



    def style_section_save(self, current=None):
        if not current:
            if self.previous_section == "":
                return
            current = self.previous_section

        self.style_ini[current]["row"] = self.styleentries["row"].get()
        self.style_ini[current]["column"] = self.styleentries["column"].get()

        self.style_ini[current]["path"] = self.styleentries["path"].get()
        self.style_ini[current]["data"] = self.styleentries["datalist"].get("1.0", tk.END).strip()

    def style_section_new(self, get):
        item = get().strip()
        if not item:
            MessageBM("Invalid Section name", "Please enter atleast a single character")
            return "Nope."

        if item in self.style_ini.sections():
            MessageBM("Invalid Section name", f"The name \"{item}\" already exists. Please pick a unique name.")
            return "Nope."

        for widget in self.styleentries:
            self.styleentries[widget].clear()

        self.style_ini[item] = {}
        self.section_get()
        self.sctn_header.set(item)

        return True

    def style_section_delete(self):

        current = self.sctn_header.get()
        answer = askyesno(title='Confirmation',
                          message=f'Are you sure that you want to delete section "{current}"?')
        if answer:
            try:
                self.style_ini.remove_section(current)
            except:
                pass

            self.section_get()
            self.sctn_header.current(0)
            self.style_section_insert(self.sctn_header.get(), True)
        return

    def section_get(self):
        if len(self.style_ini.sections()) == 1:
            self.sctn_header["completevalues"] = [""]
            return
        sections_ = []
        for i in self.style_ini.sections():
            if i == "METADATA":
                continue
            sections_.append(i)

        self.sctn_header["completevalues"] = sections_

    def splice_image(self):


        def _end_splice():
            self.btn_splice.config(state=tk.NORMAL)
            self.sett.title("Settings - Done splicing...")

        self.btn_splice.config(state=tk.DISABLED)
        self.sett.title("Settings - Splicing image...")

        style = self.handstyle2.get().replace(".ini", "")
        section = self.sctn_header.get()
        path = f'./Data/{style}/{section}'
        
        if not os.path.exists(path):
            os.makedirs(path)

        thread = Thread(target=self.parser.disect_data,
                        args=[
                             style,
                             section,
                             self.style_ini[section],
                             _end_splice
                        ])
        thread.start()
        

    def save_settings(self):
        """Saves the settings json"""
        with open('./settings.json', 'w', encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def increase_count(self):
        """Increases the Image name count"""
        self.settings["settings"]["Image"] = int(self.settings["settings"]["Image"])+1
        self.save_settings()

    def open_setting(self):
        """Opens setting only if its not opened already"""
        try:
            if not tk.Toplevel.winfo_exists(self.sett):
                self.settings_window()
        except:
            self.settings_window()


    def handstyle_get(self):
        """Gets lists of handstyles ini"""
        if not os.path.exists("./Style/"):
            os.makedirs("./Style/")

        _handstyles = glob.glob("./Style/*.ini")
        self.handstyle_list = []
        for style in _handstyles:
            self.handstyle_list.append(style.split("\\")[-1])

        if hasattr(self, 'handstyle'):
            self.handstyle['completevalues'] = self.handstyle_list
        if hasattr(self, 'handstyle2'):
            self.handstyle2['completevalues'] = self.handstyle_list



    def widget_check(self, e):
        """Checks if passed value is string or a widget
            :e: str -> manual function invocation
                widgetObj -> Automated invocation
        """
        if type(e) == str:
            return e
        else:
            return e.widget.get().strip()
        # return current

    def file_settings(self, file):
        self.thread_handler(lambda: os.system(file))

    def unlock_buttons(self):
        """Makes the buttons normal"""
        self.text_log['state'] = tk.NORMAL
        self.text_log['fg'] = s.bg
        self.btn_print['state'] = tk.NORMAL
        self.btn_setting['state'] = tk.NORMAL

    def insert_generic(self):
        """Inserts generic text on the main text"""
        self.text_log.insert(tk.INSERT, self.genertic_texts.replace(".", "").replace(",", ""))

    def thread_handler(self, function):
        self.t1 = Thread(target=function, args=[])
        self.t1.start()

    def start_printing(self):
        """Prints the text in the textlog"""
        if not self.profile_list:
            MessageBM("No Profiles", "Please open the Settings and create a Profile to use the software.")
            return

        self.text = self.text_log.get(1.0, tk.END).strip()
        if self.text == "Type Something here....":
            MessageBM("Empty Text", "Please input something on the text field to print")
            return

        if self.text.strip() == "":
            MessageBM("Empty Text", "Please input something on the text field to print")
            return

        self.master.title("Bloom Writer v.1.0.0 - Printing in progress...")
        thread = Thread(target=self.converter,
                        args=[
                            self.page_width,
                            self.page_height,
                            self.border_left,
                            self.line_height,
                            self.letter_spacing,
                            self.word_spacing,
                            self.size,
                            lambda: self.master.title("Bloom Writer v.1.0.0 - Done printing..."),
                            self.charconfigs,
                            False
                        ])
        thread.start()

    def converter(self, 
                  page_width,
                  page_height,
                  border_left,
                  line_height,
                  letter_spacing,
                  word_spacing,
                  letter_size,
                  end_message,
                  char_config={},
                  preview=False,
        ):
        """Converts the text into handwriting"""
        
        self.btn_print['state'] = tk.DISABLED
        self.btn_setting['state'] = tk.DISABLED
        self.text_log['state'] = tk.DISABLED
        self.text_log['fg'] = 'grey'

        # try:
        # creates output if none existent yet
        if not os.path.exists("./Output/"):
            os.makedirs("./Output/")

        # The text document
        if preview:
            self.text = self.genertic_texts



        # page temp config
        page_limit_x = int(page_width - (page_width*0.25))
        page_limit_x = int(page_width - (page_width*0.10))
        page_limit_y = page_height - (page_height*0.1)
        print(f"Y Limit: {page_limit_y}\tHeight: {page_height}")
        print(f"X Limit: {page_limit_x}\tHeight: {page_width}")
        x = border_left
        y = line_height
        page_count = 1

        img = Image.new("RGB", (page_width, page_height), color="White")


        paragraphs = self.text.strip().split("\n")

        pprint(self.parser.master_table)
        
        for paragraph in paragraphs:
            y += line_height
            x = border_left

            if not paragraph.strip():
                y += line_height
                continue

            words = paragraph.split(" ")
            for word in words:
                
                if word.strip() == "":
                    x += word_spacing
                    continue

                if y >= page_limit_y:
                    if preview:
                        break
                    x = border_left
                    y = line_height
                    img.save(f'./Output/{self.settings["settings"]["Image"]}_{page_count}.png', quality=50)
                    img = Image.new("RGB", (page_width, page_height), color="White")
                    page_count += 1

                letterlist = []
                word_size = 0

                for letter_ in word:
                    letter = letter_.upper()
                    if letter not in self.parser.master_table:
                        self.unlock_buttons()
                        MessageBM("Character Error", f"The  character \" {letter} \"is not registered in current Style.")
                        raise CharacterDoesNotExists(f"Char: {letter} is not registered.")
                        
                        return

                    location = self.parser.master_table[letter]
                    letter_variant = str(randrange(len(glob.glob(location + "*.png")))+1)
                    alp = Image.open(location + "/" + letter_variant + ".png")
                    if letter_size != 1:
                        alp = alp.resize((int(alp.size[0]*letter_size), int(alp.size[1]*letter_size)))

                    word_size+=alp.size[0]

                    letterlist.append((letter, alp))
                    if letter in char_config:
                        for space in char_config[letter]:
                            word_size += char_config[letter][space]

                word_size += x

                if word_size > page_limit_x:
                    x = border_left
                    y += line_height

                for item in letterlist:
                    letter = item[0]
                    letterimg = item[1]
                    if letter in char_config:
                        x_left = 0
                        y_vertical = 0
                        if "l" in char_config[letter]:
                            x_left = char_config[letter]["l"]
                        if "v" in char_config[letter]:
                            y_vertical = -1*char_config[letter]["v"]
                        img.paste(letterimg, (x+x_left, y+y_vertical), mask=letterimg)
                        if "r" in char_config[letter]:
                            x += char_config[letter]["r"]
                        if x_left:
                            x+= x_left
                    else:
                        img.paste(letterimg, (x, y), mask=letterimg)
                    x+= (letterimg.size[0] + letter_spacing)


                word_size = 0
                x += word_spacing

            else:
                continue
            break

        self.btn_print['state'] = tk.NORMAL
        self.btn_setting['state'] = tk.NORMAL
        self.text_log['state'] = tk.NORMAL
        self.text_log['fg'] = s.bg

        if preview:
            # img.show()
            img.save('./lib/cache/temp.png', quality=50)
            self.profile_viewer()
            end_message()
            return 

        img.save(f'./Output/{self.settings["settings"]["Image"]}_{page_count}.png',
                 quality=50)

        self.increase_count()

        end_message()
        print("Done")
        # except:
        #     self.text_log['state'] = tk.NORMAL
        #     self.text_log['fg'] = s.bg
        #     self.btn_print['state'] = tk.NORMAL
        #     self.btn_setting['state'] = tk.NORMAL
        #     return

if __name__ == "__main__":
    root = tk.Tk()
    HandWriter(root).pack(side="top", fill="both", expand=True)
    root.mainloop()






