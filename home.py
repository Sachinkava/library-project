from tkinter import *
from tkinter import messagebox
import os

def show_message(message):
    messagebox.showinfo("Information", message)

def add_books():
    import add_book

def manage_borrowers():
    show_message("Manage Borrowers page opened")

def issue_books():
    show_message("Issue Books page opened")

def return_books():
    show_message("Return Books page opened")

# Create the main window
root = Tk()
root.title("Library Management System")
root.geometry("400x300")

# Create a label for the title
title_label = Label(root, text="Library Management System", font=("Arial", 20))
title_label.pack(pady=20)

# Create buttons for different functionalities
btn_add_book = Button(root, text="Add Books", command=add_books, width=20)
btn_add_book.pack(pady=10)

btn_issue_books = Button(root, text="Issued Books", command=issue_books, width=20)
btn_issue_books.pack(pady=10)

btn_return_books = Button(root, text="Return Books", command=return_books, width=20)
btn_return_books.pack(pady=10)

# Start the main event loop
root.mainloop()