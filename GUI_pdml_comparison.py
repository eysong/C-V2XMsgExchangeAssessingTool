import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, PhotoImage, StringVar
from PIL import ImageTk, Image

MAIN_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "C-V2XMsgExchangeAssess.py")

def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

class PdmlCompareGUI:
    def __init__(self, root):
        self.root = root
        root.title("C-V2X Message Exchange Analyzer")
        root.geometry("750x800")
        root.config(background = "#e3e9f8")
        try:
            self.icon = PhotoImage(file = "nist_logo.png") #Tries to set logo to NIST if pic is present
            root.iconphoto(True, self.icon)
        except Exception:
            pass #Skips otherwise

        self.file1_path = tk.StringVar(value="Select a PDML file")
        self.file2_path = tk.StringVar(value="Select a PDML file")

        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=0)
        root.rowconfigure(7, weight=2)

        #Title row
        self.logo = Image.open("NIST_CTL_logo.png").resize((160, 29))
        self.logo = ImageTk.PhotoImage(self.logo)
        logo_label = tk.Label(root, image=self.logo)
        logo_label.place(x=0, y=5)
        tk.Label(root, text="C-V2X Message Exchange Analyzer", font=("Calibri", 17), bg="#e3e9f8").grid(row=0, column=1, padx=8, pady=8)

        #File 1 row
        tk.Label(root, text="Transmitted PDML", font=("Calibri", 12), bg="#e3e9f8").grid(row=1, column=0, padx=8, pady=8, ipadx=5, sticky="w")
        self.opt1 = StringVar(value = "Select a vendor")
        self.vendors = ["Cohda", "Commsignia", "Kapsch", "Qualcomm", "Ettifos"]
        self.dropdown1 = tk.OptionMenu(root, self.opt1, *self.vendors)
        self.dropdown1.grid(row=2, column=0, padx=4, pady=8, sticky="w")
        self.add_hover_effect(self.dropdown1, "#f0f0f0", "#E2E2E2")
        tk.Entry(root, textvariable=self.file1_path, width=60).grid(row=2, column=1, padx=4, pady=8, sticky="ew")
        
        self.browse1 = tk.Button(root, text="Browse...", command=self.browse_file1)
        self.browse1.grid(row=2, column=2, padx=8, pady=8, sticky="w")
        self.add_hover_effect(self.browse1, "#f0f0f0", "#E2E2E2")

        #File 2 row
        tk.Label(root, text="Received PDML", font=("Calibri", 12), bg="#e3e9f8").grid(row=3, column=0, padx=8, pady=8, ipadx = 5, sticky="w")
        self.opt2 = StringVar(value = "Select a vendor")
        self.dropdown2 = tk.OptionMenu(root, self.opt2, *self.vendors)
        self.dropdown2.grid(row=4, column=0, padx=4, pady=8, sticky="w")
        self.add_hover_effect(self.dropdown2, "#f0f0f0", "#E2E2E2")
        tk.Entry(root, textvariable=self.file2_path, width=60).grid(row=4, column=1, padx=4, pady=8, sticky="ew")
        self.browse2 = tk.Button(root, text="Browse...", command=self.browse_file2)
        self.browse2.grid(row=4, column=2, padx=8, pady=8, sticky="w")
        self.add_hover_effect(self.browse2, "#f0f0f0", "#E2E2E2")

        #Compare button
        self.compare_btn = tk.Button(
            root, text="Compare", font=("Calibri", 16, "bold"), command=lambda: self.run_compare(self.opt1.get(), self.opt2.get()),
            bg="#005EA2", fg="white", height=1, width=15)
        self.compare_btn.grid(row=5, column=0, columnspan=3, pady=8)
        self.add_hover_effect(self.compare_btn, "#005EA2", "#1A4480")

        #Output box
        tk.Label(root, text="Result:", font=("Calibri", 12)).grid(row=6, column=0, padx=8, ipadx=6, sticky="w")
        self.output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=85, height=20)
        self.output_box.grid(row=7, column=0, columnspan=3, padx=8, pady=4, sticky="nsew")
        self.output_box.config(background = "#f3f5fa")

        #Save button
        self.save_btn = tk.Button(root, text="Save As CSV...", command=self.save_output)
        self.save_btn.grid(row=8, column=0, columnspan=3, pady=8)
        self.add_hover_effect(self.save_btn, "#f0f0f0", "#F9F9F9")

        #View map button
        self.map_btn = tk.Button(root, text="View Car Path", command=self.view_map)
        self.map_btn.grid(row=8, column=2, padx=8, pady=8)
        self.add_hover_effect(self.map_btn, "#f0f0f0", "#F9F9F9")

    def browse_file1(self):
        path = filedialog.askopenfilename(filetypes=[("PDML files", "*.pdml"), ("All files", "*.*")])
        if path:
            self.file1_path.set(path)

    def browse_file2(self):
        path = filedialog.askopenfilename(filetypes=[("PDML files", "*.pdml"), ("All files", "*.*")])
        if path:
            self.file2_path.set(path)

    def run_compare(self, vendor1, vendor2):
        f1 = self.file1_path.get().strip()
        f2 = self.file2_path.get().strip()

        if f1 == "Select a PDML file" or f2 == "Select a PDML file": #Both PDML files need to be selected
            messagebox.showwarning("Missing files", "Please select both PDML files first.")
            return
        if not os.path.isfile(MAIN_SCRIPT): #If PDML files cannot be found
            messagebox.showerror("C-V2XMsgExchangeAssess.py not found", f"Could not find:\n{MAIN_SCRIPT}\n\n"
                                  "Edit MAIN_SCRIPT at the top of this file to point to your script.")
            return
        if vendor1 == "Select a vendor" or vendor2 == "Select a vendor": #If both vendors are not selected yet
            messagebox.showwarning("Missing vendor", "Please choose the appropriate vendors before continuing")
            return
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Running comparison, please wait...\n")
        self.root.update_idletasks()

        try:
            result = subprocess.run(
                [sys.executable, MAIN_SCRIPT, vendor1, f1, vendor2, f2], #matches the order of parameters needed to run the program
                capture_output=True, text=True, check=False
            )
        except Exception as e:
            messagebox.showerror("Error running script", str(e))
            return

        self.output_box.delete("1.0", tk.END)

        if result.returncode != 0:
            self.output_box.insert(tk.END, "ERROR while running C-V2XMsgExchangeAssess.py:\n\n")
            self.output_box.insert(tk.END, result.stderr or "(no error message returned)")
            return

        #Prints all the message analysis to the output box
        self.output_box.insert(tk.END, result.stdout)

    def save_output(self):
        content = self.output_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("Nothing to save", "Run a comparison first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="output.csv"
        )
        if path:
            with open(path, "w", newline="") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Saved to:\n{path}")

    def view_map(self):
        self.map_btn.config(text="Loading...")
        self.map_btn.update()
        subprocess.run([sys.executable, "Draw_map.py"])
        self.map_btn.config(text="View Car Map")

    def add_hover_effect(self, button, normal_color, hover_color):
        button.bind("<Enter>", lambda event: button.config(bg=hover_color))
        button.bind("<Leave>", lambda event: button.config(bg=normal_color))

if __name__ == "__main__":
    root = tk.Tk()
    app = PdmlCompareGUI(root)
    root.mainloop()