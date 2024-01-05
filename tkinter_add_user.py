import tkinter as tk
from tkinter import messagebox
from ldapserver import LDAPServer
from MessageSender import MessageSender


class TkinterAddUser:
    def __init__(self, root, callback):
        self.root = root
        self.root.title("Add User to LDAP")
        self.callback = callback

        label_style = ('Helvetica', 12)
        button_style = ('Helvetica', 12, 'bold')

        self.root.configure(bg='#F0F0F0')

        self.ldap_server = LDAPServer()
        self.ldap_server.ldap_initialize()

        labels = ['Login:', 'First Name:', 'Last Name:', 'Email:', 'Password:']
        self.entries = []

        for i, label_text in enumerate(labels):
            label = tk.Label(self.root, text=label_text, font=label_style, bg='#F0F0F0')
            label.grid(row=i, column=0, padx=10, pady=5, sticky='w')
            entry = tk.Entry(self.root, font=label_style)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky='e')
            self.entries.append((label_text[:-1].lower(), entry))

        add_button = tk.Button(self.root, text="Add User", command=self.add_user_to_ldap,
                               font=button_style, bg='#4CAF50', fg='white')
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

        # Generate private and public keys
        username = user_data['login']
        password = user_data['password']
        sender = MessageSender(username, password)
        sender.connect_to_rabbitmq()
        sender.generate_keys_if_not_exist(username)
        sender.close_connection()

        messagebox.showinfo("Success", "User added successfully.")
        self.root.destroy()
        if self.callback:
            self.callback()

    def create_user_gui(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    user_adder = TkinterAddUser(root)
    user_adder.create_user_gui()
