import tkinter as tk
from ldapserver import LDAPServer

def add_user(entries, ldap_server):
    user_data = {}
    for entry in entries:
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

    ldap_server.add_user_to_ldap(user_data)


def create_user_gui():
    root = tk.Tk()
    root.title("Add User to LDAP")

    # Define style for labels and buttons
    label_style = ('Helvetica', 12)
    button_style = ('Helvetica', 12, 'bold')

    # Configure root window background color
    root.configure(bg='#F0F0F0')

    ldap_server = LDAPServer()
    ldap_server.ldap_initialize()

    # Labels and entry fields for user information
    labels = ['Login:', 'First Name:', 'Last Name:', 'Email:', 'Password:']
    entries = []

    for i, label_text in enumerate(labels):
        label = tk.Label(root, text=label_text, font=label_style, bg='#F0F0F0')
        label.grid(row=i, column=0, padx=10, pady=5, sticky='w')
        entry = tk.Entry(root, font=label_style)
        entry.grid(row=i, column=1, padx=10, pady=5, sticky='e')
        entries.append((label_text[:-1].lower(), entry))

    # Button to add user
    add_button = tk.Button(root, text="Add User", command=lambda: add_user(entries, ldap_server),
                           font=button_style, bg='#4CAF50', fg='white')
    add_button.grid(row=len(labels), columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_user_gui()


