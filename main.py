from PIL import Image
from pytesseract import pytesseract
import re
import tkinter as tk
import spacy
from tkinter import filedialog, ttk

nlp = spacy.load("en_core_web_sm")
nlp_fr = spacy.load("fr_core_news_sm")


def extract_information(image_path, tesseract_path):
    # Configure the path to the Tesseract executable
    pytesseract.tesseract_cmd = tesseract_path

    # Open the image
    img = Image.open(image_path)

    # Convert the image to text
    text = pytesseract.image_to_string(img, config='--psm 3 --oem 3')

    # Define the regular expression for email addresses
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Find all email addresses in the text
    emails = re.findall(email_regex, text)

    # Use spaCy to find names
    doc = nlp(text)
    names = [entity.text for entity in doc.ents if entity.label_ == "PERSON"]

    return emails, names

    # Path access to the image and Tesseract executable


tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def is_valid_email(email):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return bool(re.match(email_regex, email))


def browse_image_and_extract_emails():
    global is_loading
    is_loading = True
    filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if filename:
        emails, _ = extract_information(filename, tesseract_path_entry.get())
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Adresses e-mail trouvées :\n")
        for email in emails:
            if is_valid_email(email):
                result_text.insert(tk.END, email + "\n")
            else:
                result_text.insert(tk.END, email + " (non valide)\n")
        result_text.config(state=tk.DISABLED)
    is_loading = False


def browse_image_and_extract_names():
    global is_loading
    is_loading = True
    filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if filename:
        _, names = extract_information(filename, tesseract_path_entry.get())
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Noms trouvés :\n")
        for name in names:
            result_text.insert(tk.END, name + "\n")
        result_text.config(state=tk.DISABLED)
    is_loading = False


def save_emails_to_file():
    emails_text = result_text.get("1.0", tk.END)
    if emails_text.strip():  # Check if the text is not empty
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Fichier texte", "*.txt"), ("Fichier CSV", "*.csv"),
                                                           ("Fichier JSON", "*.json")])
        if filename:
            with open(filename, "w") as file:
                file.write(emails_text)


# Create the main window
root = tk.Tk()
root.title("Extraction de texte à partir d'une image")

# Define the default path to the Tesseract executable
default_tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Frame for the Tesseract path
tesseract_path_frame = ttk.Frame(root, padding="10")
tesseract_path_frame.grid(row=0, column=0, padx=5, pady=5)

# Label for the Tesseract path
tesseract_path_label = tk.Label(tesseract_path_frame, text="Chemin de Tesseract :", font=("Arial", 14))
tesseract_path_label.grid(row=0, column=0, padx=5, pady=5)

# Entry for the Tesseract path
tesseract_path_entry = tk.Entry(tesseract_path_frame, font=("Arial", 12))
tesseract_path_entry.insert(tk.END, default_tesseract_path)
tesseract_path_entry.grid(row=0, column=1, padx=5, pady=5)

# Frame for the buttons
browse_button_frame = ttk.Frame(root)
browse_button_frame.grid(row=1, column=0, padx=10, pady=5)

# Button to browse an image
browse_button_emails = ttk.Button(browse_button_frame, text="Extraire des mails",
                                  command=browse_image_and_extract_emails)
browse_button_emails.grid(row=1, column=0, padx=10, pady=5)

# Button to browse an image and extract names
browse_button_names = ttk.Button(browse_button_frame, text="Extraire des noms", command=browse_image_and_extract_names)
browse_button_names.grid(row=1, column=1, padx=10, pady=5)


is_loading = False

# Create a label to display an animation
animation_label = ttk.Label(root, text="Extraction en cours", font=("Arial", 18))
animation_label.grid(row=4, column=0, padx=5, pady=10)


def animate_label():
    if is_loading:
        current_text = animation_label.cget("text")
        dot_count = current_text.count(".")
        if dot_count < 5:
            new_text = "Extraction en cours" + "." * (dot_count + 1)
        else:
            new_text = "Extraction en cours"
        animation_label.config(text=new_text)
    else:
        animation_label.config(text="")
    root.after(1000, animate_label)   # Schedule the next animation in 1 second


# Start the animation
animate_label()

# Frame to display the result
result_frame = ttk.Frame(root)
result_frame.grid(row=2, column=0, padx=5, pady=5)

# Text widget to display the result
result_text = tk.Text(result_frame, height=10, width=50, font=("Arial", 13))
result_text.config(state=tk.DISABLED)
result_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Scrollbar for the result text
scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=result_text.yview)
scrollbar.grid(row=2, column=2, sticky="ns")
result_text.config(yscrollcommand=scrollbar.set)

# Frame for the save button
save_button_frame = ttk.Frame(root, padding="10")
save_button_frame.grid(row=3, column=0, padx=5, pady=5)

# Button to save the emails to a file
save_emails_to_file_button = tk.Button(save_button_frame, text="Enregistrer dans un fichier",
                                       command=save_emails_to_file)
save_emails_to_file_button.grid(row=3, column=0, padx=5, pady=5)

# Execute the main loop
root.mainloop()
