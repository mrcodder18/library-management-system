import os
import csv
import bcrypt
from datetime import datetime, timedelta
from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# File paths
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
MEMBERS_CSV = os.path.join(DATA_DIR, "members.csv")
BOOKS_CSV = os.path.join(DATA_DIR, "books.csv")
LOANS_CSV = os.path.join(DATA_DIR, "loans.csv")

# Session management
session = {}

# Data classes
@dataclass
class Member:
    MemberID: str
    Name: str
    PasswordHash: str
    Email: str
    JoinDate: str

@dataclass
class Book:
    ISBN: str
    Title: str
    Author: str
    CopiesTotal: int
    CopiesAvailable: int

@dataclass
class Loan:
    LoanID: str
    MemberID: str
    ISBN: str
    IssueDate: str
    DueDate: str
    ReturnDate: str

# Load/save handlers
def load_members(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r') as file:
        return [Member(**row) for row in csv.DictReader(file)]

def save_members(members, file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=Member.__annotations__.keys())
        writer.writeheader()
        for m in members:
            writer.writerow(m.__dict__)

def load_books(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r') as file:
        return [Book(row['ISBN'], row['Title'], row['Author'], int(row['CopiesTotal']), int(row['CopiesAvailable']))
                for row in csv.DictReader(file)]

def save_books(books, file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=Book.__annotations__.keys())
        writer.writeheader()
        for b in books:
            writer.writerow(b.__dict__)

def load_loans(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r') as file:
        return [Loan(**row) for row in csv.DictReader(file)]

def save_loans(loans, file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=Loan.__annotations__.keys())
        writer.writeheader()
        for l in loans:
            writer.writerow(l.__dict__)

# Logic
def register_member(data):
    members = load_members(MEMBERS_CSV)
    if any(m.MemberID == data["MemberID"] for m in members):
        raise ValueError("MemberID already exists.")
    password_hash = bcrypt.hashpw(data["Password"].encode(), bcrypt.gensalt()).decode()
    data["PasswordHash"] = password_hash
    del data["Password"]
    members.append(Member(**data))
    save_members(members, MEMBERS_CSV)

def login(member_id, password, role):
    members = load_members(MEMBERS_CSV)
    member = next((m for m in members if m.MemberID == member_id), None)
    if member and bcrypt.checkpw(password.encode(), member.PasswordHash.encode()):
        session['user'] = member
        session['role'] = role
        return True
    return False

# GUI
def gui_register():
    win = tk.Toplevel(root)
    win.title("Register")

    fields = ["MemberID", "Name", "Password", "Email"]
    entries = {}
    for i, field in enumerate(fields):
        tk.Label(win, text=field).grid(row=i, column=0)
        entries[field] = tk.Entry(win, show="*" if field == "Password" else "")
        entries[field].grid(row=i, column=1)

    def submit():
        data = {field: entries[field].get() for field in fields}
        data["JoinDate"] = datetime.now().strftime("%Y-%m-%d")
        try:
            register_member(data)
            messagebox.showinfo(" Success", " ✅✅Registration successful!")
            win.destroy()
        except ValueError as ve:
            messagebox.showerror("❌Error", str(ve))

    tk.Button(win, text="Register", command=submit).grid(row=len(fields), columnspan=2)

def gui_login():
    member_id = simpledialog.askstring("Login", "Enter Member ID:")
    password = simpledialog.askstring("Login", "Enter Password:", show="*")
    role = simpledialog.askstring("Login", "✅✅Enter Role (librarian/member):").lower()
    if login(member_id, password, role):
        messagebox.showinfo("Success", f"Welcome {session['user'].Name} ({role})")
        if role == "librarian":
            librarian_menu()
        else:
            member_menu()
    else:
        messagebox.showerror("❌Failed", "Login failed.")

def librarian_menu():
    win = tk.Toplevel(root)
    win.title("Librarian Menu")
    options = [
        ("Add Book", add_book_gui),
        ("Issue Book", issue_book_gui),
        ("Return Book", return_book_gui),
        ("View Members", lambda: view_data_gui(load_members(MEMBERS_CSV))),
        ("View Books", lambda: view_data_gui(load_books(BOOKS_CSV))),
        ("View Loans", lambda: view_data_gui(load_loans(LOANS_CSV)))
    ]
    for i, (label, cmd) in enumerate(options):
        tk.Button(win, text=label, command=cmd).pack(fill='x')

def member_menu():
    win = tk.Toplevel(root)
    win.title("Member Menu")
    tk.Button(win, text="Search Books", command=search_books_gui).pack(fill='x')
    tk.Button(win, text="View My Loans", command=view_my_loans_gui).pack(fill='x')

def add_book_gui():
    win = tk.Toplevel(root)
    win.title("Add Book")
    fields = ["ISBN", "Title", "Author", "CopiesTotal", "CopiesAvailable"]
    entries = {}
    for i, field in enumerate(fields):
        tk.Label(win, text=field).grid(row=i, column=0)
        entries[field] = tk.Entry(win)
        entries[field].grid(row=i, column=1)

    def submit():
        data = {f: entries[f].get() for f in fields}
        data["CopiesTotal"] = int(data["CopiesTotal"])
        data["CopiesAvailable"] = int(data["CopiesAvailable"])
        books = load_books(BOOKS_CSV)
        books.append(Book(**data))
        save_books(books, BOOKS_CSV)
        messagebox.showinfo("Added", "Book added.")
        win.destroy()

    tk.Button(win, text="Add", command=submit).grid(row=len(fields), columnspan=2)

def issue_book_gui():
    isbn = simpledialog.askstring("Issue Book", "Enter ISBN:")
    member_id = simpledialog.askstring("Issue Book", "Enter Member ID:")
    books = load_books(BOOKS_CSV)
    members = load_members(MEMBERS_CSV)
    loans = load_loans(LOANS_CSV)
    book = next((b for b in books if b.ISBN == isbn), None)
    member = next((m for m in members if m.MemberID == member_id), None)
    if book and member and book.CopiesAvailable > 0:
        loan = Loan(str(len(loans) + 1), member_id, isbn,
                    datetime.now().strftime("%Y-%m-%d"),
                    (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                    "")
        loans.append(loan)
        book.CopiesAvailable -= 1
        save_books(books, BOOKS_CSV)
        save_loans(loans, LOANS_CSV)
        messagebox.showinfo("Issued", f"Book '{book.Title}' issued.")
    else:
        messagebox.showerror("Failed", "Book/member not found or unavailable.")

def return_book_gui():
    isbn = simpledialog.askstring("Return Book", "Enter ISBN:")
    member_id = simpledialog.askstring("Return Book", "Enter Member ID:")
    loans = load_loans(LOANS_CSV)
    books = load_books(BOOKS_CSV)
    loan = next((l for l in loans if l.MemberID == member_id and l.ISBN == isbn and not l.ReturnDate), None)
    if loan:
        loan.ReturnDate = datetime.now().strftime("%Y-%m-%d")
        book = next(b for b in books if b.ISBN == isbn)
        book.CopiesAvailable += 1
        save_books(books, BOOKS_CSV)
        save_loans(loans, LOANS_CSV)
        messagebox.showinfo("Returned", f"Book '{book.Title}' returned.")
    else:
        messagebox.showerror("Error", "No such active loan.")

def search_books_gui():
    query = simpledialog.askstring("Search Books", "Enter title or author:").lower()
    results = [b for b in load_books(BOOKS_CSV) if query in b.Title.lower() or query in b.Author.lower()]
    view_data_gui(results)

def view_my_loans_gui():
    member_id = session['user'].MemberID
    loans = [l for l in load_loans(LOANS_CSV) if l.MemberID == member_id]
    view_data_gui(loans)

def view_data_gui(data_list):
    win = tk.Toplevel(root)
    win.title("Data View")
    if not data_list:
        tk.Label(win, text="No data found").pack()
        return
    tree = ttk.Treeview(win, columns=list(data_list[0].__dict__.keys()), show='headings')
    for col in tree["columns"]:
        tree.heading(col, text=col)
    for obj in data_list:
        tree.insert('', 'end', values=list(obj.__dict__.values()))
    tree.pack(fill='both', expand=True)

# Main GUI setup
root = tk.Tk()
root.geometry("400x300")
root.title("📚 Library Management System")
tk.Label(root, text="Welcome to the Library", font=("Arial", 16)).pack(pady=20)
tk.Button(root, text="Register", width=30, command=gui_register).pack(pady=10)
tk.Button(root, text="Login", width=30, command=gui_login).pack(pady=10)
tk.Button(root, text="Exit", width=30, command=root.destroy).pack(pady=10)
root.mainloop()