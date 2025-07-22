#!/usr/bin/env python3
"""Utility to manage a large multilingual content.json file.

Core commands:
  validate              Validate JSON structure
  format                Pretty-print + sort keys (writes backup)
  list                  List languages and pages
  ensure                Ensure a page skeleton exists
  edit                  Set a field value (auto-parses JSON fragments)
  delete                Remove a page
  split                 Split top-level languages into <outdir>/<lang>.json
  merge                 Merge per-language JSON files back into one
  export-sql            Print SQL INSERT statements for a page (or all)
  shell                 Interactive prompt (type commands without python relaunch)
  wizard                Guided CLI wizard to fill missing content

Examples:
  python content_tool.py list content.json
  python content_tool.py ensure content.json --lang en --page solar_cooker
  python content_tool.py edit content.json --lang en --page solar_cooker --field title --value "Solar Cooker Basics"
  python content_tool.py delete content.json --lang sp --page solar_oven
  python content_tool.py export-sql content.json --lang en --page solar_cooker > seed.sql
  python content_tool.py wizard content.json
  python content_tool.py shell content.json
"""
from __future__ import annotations
import argparse, json, sys, shutil, difflib, shlex
from pathlib import Path

# Required keys inside each page block
REQUIRED_PAGE_KEYS = ["title", "intro_text"]

# Default skeleton for new pages
DEFAULT_PAGE_BLOCK = {
    "title": "<Title>",
    "intro_text": "<Intro text>",
    "videos": [],  # generic list – can rename per template later
    "books": {},
}

# ---------------- Utility helpers ---------------- #

def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON parse error at line {e.lineno}, column {e.colno}: {e.msg}", file=sys.stderr)
        raise SystemExit(1)


def save_json(path: Path, data: dict, backup: bool = True):
    if backup and path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    path.write_text(text + "\n", encoding="utf-8")
    print(f"✅ Wrote {path} (backup: {path.with_suffix(path.suffix + '.bak').name if backup else 'none'})")


def validate(data: dict) -> bool:
    if not isinstance(data, dict):
        print("Top-level JSON must be an object.", file=sys.stderr)
        return False
    ok = True
    for lang, block in data.items():
        if not isinstance(block, dict):
            print(f"Language '{lang}' is not an object.", file=sys.stderr)
            ok = False
    return ok


def autodetect_langs(data: dict) -> list[str]:
    return [k for k, v in data.items() if isinstance(v, dict)]

# ---------------- Schema / Page ops ---------------- #


# (Find this function in your file)
def ensure_page(data, lang, page):
    """Ensures a page exists and is a dictionary with required fields."""
    lang_block = data.setdefault(lang, {})
    
    # --- START of the fix ---
    # If the page exists but is a string (or anything other than a dict),
    # convert it into a proper dictionary.
    page_content = lang_block.get(page)
    if not isinstance(page_content, dict):
        # Preserve the old string value as the title, if possible.
        title_val = str(page_content) if page_content is not None else f"<{page}>"
        lang_block[page] = {"title": title_val}
    # --- END of the fix ---

    # Now we can safely assume lang_block[page] is a dictionary
    for k in REQUIRED_FIELDS:
        lang_block[page].setdefault(k, f"<{k}>")

def delete_page(data: dict, lang: str, page: str):
    if lang not in data or page not in data[lang]:
        print(f"⚠ Page {lang}.{page} not found")
        return
    del data[lang][page]
    if not data[lang]:
        print(f"ℹ Removing empty language container '{lang}'")
        del data[lang]
    print(f"🗑 Deleted {lang}.{page}")


def edit_field(data: dict, lang: str, page: str, field: str, value: str):
    ensure_page(data, lang, page)
    block = data[lang][page]
    # Try JSON parse if value starts with object/array
    if value.strip().startswith(('{', '[')):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
    old = block.get(field)
    block[field] = value
    print(f"✏️  Set {lang}.{page}.{field}: {old!r} -> {value!r}")

# ---------------- Split & Merge ---------------- #

