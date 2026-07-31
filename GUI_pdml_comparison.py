import os
import subprocess
import sys
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, PhotoImage, StringVar
from PIL import ImageTk, Image
import csv
from tabulate import tabulate

MAIN_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "C-V2XMsgExchangeAssess.py")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def add_hover_effect(button, normal_color, hover_color):
    button.bind("<Enter>", lambda event: button.config(bg=hover_color))
    button.bind("<Leave>", lambda event: button.config(bg=normal_color))


class C_V2X_App:
    def __init__(self, root):
        self.root = root
        self.root.title("C-V2X Message Exchange Analyzer")
        self.root.geometry("750x850")
        self.root.config(background="#e3e9f8")
        
        try:
            self.icon = PhotoImage(file="DOC_emblem.png")
            self.root.iconphoto(True, self.icon)
        except Exception:
            pass

        # Global Image caching to prevent garbage collection bugs in tkinter frames
        try:
            self.logo_img = Image.open("NIST_CTL_logo.png").resize((160, 29))
            self.logo_photo = ImageTk.PhotoImage(self.logo_img)
        except Exception:
            self.logo_photo = None

        # Build the structural stacking container
        container = tk.Frame(self.root, bg="#e3e9f8")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.pages = {}

        # Instantiate both frame layouts
        for PageClass in (MainPage, AboutPage, CSVPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=container, controller=self)
            self.pages[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start user tracking on the Main functional screen
        self.show_page("MainPage")

    def show_page(self, page_name):
        #Brings the chosen frame to the foreground
        frame = self.pages[page_name]
        frame.tkraise()

#The main page for all the analysis
class MainPage(tk.Frame):
    """Contains all your original C-V2X parsing and rendering visual widgets."""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e3e9f8")
        self.controller = controller

        self.file1_path = tk.StringVar(value="Select a PDML file")
        self.file2_path = tk.StringVar(value="Select a PDML file")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(7, weight=2)

        # Title row (pulls cached logo asset safely from controller)
        if self.controller.logo_photo:
            logo_label = tk.Label(self, image=self.controller.logo_photo, bg="#e3e9f8")
            logo_label.place(x=0, y=5)
            
        tk.Label(self, text="C-V2X Message Exchange Analyzer", font=("Calibri", 17), bg="#e3e9f8").grid(row=0, column=1, padx=8, pady=8)

        # Button that takes user to the "ABOUT" screen
        self.about_btn_border = tk.Frame(self, highlightbackground="#005EA2", highlightcolor="#005EA2", highlightthickness=2, bd=0)
        self.about_btn_border.grid(row=0, column=2, padx=4, pady=8)
        self.about_btn = tk.Button(self.about_btn_border, text="About", command=lambda: self.controller.show_page("AboutPage"), fg="#00080E", bg="#f0f0f0", bd=0)
        self.about_btn.grid(row=0, column=2, padx=5, pady=2)
        add_hover_effect(self.about_btn, "#f0f0f0", "#F9F9F9")

        # File 1 row
        tk.Label(self, text="Transmitted PDML", font=("Calibri", 12), bg="#e3e9f8").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.opt1 = StringVar(value="Select a vendor")
        self.vendors = ["Cohda", "Commsignia", "Kapsch", "Qualcomm", "Ettifos"]
        self.dropdown1 = tk.OptionMenu(self, self.opt1, *self.vendors)
        self.dropdown1.grid(row=2, column=0, padx=4, pady=8, sticky="w")
        add_hover_effect(self.dropdown1, "#f0f0f0", "#E2E2E2")
        tk.Entry(self, textvariable=self.file1_path, width=60).grid(row=2, column=1, padx=4, pady=8, sticky="ew")
        
        self.browse1 = tk.Button(self, text="Browse...", command=self.browse_file1)
        self.browse1.grid(row=2, column=2, padx=14, pady=8, sticky="w")
        add_hover_effect(self.browse1, "#f0f0f0", "#E2E2E2")

        # File 2 row
        tk.Label(self, text="Received PDML", font=("Calibri", 12), bg="#e3e9f8").grid(row=3, column=0, padx=8, pady=8, ipadx=5, sticky="w")
        self.opt2 = StringVar(value="Select a vendor")
        self.dropdown2 = tk.OptionMenu(self, self.opt2, *self.vendors)
        self.dropdown2.grid(row=4, column=0, padx=4, pady=8, sticky="w")
        add_hover_effect(self.dropdown2, "#f0f0f0", "#E2E2E2")
        tk.Entry(self, textvariable=self.file2_path, width=60).grid(row=4, column=1, padx=4, pady=8, sticky="ew")
        self.browse2 = tk.Button(self, text="Browse...", command=self.browse_file2)
        self.browse2.grid(row=4, column=2, padx=14, pady=8, sticky="w")
        add_hover_effect(self.browse2, "#f0f0f0", "#E2E2E2")

        # Compare button
        self.compare_btn = tk.Button(
            self, text="Compare", font=("Calibri", 16, "bold"), command=lambda: self.run_compare(self.opt1.get(), self.opt2.get()),
            bg="#005EA2", fg="white", height=1, width=15)
        self.compare_btn.grid(row=5, column=0, columnspan=3, pady=8)
        add_hover_effect(self.compare_btn, "#005EA2", "#1A4480")

        # Output box
        tk.Label(self, text="Result:", font=("Calibri", 12), bg="#e3e9f8").grid(row=6, column=0, padx=8, ipadx=6, sticky="w")
        self.output_box = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=85, height=20)
        self.output_box.grid(row=7, column=0, columnspan=3, padx=8, pady=4, sticky="nsew")
        self.output_box.config(background="#f3f5fa")


        SMALL_BUTTON_BEFORE = "#1A365D"
        SMALL_BUTTON_AFTER = "#0F294A"
        # Action Buttons Layout (Row 8)
        self.save_btn = tk.Button(self, text="Save As CSV...", font=("Calibri", 12), command=self.save_output, bg=SMALL_BUTTON_BEFORE, fg="white", height=1, width=13)
        self.save_btn.grid(row=8, column=0, columnspan=3, padx=8, pady=8, sticky="s")
        add_hover_effect(self.save_btn, SMALL_BUTTON_BEFORE, SMALL_BUTTON_AFTER)


        self.map_btn = tk.Button(self, text="View Car Path", font=("Calibri", 12), command=self.view_map, bg=SMALL_BUTTON_BEFORE, fg="white", height=1, width=13)
        self.map_btn.grid(row=8, column=2, padx=8, pady=8, sticky="e")
        add_hover_effect(self.map_btn, SMALL_BUTTON_BEFORE, SMALL_BUTTON_AFTER)

        self.csv_btn = tk.Button(self, text="Read CSV File", font=("Calibri", 12), command=lambda: self.controller.show_page("CSVPage"), bg=SMALL_BUTTON_BEFORE, fg="white", height=1, width=13)
        self.csv_btn.grid(row=8, column=0, padx=8, pady=8, sticky="w")
        add_hover_effect(self.csv_btn, SMALL_BUTTON_BEFORE, SMALL_BUTTON_AFTER)

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

        if f1 == "Select a PDML file" or f2 == "Select a PDML file":
            messagebox.showwarning("Missing files", "Please select both PDML files first.")
            return
        if not os.path.isfile(MAIN_SCRIPT):
            messagebox.showerror("C-V2XMsgExchangeAssess.py not found", f"Could not find:\n{MAIN_SCRIPT}\n\n"
                                  "Edit MAIN_SCRIPT at the top of this file to point to your script.")
            return
        if vendor1 == "Select a vendor" or vendor2 == "Select a vendor":
            messagebox.showwarning("Missing vendor", "Please choose the appropriate vendors before continuing")
            return
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Running comparison, please wait...\n")
        self.controller.root.update_idletasks()

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
        coords_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coords.csv")
        if not os.path.isfile(coords_path):
            messagebox.showinfo("No map available", "Run a comparison first.")
            return
        self.map_btn.config(text="Loading...")
        self.map_btn.update()
        subprocess.run([sys.executable, "Draw_map.py"])
        self.map_btn.config(text="View Car Map")


