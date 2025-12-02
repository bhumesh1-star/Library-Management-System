# utils/auth.py
def login() -> bool:
    """Simple CLI login. Default admin/admin123 style credentials."""
    print("Admin login required.")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    if username == "admin" and password == "1234":
        print("Login successful.")
        return True
    print("Invalid credentials.")
    return False
