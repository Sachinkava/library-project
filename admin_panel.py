import mysql.connector
import customtkinter as ctk
from tkinter import messagebox, ttk
from contextlib import contextmanager

# Connect to MySQL
@contextmanager
def db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sk"
    )
    try:
        yield conn
    finally:
        conn.close()

# Check login credentials
def authenticate(username, password):
    with db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin_login WHERE username = %s AND password = %s", (username, password))
        return cursor.fetchone()

# Main Application Class
class LibraryAdminPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("600x400")
        
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(pady=20, fill="both", expand=True)
        
        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username")
        self.username_entry.pack(pady=5, padx=20, fill="x")
        
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=5, padx=20, fill="x")
        
        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login)
        self.login_button.pack(pady=20)

        self.tree_books = None
        self.tree_members = None

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = authenticate(username, password)
        
        if user:
            self.login_frame.pack_forget()
            self.show_admin_panel()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def show_admin_panel(self):
        self.admin_frame = ctk.CTkFrame(self)
        self.admin_frame.pack(pady=20, fill="both", expand=True)
        
        self.add_book_button = ctk.CTkButton(self.admin_frame, text="Add Book", command=self.add_book)
        self.add_book_button.pack(pady=10)

        self.view_books_button = ctk.CTkButton(self.admin_frame, text="View Books", command=self.view_books)
        self.view_books_button.pack(pady=10)

        self.add_member_button = ctk.CTkButton(self.admin_frame, text="Add Member", command=self.add_member)
        self.add_member_button.pack(pady=10)

        self.view_members_button = ctk.CTkButton(self.admin_frame, text="View Members", command=self.view_members)
        self.view_members_button.pack(pady=10)

    def add_book(self):
        form_window = ctk.CTkToplevel(self)
        form_window.title("Add Book")
        form_window.geometry("300x250")

        form_frame = ctk.CTkFrame(form_window)
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        title_entry = ctk.CTkEntry(form_frame, placeholder_text="Book Title")
        title_entry.pack(pady=5)

        author_entry = ctk.CTkEntry(form_frame, placeholder_text="Book Author")
        author_entry.pack(pady=5)

        genre_entry = ctk.CTkEntry(form_frame, placeholder_text="Book Genre")
        genre_entry.pack(pady=5)

        def submit_form():
            title = title_entry.get()
            author = author_entry.get()
            genre = genre_entry.get()

            if title and author and genre:
                try:
                    with db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)", 
                                       (title, author, genre))
                        conn.commit()
                        messagebox.showinfo("Success", "Book added successfully")
                        form_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error: {err}")
            else:
                messagebox.showwarning("Input Error", "Please fill out all fields")

        submit_button = ctk.CTkButton(form_frame, text="Add Book", command=submit_form)
        submit_button.pack(pady=20)

    def view_books(self):
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM books")
            books = cursor.fetchall()
        
        books_window = ctk.CTkToplevel(self)
        books_window.title("Books List")
        books_window.geometry("700x400")

        frame = ctk.CTkFrame(books_window)
        frame.pack(fill="both", expand=True)
        
        self.tree_books = ttk.Treeview(frame, columns=("ID", "Title", "Author", "Genre"), show='headings')
        self.tree_books.heading("ID", text="ID")
        self.tree_books.heading("Title", text="Title")
        self.tree_books.heading("Author", text="Author")
        self.tree_books.heading("Genre", text="Genre")
        
        # Set column widths
        self.tree_books.column("ID", width=50)
        self.tree_books.column("Title", width=200)
        self.tree_books.column("Author", width=150)
        self.tree_books.column("Genre", width=150)

        self.tree_books.pack(side="top", fill="both", expand=True)

        for book in books:
            self.tree_books.insert("", "end", values=(book["id"], book["title"], book["author"], book["genre"]))
        
        delete_button = ctk.CTkButton(books_window, text="Delete Book", command=self.delete_book)
        delete_button.pack(pady=10)

        update_button = ctk.CTkButton(books_window, text="Update Book", command=self.update_book)
        update_button.pack(pady=10)

    def delete_book(self):
        selected_item = self.tree_books.selection()
        if not selected_item:
            messagebox.showwarning("Select a Book", "Please select a book to delete.")
            return

        book_id = self.tree_books.item(selected_item[0], 'values')[0]  # Get the selected book ID
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this book?")
        if confirm:
            try:
                with db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "Book deleted successfully.")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
            self.refresh_books_treeview()

    def update_book(self):
        selected_item = self.tree_books.selection()
        if not selected_item:
            messagebox.showwarning("Select a Book", "Please select a book to update.")
            return

        book_data = self.tree_books.item(selected_item[0], 'values')
        book_id = book_data[0]

        form_window = ctk.CTkToplevel(self)
        form_window.title("Update Book")
        form_window.geometry("300x250")

        form_frame = ctk.CTkFrame(form_window)
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        title_entry = ctk.CTkEntry(form_frame, placeholder_text="Book Title")
        title_entry.pack(pady=5)
        title_entry.insert(0, book_data[1])  # Set initial value

        author_entry = ctk.CTkEntry(form_frame, placeholder_text="Book Author")
        author_entry.pack(pady=5)
        author_entry.insert(0, book_data[2])  # Set initial value

        genre_entry = ctk.CTkEntry(form_frame, placeholder_text="Book Genre")
        genre_entry.pack(pady=5)
        genre_entry.insert(0, book_data[3])  # Set initial value

        def submit_update():
            title = title_entry.get()
            author = author_entry.get()
            genre = genre_entry.get()

            if title and author and genre:
                try:
                    with db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE books SET title = %s, author = %s, genre = %s WHERE id = %s", 
                                    (title, author, genre, book_id))
                        conn.commit()
                        messagebox.showinfo("Success", "Book updated successfully")
                        form_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error: {err}")
                self.refresh_books_treeview()
                    
            else:
                messagebox.showwarning("Input Error", "Please fill out all fields")

        submit_button = ctk.CTkButton(form_frame, text="Update Book", command=submit_update)
        submit_button.pack(pady=20)
        

    def refresh_books_treeview(self):
        if self.tree_books is None:
            return

        for item in self.tree_books.get_children():
            self.tree_books.delete(item)

        try:
            with db_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM books")
                books = cursor.fetchall()

                for book in books:
                    self.tree_books.insert("", "end", values=(book["id"], book["title"], book["author"], book["genre"]))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def add_member(self):
        form_window = ctk.CTkToplevel(self)
        form_window.title("Add Member")
        form_window.geometry("300x350")

        form_frame = ctk.CTkFrame(form_window)
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        first_name_entry = ctk.CTkEntry(form_frame, placeholder_text="First Name")
        first_name_entry.pack(pady=5)

        last_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Last Name")
        last_name_entry.pack(pady=5)

        address_entry = ctk.CTkEntry(form_frame, placeholder_text="Address")
        address_entry.pack(pady=5)

        mobile_no_entry = ctk.CTkEntry(form_frame, placeholder_text="Mobile No")
        mobile_no_entry.pack(pady=5)

        email_entry = ctk.CTkEntry(form_frame, placeholder_text="Email")
        email_entry.pack(pady=5)

        username_entry = ctk.CTkEntry(form_frame, placeholder_text="Username")
        username_entry.pack(pady=5)

        password_entry = ctk.CTkEntry(form_frame, placeholder_text="Password", show="*")
        password_entry.pack(pady=5)

        def submit_form():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            address = address_entry.get()
            mobile_no = mobile_no_entry.get()
            email = email_entry.get()
            username = username_entry.get()
            password = password_entry.get()

            if all([first_name, last_name, address, mobile_no, email, username, password]):
                try:
                    with db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO reg_table (first_name, last_name, address, mobile_no, email, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                                       (first_name, last_name, address, mobile_no, email, username, password))
                        conn.commit()
                        messagebox.showinfo("Success", "Member added successfully")
                        form_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error: {err}")
            else:
                messagebox.showwarning("Input Error", "Please fill out all fields")

        submit_button = ctk.CTkButton(form_frame, text="Add Member", command=submit_form)
        submit_button.pack(pady=20)

    def view_members(self):
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM reg_table")
            members = cursor.fetchall()
        
        members_window = ctk.CTkToplevel(self)
        members_window.title("Members List")
        members_window.geometry("700x400")

        frame = ctk.CTkFrame(members_window)
        frame.pack(fill="both", expand=True)

        # Create Treeview with password field
        self.tree_members = ttk.Treeview(frame, columns=("ID", "First Name", "Last Name", "Address", "Mobile No", "Email", "Username", "Password"), show='headings')
        self.tree_members.heading("ID", text="ID")
        self.tree_members.heading("First Name", text="First Name")
        self.tree_members.heading("Last Name", text="Last Name")
        self.tree_members.heading("Address", text="Address")
        self.tree_members.heading("Mobile No", text="Mobile No")
        self.tree_members.heading("Email", text="Email")
        self.tree_members.heading("Username", text="Username")
        self.tree_members.heading("Password", text="Password")  # Add heading for Password

        # Set column widths
        self.tree_members.column("ID", width=50)
        self.tree_members.column("First Name", width=100)
        self.tree_members.column("Last Name", width=100)
        self.tree_members.column("Address", width=150)
        self.tree_members.column("Mobile No", width=100)
        self.tree_members.column("Email", width=150)
        self.tree_members.column("Username", width=100)
        self.tree_members.column("Password", width=100)  # Set width for Password

        # Create a scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_members.yview)
        self.tree_members.configure(yscroll=scrollbar.set)

        # Pack the Treeview and scrollbar
        self.tree_members.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for member in members:
            self.tree_members.insert("", "end", values=(member["id"], member["first_name"], member["last_name"], member["address"], member["mobile_no"], member["email"], member["username"], member["password"]))
        
        delete_button = ctk.CTkButton(members_window, text="Delete Member", command=self.delete_member)
        delete_button.pack(pady=10)

        update_button = ctk.CTkButton(members_window, text="Update Member", command=self.update_member)
        update_button.pack(pady=10)

    def delete_member(self):
        selected_item = self.tree_members.selection()
        if not selected_item:
            messagebox.showwarning("Select a Member", "Please select a member to delete.")
            return

        member_id = self.tree_members.item(selected_item[0], 'values')[0]  # Get the selected member ID
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this member?")
        if confirm:
            try:
                with db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM reg_table WHERE id = %s", (member_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "Member deleted successfully.")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
            self.refresh_members_treeview()

    def update_member(self):
        selected_item = self.tree_members.selection()
        if not selected_item:
            messagebox.showwarning("Select a Member", "Please select a member to update.")
            return

        member_data = self.tree_members.item(selected_item[0], 'values')
        member_id = member_data[0]

        form_window = ctk.CTkToplevel(self)
        form_window.title("Update Member")
        form_window.geometry("300x350")

        form_frame = ctk.CTkFrame(form_window)
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        first_name_entry = ctk.CTkEntry(form_frame, placeholder_text="First Name")
        first_name_entry.pack(pady=5)
        first_name_entry.insert(0, member_data[1])  # Set initial value

        last_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Last Name")
        last_name_entry.pack(pady=5)
        last_name_entry.insert(0, member_data[2])  # Set initial value

        address_entry = ctk.CTkEntry(form_frame, placeholder_text="Address")
        address_entry.pack(pady=5)
        address_entry.insert(0, member_data[3])  # Set initial value

        mobile_no_entry = ctk.CTkEntry(form_frame, placeholder_text="Mobile No")
        mobile_no_entry.pack(pady=5)
        mobile_no_entry.insert(0, member_data[4])  # Set initial value

        email_entry = ctk.CTkEntry(form_frame, placeholder_text="Email")
        email_entry.pack(pady=5)
        email_entry.insert(0, member_data[5])  # Set initial value

        username_entry = ctk.CTkEntry(form_frame, placeholder_text="Username")
        username_entry.pack(pady=5)
        username_entry.insert(0, member_data[6])  # Set initial value

        password_entry = ctk.CTkEntry(form_frame, placeholder_text="Password", show="*")
        password_entry.pack(pady=5)
        password_entry.insert(0, "") # Set initial value

        def submit_update():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            address = address_entry.get()
            mobile_no = mobile_no_entry.get()
            email = email_entry.get()
            username = username_entry.get()
            password = password_entry.get()

            if all([first_name, last_name, address, mobile_no, email, username, password]):
                try:
                    with db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE reg_table SET first_name = %s, last_name = %s, address = %s, mobile_no = %s, email = %s, username = %s, password = %s WHERE id = %s", 
                                    (first_name, last_name, address, mobile_no, email, username, password, member_id))
                        conn.commit()
                        messagebox.showinfo("Success", "Member updated successfully")
                        form_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error: {err}")
            else:
                messagebox.showwarning("Input Error", "Please fill out all fields")

        submit_button = ctk.CTkButton(form_frame, text="Update Member", command=submit_update)
        submit_button.pack(pady=20)


    def refresh_members_treeview(self):
        if self.tree_members is None:
            return

        for item in self.tree_members.get_children():
            self.tree_members.delete(item)

        try:
            with db_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM reg_table")
                members = cursor.fetchall()

                for member in members:
                    self.tree_members.insert("", "end", values=(member["id"], member["first_name"], member["last_name"], member["address"], member["mobile_no"], member["email"], member["username"]))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

# Run the application
if __name__ == "__main__":
    app = LibraryAdminPanel()
    app.mainloop()
