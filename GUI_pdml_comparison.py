import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, PhotoImage, StringVar

# If C-V2XMsgExchangeAssess.py is somewhere else, change this to the full path, e.g.
# MAIN_SCRIPT = r"C:\Users\you\project\C-V2XMsgExchangeAssess.py"
MAIN_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "C-V2XMsgExchangeAssess.py")


class PdmlCompareGUI:
    def __init__(self, root):
        self.root = root
        root.title("PDML Comparator")
        root.geometry("720x650")
        root.config(background = "#C4DDFF")
        try:
            self.icon = PhotoImage(file = "nist_logo.png") #Tries to set logo to NIST if pic is present
            root.iconphoto(True, self.icon)
        except Exception:
            pass #Skips otherwise

        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()

        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=0)
        root.columnconfigure(3, weight=1)
        root.columnconfigure(4, weight=1)
        root.columnconfigure(5, weight=1)
        root.columnconfigure(6, weight=2)

        #File 1 row
        tk.Label(root, text="File 1:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.opt1 = StringVar(value = "Select a vendor")
        self.vendors = ["Cohda", "Commsignia", "Kapsch", "Qualcomm"]
        tk.OptionMenu(root, self.opt1, *self.vendors).grid(row=1, column=0, padx=4, pady=8, sticky="w")
        tk.Entry(root, textvariable=self.file1_path, width=60).grid(row=1, column=1, padx=4, pady=8, sticky="ew")
        tk.Button(root, text="Browse...", command=self.browse_file1).grid(row=1, column=2, padx=8, pady=8, sticky="w")

        #File 2 row
        tk.Label(root, text="File 2:").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.opt2 = StringVar(value = "Select a vendor")
        tk.OptionMenu(root, self.opt2, *self.vendors).grid(row=3, column=0, padx=4, pady=8, sticky="w")
        tk.Entry(root, textvariable=self.file2_path, width=60).grid(row=3, column=1, padx=4, pady=8, sticky="ew")
        tk.Button(root, text="Browse...", command=self.browse_file2).grid(row=3, column=2, padx=8, pady=8, sticky="w")

        #Compare button
        tk.Button(
            root, text="Compare", command=lambda: self.run_compare(self.opt1.get(), self.opt2.get()),
            bg="#4CAF50", fg="white", height=2, width=20
        ).grid(row=4, column=0, columnspan=3, pady=12)

        #Output box
        tk.Label(root, text="Result:").grid(row=5, column=0, padx=8, sticky="w")
        self.output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=85, height=20)
        self.output_box.grid(row=6, column=0, columnspan=3, padx=8, pady=4, sticky="ew")
        self.output_box.config(background = "#e5eaf5")

        #Save button
        tk.Button(root, text="Save As CSV...", command=self.save_output).grid(
            row=7, column=0, columnspan=3, pady=8
        )

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

        if not f1 or not f2:
            messagebox.showwarning("Missing files", "Please select both PDML files first.")
            return
        if not os.path.isfile(MAIN_SCRIPT):
            messagebox.showerror("C-V2XMsgExchangeAssess.py not found", f"Could not find:\n{MAIN_SCRIPT}\n\n"
                                  "Edit MAIN_SCRIPT at the top of this file to point to your script.")
            return

        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Running comparison, please wait...\n")
        self.root.update_idletasks()

        try:
            result = subprocess.run(
                [sys.executable, MAIN_SCRIPT, vendor1, f1, vendor2, f2],
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

        # stdout is the CSV content your script normally redirects with '>'
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


if __name__ == "__main__":
    root = tk.Tk()
    app = PdmlCompareGUI(root)
    root.mainloop()