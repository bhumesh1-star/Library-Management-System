
import json
from pathlib import Path
import csv
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

BOOKS_FILE = Path("books.json")   # same filename used in your LMS.py. See your CLI: :contentReference[oaicite:3]{index=3} and data example: :contentReference[oaicite:4]{index=4}
REQUIRED_KEYS = ["isbn", "title", "author", "year", "copies"]

# Optional nicer styling
USE_TTB = False
try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    USE_TTB = True
except Exception:
    ttkb = ttk  # fallback

def read_books_as_dict():
    """
    Read BOOKS_FILE and return a dict mapping isbn -> book_dict.
    Accepts both dict (isbn -> book) format and list[book] format.
    """
    if not BOOKS_FILE.exists():
        BOOKS_FILE.write_text("{}", encoding="utf-8")
        return {}

    try:
        raw = json.loads(BOOKS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        # corrupted file: backup and recreate empty
        try:
            BOOKS_FILE.rename(BOOKS_FILE.with_suffix(".backup.json"))
        except Exception:
            pass
        BOOKS_FILE.write_text("{}", encoding="utf-8")
        return {}

    # If it's a dict keyed by ISBN (preferred), ensure values are dicts
    if isinstance(raw, dict):
        books = {}
        for k, v in raw.items():
            # if v is not a dict (unexpected), skip
            if not isinstance(v, dict):
                continue
            books[str(k)] = {rk: v.get(rk, "") for rk in REQUIRED_KEYS}
        return books

    # If it's a list of book dicts, convert to dict keyed by isbn
    if isinstance(raw, list):
        books = {}
        for item in raw:
            if not isinstance(item, dict):
                continue
            isbn = str(item.get("isbn", "")).strip()
            if not isbn:
                continue
            books[isbn] = {rk: item.get(rk, "") for rk in REQUIRED_KEYS}
        return books

    # otherwise, unknown format -> empty
    return {}

def save_books_from_dict(books_dict):
    """
    Save as dict keyed by ISBN to BOOKS_FILE (matching LMS.py behavior).
    """
    # ensure keys exist and values are simple types
    out = {}
    for isbn, b in books_dict.items():
        rec = {}
        for k in REQUIRED_KEYS:
            rec[k] = "" if b.get(k) is None else str(b.get(k))
        out[str(isbn)] = rec
    BOOKS_FILE.write_text(json.dumps(out, indent=4), encoding="utf-8")

def books_dict_to_list(books_dict):
    """Return a list of book dicts for table display."""
    return [books_dict[k] for k in books_dict]

# ---------- GUI application ----------
class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management - GUI (books.json)")
        self.root.geometry("980x620")

        # style
        if USE_TTB:
            self.style = ttkb.Style(theme="flatly")
            Frame = ttkb.Frame
            Label = ttkb.Label
            Button = ttkb.Button
            Entry = ttkb.Entry
            Treeview = ttkb.Treeview
        else:
            self.style = ttk.Style()
            Frame = ttk.Frame
            Label = ttk.Label
            Button = ttk.Button
            Entry = ttk.Entry
            Treeview = ttk.Treeview

        # sidebar
        sidebar = Frame(root, width=200)
        sidebar.pack(side="left", fill="y", padx=6, pady=6)
        Label(sidebar, text="MENU", font=("Arial", 14, "bold")).pack(pady=8)
        Button(sidebar, text="Add Book", width=18, command=self.add_page).pack(pady=6)
        Button(sidebar, text="Search", width=18, command=self.search_page).pack(pady=6)
        Button(sidebar, text="View All", width=18, command=self.view_page).pack(pady=6)
        Button(sidebar, text="Update", width=18, command=self.update_page).pack(pady=6)
        Button(sidebar, text="Delete", width=18, command=self.delete_page).pack(pady=6)
        Button(sidebar, text="Export CSV", width=18, command=self.export_csv).pack(pady=10)

        # main content
        self.content = Frame(root)
        self.content.pack(side="right", expand=True, fill="both", padx=6, pady=6)

        # prepare table placeholder
        self.table_frame = None
        self.tree = None

        self.view_page()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ---------- Add ----------
    def add_page(self):
        self.clear_content()
        ttkb.Label(self.content, text="Add Book", font=("Arial",16,"bold")).pack(pady=8) if USE_TTB else ttk.Label(self.content, text="Add Book", font=("Arial",16,"bold")).pack(pady=8)
        frm = ttk.Frame(self.content)
        frm.pack(anchor="w", pady=6)

        labels = ["ISBN","Title","Author","Year","Copies"]
        self.add_entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(frm, text=lab, width=12).grid(row=i, column=0, padx=6, pady=6, sticky="w")
            e = ttk.Entry(frm, width=56)
            e.grid(row=i, column=1, pady=6, sticky="w")
            self.add_entries[lab] = e

        ttk.Button(self.content, text="Add", command=self.gui_add).pack(pady=8, anchor="w")

    def gui_add(self):
        data = read_books_as_dict()
        isbn = self.add_entries["ISBN"].get().strip()
        if not isbn:
            messagebox.showerror("Input Error", "ISBN required")
            return
        if isbn in data:
            messagebox.showerror("Error", "ISBN already exists")
            return
        rec = {k.lower(): self.add_entries[k].get().strip() for k in self.add_entries}
        # ensure required keys
        for k in REQUIRED_KEYS:
            rec.setdefault(k, "")
        data[isbn] = rec
        save_books_from_dict(data)
        messagebox.showinfo("Success", "Book added")
        self.view_page()

    # ---------- Search ----------
    def search_page(self):
        self.clear_content()
        ttk.Label(self.content, text="Search Books", font=("Arial",16,"bold")).pack(pady=8) if USE_TTB else ttk.Label(self.content, text="Search Books", font=("Arial",16,"bold")).pack(pady=8)
        frm = ttk.Frame(self.content); frm.pack(anchor="w", pady=6)
        ttk.Label(frm, text="Keyword:", width=12).grid(row=0, column=0)
        self.search_ent = ttk.Entry(frm, width=44); self.search_ent.grid(row=0, column=1)
        ttk.Button(self.content, text="Search", command=self.gui_search).pack(pady=6, anchor="w")
        self.table_frame = ttk.Frame(self.content); self.table_frame.pack(fill="both", expand=True, pady=6)
        self.create_table()
        self.update_table([])

    def gui_search(self):
        q = self.search_ent.get().strip().lower()
        if not q:
            result = list(read_books_as_dict().values())
        else:
            result = []
            for b in read_books_as_dict().values():
                if q in str(b.get("isbn","")).lower() or q in str(b.get("title","")).lower() or q in str(b.get("author","")).lower():
                    result.append(b)
        self.update_table(result)

    # ---------- View All ----------
    def view_page(self):
        self.clear_content()
        ttk.Label(self.content, text="All Books", font=("Arial",16,"bold")).pack(pady=8) if USE_TTB else ttk.Label(self.content, text="All Books", font=("Arial",16,"bold")).pack(pady=8)
        self.table_frame = ttk.Frame(self.content); self.table_frame.pack(fill="both", expand=True, pady=6)
        self.create_table()
        self.update_table(list(read_books_as_dict().values()))

    # ---------- Update ----------
    def update_page(self):
        self.clear_content()
        ttk.Label(self.content, text="Update Book (by ISBN)", font=("Arial",14,"bold")).pack(pady=8) if USE_TTB else ttk.Label(self.content, text="Update Book (by ISBN)", font=("Arial",14,"bold")).pack(pady=8)
        frm = ttk.Frame(self.content); frm.pack(anchor="w", pady=6)
        ttk.Label(frm, text="ISBN to modify:", width=16).grid(row=0, column=0)
        self.up_isbn = ttk.Entry(frm, width=44); self.up_isbn.grid(row=0, column=1, pady=6)
        labels = ["New Title","New Author","New Year","New Copies"]
        self.update_entries = {}
        for i, lab in enumerate(labels, start=1):
            ttk.Label(frm, text=lab, width=16).grid(row=i, column=0)
            ent = ttk.Entry(frm, width=48); ent.grid(row=i, column=1, pady=4)
            self.update_entries[lab] = ent
        ttk.Button(self.content, text="Apply Update", command=self.gui_update).pack(pady=8, anchor="w")

    def gui_update(self):
        isbn = self.up_isbn.get().strip()
        if not isbn:
            messagebox.showerror("Input Error", "ISBN required to identify record")
            return
        data = read_books_as_dict()
        if isbn not in data:
            messagebox.showerror("Not found", "ISBN not present")
            return
        b = data[isbn]
        nt = self.update_entries["New Title"].get().strip()
        na = self.update_entries["New Author"].get().strip()
        ny = self.update_entries["New Year"].get().strip()
        nc = self.update_entries["New Copies"].get().strip()
        if nt: b["title"] = nt
        if na: b["author"] = na
        if ny: b["year"] = ny
        if nc: b["copies"] = nc
        data[isbn] = b
        save_books_from_dict(data)
        messagebox.showinfo("Success", "Book updated")
        self.view_page()

    # ---------- Delete ----------
    def delete_page(self):
        self.clear_content()
        ttk.Label(self.content, text="Delete Book", font=("Arial",14,"bold")).pack(pady=8) if USE_TTB else ttk.Label(self.content, text="Delete Book", font=("Arial",14,"bold")).pack(pady=8)
        frm = ttk.Frame(self.content); frm.pack(anchor="w", pady=6)
        ttk.Label(frm, text="ISBN to delete:", width=16).grid(row=0, column=0)
        self.del_isbn = ttk.Entry(frm, width=44); self.del_isbn.grid(row=0, column=1, pady=6)
        ttk.Button(self.content, text="Delete", command=self.gui_delete).pack(pady=8, anchor="w")

    def gui_delete(self):
        isbn = self.del_isbn.get().strip()
        if not isbn:
            messagebox.showerror("Input Error", "ISBN required")
            return
        data = read_books_as_dict()
        if isbn not in data:
            messagebox.showerror("Not found", "ISBN not present")
            return
        if not messagebox.askyesno("Confirm", f"Delete '{data[isbn].get('title','')}'?"):
            return
        del data[isbn]
        save_books_from_dict(data)
        messagebox.showinfo("Deleted", "Book deleted")
        self.view_page()

    # ---------- Export CSV ----------
    def export_csv(self):
        data = read_books_as_dict()
        if not data:
            messagebox.showinfo("Export CSV", "No data to export.")
            return
        csv_path = "books_export.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(REQUIRED_KEYS)
            for isbn, b in data.items():
                writer.writerow([b.get(k,"") for k in REQUIRED_KEYS])
        messagebox.showinfo("Export CSV", f"Exported to {csv_path}")

    # ---------- Table helpers ----------
    def create_table(self):
        try:
            self.tree.destroy()
        except Exception:
            pass
        cols = ("isbn","title","author","year","copies")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=180 if c=="title" else 100, anchor="w")
        self.tree.pack(fill="both", expand=True)

    def update_table(self, rows):
        # clear
        for r in self.tree.get_children():
            self.tree.delete(r)
        for b in rows:
            self.tree.insert("", "end", values=(b.get("isbn",""), b.get("title",""), b.get("author",""), b.get("year",""), b.get("copies","")))

# ---------- run ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()
