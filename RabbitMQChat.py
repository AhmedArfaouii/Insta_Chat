import tkinter as tk
from tkinter import messagebox
from RabbitMQAuth import RabbitMQAuth
from MessageSender import MessageSender
from MessageReceiver import MessageReceiver

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
            chatroom_root = tk.Tk()
            chatroom_root.title("Chatroom")
            chatroom_gui = ChatroomGUI(chatroom_root, username, password)
            chatroom_root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")

class ChatroomGUI:
    def __init__(self, root, username, password):
        self.root = root
        self.root.title("Chatroom")
        self.username = username
        self.password = password

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

    def receive_messages(self):
        receiver = MessageReceiver(self.username, self.password)
        receiver.connect_to_rabbitmq()
        private_key = receiver.load_private_key_from_file(f"{self.username}_private.pem")
        received_message = receiver.receive_and_decrypt_message("queue", private_key)
        receiver.close_connection()
        if received_message:
            self.chatroom_text.insert(tk.END, f"{received_message}\n")
        self.root.after(1000, self.receive_messages)  


    def send_message(self):
        recipient = self.recipient_entry.get()
        message = self.message_entry.get()
        sender = MessageSender(self.username, self.password)
        sender.connect_to_rabbitmq()
        sender.generate_keys_if_not_exist(self.username)
        recipient_public_key = sender.load_public_key_from_file(f"{recipient}_public.pem")
        encrypted_message = sender.encrypt_message(message, recipient_public_key)
        sender.send_encrypted_message(recipient, encrypted_message, "queue")
        sender.close_connection()
        messagebox.showinfo("Message Sent", "Your message has been sent.")

if __name__ == "__main__":
    root = tk.Tk()
    login_gui = LoginGUI(root)
    root.mainloop()
