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
from ttkwidgets import ScrolledListbox
from ttkwidgets.frames import ScrolledFrame, ToggledFrame
from ttkwidgets.autocomplete import AutocompleteCombobox

from PIL import Image, ImageDraw, ImageTk, ImageOps
from random import randrange
from pprintpp import pprint
from threading import Thread

from lib.Widgets import rClicker, ButtonBM, LabelEntryBM, MessageBM, TextBM, Tip
from lib.Style import s
from lib.Parser import ImageParser

os.chdir(os.path.dirname(os.path.abspath(__file__)))
ctypes.windll.shcore.SetProcessDpiAwareness(1)



class HandWriter(tk.Frame):
    """The main program code that contains UI and converter code"""

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        # Master configs
        self.master.geometry("800x400")
        self.config(bg = s.bg)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Variable declaration
        self.handstyle_selected = ""
        self.page_width = 6000      # page config
        self.page_height = 6000
        self.border_left = 100

        self.line_height = 120      # letter config
        self.letter_spacing = 5
        self.word_spacing = 50

        self.size = 1

        self.profile_list = []
        self.handstyle_list = []

        # Setups
        with open('./settings.json', 'r', encoding="utf-8") as f:
            self.settings = json.load(f)
        if self.settings["profiles"] != {}:
            self.parser = ImageParser(self.settings)
        else:
            self.parser = None
            self.settings["settings"]["Selected"] = ""
            self.save_settings()

        with open('./lib/texts/generic_text2.txt') as f:
            self.genertic_texts = f.read().replace(",", "").replace(".", "")

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
        scroll_bar1 = tk.Scrollbar(self)
        scroll_bar1.grid(row=1, column=3, sticky="NS")
        self.debug_log = tk.Text(self, bg=s.fg, fg=s.bg, bd=0,
                                relief=tk.FLAT, undo=True, font=s.font,
                                yscrollcommand=scroll_bar1.set)
        self.debug_log.grid(row=1, column=0, columnspan=3, sticky="nswe")
        scroll_bar1.config(command=self.debug_log.yview)
        self.debug_log.bind('<Button-3>', rClicker, add='')

        # Function Calls

        self.ui()
        # self.iconify()
        # self.profile_windownew()



    def ui(self):
        title = tk.Label(self, bg=s.bg, fg=s.fg,
                text="BloomWriter v.2.0", font=(s.fstyle, s.fsize))
        title.grid(row=0, column=0, sticky="W", padx=10)
        
        
        # Button top
        buttonframe = tk.Frame(self, bg=s.bg)
        buttonframe.grid(row=0, column=1, columnspan=2, padx=5, sticky="E")

        self.btn_print = ButtonBM(buttonframe, text="Print", command=self.start_printing)
        self.btn_print.grid(row=0, column=1, sticky="E")

        self.btn_output = ButtonBM(buttonframe, text="Output",
                              command=lambda: os.startfile(os.path.relpath("./Output/")))
        self.btn_output.grid(row=0, column=2, padx=5, sticky="E")

        self.btn_setting = ButtonBM(buttonframe, text="Settings",
                               command=self.settings_window)
        self.btn_setting.grid(row=0, column=3, sticky="E")

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

        self.sett = tk.Toplevel()
        self.sett.geometry("700x300")
        self.sett.title("Settings")
        self.sett.focus_set()
        bg = 'WhiteSmoke'
        self.sett['bg'] = bg

        notebook = ttk.Notebook(self.sett, style='lefttab.TNotebook')
        notebook.pack(expand=True, fill=tk.BOTH)

        pageframe = tk.Frame(notebook, bg='WhiteSmoke', width=200, height=200)
        sysframe = tk.Frame(notebook, bg='WhiteSmoke', width=200, height=200)
        output = tk.Frame(notebook, bg='WhiteSmoke', width=200, height=200)

        notebook.add(pageframe, text='Page')
        notebook.add(sysframe, text='Words')
        notebook.add(output, text='Output')

        pageframe.columnconfigure(2, weight=1)
        sysframe.columnconfigure(0, weight=1)
        sysframe.columnconfigure(1, weight=1)
        sysframe.columnconfigure(2, weight=1)


        """Pageframe"""
        # Profile Buttons
        btn_preframe = tk.LabelFrame(pageframe, text="Preview", bg=bg)
        btn_preframe.grid(row=0, column=0, padx=5, ipady=3,
                         sticky="nw")
        self.btn_preview = ButtonBM(btn_preframe, text="Preview", w=10,
                               command=lambda: self.start_printing(True))
        self.btn_preview.grid(row=0, column=0, padx=10,  sticky="w")


        # Profile Buttons
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


        # Letter size
        lettersizeframe = tk.LabelFrame(pageframe, text="In decimal percent",
                                        bg=bg, width=50)
        lettersizeframe.grid(row=1, column=2, padx=10, ipady=3, sticky="nw")
        eny_lettersize = LabelEntryBM(lettersizeframe, text="      Letter Size",
                                        bg=bg, tip="Percentage size of the "\
                                        "Letters. Example -> 0.5 or 0.2 or 1.0")
        eny_lettersize.grid(row=0, column=0, padx=10, sticky="w")

        


        # Handwritign Style
        handframe = tk.LabelFrame(pageframe, text="Handwritting Style", bg=bg)           
        handframe.grid(row=1, column=1, padx=10, ipady=3, 
                       sticky="nw")
        self.handstyle = AutocompleteCombobox(handframe, width=22,
                                                state="readonly", 
                                                completevalues=self.handstyle_list)
        self.handstyle.grid(row=0, column=0, padx=5, sticky="we")


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
        lettersettingframe.grid(row=2, column=2, padx=10, ipady=3, sticky="w")

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
        
        """SysFrame"""
        textframe = tk.LabelFrame(sysframe, text="Data list", bd=0, bg=bg, fg=s.bg, font=(s.fstyle, s.fsizesub))
        textdata = tk.Text(textframe, fg="black", width=41, height=2, font=(s.fstyle, s.fsize), undo=True)
        textdata.pack(expand=True, fill=tk.BOTH)
        textframe.grid(row=0, column=1, columnspan=2, padx=5, sticky="w")
        textdata.bind('<Button-3>', rClicker, add='')

        # Widget Row 2
        dimensionframe = tk.Frame(sysframe, bg=bg)
        dimensionframe.grid(row=1, column=1, columnspan=2, padx=5, sticky="w")
        dimensionframe.columnconfigure(0, weight=1)

        rowframe = tk.LabelFrame(dimensionframe, text="Row", bg=bg, fg=s.bg, font=(s.fstyle, s.fsizesub))
        rowentry = tk.Entry(rowframe, fg="black", width=6, font=(s.fstyle, s.fsize))
        rowentry.pack(expand=True, fill=tk.BOTH)
        rowframe.grid(row=0, column=1, padx=5)

        columnframe = tk.LabelFrame(dimensionframe, text="Column", bg=bg, fg=s.bg, font=(s.fstyle, s.fsizesub))
        columnentry = tk.Entry(columnframe, fg="black", width=6, font=(s.fstyle, s.fsize))
        columnentry.pack(expand=True, fill=tk.BOTH)
        columnframe.grid(row=0, column=2)


        processframe = tk.LabelFrame(dimensionframe, text="Start splicing image", bg=bg, fg=s.bg, font=(s.fstyle, s.fsizesub))
        processbutton = ButtonBM(processframe, text="Process", w=10)
        processbutton.pack(expand=True, fill=tk.BOTH)
        processframe.grid(row=0, column=0, padx=0)



        # Widget Row 3
        editframe = tk.LabelFrame(sysframe, text="Chars", bg=bg, fg=s.bg, font=(s.fstyle, s.fsizesub))
        editframe.grid(row=2, column=1, columnspan=2, padx=5, sticky="nsw")

        letterbox = ScrolledListbox(editframe, height=6, width=4)
        for i in range(0,26):
            letterbox.listbox.insert(i, string.ascii_uppercase[i])
        letterbox.grid(row=0, column=0, sticky="ns")
        


        imageframe = tk.LabelFrame(sysframe, text="Input Images", bd=1, bg=bg, fg=s.bg, font=(s.fstyle, s.fsizesub))
        imageframe.grid(row=0, column=0, padx=5, rowspan=12, ipady=20)
        imagecontainer = ScrolledFrame(imageframe, compound=tk.LEFT, canvaswidth=5, canvasheight=270, height=10)
        imagecontainer.grid(row=0, column=0, pady=10)
        

        self.img1 = Image.open("./Input/alphabet-upper.png")
        self.img1 = ImageOps.contain(self.img1, (200,200))
        self.img1 = ImageTk.PhotoImage(self.img1)

        x1 = tk.LabelFrame(imagecontainer.interior, text="img1", bd=0, bg=bg, fg=s.bg, font=(s.fstyle, s.fsizesub))
        x2 = tk.LabelFrame(imagecontainer.interior, text="img2", bd=0, bg=bg, fg=s.bg, font=(s.fstyle, s.fsizesub))
        x3 = tk.LabelFrame(imagecontainer.interior, text="img3", bd=0, bg=bg, fg=s.bg, font=(s.fstyle, s.fsizesub))
        x4 = tk.LabelFrame(imagecontainer.interior, text="img4", bd=0, bg=bg, fg=s.bg, font=(s.fstyle, s.fsizesub))

        x1.grid(row=0, column=0, pady=10)
        x2.grid(row=1, column=0, pady=10)
        x3.grid(row=2, column=0, pady=10)
        x4.grid(row=3, column=0, pady=10)

        img_pack1 = tk.Label(x1, image=self.img1).pack()
        img_pack2 = tk.Label(x2, image=self.img1).pack()
        img_pack3 = tk.Label(x3, image=self.img1).pack()
        img_pack4 = tk.Label(x4, image=self.img1).pack()

    def profile_windownew(self):
        prof = tk.Toplevel()
        prof.grab_set()
        prof.lift()
        prof.attributes('-topmost', 'true')
        prof.title("New Profile")
        prof.geometry("550x100")
        bg = 'WhiteSmoke'
        prof['bg'] = bg

        prof.columnconfigure(0, weight=1)

        def _release():
            prof.grab_release()
            prof.destroy()

        entry = LabelEntryBM(prof, text="Name", bg=bg, width=35)
        entry.grid(row=0, column=0, pady=30, padx=10, sticky="w")
        entry.bindkey('<Return>', lambda e: self.profile_new(prof, entry.get))
        frame = tk.Frame(prof, bg=bg)
        frame.grid(row=0, column=1, pady=5, sticky="w")



        btn_save = ButtonBM(frame, text="Save", bg=bg,
                            command=lambda: self.profile_new(prof, entry.get))
        btn_save.grid(row=0, column=0, padx=5, sticky="w")

        btn_cancel = ButtonBM(frame, text="Cancel", bg=bg,
                              command=_release)
        btn_cancel.grid(row=0, column=1, padx=5, sticky="e")

        entry.entry.focus_set()

    def profile_use(self):
        current = self.pagelistbox.get()
        self.settings["settings"]["Selected"] = current 
        self.save_settings()

        # Value Check
        for entry in self.pageentries:
            if entry == "size":
                if not self.pageentries[entry].getfloat():
                    MessageBM("Invalid Value", f"Please enter only integer in the {entry} entry.")
                    self.sett.lift()
                    return
                else: continue
            if not self.pageentries[entry].getint():
                MessageBM("Invalid Value", f"Please enter only integer in the {entry} entry.")
                self.sett.lift()
                return

        self.page_width = self.pageentries["width"].getint()
        self.page_height = self.pageentries["height"].getint()
        self.border_left = self.pageentries["leftBorder"].getint()

        self.line_height = self.pageentries["lineHeight"].getint()
        self.letter_spacing = self.pageentries["letterSpacing"].getint()
        self.word_spacing = self.pageentries["wordSpacing"].getint()

        self.size = self.pageentries["size"].getfloat()

        self.handstyle_selected = self.handstyle.get()

        self.parser.update_data(self.settings)

    def profile_save(self):
        """Gathers the page frame setting values"""
        
        # Value Check
        for entry in self.pageentries:
            if entry == "size":
                if not self.pageentries[entry].getfloat():
                    MessageBM("Invalid Value", f"Please enter only integer in the {entry} entry.")
                    self.sett.lift()
                    return
                else: continue
            if not self.pageentries[entry].getint():
                MessageBM("Invalid Value", f"Please enter only integer in the {entry} entry.")
                self.sett.lift()
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
        self.save_settings()

        MessageBM("Saved Successfully", f"\tDone saving profile {current}. lol\t")

    def profile_new(self, toplevel, get):
        """creates new profile entry"""
        item = get()
        if item in self.settings["profiles"]:
            MessageBM("Invalid Profile name", f"\tThe name {item} already "\
                      "exists.\t\nPlease pick a unique name.")
            return

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
            }
        }
        self.save_settings()
        self.pagelistbox['completevalues'] = self.profile_get()

        if self.profile_list:
            self.btn_use['state'] = tk.NORMAL
            self.btn_save['state'] = tk.NORMAL
            self.btn_rem['state'] = tk.NORMAL
            self.btn_preview['state'] = tk.NORMAL
            self.pagelistbox.current(0)

        toplevel.grab_release()
        toplevel.destroy()

    def profile_delete(self):
        """deletes the current profile"""
        current = self.pagelistbox.get()
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

    def handstyle_get(self):
        """Gets lists of handstyles ini"""
        if not os.path.exists("./Style/"):
            os.makedirs("./Style/")

        _handstyles = glob.glob("./Style/*.ini")
        for style in _handstyles:
            self.handstyle_list.append(style.split("\\")[-1])

        if hasattr(self, 'handstyle'):
            self.handstyle['completevalues'] = self.handstyle_list
        print(self.handstyle_list)


    def save_settings(self):
        """Saves the settings json"""
        with open('./settings.json', 'w', encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def increase_count(self):
        """Increases the Image name count"""
        self.settings["settings"]["Image"] = int(self.settings["settings"]["Image"])+1
        self.save_settings()

    def start_printing(self, preview=False):
        if not self.parser:
            MessageBM("No Profiles", "Please open the Settings and create a Profile to use the software.")
            return

        if not preview:
            self.text = self.text_log.get(1.0, tk.END).strip()
            if self.text == "Type Something here....":
                MessageBM("Empty Text", "Please input something on the text field to print")
                return

            if self.text.strip() == "":
                MessageBM("Empty Text", "Please input something on the text field to print")
                return

            self.text_log['state'] = tk.DISABLED
            self.text_log['fg'] = 'grey'

        thread = Thread(target=self.converter, args=[preview])
        thread.start()
        # thread.join()

    def converter(self, preview=False):
        """Converts the text into handwriting"""

        try:
            # creates output if none existent yet
            if not os.path.exists("./Output/"):
                os.makedirs("./Output/")

            # The text document
            if preview:
                self.text = self.genertic_texts

            self.btn_print['state'] = tk.DISABLED
            self.btn_setting['state'] = tk.DISABLED

            # page temp config
            page_limit_x = int(self.page_width - (self.page_width*0.25))
            page_limit_x = 5800
            page_limit_y = self.page_height - (self.page_height*0.1)
            print(f"Y Limit: {page_limit_y}\tHeight: {self.page_height}")
            print(f"X Limit: {page_limit_x}\tHeight: {self.page_width}")
            x = self.border_left
            y = self.line_height
            page_count = 1

            img = Image.new("RGB", (self.page_width, self.page_height), color="White")


            paragraphs = self.text[:-1].split("\n")

            pprint(self.parser.master_table)
            
            for paragraph in paragraphs:
                y += self.line_height
                x = self.border_left

                if not paragraph.strip():
                    y += self.line_height
                    continue

                words = paragraph.split(" ")
                for word in words:
                    
                    if word.strip() == "":
                        x += self.word_spacing
                        continue

                    if y >= page_limit_y:
                        if preview:
                            break
                        x = self.border_left
                        y = self.line_height
                        img.save(f'./Output/{self.settings["settings"]["Image"]}_{page_count}.png', quality=50)
                        img = Image.new("RGB", (self.page_width, self.page_height), color="White")
                        page_count += 1

                    letterlist = []
                    word_size = 0

                    for letter_ in word:
                        letter = letter_.upper()
                        location = self.parser.master_table[letter]
                        letter_variant = str(randrange(len(glob.glob(location + "*.png")))+1)
                        alp = Image.open(location + "/" + letter_variant + ".png")
                        if self.size != 1:
                            alp = alp.resize((int(alp.size[0]*self.size), int(alp.size[1]*self.size)))

                        word_size+=alp.size[0]

                        letterlist.append((letter, alp))
                        if letter in self.parser.space_settings:
                            for space in self.parser.space_settings[letter]:
                                word_size += self.parser.space_settings[letter][space]

                    word_size += x

                    if word_size > page_limit_x:
                        x = self.border_left
                        y += self.line_height

                    for item in letterlist:
                        letter = item[0]
                        letterimg = item[1]
                        if letter in self.parser.space_settings:
                            x_left = 0
                            y_vertical = 0
                            if "left" in self.parser.space_settings[letter]:
                                x_left = self.parser.space_settings[letter]["left"]
                            if "vertical" in self.parser.space_settings[letter]:
                                y_vertical = self.parser.space_settings[letter]["vertical"]
                            img.paste(letterimg, (x+x_left, y+y_vertical), mask=letterimg)
                            if "right" in self.parser.space_settings[letter]:
                                x += self.parser.space_settings[letter]["right"]
                            if x_left:
                                x+= x_left
                        else:
                            img.paste(letterimg, (x, y), mask=letterimg)
                        x+= (letterimg.size[0] + self.letter_spacing)


                    word_size = 0
                    x += self.word_spacing

                else:
                    continue
                break

            self.btn_print['state'] = tk.NORMAL
            self.btn_setting['state'] = tk.NORMAL

            if preview:
                img.show()
                return

            img.save(f'./Output/{self.settings["settings"]["Image"]}_{page_count}.png',
                     quality=50)
            self.increase_count()

            self.text_log['state'] = tk.NORMAL
            self.text_log['fg'] = s.bg

            MessageBM("Done", "            Done printing.            ")
            print("Done")
        except:
            self.text_log['state'] = tk.NORMAL
            self.text_log['fg'] = s.bg
            self.btn_print['state'] = tk.NORMAL
            self.btn_setting['state'] = tk.NORMAL
            return


if __name__ == "__main__":
    root = tk.Tk()
    HandWriter(root).pack(side="top", fill="both", expand=True)
    root.mainloop()






