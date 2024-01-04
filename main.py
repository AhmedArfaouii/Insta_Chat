import tkinter as tk
from RabbitMQChat import LoginGUI
from tkinter_add_user import TkinterAddUser


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login or Register")
        self.root.configure(bg='#333333')

        # Define button styles
        button_style = ('Helvetica', 16, 'bold')
        bg_color = '#af5b4c'

        # Login button
        self.login_button = tk.Button(
            root,
            text="Login",
            command=self.login,
            font=button_style,
            bg=bg_color,
            fg='white',
            width=20,
            height=2,
        )
        self.login_button.pack(pady=20)

        # Register button
        self.register_button = tk.Button(
            root,
            text="Register",
            command=self.register,
            font=button_style,
            bg=bg_color,
            fg='white',
            width=20,
            height=2,
        )
        self.register_button.pack()

    def login(self):
        chat_root = tk.Tk()
        chat_root.title("Chat Room")
        chat = LoginGUI(chat_root)
        self.root.destroy()
        chat_root.mainloop()

    def register(self):
        register_root = tk.Tk()
        register_root.title("Register User")
        register = TkinterAddUser(register_root)
        self.root.destroy()
        register_root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    main_app = MainApp(root)
    root.mainloop()
