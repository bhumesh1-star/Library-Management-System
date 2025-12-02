#!/usr/bin/env python3
"""
Library Management System - CLI
Uses JSON file for storage and provides CSV export.
"""
import json
import csv
import os
from typing import List, Dict, Optional
from utils.auth import login

DATA_FILE = "books.json"
EXPORT_FOLDER = "exports"
EXPORT_FILE = os.path.join(EXPORT_FOLDER, "books.csv")


class Book:
    def __init__(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = int(year)
        self.copies = int(copies)

    def to_dict(self) -> Dict:
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "copies": self.copies,
        }

    @staticmethod
    def from_dict(d: Dict):
        return Book(d["isbn"], d["title"], d["author"], d["year"], d.get("copies", 1))


class LibrarySystem:
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.books: Dict[str, Book] = {}
        self.load()

    def load(self):
        if not os.path.exists(self.data_file):
            self.save()  # create empty file
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                content = f.read()
                data = json.loads(content) if content.strip() else {}
        except json.JSONDecodeError:
            data = {}
        # If data is a list convert to dict keyed by isbn
        if isinstance(data, list):
            data = {b["isbn"]: b for b in data}
        if isinstance(data, dict):
            for isbn, b in data.items():
                self.books[isbn] = Book.from_dict(b)

    def save(self):
        os.makedirs(os.path.dirname(self.data_file) or ".", exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump({isbn: book.to_dict() for isbn, book in self.books.items()}, f, indent=2)

    def add_book(self, book: Book) -> bool:
        if book.isbn in self.books:
            return False
        self.books[book.isbn] = book
        self.save()
        return True

    def update_book(self, isbn: str, **kwargs) -> bool:
        if isbn not in self.books:
            return False
        book = self.books[isbn]
        for k, v in kwargs.items():
            if hasattr(book, k):
                setattr(book, k, int(v) if k in ("year", "copies") else v)
        self.save()
        return True

    def delete_book(self, isbn: str) -> bool:
        if isbn in self.books:
            del self.books[isbn]
            self.save()
            return True
        return False

    def get_book(self, isbn: str) -> Optional[Book]:
        return self.books.get(isbn)

    def search(self, query: str) -> List[Book]:
        q = query.lower()
        results = []
        for book in self.books.values():
            if q in book.title.lower() or q in book.author.lower() or q in book.isbn.lower():
                results.append(book)
        return results

    def list_books(self) -> List[Book]:
        return list(self.books.values())

    def export_to_csv(self, path: str = EXPORT_FILE):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        # use a variable name that doesn't trigger common spell-checkers
        with open(path, "w", newline="", encoding="utf-8") as out_file:
            writer = csv.writer(out_file)
            writer.writerow(["ISBN", "Title", "Author", "Year", "Copies"])
            for b in self.list_books():
                writer.writerow([b.isbn, b.title, b.author, b.year, b.copies])
        return path


def print_table(books: List[Book]):
    if not books:
        print("No books to display.")
        return
    headers = ["ISBN", "Title", "Author", "Year", "Copies"]
    rows = [[b.isbn, b.title, b.author, str(b.year), str(b.copies)] for b in books]
    col_widths = [max(len(row[i]) for row in ([headers] + rows)) for i in range(len(headers))]
    header_line = " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))
    sep = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    print(header_line)
    print(sep)
    for row in rows:
        print(" | ".join(row[i].ljust(col_widths[i]) for i in range(len(row))))


def menu():
    print("\nLibrary Management System")
    print("1. Add book")
    print("2. View book (by ISBN)")
    print("3. Update book")
    print("4. Delete book")
    print("5. Search books")
    print("6. List all books")
    print("7. Export to CSV")
    print("8. Exit")


def main():
    print("Welcome to Library Management System")
   

    system = LibrarySystem()

    while True:
        menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            isbn = input("ISBN: ").strip()
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            year = input("Year of publication: ").strip()
            copies = input("Copies: ").strip() or "1"
            try:
                book = Book(isbn, title, author, int(year), int(copies))
            except ValueError:
                print("Year and copies must be numbers.")
                continue
            if system.add_book(book):
                print("Book added.")
            else:
                print("Book with this ISBN already exists.")
        elif choice == "2":
            isbn = input("Enter ISBN: ").strip()
            b = system.get_book(isbn)
            if b:
                print_table([b])
            else:
                print("Book not found.")
        elif choice == "3":
            isbn = input("ISBN of book to update: ").strip()
            if not system.get_book(isbn):
                print("No such book.")
                continue
            print("Leave blank to keep current value.")
            title = input("New Title: ").strip()
            author = input("New Author: ").strip()
            year = input("New Year: ").strip()
            copies = input("New Copies: ").strip()
            updates = {}
            if title:
                updates["title"] = title
            if author:
                updates["author"] = author
            if year:
                updates["year"] = year
            if copies:
                updates["copies"] = copies
            if system.update_book(isbn, **updates):
                print("Book updated.")
            else:
                print("Update failed.")
        elif choice == "4":
            isbn = input("ISBN to delete: ").strip()
            confirm = input(f"Are you sure you want to delete {isbn}? (y/n): ").strip().lower()
            if confirm == "y":
                if system.delete_book(isbn):
                    print("Deleted.")
                else:
                    print("Book not found.")
        elif choice == "5":
            q = input("Search query (title/author/isbn): ").strip()
            results = system.search(q)
            print_table(results)
        elif choice == "6":
            print_table(system.list_books())
        elif choice == "7":
            path = system.export_to_csv()
            print(f"Exported to: {path}")
        elif choice == "8":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
