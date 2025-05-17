# library-management-system
My second  massai project 
# 📚 Library Management System (LMS) — Python (Single File)

This is a terminal-based Library Management System built using **Python** with **CSV files** as the backend for data persistence. The entire logic resides in a single file: `main.py`. It supports secure registration and login, book and member management, and lending/returning of books.

---

## 🧩 Features

- 🔐 Member Registration with password hashing using `bcrypt`
- 🔑 Secure Login with role distinction (Librarian / Member)
- 📘 Member Features:
  - Search for books
  - View personal loan records
  - Return borrowed books
- 📖 Librarian Features:
  - Add, edit, delete books
  - Issue books to members
  - Accept returned books
  - View all members
  - View all books
  - View all loan records
- 💾 Data storage in simple CSV files — no database required
- 🕒 Due date calculation with 14-day issue period

---

## 📁 Project Structure
-project/
 -│
 -├── finallibrary.py # Main application logic (single file)
 -└── data/ # Folder containing all CSV files
 -├── members.csv # Stores member info with hashed passwords
 -├── books.csv # Stores book catalog and availability
 -└── loans.csv # Stores issued/returned book history
---

##Install Required Package
-Install bcrypt for password hashing:
  -pip install bcrypt

---
##Setup CSV Files (If Not Already Created)
-Create the data/ folder and add the following empty CSV files:

-📄 members.csv
-MemberID,Name,PasswordHash,Email,JoinDate
-📄 books.csv

-ISBN,Title,Author,CopiesTotal,CopiesAvailable
-📄 loans.csv
-LoanID,MemberID,ISBN,IssueDate,DueDate,ReturnDate
