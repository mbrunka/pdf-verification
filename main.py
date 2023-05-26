import tkinter as tk
from tkinter import filedialog
from functions import sign_file, check_signature, new_keys

# Global variables to store the file paths
SOUND_FILE_PATH = "data/sound-samples/test.wav"
pdf_file_path = ""
sign_file_path = ""
publickey_file_path = ""

# Create the main window
window = tk.Tk()
window.title("Hacker Tool")
window.geometry("500x280")

# Set custom colors
background_color = "#282C34"
menu_background_color = "#1C1F24"
line_color = "#444444"
button_color = "#61AFEF"
button_hover_color = "#C678DD"
button_font_color = "white"

# Configure window style
window.configure(bg=background_color)
window.option_add("*Font", "Arial 10")


# Function to choose PDF file
def choose_pdf_file():
    global pdf_file_path
    pdf_file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    pdf_button.config(text=pdf_file_path)  # Update button text with file path


# Function to choose sign file
def choose_sign_file():
    global sign_file_path
    sign_file_path = filedialog.askopenfilename(filetypes=[("DAT Files", "*.dat")])
    sign_button.config(text=sign_file_path)  # Update button text with file path


# Function to choose public key file
def choose_publickey_file():
    global publickey_file_path
    publickey_file_path = filedialog.askopenfilename(filetypes=[("PEM Files", "*.pem")])
    publickey_button.config(
        text=publickey_file_path
    )  # Update button text with file path


# Function to generate
def generate():
    new_keys(SOUND_FILE_PATH)
    sign_file(pdf_file_path)


# Function to verify
def verify():
    check_signature(sign_file_path, pdf_file_path, publickey_file_path)


# Function to hide buttons
def hide_buttons():
    pdf_button.pack_forget()
    sign_button.pack_forget()
    publickey_button.pack_forget()
    confirm_ver_button.pack_forget()
    confirm_gen_button.pack_forget()


# Function to show buttons
def show_buttons(buttons):
    for button in buttons:
        button.pack(pady=10)


# Menu screen
menu_frame = tk.Frame(window, bg=menu_background_color)
menu_frame.pack(pady=10)

# Menu option variable
menu_option = tk.StringVar()


def menu_option_changed():
    hide_buttons()
    if menu_option.get() == "Generate":
        show_buttons([pdf_button, confirm_gen_button])
    elif menu_option.get() == "Verify":
        show_buttons([pdf_button, sign_button, publickey_button, confirm_ver_button])


generate_button = tk.Radiobutton(
    menu_frame,
    text="Generate",
    variable=menu_option,
    value="Generate",
    command=menu_option_changed,
    bg=menu_background_color,
    fg=button_font_color,
    selectcolor=menu_background_color,
    activebackground=menu_background_color,
    activeforeground=button_font_color,
)
generate_button.pack(side=tk.LEFT, padx=5)

verify_button = tk.Radiobutton(
    menu_frame,
    text="Verify",
    variable=menu_option,
    value="Verify",
    command=menu_option_changed,
    bg=menu_background_color,
    fg=button_font_color,
    selectcolor=menu_background_color,
    activebackground=menu_background_color,
    activeforeground=button_font_color,
)
verify_button.pack(side=tk.LEFT, padx=5)

exit_button = tk.Button(
    menu_frame,
    text="Exit",
    command=window.quit,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)
exit_button.pack(side=tk.LEFT, padx=5)

# Separating line
line = tk.Frame(window, bg=line_color, height=2)
line.pack(fill=tk.X)

# PDF File Button
pdf_button = tk.Button(
    window,
    text="Choose PDF File",
    command=choose_pdf_file,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)

# Sign File Button
sign_button = tk.Button(
    window,
    text="Choose Sign File",
    command=choose_sign_file,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)

# Public Key File Button
publickey_button = tk.Button(
    window,
    text="Choose Public Key File",
    command=choose_publickey_file,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)

# Confirm GENERATION Button
confirm_gen_button = tk.Button(
    window,
    text="Confirm",
    command=generate,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)
# Confirm VERYFICATION Button
confirm_ver_button = tk.Button(
    window,
    text="Confirm",
    command=verify,
    bg=button_color,
    fg=button_font_color,
    activebackground=button_hover_color,
    activeforeground=button_font_color,
)

# Start with menu screen
show_buttons([generate_button, verify_button, exit_button])
menu_option.set("Generate")
menu_option_changed()

# Start the main loop
window.mainloop()
