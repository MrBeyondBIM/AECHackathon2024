import pandas as pd
import Processors.config_processor as config_p

import tkinter as tk
from tkinter import filedialog
import os

# Function to select an Excel file
def select_excel_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    excel_entry.delete(0, tk.END)
    excel_entry.insert(0, file_path)


# Function to run your program
def run_program():



    ####################################
    ####################################
    ###>>>MAIN PROGRAM START HERE<<<####
    ####################################
    ####################################

    ##Message Intro
    info_text.config(state=tk.NORMAL)
    info_text.delete(1.0, tk.END)
    info_text.insert(tk.END, ">> Prozess gestartet.\n")
    info_text.config(state=tk.DISABLED)
    info_text.update_idletasks()

    excel_file_path = excel_entry.get()    
    output = config_p.load_config_excel(excel_file_path)

    ##Message Config
    info_text.config(state=tk.NORMAL)
    info_text.insert(tk.END, ">> Konfiguration ausgelesen.\n")
    info_text.insert(tk.END, f">> Anzahl Spezifikationen: {str(output[1])}.\n")
    info_text.insert(tk.END, f">> Anzahl Anforderungen: {str(output[2])}.\n")
    info_text.config(state=tk.DISABLED)
    info_text.update_idletasks()

    ##Message Extract
    info_text.config(state=tk.NORMAL)

    info_text.insert(tk.END, f">> Berechnung Output:\n {output[0]}.\n")
    info_text.config(state=tk.DISABLED)
    info_text.update_idletasks()


    ##Message Finale Data
    info_text.config(state=tk.NORMAL)
    info_text.insert(tk.END, ">> Prozess abgeschlossen...\n")
    info_text.config(state=tk.DISABLED)


# Create the main window
root = tk.Tk()
root.title("LakeHub Standalone - Tools")

root.wm_geometry("500x500")

# Load and display an image
image = tk.PhotoImage(file="Image/Logo_LakeHub.png")
image = image.subsample(6, 6)

# Create a label to display the image
image_label = tk.Label(root, image=image)
image_label.pack()

excel_label = tk.Label(root, text="Select Excel File:")
excel_label.pack()

excel_entry = tk.Entry(root, width=50)
excel_entry.pack()

excel_button = tk.Button(root, text="Browse", command=select_excel_file, width=50)
excel_button.pack(pady=5)

run_button = tk.Button(root, text="Run", command=run_program, width=50) 
run_button.pack(pady=5)

info_label = tk.Label(root, text="Information:")
info_label.pack()

info_text = tk.Text(root, width=50, height=10, state=tk.DISABLED)
info_text.pack()

# Start the GUI event loop
root.mainloop()
