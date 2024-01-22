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

        # Use a consistent style
        heading_style = ('Helvetica', 36, 'italic', 'bold')
        label_style = ('Helvetica', 16)
        entry_style = ('Helvetica', 14)
        button_style = ('Helvetica', 14, 'bold')

        # Set the background color for the entire window
        self.root.configure(bg='#000000')

        # Instachat Label
        instachat_label = tk.Label(root, text="Instachat", font=heading_style, fg='green', bg='#000000')
        instachat_label.grid(row=0, column=0, columnspan=2, pady=20)

        self.ldap_server = LDAPServer()
        self.ldap_server.ldap_initialize()

        labels = ['Login:', 'First Name:', 'Last Name:', 'Email:', 'Password:']
        self.entries = []

        for i, label_text in enumerate(labels):
            label = tk.Label(self.root, text=label_text, font=label_style, bg='#000000', fg='white')  # Adjust label color
            label.grid(row=i + 1, column=0, padx=10, pady=5, sticky='e')

            if label_text == 'Password:':
                entry = tk.Entry(self.root, font=entry_style, show='*')
            else:
                entry = tk.Entry(self.root, font=entry_style)

            entry.grid(row=i + 1, column=1, padx=10, pady=5, sticky='w')
            self.entries.append((label_text[:-1].lower(), entry))

        add_button = tk.Button(self.root, text="Add User", command=self.add_user_to_ldap,
                            font=button_style, bg='#4CAF50', fg='white')  # Adjust button color
        add_button.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

        # Center the form elements within the window
        for i in range(len(labels) + 2):
            self.root.grid_columnconfigure(i, weight=1)

        self.center_window()


    def add_user_to_ldap(self):
        user_data = {}
        for entry in self.entries:
            field = entry[0]
            value = entry[1].get()
            user_data[field] = value

        keys = ['login', 'first name', 'last name', 'email', 'password']
        for key in keys:
            if key not in user_data:
                messagebox.showerror("Error", f"Missing {key.capitalize()} field.")
                return

        user_data['first_name'] = user_data.pop('first name')
        user_data['last_name'] = user_data.pop('last name')

        self.ldap_server.add_user_to_ldap(user_data)

        # Authenticate with RabbitMQ using the new user's credentials
        username = user_data['login']
        password = user_data['password']
        rabbitmq_auth = RabbitMQAuth(username, password)
        rabbitmq_auth.connect_to_rabbitmq()

        # Check if authentication is successful, create a queue, generate keys, and close connection
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

    def center_window(self):
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate x and y coordinates for the window to be centered
        x = (screen_width / 2) - (600 / 2)
        y = (screen_height / 2) - (600 / 2)

        self.root.geometry(f"600x600+{int(x)}+{int(y)}")

if __name__ == "__main__":
    root = tk.Tk()
    user_adder = TkinterAddUser(root, callback=None)
    root.mainloop()
