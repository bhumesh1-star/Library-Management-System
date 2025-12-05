# Library Management System

A Python-based CLI tool to manage library book records using JSON storage and CSV export. Built for academic submission and demonstration.

---

## Features

- Add / Update / Delete / Search / List books
- JSON-based persistent storage (`books.json`)
- CSV export (`books_export.csv`)
- GUI using Tkinter (optional `ttkbootstrap` for nicer theme)
- CLI for quick terminal usage
- Demo script and simple run scripts included

---

## How to run
1. Install Python 3.8+.
2. Optional UI dependency for nicer look:
   ```
   pip install ttkbootstrap
   ```
3. Run GUI:
   ```
   python gui.py
   ```
4. Run CLI (if `LMS.py` present):
   ```
   python LMS.py
   ```
5. If `books.json` is in an old/list format, normalize it:
   ```
   python normalize_library.py
   ```
---

## Folder Structure
```
LibraryManagementSystem/
├── LMS.py
├── gui.py                    
├── books.json
├── submission.txt
├── README.md
├── demo_script.txt
├── run.bat
├── run.sh
├── LICENSE
├── .gitignore
├── exports/
│   └── books.csv
├── utils/
│   └── auth.py
└── tests/
    ├── test_book.py
    └── test_system.py
```

---

## Demo Script
See `demo_script.txt` for full walkthrough.

---

## 🎯 Project Goals

- Provide a simple, easy-to-use library management tool  
- Maintain synchronization between GUI and CLI  
- Ensure clean data storage using JSON  
- Allow future expansion such as login system, issuing books, analytics, etc.


## Testing
```
python -m unittest discover tests
```

---

## Submitted By
**Name:** Bhumesh Singh  
**Roll No:** BU2023UGBCA070  

---

## License
MIT License  
