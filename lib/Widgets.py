import tkinter as tk
from .Style import s
from ttkwidgets.frames import Tooltip

def rClicker(e):
    ''' right click context menu for all Tk Entry and Text widgets'''
    
    try:
        def rClick_Copy(e, apnd=0):
            e.widget.event_generate('<Control-c>')
        def rClick_Cut(e):
            e.widget.event_generate('<Control-x>')
        def rClick_Paste(e):
            e.widget.event_generate('<Control-v>')

        e.widget.focus()

        nclst=[
               (' Cut', lambda e=e: rClick_Cut(e)),
               (' Copy', lambda e=e: rClick_Copy(e)),
               (' Paste', lambda e=e: rClick_Paste(e)),
              ]

        rmenu = tk.Menu(None, tearoff=0, takefocus=0)

        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)

        rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")
    except tk.TclError:
        pass
    return "break"

def rClickbinder(r):
    try:
        for b in [ 'Text', 'Entry', 'Listbox', 'Label']: #
            r.bind_class(b, sequence='<Button-3>',
                         func=rClicker, add='')
    except TclError:
        pass

def on_enter(event, color):
    event.widget['background'] = color

def on_leave(event, color):
    event.widget['background'] = color


class Tip(Tooltip):
    def __init__(self, master, text, ht="Info", *args, **kwargs):
        super().__init__(master, headertext=ht, text=text, *args, **kwargs)

class LabelEntryBM(tk.Frame):
    def __init__(self, master, text, width=8, tip="", *args, **kwargs):
        if not kwargs:
            kwargs = dict()

        super().__init__(master, *args, **kwargs)

        self.entry = tk.Entry(self, bg=s.fg, fg=s.bg, width=width, font=s.font)
        self.entry.bind('<Button-3>', rClicker, add='')
        self.entry.pack(side="right", expand=True, fill=tk.BOTH)

        self.label = tk.Label(self, text=f"{text}: ", font=s.font)
        self.label.pack(side="left", expand=True, fill=tk.BOTH)

        if tip:
            Tip(self, text=tip)

    def get(self):
        """returns entry value"""
        return self.entry.get()

    def getint(self):
        """checks if entry is int"""
        try: x = int(self.entry.get())
        except: x = None
        return x

    def getfloat(self):
        """checks if entry is float"""
        try: x = float(self.entry.get())
        except: x = None
        return x

    def insert(self, text):
        """Inserts value to the internal entry widget
            :text: text to input
        """
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(text))
        
    def clear(self):
        """clears entry"""
        self.entry.delete(0, tk.END)

    def bindkey(self, key, func):
        """binds the internal entry widget to a function
            :key: the key string
            :func: the function to bind
        """
        self.entry.bind(key, func)


class ButtonBM(tk.Button):
    def __init__(self, *args, **kwargs):
        if not kwargs:
            kwargs = dict()
        kwargs['bg'] = s.sub
        kwargs['fg'] = s.fg
        kwargs['bd'] = 0
        if 'w' in kwargs:
            kwargs['width'] = kwargs['w']
            kwargs.pop('w', None)
        else:
            kwargs['width'] = 7
        kwargs['relief'] = tk.FLAT
        kwargs['cursor'] = "hand2"
        kwargs['font'] = s.font
        kwargs['activebackground'] = "white"
        kwargs['activeforeground'] = "black"
        super().__init__(*args, **kwargs)

        self.bind("<Enter>", lambda e: on_enter(e, "#cc3b3b"))
        self.bind("<Leave>", lambda e: on_leave(e, "#f04646"))

class MessageBM(tk.Toplevel):
    def __init__(self, title, message, *args, **kwargs):
        if not kwargs:
            kwargs = dict()

        super().__init__(*args, **kwargs)
        
        self.title(title)
        # self.geometry("400x100")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        tk.Label(self, text=message, justify=tk.CENTER).grid(
                 row=0, column=0, padx=20, pady=10, sticky="nswe")
        btn = tk.Button(self, text="Okay", width=15, bg=s.bg, fg=s.fg,
                  relief=tk.FLAT, command=self.destroy)
        btn.bind("<Enter>", lambda e: on_enter(e, "#101010"))
        btn.bind("<Leave>", lambda e: on_leave(e, s.bg))
        # btn.bind("<Enter>", lambda e: on_enter(e, "#cc3b3b"))
        # btn.bind("<Leave>", lambda e: on_leave(e, "#f04646"))

        btn.grid(row=1, column=0, padx=10)
        tk.Label(self, text="", font=(s.fstyle, 5)).grid(row=2, column=0)

        self.attributes('-topmost', 'true')
        self.grab_set()
        self.focus_set()

class TextBM(tk.Text):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.placeholder = "Type Something here...."
        self.placeholder_color = '#454545'
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(tk.INSERT, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('1.0', tk.END)
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        print("whatt")
        if not self.get('1.0', tk.END).strip():
            self.insert(tk.INSERT, self.placeholder)
            self['fg'] = self.placeholder_color


