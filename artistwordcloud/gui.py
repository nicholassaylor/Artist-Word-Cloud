from artistwordcloud.cloud_core import cloud_hook
from wordcloud import WordCloud
from PIL import ImageTk, Image
from pathvalidate import sanitize_filename
from multiprocessing import freeze_support
import tkinter as tk
from copy import deepcopy
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk
import sys
import threading

current_cloud: WordCloud
next_cloud: WordCloud
thread: threading.Thread


class TextRedirector:
    """
    Directs console output from stdout to a text widget provided in the constructor.
    """

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Scroll to the end

    def flush(self):
        pass  # Required for file-like object compatibility


def threaded_generation(artist: str):
    """
    Thread wrapper for cloud_hook
    """
    global next_cloud
    next_cloud = cloud_hook(artist)
    if next_cloud is not None:
        print("Word cloud complete!")
    else:
        print(f"Error with artist: {artist}")
    return


def check_thread():
    """
    Periodically checks thread for completion, after which it displays current word cloud
    or gives error for invalid artist
    """
    if thread.is_alive():
        window.after(100, check_thread)
    else:
        global current_cloud
        if next_cloud:
            current_cloud = next_cloud
            display_cloud()
            window.nametowidget("entry_frame_wrapper.entry_frame.save_button")[
                "state"
            ] = tk.NORMAL
        else:
            messagebox.showerror(
                "Could not find artist",
                "Artist could not be found on Genius, ensure that it is spelled correctly.",
            )
        window.nametowidget("entry_frame_wrapper.entry_frame.submit_button")[
            "state"
        ] = tk.NORMAL


def save_cloud(artist: str):
    # Avoid race conditions by copying current cloud immediately
    cloud_copy = deepcopy(current_cloud)
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("Bitmap", "*.bmp"),
                ("GIF", "*.gif"),
                ("WebP", "*.webp"),
            ],
            confirmoverwrite=True,
            initialfile=f"{sanitize_filename(artist)}.png",
        )
        if file_path:
            print(f"Saving file to {file_path}")
            cloud_copy.to_file(file_path)
            print("Successfully saved file!")
        else:
            print("Cancelled saving file")
    except OSError:
        messagebox.showerror("Error Saving File", "File could not be saved.")


def get_cloud(artist: str):
    """
    Initiates thread for building word cloud
    Calls check_queue on a delay to retrieve word cloud
    """
    global thread
    thread = threading.Thread(target=threaded_generation, args=(artist,))
    thread.start()
    window.nametowidget("entry_frame_wrapper.entry_frame.submit_button")["state"] = (
        tk.DISABLED
    )
    window.after(1000, check_thread)


def display_cloud(event=None):
    """
    Displays word cloud based on window size
    This is called from cloud completion and window resizing, so code should be performant wherever possible
    event is unused but required for tkinter
    """
    if current_cloud is not None:
        cloud_frame = window.nametowidget("cloud_frame")
        size = min(cloud_frame.winfo_width(), cloud_frame.winfo_height())
        wc_image = current_cloud.to_image().resize((size, size), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(wc_image)
        # Remove old clouds
        if not cloud_frame.winfo_children():
            image = ttk.Label(cloud_frame, name="image")
            image.pack()
        image = window.nametowidget("cloud_frame.image")
        image.config(image=tk_image)
        image.image = tk_image


def set_up_gui() -> tk.Tk:
    """
    Creates layout for GUI as well as setting styles and features for widgets
    """
    # Prevent error on start-up
    global current_cloud
    current_cloud = None
    # Create window
    root = ThemedTk(theme="equilux")
    root.title("WordCloud")
    root.geometry("900x700")
    # Create Frames
    text_frame = ttk.Frame(root)
    text_frame.pack(side=tk.BOTTOM, fill=tk.X)
    entry_frame_wrapper = ttk.Frame(root, name="entry_frame_wrapper")
    entry_frame_wrapper.pack(side=tk.BOTTOM, fill=tk.X)
    entry_frame = ttk.Frame(entry_frame_wrapper, name="entry_frame")
    entry_frame.pack(side=tk.BOTTOM, anchor=tk.CENTER)
    cloud_frame = ttk.Frame(root, name="cloud_frame")
    cloud_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(0, 5), padx=5)
    # For changing size of cloud
    cloud_frame.bind("<Configure>", display_cloud)
    # Create content
    artist_entry_label = ttk.Label(entry_frame, text="Enter an artist:")
    artist_entry = ttk.Entry(entry_frame, width=30)
    submit_button = ttk.Button(
        entry_frame,
        text="Submit",
        command=lambda: get_cloud(artist_entry.get()),
        name="submit_button",
    )
    save_button = ttk.Button(
        entry_frame,
        text="Save as...",
        command=lambda: save_cloud(artist_entry.get()),
        name="save_button",
    )
    save_button["state"] = tk.DISABLED
    text_output = tk.Text(text_frame, wrap=tk.WORD, height=6, width=75)
    # Fill frames
    artist_entry_label.pack(side=tk.LEFT, padx=2)
    artist_entry.pack(side=tk.LEFT)
    submit_button.pack(side=tk.LEFT, padx=5)
    save_button.pack(side=tk.LEFT, padx=40, ipadx=10)
    text_output.pack(pady=20)
    # Redirect output to text widget
    sys.stdout = TextRedirector(text_output)
    return root


if __name__ == "__main__":
    freeze_support()
    window = set_up_gui()
    window.mainloop()
