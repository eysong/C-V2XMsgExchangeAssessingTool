import os
import subprocess
import sys
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, PhotoImage, StringVar, ttk
import tkinter.font as tkfont
from PIL import ImageTk, Image
import csv
from tabulate import tabulate

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

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

def enable_file_drop(widget, target_var, normal_bg="white", hover_bg="#d9e8fb"):
    if not DND_AVAILABLE:
        return

    widget.drop_target_register(DND_FILES)

    def on_enter(event):
        widget.config(background=hover_bg)

    def on_leave(event):
        widget.config(background=normal_bg)

    def on_drop(event):
        widget.config(background=normal_bg)
        paths = widget.tk.splitlist(event.data)
        if paths:
            target_var.set(paths[0])

    widget.dnd_bind("<<DropEnter>>", on_enter)
    widget.dnd_bind("<<DropLeave>>", on_leave)
    widget.dnd_bind("<<Drop>>", on_drop)


def create_drop_zone(parent, target_var, browse_command, height=44):
    NORMAL_BG = "#f3f5fa"
    HOVER_BG = "#d9e8fb"

    canvas = tk.Canvas(parent, height=height, bg=NORMAL_BG, highlightthickness=0, cursor="hand2")

    label_text = "Drag & drop PDML file here, or" if DND_AVAILABLE else "Select a PDML file:"
    label_font = tkfont.Font(family="Calibri", size=10)

    browse_btn = tk.Button(canvas, text="Browse...", command=browse_command)
    add_hover_effect(browse_btn, "#f0f0f0", "#E2E2E2")

    def redraw(event=None):
        canvas.delete("all")
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w < 2 or h < 2:
            return
        canvas.create_rectangle(2, 2, w - 2, h - 2, dash=(6, 3), outline="#8a94a6", width=2)

        text_width = label_font.measure(label_text)
        btn_width = browse_btn.winfo_reqwidth()
        gap = 8
        start_x = (w - (text_width + gap + btn_width)) / 2

        canvas.create_text(start_x, h / 2, text=label_text, anchor="w", fill="#5b6472", font=label_font)
        canvas.create_window(start_x + text_width + gap, h / 2, window=browse_btn, anchor="w")

    canvas.bind("<Configure>", redraw)
    canvas.bind("<Button-1>", lambda event: browse_command())

    enable_file_drop(canvas, target_var, normal_bg=NORMAL_BG, hover_bg=HOVER_BG)

    return canvas

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
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e3e9f8")
        self.controller = controller

        self.file1_placeholder = "Please select a Transmitted PDML file"
        self.file1_path = tk.StringVar(value=self.file1_placeholder)
        self.file2_placeholder = "Please select a Received PDML file"
        self.file2_path = tk.StringVar(value=self.file2_placeholder)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(12, weight=2)

        # Title row (pulls cached logo asset safely from controller)
        if self.controller.logo_photo:
            logo_label = tk.Label(self, image=self.controller.logo_photo, bg="#e3e9f8")
            logo_label.place(x=10, y=8)

        tk.Label(self, text="C-V2X Message Exchange Analyzer", font=("Calibri", 17, "bold"), bg="#e3e9f8").grid(row=0, column=1, padx=8, pady=8)

        # Button that takes user to the "ABOUT" screen
        self.about_btn_border = tk.Frame(self, highlightbackground="#005EA2", highlightcolor="#005EA2", highlightthickness=2, bd=0)
        self.about_btn_border.grid(row=0, column=2, padx=4, pady=8)
        self.about_btn = tk.Button(self.about_btn_border, text="About", command=lambda: self.controller.show_page("AboutPage"), fg="#00080E", bg="#f0f0f0", bd=0)
        self.about_btn.grid(row=0, column=2, padx=2, pady=2, sticky="e")
        add_hover_effect(self.about_btn, "#f0f0f0", "#F9F9F9")

        # Separator above the Tx PDML section
        ttk.Separator(self, orient="horizontal").grid(row=1, column=0, columnspan=3, padx=1, pady=(2, 2), sticky="ew")

        # File 1 row
        tk.Label(self, text="Transmitted PDML", font=("Calibri", 14), bg="#e3e9f8").grid(row=2, column=0, columnspan=3, padx=8, pady=(2, 2))
        self.entry1 = tk.Label(self, textvariable=self.file1_path, font=("Calibri", 12, "italic"), bg="#e3e9f8", fg="#1A365D", anchor="center", justify="center")
        self.entry1.grid(row=3, column=1, columnspan=1, padx=4, pady=(2, 8), sticky="ew")
        self.file1_path.trace_add("write", self.update_file1_font)

        self.dropzone1 = create_drop_zone(self, self.file1_path, self.browse_file1)
        self.dropzone1.grid(row=4, column=0, columnspan=3, padx=8, pady=(0, 8), sticky="ew")

        # Separator between the Tx and Rx sections
        ttk.Separator(self, orient="horizontal").grid(row=5, column=0, columnspan=3, padx=8, pady=(2, 2), sticky="ew")

        # File 2 row
        tk.Label(self, text="Received PDML", font=("Calibri", 14), bg="#e3e9f8").grid(row=6, column=0, columnspan=3, padx=8, pady=(2, 2))
        self.entry2 = tk.Label(self, textvariable=self.file2_path, font=("Calibri", 12, "italic"), bg="#e3e9f8", fg="#1A365D", anchor="center", justify="center")
        self.entry2.grid(row=7, column=1, columnspan=1, padx=4, pady=(2, 8), sticky="ew")
        self.file2_path.trace_add("write", self.update_file2_font)

        self.dropzone2 = create_drop_zone(self, self.file2_path, self.browse_file2)
        self.dropzone2.grid(row=8, column=0, columnspan=3, padx=8, pady=(0, 8), sticky="ew")

        # Separator below the Rx PDML section
        ttk.Separator(self, orient="horizontal").grid(row=9, column=0, columnspan=3, padx=8, pady=(2, 6), sticky="ew")

        # Compare button
        self.compare_btn = tk.Button(
            self, text="Compare", font=("Calibri", 16, "bold"), command=lambda: self.run_compare(),
            bg="#005EA2", fg="white", height=1, width=15)
        self.compare_btn.grid(row=10, column=0, columnspan=3, pady=8)
        add_hover_effect(self.compare_btn, "#005EA2", "#1A4480")

        # Output box
        tk.Label(self, text="Result:", font=("Calibri", 14), bg="#e3e9f8").grid(row=11, column=0, padx=8, ipadx=6, sticky="w")
        self.output_box = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=85, height=20)
        self.output_box.grid(row=12, column=0, columnspan=3, padx=8, pady=4, sticky="nsew")
        self.output_box.config(background="#f3f5fa")


        SMALL_BUTTON_BEFORE = "#1A365D"
        SMALL_BUTTON_AFTER = "#0F294A"
        # Action Buttons Layout (Row 13)
        self.save_btn = tk.Button(self, text="Save As CSV...", font=("Calibri", 12), command=self.save_output, bg=SMALL_BUTTON_BEFORE, fg="white", height=1, width=13)
        self.save_btn.grid(row=13, column=0, columnspan=3, padx=8, pady=8, sticky="s")
        add_hover_effect(self.save_btn, SMALL_BUTTON_BEFORE, SMALL_BUTTON_AFTER)


        self.map_btn = tk.Button(self, text="View Car Path", font=("Calibri", 12), command=self.view_map, bg=SMALL_BUTTON_BEFORE, fg="white", height=1, width=13)
        self.map_btn.grid(row=13, column=2, padx=8, pady=8, sticky="e")
        add_hover_effect(self.map_btn, SMALL_BUTTON_BEFORE, SMALL_BUTTON_AFTER)

        self.csv_btn = tk.Button(self, text="Read CSV File", font=("Calibri", 12), command=lambda: self.controller.show_page("CSVPage"), bg=SMALL_BUTTON_BEFORE, fg="white", height=1, width=13)
        self.csv_btn.grid(row=13, column=0, padx=8, pady=8, sticky="w")
        add_hover_effect(self.csv_btn, SMALL_BUTTON_BEFORE, SMALL_BUTTON_AFTER)

    def browse_file1(self):
        path = filedialog.askopenfilename(filetypes=[("PDML files", "*.pdml"), ("All files", "*.*")])
        if path:
            self.file1_path.set(path)

    def update_file1_font(self, *args):
        is_placeholder = self.file1_path.get() == self.file1_placeholder
        style = "italic" if is_placeholder else "roman"
        self.entry1.config(font=("Calibri", 12, style))

    def browse_file2(self):
        path = filedialog.askopenfilename(filetypes=[("PDML files", "*.pdml"), ("All files", "*.*")])
        if path:
            self.file2_path.set(path)

    def update_file2_font(self, *args):
        is_placeholder = self.file2_path.get() == self.file2_placeholder
        style = "italic" if is_placeholder else "roman"
        self.entry2.config(font=("Calibri", 12, style))

    def run_compare(self):
        f1 = self.file1_path.get().strip()
        f2 = self.file2_path.get().strip()

        if not os.path.isfile(f1) or not os.path.isfile(f2):
            messagebox.showwarning("Missing files", "Please select both PDML files first.")
            return
        if not os.path.isfile(MAIN_SCRIPT):
            messagebox.showerror("C-V2XMsgExchangeAssess.py not found", f"Could not find:\n{MAIN_SCRIPT}\n\n"
                                  "Edit MAIN_SCRIPT at the top of this file to point to your script.")
            return
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Running comparison, please wait...\n")
        self.controller.root.update_idletasks()

        try:
            result = subprocess.run(
                [sys.executable, MAIN_SCRIPT, f1, f2],
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


# Page to import & view formatted CSV of packets
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
        csv_placeholder = "Select or drag & drop a CSV file" if DND_AVAILABLE else "Select a CSV file"
        self.csv_path = tk.StringVar(value=csv_placeholder)
        self.csv_path.trace_add("write", self.auto_run_program)

        self.csv_entry = tk.Entry(self.scrollable_frame, textvariable=self.csv_path, width=60)
        self.csv_entry.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="ew")
        enable_file_drop(self.csv_entry, self.csv_path)

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

    #Helper scroll func.
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

        if not file_path or not os.path.isfile(file_path):
            return

        # Defining multi-row headers for different message types
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
                              text= "This is an open-source software tool that automatically analyzes the V2X message exchange process between the sender and receiver based on the dataset in the PDML format and allows for the visualization of the results on an interactive geographic map.\n\n\nUse the browse buttons or drag & drop to select your designated transmitted and received PDML files. After running, you can save the comparison results to a CSV file and click on the 'View Car Map' button on the lower-right hand corner to automatically load the map.",
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
    root = TkinterDnD.Tk() if DND_AVAILABLE else tk.Tk()
    app = C_V2X_App(root)
    root.mainloop()
