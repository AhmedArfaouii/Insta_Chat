import tkinter as tk
from ldapserver import LDAPServer

class TkinterAddUser:
    def __init__(self, root):
        self.root = root
        self.root.title("Add User to LDAP")

        # Define style for labels and buttons
        label_style = ('Helvetica', 12)
        button_style = ('Helvetica', 12, 'bold')

        # Configure root window background color
        self.root.configure(bg='#F0F0F0')

        self.ldap_server = LDAPServer()
        self.ldap_server.ldap_initialize()

        # Labels and entry fields for user information
        labels = ['Login:', 'First Name:', 'Last Name:', 'Email:', 'Password:']
        self.entries = []

        for i, label_text in enumerate(labels):
            label = tk.Label(self.root, text=label_text, font=label_style, bg='#F0F0F0')
            label.grid(row=i, column=0, padx=10, pady=5, sticky='w')
            entry = tk.Entry(self.root, font=label_style)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky='e')
            self.entries.append((label_text[:-1].lower(), entry))

        # Button to add user
        add_button = tk.Button(self.root, text="Add User", command=self.add_user_to_ldap,
                               font=button_style, bg='#4CAF50', fg='white')
        add_button.grid(row=len(labels), columnspan=2, pady=10)

    def add_user_to_ldap(self):
        user_data = {}
        for entry in self.entries:
            field = entry[0]
            value = entry[1].get()
            user_data[field] = value

        # Ensure the correct keys are used to create the user_data dictionary
        keys = ['login', 'first name', 'last name', 'email', 'password']
        for key in keys:
            if key not in user_data:
                print(f"Missing {key.capitalize()} field.")
                return

        # Rename keys to match LDAP attribute names
        user_data['first_name'] = user_data.pop('first name')
        user_data['last_name'] = user_data.pop('last name')

        self.ldap_server.add_user_to_ldap(user_data)

    def create_user_gui(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    user_adder = TkinterAddUser(root)
    user_adder.create_user_gui()
