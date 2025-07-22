import sys
import json
from pathlib import Path
import traceback
import subprocess
# Import tkinter with necessary widgets
from tkinter import Tk, Toplevel, Frame, Label, Entry, Button, Listbox, Scrollbar, END, StringVar, messagebox, Text, filedialog
from tkinter import BOTH, LEFT, RIGHT, Y, X, TOP, BOTTOM
import tkinter.ttk as ttk

"""
Enhanced Tkinter-based GUI wrapper for the content_tool script.

Goals / UX Improvements:
- Modernized layout using ttk widgets
- Status bar + autosave feedback
- Add / Delete languages & pages directly from GUI
- Edit title + intro_text
- Edit simple video list (add/remove)
- Run CLI wizard from inside the app
- Validate + pretty format JSON
- Keyboard shortcuts

Usage:
    python content_ux.py content.json

You may still use the CLI tool for advanced features.
"""

REQUIRED_FIELDS = ["title", "intro_text"]

class ContentToolGUI:
    def __init__(self, master, json_path):
        self.master = master
        self.master.title('Content Manager')
        self.master.geometry('1000x640')
        self.json_path = Path(json_path)
        self.data = self._load()
        self.current_lang = None
        self.current_page = None
        self._dirty = False

        self._build_ui()
        self._populate_languages()
        self._bind_shortcuts()
        self._set_status(f"Loaded {self.json_path}")

    # ---------------- I/O ---------------- #
    def _load(self):
        try:
            return json.loads(self.json_path.read_text(encoding='utf-8'))
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load JSON: {e}')
            raise SystemExit(1)

    def _save(self, silent=False):
        try:
            formatted = json.dumps(self.data, ensure_ascii=False, indent=2)
            self.json_path.write_text(formatted + '\n', encoding='utf-8')
            self._dirty = False
            if not silent:
                self._set_status('Saved.')
        except Exception as e:
            messagebox.showerror('Save Error', str(e))

    # ---------------- UI Construction ---------------- #
    def _build_ui(self):
        self.master.option_add('*tearOff', False)

        # Menu
        menubar = ttk.Menu(self.master)
        filemenu = ttk.Menu(menubar)
        filemenu.add_command(label='Save (Ctrl+S)', command=self._save)
        filemenu.add_command(label='Reload', command=self._reload)
        filemenu.add_separator()
        filemenu.add_command(label='Validate JSON', command=self._validate_json)
        filemenu.add_command(label='Run Wizard', command=self._run_wizard)
        filemenu.add_separator()
        filemenu.add_command(label='Quit', command=self.master.quit)
        menubar.add_cascade(label='File', menu=filemenu)

        editmenu = ttk.Menu(menubar)
        editmenu.add_command(label='Add Language', command=self._add_language_dialog)
        editmenu.add_command(label='Delete Language', command=self._delete_language)
        editmenu.add_separator()
        editmenu.add_command(label='Add Page', command=self._add_page_dialog)
        editmenu.add_command(label='Delete Page', command=self._delete_page)
        menubar.add_cascade(label='Edit', menu=editmenu)

        self.master.config(menu=menubar)

        # Layout
        paned = ttk.Panedwindow(self.master, orient='horizontal')
        paned.pack(fill=BOTH, expand=True)

        # Sidebar
        sidebar = Frame(paned)
        paned.add(sidebar, weight=1)
        Label(sidebar, text='Languages', font=('Arial', 10, 'bold')).pack(anchor='w', padx=4, pady=(4,0))
        self.lang_list = Listbox(sidebar, exportselection=False, height=6)
        self.lang_list.pack(fill=X, padx=4)
        self.lang_list.bind('<<ListboxSelect>>', self._on_lang_select)
        btn_lang_frame = Frame(sidebar)
        btn_lang_frame.pack(fill=X, padx=4, pady=(2,6))
        ttk.Button(btn_lang_frame, text='+', width=3, command=self._add_language_dialog).pack(side=LEFT)
        ttk.Button(btn_lang_frame, text='−', width=3, command=self._delete_language).pack(side=LEFT, padx=2)

        Label(sidebar, text='Pages', font=('Arial', 10, 'bold')).pack(anchor='w', padx=4)
        self.page_list = Listbox(sidebar, exportselection=False)
        self.page_list.pack(fill=BOTH, expand=True, padx=4)
        self.page_list.bind('<<ListboxSelect>>', self._on_page_select)
        btn_page_frame = Frame(sidebar)
        btn_page_frame.pack(fill=X, padx=4, pady=4)
        ttk.Button(btn_page_frame, text='+', width=3, command=self._add_page_dialog).pack(side=LEFT)
        ttk.Button(btn_page_frame, text='−', width=3, command=self._delete_page).pack(side=LEFT, padx=2)

        # Editor
        editor_container = Frame(paned)
        paned.add(editor_container, weight=3)
        form = Frame(editor_container)
        form.pack(fill=X, padx=10, pady=6)
        Label(form, text='Title').grid(row=0, column=0, sticky='w')
        self.title_var = StringVar()
        self.title_entry = ttk.Entry(form, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=1, sticky='ew', padx=(4,0))
        Label(form, text='Intro').grid(row=1, column=0, sticky='nw', pady=(6,0))
        self.intro_text = Text(form, height=4, wrap='word')
        self.intro_text.grid(row=1, column=1, sticky='ew', padx=(4,0), pady=(6,0))
        form.columnconfigure(1, weight=1)

        # Videos
        videos_frame = Frame(editor_container)
        videos_frame.pack(fill=BOTH, expand=True, padx=10, pady=4)
        Label(videos_frame, text='Videos', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.video_list = Listbox(videos_frame, height=6)
        self.video_list.pack(fill=BOTH, expand=True, side=LEFT)
        vscroll = Scrollbar(videos_frame, command=self.video_list.yview)
        vscroll.pack(side=RIGHT, fill=Y)
        self.video_list.config(yscrollcommand=vscroll.set)
        btn_vids = Frame(editor_container)
        btn_vids.pack(fill=X, padx=10)
        ttk.Button(btn_vids, text='Add Video', command=self._add_video_dialog).pack(side=LEFT)
        ttk.Button(btn_vids, text='Remove Selected', command=self._remove_selected_video).pack(side=LEFT, padx=4)

        # Actions
        action_frame = Frame(editor_container)
        action_frame.pack(fill=X, padx=10, pady=6)
        ttk.Button(action_frame, text='Save (Ctrl+S)', command=self._save).pack(side=LEFT)
        ttk.Button(action_frame, text='Reload', command=self._reload).pack(side=LEFT, padx=4)
        ttk.Button(action_frame, text='Wizard', command=self._run_wizard).pack(side=LEFT)

        # Status
        self.status_var = StringVar(value='Ready')
        status = Label(self.master, textvariable=self.status_var, anchor='w', relief='sunken')
        status.pack(fill=X, side=BOTTOM)

    # ... rest unchanged ...

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python content_ux.py <content.json>')
        sys.exit(1)
    root = Tk()
    app = ContentToolGUI(root, sys.argv[1])
    root.protocol('WM_DELETE_WINDOW', app.on_close)
    root.mainloop()

