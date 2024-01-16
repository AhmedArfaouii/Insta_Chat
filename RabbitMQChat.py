import tkinter as tk
from tkinter import messagebox
from RabbitMQAuth import RabbitMQAuth
from MessageSender import MessageSender
from MessageReceiver import MessageReceiver
from datetime import datetime
import threading

class LoginGUI:
    def __init__(self, root):

        self.root = root
        self.root.title("Login")

        self.login_label = tk.Label(root, text="Username:")
        self.login_label.pack()
        self.login_entry = tk.Entry(root)
        self.login_entry.pack()



        self.password_label = tk.Label(root, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(root, text="Login", command=self.authenticate)
        self.login_button.pack()




    def authenticate(self):
        username = self.login_entry.get()
        password = self.password_entry.get()
        auth = RabbitMQAuth(username, password)
        auth.connect_to_rabbitmq()

        if auth.authenticate():
            messagebox.showinfo("Login Successful", "You have successfully logged in.")
            self.chatroom_window = tk.Toplevel(self.root)
            self.chatroom_window.title("Chatroom")
            chatroom_gui = ChatroomGUI(self.chatroom_window, username, password, self.root)  # Pass root window reference
            self.root.withdraw()  # Hide the main app window
        else:
            messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")


class ChatroomGUI:
    def __init__(self, root, username, password, main_window):
        self.root = root
        self.root.title("Chatroom")
        self.username = username
        self.password = password
        self.main_window = main_window  # Reference to the main window

        self.receive_thread = threading.Thread(target=self.background_receive_messages)  # Thread for receiving messages
        self.receive_thread.daemon = True  # Set the thread as a daemon to stop when the main thread stops
        self.receive_thread.start()  # Start the receive thread

        self.chatroom_text = tk.Text(root, height=20, width=50)
        self.chatroom_text.pack()

        self.receive_messages()

        self.recipient_label = tk.Label(root, text="Recipient:")
        self.recipient_label.pack()
        self.recipient_entry = tk.Entry(root)
        self.recipient_entry.pack()

        self.message_label = tk.Label(root, text="Message:")
        self.message_label.pack()
        self.message_entry = tk.Entry(root)
        self.message_entry.pack()

        self.send_button = tk.Button(root, text="Send Message", command=self.send_message)
        self.send_button.pack()

        self.logout_button = tk.Button(root, text="Logout", command=self.logout)
        self.logout_button.pack()

    def background_receive_messages(self):
        # Function to be run in a separate thread for receiving messages
        receiver = MessageReceiver(self.username, self.password)
        receiver.connect_to_rabbitmq()
        private_key = receiver.load_private_key_from_file(f"{self.username}_private.pem")
        
        # Continuously check for new messages in the background
        while True:
            received_message = receiver.receive_and_decrypt_message(self.username, private_key)
            if received_message:
                # Use Tkinter's after method to update the GUI in the main thread
                self.root.after(0, lambda message=received_message: self.update_chatroom(message))

    def receive_messages(self):
        receiver = MessageReceiver(self.username, self.password)
        receiver.connect_to_rabbitmq()
        private_key = receiver.load_private_key_from_file(f"{self.username}_private.pem")
        received_message = receiver.receive_and_decrypt_message(self.username, private_key)
        receiver.close_connection()
        if received_message:
            self.chatroom_text.insert(tk.END, f"{received_message}\n")
        self.root.after(1000, self.receive_messages)  

    def update_chatroom(self, message):
        # Update the chatroom GUI with the received message
        self.chatroom_text.insert(tk.END, f"{message}\n")

    def send_message(self):
        recipient = self.recipient_entry.get()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_content = self.message_entry.get()
        message = f"{current_time} - {self.username}: {message_content}"

        sender = MessageSender(self.username, self.password)
        sender.connect_to_rabbitmq()
        sender.generate_keys_if_not_exist(self.username)
        recipient_public_key = sender.load_public_key_from_file(f"{recipient}_public.pem")
        encrypted_message = sender.encrypt_message(message, recipient_public_key)
        sender.send_encrypted_message(recipient, encrypted_message, recipient)
        sender.close_connection()
        messagebox.showinfo("Message Sent", "Your message has been sent.")

    def logout(self):
        self.main_window.deiconify()  # Re-show the main window
        self.root.destroy()  # Close the chatroom window

if __name__ == "__main__":
    root = tk.Tk()
    login_gui = LoginGUI(root)
    root.mainloop()