import tkinter as tk
from tkinter import scrolledtext, filedialog

class CSVPage(tk.Frame):
    def __init__(self, parent, controller):
        CSV_BG_COLOR = "#e3e9f8"
        super().__init__(parent, bg=CSV_BG_COLOR)
        self.controller = controller

        #Config base grid stretch
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        #Set up canvas + scrollbar
        self.canvas = tk.Canvas(self, bg=CSV_BG_COLOR, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=CSV_BG_COLOR)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        
        # row 0
        self.exit_btn = tk.Button(self.scrollable_frame, text="Exit", command=lambda: self.controller.show_page("MainPage"))
        self.exit_btn.grid(row=0, column=0, padx=5, pady=(5,1), ipadx=8, ipady=1, sticky="w")
        if 'add_hover_effect' in globals():
            add_hover_effect(self.exit_btn, "#f0f0f0", "#F9F9F9")

        # row 1
        self.csv_path = tk.StringVar(value="Select a CSV file")
        self.csv_path.trace_add("write", self.auto_run_program)
        
        self.csv_entry = tk.Entry(self.scrollable_frame, textvariable=self.csv_path, width=60)
        self.csv_entry.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="ew")
        
        self.browsecsv = tk.Button(self.scrollable_frame, text="Browse...", command=self.browse_csv)
        self.browsecsv.grid(row=1, column=2, padx=8, pady=8, sticky="w")
        if 'add_hover_effect' in globals():
            add_hover_effect(self.browsecsv, "#f0f0f0", "#E2E2E2")

        # rows 2 & 3: BSM
        self.bsm_label = tk.Label(self.scrollable_frame, text="BSM", font=("Calibri", 12, "bold"), bg=CSV_BG_COLOR)
        self.bsm_label.grid(row=2, column=0, padx=8, ipadx=6, sticky="w")
        self.bsm_box = scrolledtext.ScrolledText(self.scrollable_frame, wrap=tk.WORD, height=10)
        self.bsm_box.grid(row=3, column=0, columnspan=3, padx=8, pady=4, sticky="nsew")
        self.bsm_box.config(background="#f3f5fa")

        # rows 4 & 5: SPaT
        self.spat_label = tk.Label(self.scrollable_frame, text="SPaT", font=("Calibri", 12, "bold"), bg=CSV_BG_COLOR)
        self.spat_label.grid(row=4, column=0, padx=8, ipadx=6, sticky="w")
        self.spat_box = scrolledtext.ScrolledText(self.scrollable_frame, wrap=tk.WORD, height=10)
        self.spat_box.grid(row=5, column=0, columnspan=3, padx=8, pady=4, sticky="nsew")
        self.spat_box.config(background="#f3f5fa")
        
        # rows 6 & 7: TIM
        self.tim_label = tk.Label(self.scrollable_frame, text="TIM", font=("Calibri", 12, "bold"), bg=CSV_BG_COLOR)
        self.tim_label.grid(row=6, column=0, padx=8, ipadx=6, sticky="w")
        self.tim_box = scrolledtext.ScrolledText(self.scrollable_frame, wrap=tk.WORD, height=10)
        self.tim_box.grid(row=7, column=0, columnspan=3, padx=8, pady=4, sticky="nsew")
        self.tim_box.config(background="#f3f5fa")

        # rows 8 & 9: MAP
        self.map_label = tk.Label(self.scrollable_frame, text="MAP", font=("Calibri", 12, "bold"), bg=CSV_BG_COLOR)
        self.map_label.grid(row=8, column=0, padx=8, ipadx=6, sticky="w")
        self.map_box = scrolledtext.ScrolledText(self.scrollable_frame, wrap=tk.WORD, height=10)
        self.map_box.grid(row=9, column=0, columnspan=3, padx=8, pady=4, sticky="nsew")
        self.map_box.config(background="#f3f5fa")

        # Allow textboxes stretch cleanly
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)

    # --- HELPER SCROLL METHODS ---
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def browse_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path:
            self.csv_path.set(path)

    # Function to add distinguish message types in CSV and write them
    #to their respective text boxes
    def auto_run_program(self, *args):
        file_path = self.csv_path.get()

        if file_path == "Select a CSV file" or not file_path:
            return

        # Defining multi-row headers for diff message types
        headers_config = {
            "BSM": pd.MultiIndex.from_tuples([
                ('Packet Num.', ''),
                ('Tx', 'Msg Type'), ('Tx', 'Msg Count'), ('Tx', 'Sec. Mark'), ('Tx', 'Width'), ('Tx', 'Length'),
                ('Rx', 'Msg Type'), ('Rx', 'Msg Count'), ('Rx', 'Sec. Mark'), ('Tx', 'Width'), ('Tx', 'Length'),
                ('Result', 'Occurrences'), ('Result', 'Status')
            ]),

            "SPAT": pd.MultiIndex.from_tuples([
                ('Packet Num.', ''),
                ('Tx', 'Msg Type'), ('Tx', 'ID'), ('Tx', 'Revision Num.'),
                ('Rx', 'Msg Type'), ('Rx', 'ID'), ('Rx', 'Revision Num.'),
                ('Result', 'Occurrences'), ('Result', 'Status')
            ]),

            "MAP": pd.MultiIndex.from_tuples([
                ('Packet Num.', ''),
                ('Tx', 'Msg Type'), ('Tx', 'Latitude'), ('Tx', 'Longitude'),
                ('Rx', 'Msg Type'), ('Rx', 'Latitude'), ('Rx', 'Longitude'),
                ('Result', 'Occurrences'), ('Result', 'Status')
            ]),

            "TIM": pd.MultiIndex.from_tuples([
                ('Packet Num.', ''),
                ('Tx', 'Msg Type'), ('Tx', 'Latitude'), ('Tx', 'Longitude'),
                ('Rx', 'Msg Type'), ('Rx', 'Latitude'), ('Rx', 'Longitude'),
                ('Result', 'Occurrences'), ('Result', 'Status')
            ])
        }

        filtered_data = {"BSM": [], "SPAT": [], "TIM": [], "MAP": []}

        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                #Skip empty rows
                for row in csv_reader:
                    if not row:
                        continue
                    
                    #Identifies msg type
                    msg_type = None
                    for val in row:
                        val_upper = str(val).upper().strip()
                        if val_upper in filtered_data:
                            msg_type = val_upper
                            break
                        
                    if msg_type:
                        filtered_data[msg_type].append(row)

            ui_mapping = {
                "BSM": self.bsm_box,
                "SPAT": self.spat_box,
                "TIM": self.tim_box,
                "MAP": self.map_box
            }

            for msg_type, textbox in ui_mapping.items():
                textbox.delete("1.0", tk.END)
                rows_found = filtered_data[msg_type]
                if rows_found:
                    columns_layout = headers_config.get(msg_type)
                
                    if columns_layout is not None:
                        combined_headers = []
                        for top, bot in columns_layout:
                            header_text = f"{top}\n{bot}".strip() #New line approach to resemble 2 rows of headers
                            combined_headers.append(header_text)
                
                        table_content = rows_found
                        
                        formatted_table = tabulate(table_content, headers=combined_headers, tablefmt="pretty")
                        textbox.insert(tk.END, formatted_table)


                    else:
                        # Generic text insert backup if a config key is missing
                        formatted_table = tabulate(rows_found, tablefmt="pretty")
                        textbox.insert(tk.END, formatted_table)
                else:
                    textbox.insert(tk.END, f"No records found for type: {msg_type}")

        except Exception as e:
            self.bsm_box.delete("1.0", tk.END)
            self.bsm_box.insert(tk.END, f"Error processing message tables: {e}")



class AboutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ebebed")
        self.controller = controller

        self.exit_btn = tk.Button(self, text="Exit", command=lambda: self.controller.show_page("MainPage"))
        self.exit_btn.pack(side="top", anchor="nw", padx=5, pady=(5,1), ipadx=8, ipady=1)
        add_hover_effect(self.exit_btn, "#f0f0f0", "#F9F9F9")

        # Title Layout
        self.title_label = tk.Label(self, text="About This Software Tool", font=("Calibri", 20, "bold"), bg="#ebebed", fg="#1A4480")
        self.title_label.pack(side="top", pady=(5, 20))

        # Description Body Block
        self.about_text = tk.Message(self,
                              text= "Use the browse buttons to select your designated transmitted and received PDML files. Then, select the appropriate vendors associated with each file from the dropdown menu. After running, you can save the comparison results to a CSV file and click on the 'View Car Map' button on the lower-right hand corner to automatically load the map.",
                              font=("Calibri", 12),
                              bg="#ebebed", width=750)
        self.about_text.pack(fill="x", expand=True, anchor="n")
        self.about_text.bind("<Configure>", lambda event: self.about_text.configure(width=event.width))

        self.credit_text = tk.Message(self,
                                      text="This tool was developed by Sedric Su under the mentorship of Eugene Song during the NIST SHIP 2026 internship program.",
                                      font=("Calibri", 12),
                                      bg="#ebebed",
                                      width=750)
        self.credit_text.pack(fill="x", expand=True, anchor="n")
        self.credit_text.bind("<Configure>", lambda event: self.credit_text.configure(width=event.width))



if __name__ == "__main__":
    root = tk.Tk()
    app = C_V2X_App(root)
    root.mainloop()

