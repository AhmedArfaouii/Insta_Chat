import tkinter as tk
from tkinter_add_user import TkinterAddUser
from RabbitMQChat import LoginGUI

#Adding threading
#Adding active-users
#Chatroom UI fixes


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login or Register")
        self.root.configure(bg='black')
        self.root.geometry("600x600")


        # Center the window
        self.center_window()

        # Define button styles
        button_style = ('Helvetica', 16, 'bold')
        bg_color = 'green'
        hover_color = '#af5b4c'

        # Welcome Label
        welcome_label = tk.Label(
            root,
            text="Instachat",
            font=('Helvetica', 36, 'italic', 'bold'),
            fg='green',
            bg='black'
        )
        welcome_label.pack(pady=50)

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
        self.login_button.bind('<Enter>', lambda event: self.on_enter(event, hover_color, 'Login'))
        self.login_button.bind('<Leave>', lambda event: self.on_leave(event, bg_color, 'Login'))

        # Register button
        self.register_button = tk.Button(
            root,
            text="Join Us",
            command=self.register,
            font=button_style,
            bg=bg_color,
            fg='white',
            width=20,
            height=2,
        )
        self.register_button.pack()
        self.register_button.bind('<Enter>', lambda event: self.on_enter(event, hover_color, 'Join Us'))
        self.register_button.bind('<Leave>', lambda event: self.on_leave(event, bg_color, 'Join Us'))

    def on_enter(self, event, bg_color, text):
        event.widget.config(bg=bg_color, fg='white')
        event.widget["text"] = text

    def on_leave(self, event, bg_color, text):
        event.widget.config(bg=bg_color, fg='white')
        event.widget["text"] = text

    def login(self):
        chat_root = tk.Toplevel()  # Use Toplevel instead of Tk
        chat_root.title("Chat Room")
        chat = LoginGUI(chat_root)
        self.root.withdraw()  # Hide the main app window

    def register(self):
        def on_successful_registration():
            self.root.deiconify()  # Show the main app window

        register_root = tk.Toplevel()  # Use Toplevel instead of Tk
        register_root.title("Register User")
        register = TkinterAddUser(register_root, on_successful_registration)
        self.root.withdraw()  # Hide the main app window

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
    main_app = MainApp(root)
    root.mainloop()
