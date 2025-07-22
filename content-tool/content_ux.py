#!/usr/bin/env python3
from tkinter import (
    Tk, Toplevel, Frame, Label, Entry, Button, Listbox, Scrollbar, Menu, END, StringVar, messagebox, Text, filedialog, BOTH, LEFT, RIGHT, Y, X, TOP, BOTTOM
)
import tkinter.ttk as ttk
import traceback
import sys
import json
from pathlib import Path
import subprocess

"""
Enhanced Tkinter GUI wrapper for `content_tool.py`, now with:
- Top toolbar (Wizard, Save, Reload)
- Startup missing-field scan & prompt
- Autosave loop
- Correct usage banner
"""


# ----------------- ADD THIS CODE -----------------
PAGE_TEMPLATES = {
    # Default template for any page not listed
    "default": {
        "required_fields": ["title", "intro_text"],
        "optional_fields": ["videos"]
    },
    # Template for simple pages that don't need videos
    "simple": {
        "required_fields": ["title", "intro_text"],
        "optional_fields": []
    },
    # Template for pages that MUST have video content
    "video_page": {
        "required_fields": ["title", "intro_text", "videos"],
        "optional_fields": []
    },
}

# We can map your page slugs to these templates
PAGE_CONFIG = {
    "soakpit": "video_page",
    "water_security": "video_page",
    "mycelium": "video_page",
    "site_name": "simple",
    "footer": "simple",
    "navigation": "simple",
    "assets": "simple",
    "biodiversity_page": "simple",
    # Any other page will use the "default" template
}

REQUIRED_FIELDS = ["title", "intro_text"]





# In content_ux.py

