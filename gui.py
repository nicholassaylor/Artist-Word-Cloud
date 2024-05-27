from musicwordcloud import cloud_hook
from wordcloud import WordCloud
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from multiprocessing import freeze_support
import tkinter as tk
from tkinter import ttk, messagebox
import sys


class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)  # Scroll to the end

    def flush(self):
        pass  # Required for file-like object compatibility


def display_cloud(root: tk.Tk):
    wc: WordCloud = cloud_hook("Seether")
    if wc:
        figure = Figure(figsize=(8, 8), dpi=100)
        figure.figimage(wc)
        canvas = FigureCanvasTkAgg(figure, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    else:
        messagebox.showerror("Cannot find artist",
                             "Artist could not be found on Genius, ensure that it is spelled correctly.")


def set_up_gui() -> tk.Tk:
    root = tk.Tk()
    root.title('WordCloud')
    frame = ttk.Frame(root)
    frame.pack()
    text_entry = ttk.Entry(root)
    text_entry.pack(side=tk.LEFT)
    btn = ttk.Button(root, text='Start', command=lambda: display_cloud(root))
    btn.pack(side=tk.RIGHT)
    text_output = tk.Text(root, wrap=tk.WORD, height=10)
    text_output.pack(side=tk.BOTTOM)
    sys.stdout = TextRedirector(text_output)
    return root


if __name__ == "__main__":
    freeze_support()
    gui = set_up_gui()
    gui.mainloop()
