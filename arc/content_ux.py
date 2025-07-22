import sys
import json
from pathlib import Path
import traceback
import subprocess
from tkinter import Tk, Frame, Label, Entry, Button, Listbox, Scrollbar, END, StringVar, messagebox, Text, filedialog
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
    python gui_wrapper.py content.json

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

        # ---- Paned Layout ---- #
        paned = ttk.Panedwindow(self.master, orient='horizontal')
        paned.pack(fill=BOTH, expand=True)

        # Left sidebar
        sidebar = Frame(paned)
        paned.add(sidebar, weight=1)

        # Languages list
        Label(sidebar, text='Languages', font=('Arial', 10, 'bold')).pack(anchor='w', padx=4, pady=(4,0))
        self.lang_list = Listbox(sidebar, exportselection=False, height=6)
        self.lang_list.pack(fill=X, padx=4)
        self.lang_list.bind('<<ListboxSelect>>', self._on_lang_select)

        btn_lang_frame = Frame(sidebar)
        btn_lang_frame.pack(fill=X, padx=4, pady=(2,6))
        ttk.Button(btn_lang_frame, text='+', width=3, command=self._add_language_dialog).pack(side=LEFT)
        ttk.Button(btn_lang_frame, text='−', width=3, command=self._delete_language).pack(side=LEFT, padx=2)

        # Pages list
        Label(sidebar, text='Pages', font=('Arial', 10, 'bold')).pack(anchor='w', padx=4)
        self.page_list = Listbox(sidebar, exportselection=False)
        self.page_list.pack(fill=BOTH, expand=True, padx=4)
        self.page_list.bind('<<ListboxSelect>>', self._on_page_select)

        btn_page_frame = Frame(sidebar)
        btn_page_frame.pack(fill=X, padx=4, pady=4)
        ttk.Button(btn_page_frame, text='+', width=3, command=self._add_page_dialog).pack(side=LEFT)
        ttk.Button(btn_page_frame, text='−', width=3, command=self._delete_page).pack(side=LEFT, padx=2)

        # Main editor area
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

        # Video list editor
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

        # Action buttons
        action_frame = Frame(editor_container)
        action_frame.pack(fill=X, padx=10, pady=6)
        ttk.Button(action_frame, text='Save (Ctrl+S)', command=self._save).pack(side=LEFT)
        ttk.Button(action_frame, text='Reload', command=self._reload).pack(side=LEFT, padx=4)
        ttk.Button(action_frame, text='Wizard', command=self._run_wizard).pack(side=LEFT)

        # Status bar
        self.status_var = StringVar(value='Ready')
        status = Label(self.master, textvariable=self.status_var, anchor='w', relief='sunken')
        status.pack(fill=X, side=BOTTOM)

    def _bind_shortcuts(self):
        self.master.bind('<Control-s>', lambda e: self._save())
        self.master.bind('<Control-q>', lambda e: self.master.quit())

    # ---------------- Status Helper ---------------- #
    def _set_status(self, msg):
        self.status_var.set(msg)

    # ---------------- Populate Lists ---------------- #
    def _populate_languages(self):
        self.lang_list.delete(0, END)
        for lang in sorted([k for k,v in self.data.items() if isinstance(v, dict)]):
            self.lang_list.insert(END, lang)
        # auto-select first
        if self.lang_list.size():
            self.lang_list.selection_set(0)
            self._on_lang_select(None)

    def _populate_pages(self, lang):
        self.page_list.delete(0, END)
        pages = sorted(self.data.get(lang, {}).keys())
        for p in pages:
            self.page_list.insert(END, p)
        if pages:
            self.page_list.selection_set(0)
            self._on_page_select(None)
        else:
            self._clear_editor()

    # ---------------- Event Handlers ---------------- #
    def _on_lang_select(self, event):
        sel = self.lang_list.curselection()
        if not sel:
            self.current_lang = None
            return
        self.current_lang = self.lang_list.get(sel[0])
        self._populate_pages(self.current_lang)

    def _on_page_select(self, event):
        sel = self.page_list.curselection()
        if not sel:
            self.current_page = None
            return
        self.current_page = self.page_list.get(sel[0])
        self._load_page(self.current_lang, self.current_page)

    # ---------------- CRUD Operations ---------------- #
    def _add_language_dialog(self):
        name = simple_input(self.master, 'Add Language', 'Language code (e.g., en):')
        if not name: return
        if name in self.data:
            messagebox.showwarning('Exists', 'Language already exists.')
            return
        self.data[name] = {}
        self._dirty = True
        self._populate_languages()
        self._set_status(f'Added language {name}')

    def _delete_language(self):
        if not self.current_lang:
            return
        if not messagebox.askyesno('Delete', f'Delete language {self.current_lang}?'): return
        del self.data[self.current_lang]
        self.current_lang = None
        self._dirty = True
        self._populate_languages()
        self._set_status('Language deleted')

    def _add_page_dialog(self):
        if not self.current_lang:
            messagebox.showinfo('No language', 'Select a language first.')
            return
        slug = simple_input(self.master, 'Add Page', 'Page slug:')
        if not slug: return
        lang_block = self.data.setdefault(self.current_lang, {})
        if slug in lang_block:
            messagebox.showwarning('Exists', 'Page already exists.')
            return
        lang_block[slug] = {f: f'<{f}>' for f in REQUIRED_FIELDS}
        lang_block[slug]['videos'] = []
        self._dirty = True
        self._populate_pages(self.current_lang)
        self._set_status(f'Added page {slug}')

    def _delete_page(self):
        if not (self.current_lang and self.current_page):
            return
        if not messagebox.askyesno('Delete', f'Delete page {self.current_page}?'): return
        del self.data[self.current_lang][self.current_page]
        self.current_page = None
        self._dirty = True
        self._populate_pages(self.current_lang)
        self._set_status('Page deleted')

    # ---------------- Page Editing ---------------- #
    def _clear_editor(self):
        self.title_var.set('')
        self.intro_text.delete('1.0', END)
        self.video_list.delete(0, END)

    def _load_page(self, lang, page):
        try:
            block = self.data[lang][page]
        except KeyError:
            return
        self.title_var.set(block.get('title', ''))
        self.intro_text.delete('1.0', END)
        self.intro_text.insert(END, block.get('intro_text', ''))
        self.video_list.delete(0, END)
        for v in block.get('videos', []):
            title = v.get('title') or '(untitled)'
            link = v.get('video_link') or ''
            self.video_list.insert(END, f"{title} | {link}")

    def _persist_page(self):
        if not (self.current_lang and self.current_page):
            return
        block = self.data[self.current_lang][self.current_page]
        block['title'] = self.title_var.get().strip()
        block['intro_text'] = self.intro_text.get('1.0', END).strip()
        # videos already stored
        self._dirty = True

    def _add_video_dialog(self):
        if not (self.current_lang and self.current_page):
            return
        title = simple_input(self.master, 'Video', 'Video title:')
        if not title: return
        link = simple_input(self.master, 'Video', 'Video link (URL):')
        if not link: return
        block = self.data[self.current_lang][self.current_page]
        block.setdefault('videos', []).append({'title': title, 'video_link': link})
        self._dirty = True
        self._load_page(self.current_lang, self.current_page)

    def _remove_selected_video(self):
        if not (self.current_lang and self.current_page): return
        idxs = list(self.video_list.curselection())
        if not idxs: return
        block = self.data[self.current_lang][self.current_page]
        vids = block.get('videos', [])
        for i in reversed(idxs):
            try: vids.pop(i)
            except IndexError: pass
        self._dirty = True
        self._load_page(self.current_lang, self.current_page)

    # ---------------- Actions ---------------- #
    def _validate_json(self):
        try:
            json.dumps(self.data)
            messagebox.showinfo('Valid', 'JSON is valid.')
        except Exception as e:
            messagebox.showerror('Invalid JSON', str(e))

    def _run_wizard(self):
        # Persist current edits before launching wizard
        self._persist_page()
        self._save(silent=True)
        try:
            subprocess.call([sys.executable, 'content_tool.py', 'wizard', str(self.json_path)])
            self.data = self._load()
            self._populate_languages()
            self._set_status('Wizard finished & reloaded.')
        except FileNotFoundError:
            messagebox.showerror('Missing', 'content_tool.py not found in current directory.')

    def _reload(self):
        if self._dirty and not messagebox.askyesno('Discard changes?', 'Unsaved changes will be lost. Continue?'):
            return
        self.data = self._load()
        self._populate_languages()
        self._set_status('Reloaded from disk.')

    # ---------------- Lifecycle ---------------- #
    def on_close(self):
        self._persist_page()
        if self._dirty and messagebox.askyesno('Save?', 'Save changes before exit?'):
            self._save(silent=True)
        self.master.destroy()

# ---------------- Utility Dialog ---------------- #
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

# ---------------- Standalone entrypoint ---------------- #
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python gui_wrapper.py <content.json>')
        sys.exit(1)
    root = Tk()
    app = ContentToolGUI(root, sys.argv[1])
    root.protocol('WM_DELETE_WINDOW', app.on_close)

    def autosave_loop():
        # autosave every 15s if dirty
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