def split_file(data: dict, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    for lang, block in data.items():
        p = outdir / f"{lang}.json"
        save_json(p, block, backup=False)
    print(f"📁 Split into {outdir}/<lang>.json")


def merge_dir(indir: Path) -> dict:
    result = {}
    for file in indir.glob("*.json"):
        result[file.stem] = load_json(file)
    return result

# ---------------- Diff ---------------- #

def show_diff(original: dict, updated: dict):
    o = json.dumps(original, ensure_ascii=False, indent=2, sort_keys=True).splitlines(keepends=True)
    u = json.dumps(updated, ensure_ascii=False, indent=2, sort_keys=True).splitlines(keepends=True)
    for line in difflib.unified_diff(o, u, fromfile="original", tofile="updated"):
        sys.stdout.write(line)

# ---------------- SQL Export ---------------- #

def export_sql(data: dict, lang: str | None, page: str | None):
    # flatten into simple INSERTs (id sequencing left to database serials)
    stmts = []
    langs = autodetect_langs(data)
    targets = [(lang, page)] if lang and page else [
        (L, P) for L in langs for P in data[L].keys()
    ]
    # language table
    for L in langs:
        stmts.append(f"INSERT INTO languages(code,name) VALUES('{L}','{L}') ON CONFLICT DO NOTHING;")
    for L, P in targets:
        block = data[L][P]
        # basic page fields
        title = json.dumps(block.get('title'))
        intro = json.dumps(block.get('intro_text'))
        hero_image = json.dumps(block.get('hero_image'))
        stmt = ("WITH lang AS (SELECT id FROM languages WHERE code='{L}') "
                "INSERT INTO pages(language_id,slug,title,intro,hero_image) "
                "SELECT id,'{slug}',{title},{intro},{hero} FROM lang "
                "ON CONFLICT DO NOTHING;").format(L=L, slug=P, title=title, intro=intro, hero=hero_image)
        stmts.append(stmt)
        # books
        books = block.get('books') or {}
        for bkey, bobj in books.items():
            btitle = json.dumps(bobj.get('title', bkey))
            stmts.append(
                "WITH p AS (SELECT id FROM pages JOIN languages ON pages.language_id=languages.id "
                f"WHERE code='{L}' AND slug='{P}') INSERT INTO books(page_id,key,title) "
                f"SELECT id,'{bkey}',{btitle} FROM p ON CONFLICT DO NOTHING;"
            )
            slides = bobj.get('slides') or []
            for idx, slide in enumerate(slides, start=1):
                stitle = json.dumps(slide.get('title') or slide.get('slide_title'))
                content = json.dumps(slide.get('content',''))
                stmts.append(
                    "WITH b AS (SELECT books.id FROM books JOIN pages ON books.page_id=pages.id JOIN languages l ON pages.language_id=l.id "
                    f"WHERE l.code='{L}' AND pages.slug='{P}' AND books.key='{bkey}') "
                    "INSERT INTO book_slides(book_id,position,slide_title,content) "
                    f"SELECT id,{idx},{stitle},{content} FROM b;"
                )
    return "\n".join(stmts) + "\n"

# ---------------- Interactive Shell ---------------- #

def repl(path: Path, data: dict):
    print("Entering interactive shell. Type 'help' or 'quit'.")
    while True:
        try:
            line = input("json> ").strip()
        except (EOFError, KeyboardInterrupt):
            print() ; break
        if not line:
            continue
        if line in {"quit", "exit"}:
            break
        if line == "help":
            print("Commands: list | ensure <lang> <page> | edit <lang> <page> <field> <value> | delete <lang> <page> | save | diff | quit")
            continue
        if line == "list":
            list_pages(data)
            continue
        if line == "save":
            save_json(path, data)
            continue
        if line == "diff":
            print("(Diff vs file on disk)")
            disk = load_json(path)
            show_diff(disk, data)
            continue
        try:
            parts = shlex.split(line)
        except ValueError as e:
            print(f"Parse error: {e}")
            continue
        if parts and parts[0] == "ensure" and len(parts) == 3:
            ensure_page(data, parts[1], parts[2])
            continue
        if parts and parts[0] == "edit" and len(parts) >= 5:
            lang, page, field = parts[1:4]
            value = " ".join(parts[4:])
            edit_field(data, lang, page, field, value)
            continue
        if parts and parts[0] == "delete" and len(parts) == 3:
            delete_page(data, parts[1], parts[2])
            continue
        print("Unknown command. Type 'help'.")
    # Autosave prompt
    ans = input("Save changes? [y/N] ").lower().strip()
    if ans == 'y':
        save_json(path, data)

# ---------------- Wizard ---------------- #

def wizard(path: Path, data: dict):
    """Guided prompt to fill missing languages/pages/fields.

    Flow:
      1. Show existing languages.
      2. Offer to add a new language.
      3. For each language: list existing pages, allow adding pages.
      4. For each page: prompt for required fields if placeholder values.
      5. Optional: add simple videos list.
    """
    print("🔮 Wizard starting. Press Enter to accept defaults or type new values.")

    # Add new language?
    while True:
        print("Existing languages:", ", ".join(autodetect_langs(data)) or "(none)")
        ans = input("Add a new language code? (leave blank to continue) ").strip()
        if not ans:
            break
        if ans in data:
            print("Language already exists.")
        else:
            data[ans] = {}
            print(f"Added language '{ans}'.")

    # Iterate languages
    for lang in autodetect_langs(data):
        print(f"\n=== Language: {lang} ===")
        while True:
            pages = sorted(data[lang].keys())
            print("Current pages:", ", ".join(pages) or "(none)")
            addp = input("Add a new page slug? (blank to stop adding) ").strip()
            if not addp:
                break
            ensure_page(data, lang, addp)

        # Fill fields
        for page, block in data[lang].items():
            print(f"\n-- Page: {page} --")
            ensure_page(data, lang, page)
            # Required fields
            for field in REQUIRED_PAGE_KEYS:
                cur = block.get(field)
                if cur and not str(cur).startswith("<"):
                    # allow edit
                    newv = input(f"{field} [{cur}]: ").strip()
                    if newv:
                        block[field] = newv
                else:
                    newv = input(f"{field} (currently missing) > ").strip()
                    if newv:
                        block[field] = newv
            # Optional videos
            if not block.get("videos"):
                add_vid = input("Add a video? y/N ").lower().startswith('y')
                vids = []
                while add_vid:
                    vt = input("  Video title: ").strip()
                    vl = input("  Video link: ").strip()
                    if vt and vl:
                        vids.append({"title": vt, "video_link": vl})
                    more = input("Add another video? y/N ").lower().startswith('y')
                    if not more:
                        break
                if vids:
                    block["videos"] = vids
            # Books minimal
            if not block.get("books") and input("Add a simple book with slides? y/N ").lower().startswith('y'):
                book_key = input("  Book key (e.g. history): ").strip() or "history"
                book_title = input("  Book title: ").strip() or book_key.title()
                slides = []
                while True:
                    st = input("    Slide title (blank to finish): ").strip()
                    if not st:
                        break
                    sc = input("    Slide HTML/content: ").strip() or "<p>...</p>"
                    slides.append({"title": st, "content": sc})
                block["books"] = {book_key: {"title": book_title, "slides": slides}}

    save_json(path, data)
    print("🎉 Wizard complete.")

# ---------------- Listing ---------------- #

def list_pages(data: dict):
    langs = autodetect_langs(data)
    if not langs:
        print("(no languages)")
        return
    for lang in langs:
        pages = sorted(data[lang].keys())
        print(f"🌐 {lang}: {', '.join(pages) if pages else '(empty)'}")

# ---------------- CLI ---------------- #

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Manage multilingual content.json")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # simple commands
    for cmd in ("validate", "format", "list"):
        sc = sub.add_parser(cmd)
        sc.add_argument("file")

    psplit = sub.add_parser("split")
    psplit.add_argument("file")
    psplit.add_argument("outdir")

    pmerge = sub.add_parser("merge")
    pmerge.add_argument("indir")
    pmerge.add_argument("outfile")

    pensure = sub.add_parser("ensure")
    pensure.add_argument("file")
    pensure.add_argument("--lang", required=True)
    pensure.add_argument("--page", required=True)

    pedit = sub.add_parser("edit")
    pedit.add_argument("file")
    pedit.add_argument("--lang", required=True)
    pedit.add_argument("--page", required=True)
    pedit.add_argument("--field", required=True)
    pedit.add_argument("--value", required=True)

    pdel = sub.add_parser("delete")
    pdel.add_argument("file")
    pdel.add_argument("--lang", required=True)
    pdel.add_argument("--page", required=True)

    pexp = sub.add_parser("export-sql")
    pexp.add_argument("file")
    pexp.add_argument("--lang")
    pexp.add_argument("--page")

    pshell = sub.add_parser("shell")
    pshell.add_argument("file")

    pwizard = sub.add_parser("wizard")
    pwizard.add_argument("file")

    return ap


def main():
    ap = build_parser()
    args = ap.parse_args()

    if args.cmd == "merge":
        data = merge_dir(Path(args.indir))
        save_json(Path(args.outfile), data)
        return

    path = Path(getattr(args, "file"))
    data = load_json(path)

    if args.cmd == "validate":
        print("✅ Valid" if validate(data) else "❌ Invalid")
    elif args.cmd == "format":
        if validate(data):
            save_json(path, data)
    elif args.cmd == "list":
        list_pages(data)
    elif args.cmd == "split":
        split_file(data, Path(args.outdir))
    elif args.cmd == "ensure":
        ensure_page(data, args.lang, args.page)
        save_json(path, data)
    elif args.cmd == "edit":
        before = json.loads(json.dumps(data))
        edit_field(data, args.lang, args.page, args.field, args.value)
        show_diff(before, data)
        save_json(path, data)
    elif args.cmd == "delete":
        before = json.loads(json.dumps(data))
        delete_page(data, args.lang, args.page)
        show_diff(before, data)
        save_json(path, data)
    elif args.cmd == "export-sql":
        sql = export_sql(data, args.lang, args.page)
        sys.stdout.write(sql)
    elif args.cmd == "shell":
        repl(path, data)
    elif args.cmd == "wizard":
        wizard(path, data)
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
