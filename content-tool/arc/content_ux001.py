#!/usr/bin/env python3
import sys
import json
from pathlib import Path
import traceback
import subprocess
from tkinter import (Tk, Toplevel, Frame, Label, Entry, Button,
                     Listbox, Scrollbar, END, StringVar, messagebox,
                     Text, filedialog)
from tkinter import BOTH, LEFT, RIGHT, Y, X, TOP, BOTTOM
import tkinter.ttk as ttk

"""
Enhanced Tkinter GUI wrapper for `content_tool.py`.
Features:
- Toolbar with Launch Wizard, Save, Reload
- Startup scan for missing required fields
- Add/Delete languages & pages
- Edit title, intro_text, videos
- Run CLI wizard in-app
- JSON validation and pretty formatting
- Autosave every 15 seconds
- Keyboard shortcuts (Ctrl+S, Ctrl+Q)

Usage:
    python content_ux.py content.json
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
        self._set_status(f"Loaded: {self.json_path}")

        # Run startup missing-content check
        self._check_missing_and_alert()

    # ---------------- I/O ---------------- #
    def _load(self):
        try:
            return json.loads(self.json_path.read_text(encoding='utf-8'))
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load JSON: {e}')
            sys.exit(1)

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

        # Top toolbar
        toolbar = ttk.Frame(self.master)
        toolbar.pack(fill=X, side=TOP)
        ttk.Button(toolbar, text='🧙‍♂️ Launch Wizard', command=self._run_wizard).pack(side=LEFT, padx=4, pady=4)
        ttk.Button(toolbar, text='💾 Save',           command=self._save).pack(side=LEFT, padx=4)
        ttk.Button(toolbar, text='🔄 Reload',         command=self._reload).pack(side=LEFT, padx=4)

        # Menu
        menubar = ttk.Menu(self.master)
        filemenu = ttk.Menu(menubar)
        filemenu.add_command(label='Validate JSON', command=self._validate_json)
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

        # Main layout panes
        paned = ttk.Panedwindow(self.master, orient='horizontal')
        paned.pack(fill=BOTH, expand=True)

        # Sidebar: Languages & Pages
        sidebar = Frame(paned)
        paned.add(sidebar, weight=1)

        Label(sidebar, text='Languages', font=('Arial', 10, 'bold')).pack(anchor='w', padx=4, pady=(4,0))
        self.lang_list = Listbox(sidebar, exportselection=False, height=6)
        self.lang_list.pack(fill=X, padx=4)
        self.lang_list.bind('<<ListboxSelect>>', self._on_lang_select)
        btn_lang_frame = Frame(sidebar)
        btn_lang_frame.pack(fill=X, padx=4, pady=(2,6))
        ttk.Button(btn_lang_frame, text='+', width=3, command=self._add_language_dialog).pack(side=LEFT)
        ttk.Button(btn_lang_frame, text='−', width=3, command=self._delete_language).pack(side=LEFT, padx=4)

        Label(sidebar, text='Pages', font=('Arial', 10, 'bold')).pack(anchor='w', padx=4)
        self.page_list = Listbox(sidebar, exportselection=False)
        self.page_list.pack(fill=BOTH, expand=True, padx=4)
        self.page_list.bind('<<ListboxSelect>>', self._on_page_select)
        btn_page_frame = Frame(sidebar)
        btn_page_frame.pack(fill=X, padx=4, pady=4)
        ttk.Button(btn_page_frame, text='+', width=3, command=self._add_page_dialog).pack(side=LEFT)
        ttk.Button(btn_page_frame, text='−', width=3, command=self._delete_page).pack(side=LEFT, padx=4)

        # Editor area
        editor = Frame(paned)
        paned.add(editor, weight=3)
        form = Frame(editor)
        form.pack(fill=X, padx=10, pady=6)
        Label(form, text='Title').grid(row=0, column=0, sticky='w')
        self.title_var = StringVar()
        self.title_entry = ttk.Entry(form, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=1, sticky='ew', padx=(4,0))
        Label(form, text='Intro').grid(row=1, column=0, sticky='nw', pady=(6,0))
        self.intro_text = Text(form, height=4, wrap='word')
        self.intro_text.grid(row=1, column=1, sticky='ew', padx=(4,0), pady=(6,0))
        form.columnconfigure(1, weight=1)

        # Videos list
        vids_frame = Frame(editor)
        vids_frame.pack(fill=BOTH, expand=True, padx=10, pady=4)
        Label(vids_frame, text='Videos', font=('Arial', 10, 'bold')).pack(anchor='w')
        self.video_list = Listbox(vids_frame, height=6)
        self.video_list.pack(fill=BOTH, expand=True, side=LEFT)
        vscroll = Scrollbar(vids_frame, command=self.video_list.yview)
        vscroll.pack(side=RIGHT, fill=Y)
        self.video_list.config(yscrollcommand=vscroll.set)
        btn_vid_frame = Frame(editor)
        btn_vid_frame.pack(fill=X, padx=10)
        ttk.Button(btn_vid_frame, text='Add Video', command=self._add_video_dialog).pack(side=LEFT)
        ttk.Button(btn_vid_frame, text='Remove Selected', command=self._remove_selected_video).pack(side=LEFT, padx=4)

        # Status bar
        self.status_var = StringVar(value='Ready')
        status = Label(self.master, textvariable=self.status_var, anchor='w', relief='sunken')
        status.pack(fill=X, side=BOTTOM)

    # ---------------- Shortcuts ---------------- #
    def _bind_shortcuts(self):
        self.master.bind('<Control-s>', lambda e: self._save())
        self.master.bind('<Control-q>', lambda e: self.master.quit())

    # ---------------- Missing Content Check ---------------- #
    def _check_missing_and_alert(self):
        missing = []
        for lang, pages in self.data.items():
            for page, block in pages.items():
                for field in REQUIRED_FIELDS:
                    val = block.get(field, '')
                    if not val or str(val).startswith('<'):
                        missing.append(f"{lang}.{page}.{field}")
        if missing:
            msg = "Missing required fields:\n" + "\n".join(missing)
            if messagebox.askyesno("Missing Content Detected", msg + "\n\nRun Wizard now? "):
                self._run_wizard()

    # ---------------- Populate Lists ---------------- #
    def _populate_languages(self):
        self.lang_list.delete(0, END)
        for lang in sorted(self.data.keys()):
            self.lang_list.insert(END, lang)
        if self.lang_list.size():
            self.lang_list.selection_set(0)
            self._on_lang_select(None)

    def _populate_pages(self, lang):
        self.page_list.delete(0, END)
        for p in sorted(self.data.get(lang, {})):
            self.page_list.insert(END, p)
        if self.page_list.size():
            self.page_list.selection_set(0)
            self._on_page_select(None)
        else:
            self._clear_editor()

    # ... rest of methods unchanged ...

# ---------------- Modal Input ---------------- #
class SimpleDialog(Toplevel):
    def __init__(self, master, title, prompt):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        Label(self, text=prompt).pack(padx=10, pady=6)
        self.var = StringVar()
        entry = ttk.Entry(self, textvariable=self.var)
        entry.pack(padx=10, fill=X)
        entry.focus_set()
        btns = Frame(self)
        btns.pack(pady=6)
        ttk.Button(btns, text='OK', command=self._ok).pack(side=LEFT, padx=4)
        ttk.Button(btns, text='Cancel', command=self._cancel).pack(side=LEFT)
        self.bind('<Return>', lambda e: self._ok())
        self.bind('<Escape>', lambda e: self._cancel())
        self.result = None
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _ok(self):
        self.result = self.var.get().strip()
        self.destroy()

    def _cancel(self):
        self.destroy()


def simple_input(master, title, prompt):
    dlg = SimpleDialog(master, title, prompt)
    return dlg.result

# ---------------- Entry Point & Autosave ---------------- #
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python content_ux.py <content.json>')
        sys.exit(1)
    root = Tk()
    app = ContentToolGUI(root, sys.argv[1])
    root.protocol('WM_DELETE_WINDOW', app.on_close)

    def autosave_loop():
        try:
            app._persist_page()
            if app._dirty:
                app._save(silent=True)
                app._set_status('Autosaved.')
        except Exception:
            traceback.print_exc()
        root.after(15000, autosave_loop)

    root.after(15000, autosave_loop)
    root.mainloop()
