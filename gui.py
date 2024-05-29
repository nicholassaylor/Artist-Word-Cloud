from musicwordcloud import cloud_hook
from wordcloud import WordCloud
from PIL import ImageTk, Image
from multiprocessing import freeze_support
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import threading

current_cloud: WordCloud
next_cloud: WordCloud
cloud_frame: tk.Frame
root: tk.Tk
thread: threading.Thread


class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Scroll to the end

    def flush(self):
        pass  # Required for file-like object compatibility


def threaded_generation(artist: str):
    global next_cloud
    next_cloud = cloud_hook(artist)
    if next_cloud is not None:
        print("Word cloud complete!")
    else:
        print(f"Error with artist: {artist}")
    return


def check_queue():
    if thread.is_alive():
        root.after(100, check_queue)
    else:
        global current_cloud
        global next_cloud
        if next_cloud:
            current_cloud = next_cloud
            display_cloud(None)
        else:
            messagebox.showerror(
                "Could not find artist",
                "Artist could not be found on Genius, ensure that it is spelled correctly.",
            )


def get_cloud(artist: str):
    global thread
    thread = threading.Thread(target=threaded_generation, args=(artist,))
    thread.start()
    root.after(1000, check_queue)


def display_cloud(event):
    if current_cloud is not None:
        wc_image = current_cloud.to_array()
        pil_image = Image.fromarray(wc_image)
        size = min(cloud_frame.winfo_width(), cloud_frame.winfo_height())
        pil_image = pil_image.resize((size, size), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image)
        # Remove old clouds
        for widget in cloud_frame.winfo_children():
            widget.destroy()
        image = ttk.Label(cloud_frame)
        image.pack()
        image.config(image=tk_image)
        image.image = tk_image


def set_up_gui() -> tk.Tk:
    # Prevent error on start-up
    global current_cloud
    global root
    current_cloud = None
    root = tk.Tk()
    root.title("WordCloud")
    root.geometry("900x700")
    # Create styles
    root.style = ttk.Style()
    root.style.configure(
        "Red.TFrame", background="red"
    )  # Configure style for the red frame
    root.style.configure(
        "Blue.TFrame", background="blue"
    )  # Configure style for the blue frame
    # Create Frames
    text_frame = ttk.Frame(root, style="Red.TFrame")
    text_frame.pack(side=tk.BOTTOM, fill=tk.X)
    entry_frame = ttk.Frame(root, style="Blue.TFrame")
    entry_frame.pack(side=tk.BOTTOM, fill=tk.Y)
    global cloud_frame
    cloud_frame = ttk.Frame(root, style="Red.TFrame")
    cloud_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    # For changing size of cloud
    cloud_frame.bind("<Configure>", display_cloud)
    # Create content
    text_label = ttk.Label(entry_frame, text="Enter an artist:")
    text_entry = ttk.Entry(entry_frame, width=30)
    submit_button = ttk.Button(
        entry_frame, text="Submit", command=lambda: get_cloud(text_entry.get())
    )
    text_output = tk.Text(text_frame, wrap=tk.WORD, height=6, width=75)
    # Fill frames
    text_label.pack(side=tk.LEFT)
    text_entry.pack(side=tk.LEFT)
    submit_button.pack(side=tk.LEFT)
    text_output.pack()
    sys.stdout = TextRedirector(text_output)
    return root


if __name__ == "__main__":
    freeze_support()
    gui = set_up_gui()
    gui.mainloop()
