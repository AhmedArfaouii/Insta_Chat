import tkinter as tk
from tkinter import messagebox
from ldapserver import LDAPServer
from RabbitMQAuth import RabbitMQAuth
from MessageSender import MessageSender

class TkinterAddUser:
    def __init__(self, root, callback):
        self.root = root
        self.root.title("Add User to LDAP")
        self.callback = callback

        label_style = ('Helvetica', 12)
        button_style = ('Helvetica', 12, 'bold')

        self.root.configure(bg='black')  # Change background color

        self.ldap_server = LDAPServer()
        self.ldap_server.ldap_initialize()

        labels = ['Login:', 'First Name:', 'Last Name:', 'Email:', 'Password:']
        self.entries = []

        for i, label_text in enumerate(labels):
            label = tk.Label(self.root, text=label_text, font=label_style, bg='black', fg='white')  # Set label colors
            label.grid(row=i, column=0, padx=10, pady=5, sticky='w')
            entry = tk.Entry(self.root, font=label_style)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky='e')
            self.entries.append((label_text[:-1].lower(), entry))

        add_button = tk.Button(self.root, text="Add User", command=self.add_user_to_ldap,
                               font=button_style, bg='green', fg='white')  # Change button colors
        add_button.grid(row=len(labels), columnspan=2, pady=10)

    def add_user_to_ldap(self):
        user_data = {}
        for entry in self.entries:
            field = entry[0]
            value = entry[1].get()
            user_data[field] = value

        keys = ['login', 'first name', 'last name', 'email', 'password']
        for key in keys:
            if key not in user_data:
                print(f"Missing {key.capitalize()} field.")
                return

        user_data['first_name'] = user_data.pop('first name')
        user_data['last_name'] = user_data.pop('last name')

        self.ldap_server.add_user_to_ldap(user_data)

        # Authenticate with RabbitMQ using the new user's credentials
        username = user_data['login']
        password = user_data['password']
        rabbitmq_auth = RabbitMQAuth(username, password)
        rabbitmq_auth.connect_to_rabbitmq()

        # Check if authentication is successful, create queue, generate keys, and close connection
        if rabbitmq_auth.authenticate():
            channel = rabbitmq_auth.channel
            channel.queue_declare(queue=username)

            sender = MessageSender(username, password)
            sender.connect_to_rabbitmq()
            sender.generate_keys_if_not_exist(username)
            sender.close_connection()

            messagebox.showinfo("Success", "User added successfully.")
            self.root.destroy()
            if self.callback:
                self.callback()
        else:
            messagebox.showerror("Error", "Failed to authenticate user with RabbitMQ.")
            rabbitmq_auth.connection.close()
            
    def center_elements(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)

        self.root.geometry(f"600x600+{x}+{y}")


    def create_user_gui(self):
        self.root.mainloop()

  

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='black')  # Set main window background color
    user_adder = TkinterAddUser(root)
    user_adder.create_user_gui()


