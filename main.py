import tkinter as tk
from tkinter import filedialog
from functions import sign_file, check_signature, new_keys


# Global variables to store the file paths
SOUND_FILE_PATH = "data/sound-samples/test.wav"
pdf_file_path = ""
sign_file_path = "data/signatures/sign.dat"
publickey_file_path = "data/keys/public_key.pem"


def choose_pdf_file():
    global pdf_file_path
    pdf_file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    pdf_button.config(text="Choose File: " + pdf_file_path)


def choose_sign_file():
    global sign_file_path
    sign_file_path = filedialog.askopenfilename(filetypes=[("DAT Files", "*.dat")])
    sign_button.config(text="Choose File: " + sign_file_path)


def choose_publickey_file():
    global publickey_file_path
    publickey_file_path = filedialog.askopenfilename(filetypes=[("PEM Files", "*.pem")])
    key_button.config(text="Choose File: " + publickey_file_path)


def generate():
    global pdf_file_path
    new_keys(SOUND_FILE_PATH)
    sign_file(pdf_file_path)


def verify():
    check_signature(sign_file_path, pdf_file_path, publickey_file_path)
    pass


# Create the main window
window = tk.Tk()
window.title("Hacker Tool")
window.geometry("500x200")

# Set custom colors
background_color = "#282C34"
button_color = "#61AFEF"
button_hover_color = "#C678DD"
button_font_color = "white"

# Configure window style
window.configure(bg=background_color)
window.option_add("*Font", "Arial 10")

# Choose PDF File Button
pdf_button = tk.Button(
    window,
    text="Choose PDF File",
    command=choose_pdf_file,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)
pdf_button.pack(pady=10)

# Choose sign.dat File Button
sign_button = tk.Button(
    window,
    text="Choose Sign File",
    command=choose_sign_file,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)
sign_button.pack(pady=10)

# Choose Public Key File Button
key_button = tk.Button(
    window,
    text="Choose Public Key File",
    command=choose_publickey_file,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)
key_button.pack(pady=10)

# Generate and Verify Buttons
button_frame = tk.Frame(window, bg=background_color)
button_frame.pack(pady=10)

generate_button = tk.Button(
    button_frame,
    text="Generate",
    command=generate,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)
generate_button.pack(side=tk.LEFT, padx=5)

verify_button = tk.Button(
    button_frame,
    text="Verify",
    command=verify,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)
verify_button.pack(side=tk.LEFT, padx=5)

# Start the main loop
window.mainloop()
