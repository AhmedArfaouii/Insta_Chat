import tkinter as tk
from sender import send_to_rabbitmq



def send_message():
    message = entry.get()
    send_to_rabbitmq(message)
    entry.delete(0, tk.END)

root = tk.Tk()
root.title("Chat Room")

def create_gui():
    global entry
    frame = tk.Frame(root)
    frame.pack()

    entry = tk.Entry(frame)
    entry.pack(side=tk.LEFT)

    send_button = tk.Button(frame, text="Send", command=send_message)
    send_button.pack(side=tk.RIGHT)

create_gui()
root.mainloop()