class WizardDialog(Toplevel):
    def __init__(self, master, data, required_fields):
        super().__init__(master)
        self.master_app = master  # Reference to the main ContentToolGUI instance
        self.data = data
        
        # We need the page templates and config from the last step
        # Make sure these are defined in your script
        self.page_templates = PAGE_TEMPLATES
        self.page_config = PAGE_CONFIG

        self.steps = self._generate_steps()
        self.current_step = 0

        self.title("Content Wizard")
        self.geometry("500x170")

        # --- UI Elements ---
        self.prompt_label = Label(self, text="", wraplength=480, justify=LEFT)
        self.prompt_label.pack(padx=10, pady=(10, 5), anchor='w')

        # Frame for the text entry
        self.text_frame = Frame(self)
        self.entry_var = StringVar()
        self.entry = ttk.Entry(self.text_frame, textvariable=self.entry_var)
        self.entry.pack(fill=X)
        self.entry.bind("<Return>", lambda e: self.process_next())

        # Frame for the video action
        self.video_frame = Frame(self)
        Label(self.video_frame, text="This page is missing a required video.").pack()
        ttk.Button(self.video_frame, text="Add a Video...", command=self.add_video).pack(pady=5)

        # Main control buttons
        btn_frame = Frame(self)
        btn_frame.pack(pady=10, side=BOTTOM, fill=X)
        self.next_button = ttk.Button(btn_frame, text="Next", command=self.process_next)
        self.next_button.pack(side=RIGHT, padx=10)
        
        # Start the wizard
        if not self.steps:
            self.prompt_label.config(text="No missing required fields found. Well done!")
            self.next_button.config(text="Finish", command=self.finish)
        else:
            self.display_current_step()
            self.entry.focus()

        # Make the window modal
        self.protocol("WM_DELETE_WINDOW", self.finish)
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _generate_steps(self):
        # This method uses the page templates you created in the last step.
        steps = []
        for lang, pages in self.data.items():
            if not isinstance(pages, dict): continue
            for page_slug, content in pages.items():
                if not isinstance(content, dict): continue
                template_name = self.page_config.get(page_slug, "default")
                template = self.page_templates.get(template_name, self.page_templates["default"])
                required_fields = template.get("required_fields", [])
                for field in required_fields:
                    field_value = content.get(field)
                    is_missing = False
                    if field_value is None: is_missing = True
                    elif isinstance(field_value, str) and (not field_value or field_value.startswith('<')): is_missing = True
                    elif isinstance(field_value, list) and not field_value: is_missing = True
                    if is_missing:
                        steps.append({'lang': lang, 'page': page_slug, 'field': field})
        return steps

    def display_current_step(self):
        """Update the UI to show the correct widgets for the current step."""
        if self.current_step >= len(self.steps):
            self.finish()
            return

        step_info = self.steps[self.current_step]
        lang, page, field = step_info['lang'], step_info['page'], step_info['field']
        prompt_text = f"Language: '{lang}' > Page: '{page}'\nField: '{field}'"
        
        # Check the field type to show the correct UI
        if field == 'videos':
            self.text_frame.pack_forget()
            self.video_frame.pack(pady=5, padx=10, fill=X)
            self.prompt_label.config(text=prompt_text)
        else: # It's a text field
            self.video_frame.pack_forget()
            self.text_frame.pack(pady=5, padx=10, fill=X)
            self.prompt_label.config(text=prompt_text + "\n\nEnter new value below:")
            
            # This is the fix: It now correctly gets and displays the existing value.
            current_val = self.data[lang][page].get(field, '')
            self.entry_var.set(current_val)
            self.entry.selection_range(0, END)
            self.entry.focus()

        if self.current_step == len(self.steps) - 1:
            self.next_button.config(text="Finish")

    def process_next(self):
        """Save the current field's data and move to the next step."""
        if self.current_step >= len(self.steps):
            self.finish()
            return

        step_info = self.steps[self.current_step]
        lang, page, field = step_info['lang'], step_info['page'], step_info['field']
        
        # Only process data if the text frame is visible
        if self.text_frame.winfo_ismapped():
            new_value = self.entry_var.get()
            if new_value: 
                self.data[lang][page][field] = new_value

        self.current_step += 1
        self.display_current_step()

    def add_video(self):
        """Use the main app's dialog to add a video."""
        # We can call the SimpleDialog to get the info
        title = simple_input(self, "Add Video", "Video Title:")
        if not title: return
        link = simple_input(self, "Add Video", "Video Link:")
        if not link: return

        step_info = self.steps[self.current_step]
        lang, page = step_info['lang'], step_info['page']
        # Add the new video to our data
        self.data[lang][page].setdefault('videos', []).append({'title': title, 'video_link': link})
        
        # Now that we've added a video, we can move on
        self.process_next()

    def finish(self):
        self.grab_release()
        self.destroy()






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
        self._check_missing_and_alert()
    def _set_status(self, message):
        self.status_var.set(message)


    # I/O
    def _load(self):
        try:
            return json.loads(self.json_path.read_text(encoding='utf-8'))
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load JSON: {e}')
            sys.exit(1)

    def _save(self, silent=False):
        try:
            text = json.dumps(self.data, ensure_ascii=False, indent=2)
            self.json_path.write_text(text + '\n', encoding='utf-8')
            self._dirty=False
            if not silent: self._set_status('Saved.')
        except Exception as e:
            messagebox.showerror('Save Error', str(e))

    # UI Construction
    def _build_ui(self):
        self.master.option_add('*tearOff', False)
        # Toolbar
        tb = ttk.Frame(self.master)
        tb.pack(fill=X, side=TOP)
        ttk.Button(tb, text='🧙‍♂️ Launch Wizard', command=self._run_wizard).pack(side=LEFT, padx=4, pady=4)
        ttk.Button(tb, text='💾 Save', command=self._save).pack(side=LEFT, padx=4)
        ttk.Button(tb, text='🔄 Reload', command=self._reload).pack(side=LEFT, padx=4)
        # Menu
        menubar=Menu(self.master)
        filemenu=Menu(menubar, tearoff=False)
        editmenu=Menu(menubar, tearoff=False)
        filemenu.add_command(label='Validate JSON', command=self._validate_json)
        filemenu.add_separator()
        filemenu.add_command(label='Quit', command=self.master.quit)
        menubar.add_cascade(label='File', menu=filemenu)
        editmenu.add_command(label='Add Language', command=self._add_language_dialog)
        editmenu.add_command(label='Delete Language', command=self._delete_language)
        editmenu.add_separator()
        editmenu.add_command(label='Add Page', command=self._add_page_dialog)
        editmenu.add_command(label='Delete Page', command=self._delete_page)
        menubar.add_cascade(label='Edit', menu=editmenu)
        self.master.config(menu=menubar)
        # Panes
        paned=ttk.Panedwindow(self.master, orient='horizontal')
        paned.pack(fill=BOTH,expand=True)
        # Sidebar
        sb=Frame(paned);paned.add(sb,weight=1)
        Label(sb,text='Languages',font=('Arial',10,'bold')).pack(anchor='w',padx=4,pady=(4,0))
        self.lang_list=Listbox(sb,exportselection=False,height=6)
        self.lang_list.pack(fill=X,padx=4)
        self.lang_list.bind('<<ListboxSelect>>',self._on_lang_select)
        bl=Frame(sb);bl.pack(fill=X,padx=4,pady=(2,6))
        ttk.Button(bl,text='+',width=3,command=self._add_language_dialog).pack(side=LEFT)
        ttk.Button(bl,text='−',width=3,command=self._delete_language).pack(side=LEFT,padx=4)
        Label(sb,text='Pages',font=('Arial',10,'bold')).pack(anchor='w',padx=4)
        self.page_list=Listbox(sb,exportselection=False)
        self.page_list.pack(fill=BOTH,expand=True,padx=4)
        self.page_list.bind('<<ListboxSelect>>',self._on_page_select)
        bp=Frame(sb);bp.pack(fill=X,padx=4,pady=4)
        ttk.Button(bp,text='+',width=3,command=self._add_page_dialog).pack(side=LEFT)
        ttk.Button(bp,text='−',width=3,command=self._delete_page).pack(side=LEFT,padx=4)
        # Editor
        ed=Frame(paned);paned.add(ed,weight=3)
        frm=Frame(ed);frm.pack(fill=X,padx=10,pady=6)
        Label(frm,text='Title').grid(row=0,column=0,sticky='w')
        self.title_var=StringVar()
        self.title_entry=ttk.Entry(frm,textvariable=self.title_var)
        self.title_entry.grid(row=0,column=1,sticky='ew',padx=(4,0))
        Label(frm,text='Intro').grid(row=1,column=0,sticky='nw',pady=(6,0))
        self.intro_text=Text(frm,height=4,wrap='word')
        self.intro_text.grid(row=1,column=1,sticky='ew',padx=(4,0),pady=(6,0))
        frm.columnconfigure(1,weight=1)
        vf=Frame(ed);vf.pack(fill=BOTH,expand=True,padx=10,pady=4)
        Label(vf,text='Videos',font=('Arial',10,'bold')).pack(anchor='w')
        self.video_list=Listbox(vf,height=6)
        self.video_list.pack(fill=BOTH,expand=True,side=LEFT)
        vs=Scrollbar(vf,command=self.video_list.yview)
        vs.pack(side=RIGHT,fill=Y)
        self.video_list.config(yscrollcommand=vs.set)
        vb=Frame(ed);vb.pack(fill=X,padx=10)
        ttk.Button(vb,text='Add Video',command=self._add_video_dialog).pack(side=LEFT)
        ttk.Button(vb,text='Remove Selected',command=self._remove_selected_video).pack(side=LEFT,padx=4)
        # Status
        self.status_var=StringVar(self.master, 'Ready')
        status=Label(self.master,textvariable=self.status_var,anchor='w',relief='sunken')
        status.pack(fill=X,side=BOTTOM)
    # Shortcuts
    def _bind_shortcuts(self):
        self.master.bind('<Control-s>',lambda e:self._save())
        self.master.bind('<Control-q>',lambda e:self.master.quit())
    # Missingfields
    def _check_missing_and_alert(self):
        missing = []
        for L, pages in self.data.items():
            for P, blk in pages.items():
                # First, check if blk is a dictionary.
                if isinstance(blk, dict):
                    # If it is, check for the required fields like before.
                    for f in REQUIRED_FIELDS:
                        v = blk.get(f, '')
                        if not v or str(v).startswith('<'):
                            missing.append(f"{L}.{P}.{f}")
                else:
                    # If blk is NOT a dictionary, the whole entry is malformed.
                    missing.append(f"Error: Malformed page data for {L}.{P}")
        
        if missing:
            msg = "Missing or invalid content:\n" + "\n".join(missing)
            if messagebox.askyesno('Content Issues Found', msg + '\n\nRun Wizard to try and fix?'):
                self._run_wizard()


    # Populate
    def _populate_languages(self):
        self.lang_list.delete(0,END)
        for L in sorted(self.data.keys()): self.lang_list.insert(END,L)
        if self.lang_list.size(): self.lang_list.selection_set(0);self._on_lang_select(None)
    def _populate_pages(self, lang):
        self.page_list.delete(0, END)
    # Get the list of pages, defaulting to an empty list if not found
        pages_list = self.data.get(lang, {}).get('pages', [])
        for page_obj in sorted(pages_list, key=lambda p: p.get('slug', '')):
            self.page_list.insert(END, page_obj.get('slug'))
    
        if self.page_list.size():
            self.page_list.selection_set(0)
            self._on_page_select(None)
        else:
            self._clear_editor() 

    # Handlers
    def _on_lang_select(self,event):
        sel=self.lang_list.curselection();
        if not sel: self.current_lang=None; return
        self.current_lang=self.lang_list.get(sel[0]);self._populate_pages(self.current_lang)
    def _on_page_select(self,event):
        sel=self.page_list.curselection();
        if not sel: self.current_page=None;return
        self.current_page=self.page_list.get(sel[0]);self._load_page(self.current_lang,self.current_page)
    # Add/Delete
    def _add_language_dialog(self):
        name=simple_input(self.master,'Add Language','Language code:')
        if not name: return
        if name in self.data: messagebox.showwarning('Exists','Language exists');return
        self.data[name]={};self._dirty=True;self._populate_languages();self._set_status(f'Added {name}')
    def _delete_language(self):
        if not self.current_lang: return
        if not messagebox.askyesno('Delete',f'Delete {self.current_lang}?'):return
        del self.data[self.current_lang];self.current_lang=None;self._dirty=True;self._populate_languages();self._set_status('Lang deleted')
    def _add_page_dialog(self):
        if not self.current_lang:
            messagebox.showinfo('Select Language', 'Please select a language before adding a page.')
            return
    
        slug = simple_input(self.master, 'Add Page', 'New page slug (e.g., "about-us"):')
        if not slug:
            return

        pages_list = self.data.setdefault(self.current_lang, {}).setdefault('pages', [])
        if any(p.get('slug') == slug for p in pages_list):
            messagebox.showwarning('Exists', 'A page with this slug already exists.')
            return
        
    # Create a new, standard page object
        new_page = {
            "slug": slug,
            "title": f"<{slug.replace('_', ' ').title()}>",
            "intro_text": "<intro text>",
            "videos": [],
            "content_blocks": []
        }
        pages_list.append(new_page)
        self._dirty = True
        self._populate_pages(self.current_lang)
        # Select the newly added page
        for i, item in enumerate(self.page_list.get(0, END)):
            if item == slug:
                self.page_list.selection_set(i)
                self._on_page_select(None)
                break
        self._set_status(f"Added page: {slug}")

    def _delete_page(self):
        if not (self.current_lang and self.current_page):
            return
    
        if not messagebox.askyesno('Delete', f"Are you sure you want to delete the page '{self.current_page}'?"):
            return

        pages_list = self.data.get(self.current_lang, {}).get('pages', [])
    # Create a new list excluding the page to be deleted
        self.data[self.current_lang]['pages'] = [p for p in pages_list if p.get('slug') != self.current_page]
    
        self.current_page = None
        self._dirty = True
        self._populate_pages(self.current_lang)
        self._set_status('Page deleted.')

    # Editor
    def _clear_editor(self):
        self.title_var.set('');self.intro_text.delete('1.0',END);self.video_list.delete(0,END)
    def _load_page(self,lang,page_slug):
        self._clear_editor()
        pages_list = self.data.get(lang, {}).get('pages', [])
        # Find the page object that matches the selected slug
        page_obj = next((p for p in pages_list if p.get('slug') == page_slug), None)

        if not page_obj:
            self.title_var.set(f"!! ERROR: Could not find page '{page_slug}'.")
            return

        self.title_var.set(page_obj.get('title', ''))
        self.intro_text.delete('1.0', END)
        self.intro_text.insert(END, page_obj.get('intro_text', ''))
        self.video_list.delete(0, END)
        for v in page_obj.get('videos', []):
            self.video_list.insert(END, f"{v.get('title')} | {v.get('video_link')}")

    def _persist_page(self):
        if not (self.current_lang and self.current_page):
            return

        pages_list = self.data.get(self.current_lang, {}).get('pages', [])
        page_obj = next((p for p in pages_list if p.get('slug') == self.current_page), None)

        if not page_obj:
            return # Page doesn't exist, do nothing

        page_obj['title'] = self.title_var.get().strip()
        page_obj['intro_text'] = self.intro_text.get('1.0', END).strip()
        self._dirty = True

    def _add_video_dialog(self):
        # Ensure a language and page are selected
        if not (self.current_lang and self.current_page):
            return

        # Prompt for video title
        title = simple_input(self.master, 'Video', 'Title:')
        if not title:
            return

        # Prompt for video link
        link = simple_input(self.master, 'Video', 'Link:')
        if not link:
            return

        # Append to videos list and refresh display
        block = self.data[self.current_lang][self.current_page]
        block.setdefault('videos', []).append({
            'title': title,
            'video_link': link
        })
        self._dirty = True
        self._load_page(self.current_lang, self.current_page)
    def _remove_selected_video(self):
        if not(self.current_lang and self.current_page):return
        idxs=list(self.video_list.curselection());blk=self.data[self.current_lang][self.current_page];
        for i in reversed(idxs): blk.get('videos',[]).pop(i)
        self._dirty=True;self._load_page(self.current_lang,self.current_page)
    # Actions
    def _validate_json(self):
        try: json.dumps(self.data);messagebox.showinfo('Valid','JSON valid')
        except Exception as e: messagebox.showerror('Invalid',str(e))


    def _run_wizard(self):
        # Persist current edits before launching the wizard
        self._persist_page()

        # Launch the new GUI-based wizard
        WizardDialog(self.master, self.data, REQUIRED_FIELDS)

        # After wizard closes, mark data as changed, save, and refresh UI
        self._dirty = True
        self._save(silent=True) # Silently save changes made by the wizard
        self._populate_languages()
        self._set_status("Wizard completed. Content updated.")



    def _reload(self):
        if self._dirty and not messagebox.askyesno('Discard?','Unsaved changes lost'):return
        self.data=self._load();self._populate_languages();self._set_status('Reloaded')
    def on_close(self):
        self._persist_page()
        if self._dirty and messagebox.askyesno('Save?','Save changes?'): self._save(silent=True)
        self.master.destroy()

class SimpleDialog(Toplevel):
    def __init__(self, master, title, prompt):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)

        # Prompt label
        Label(self, text=prompt).pack(padx=10, pady=6)

        # Entry field
        self.var = StringVar()
        entry = ttk.Entry(self, textvariable=self.var)
        entry.pack(padx=10, fill=X)
        entry.focus()

        # Buttons
        btn_frame = Frame(self)
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text='OK', command=self._ok).pack(side=LEFT, padx=4)
        ttk.Button(btn_frame, text='Cancel', command=self._cancel).pack(side=LEFT)

        # Bind keys
        self.bind('<Return>', lambda e: self._ok())
        self.bind('<Escape>', lambda e: self._cancel())

        # Modal behavior
        self.result = None
        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _ok(self):
        self.result = self.var.get().strip()
        self.destroy()

    def _cancel(self):
        self.destroy()

def simple_input(master,title,prompt): return SimpleDialog(master,title,prompt).result

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

