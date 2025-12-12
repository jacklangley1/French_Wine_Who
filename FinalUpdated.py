#!/usr/bin/env python
# coding: utf-8

# In[24]:


import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
import json


class AntibodyPanelManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Antibody Panel Manager")
        self.root.geometry("1200x800")
        
        # Data storage
        self.current_user = ""
        self.inventory = [
            {
                'id': 1,
                'antigen': 'CD3',
                'clone': 'UCHT1',
                'metal': '170Er',
                'concentration': 0.5,
                'antibodyPerTest': 1.0,
                'volumePerTest': 2.0,
                'stockVolume': 500.0,
                'notes': 'Core marker',
                'dateConjugated': '2024-10-15',
                'alertThreshold': 50.0
            },
            {
                'id': 2,
                'antigen': 'CD4',
                'clone': 'RPA-T4',
                'metal': '145Nd',
                'concentration': 0.5,
                'antibodyPerTest': 1.0,
                'volumePerTest': 2.0,
                'stockVolume': 450.0,
                'notes': 'T-helper cells',
                'dateConjugated': '2024-10-12',
                'alertThreshold': 50.0
            },
            {
                'id': 3,
                'antigen': 'CD8',
                'clone': 'SK1',
                'metal': '146Nd',
                'concentration': 0.5,
                'antibodyPerTest': 1.0,
                'volumePerTest': 2.0,
                'stockVolume': 35.0,
                'notes': 'Cytotoxic T cells',
                'dateConjugated': '2024-09-20',
                'alertThreshold': 50.0
            }
        ]
        
        self.panel_history = []
        self.saved_panels = []
        self.selected_panel = []
        self.cell_count = 4.0
        self.panel_name = ""
        self.search_term = ""
        self._refresh_pending = False
        self.antibody_cards = {}
        
        self.show_login()
    
    def show_login(self):
        """Show login screen"""
        login_frame = tk.Frame(self.root, bg='black')
        login_frame.pack(fill='both', expand=True)
        
        center_frame = tk.Frame(login_frame, bg='black', padx=40, pady=40)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(center_frame, text="Welcome", font=('Arial', 24, 'bold'), 
                bg='black').pack(pady=(0, 20))
        
        tk.Label(center_frame, text="Please enter your name to continue:", 
                font=('Arial', 16), bg='black').pack()
        
        name_entry = tk.Entry(center_frame, font=('Arial', 16), width=30, bg= 'white', fg = 'black')
        name_entry.pack(pady=20, ipady=5)
        name_entry.focus()
        
        def on_submit():
            name = name_entry.get().strip()
            if name:
                self.current_user = name
                login_frame.destroy()
                self.create_main_interface()
            else:
                messagebox.showwarning("Name Required", "Please enter your name")
        
        name_entry.bind('<Return>', lambda e: on_submit())
        
        tk.Button(center_frame, text="Continue", command=on_submit,
                 bg='#4F46E5', fg='grey', font=('Arial', 12, 'bold'),
                 padx=40, pady=10, cursor='hand2').pack()
    
    def create_main_interface(self):
        """Create main application interface"""
        # Header
        header = tk.Frame(self.root, bg='black', pady=15)
        header.pack(fill='x')
        
        tk.Label(header, text="Antibody Panel Manager", 
                font=('Arial', 30, 'bold'), bg='black').pack(side='left', padx=20)
        
        tk.Label(header, text=f"Logged in as: {self.current_user}", 
                font=('Arial', 20), bg='black').pack(side='left')
        
        # Alert indicator
        self.alert_label = tk.Label(header, text="", font=('Arial', 20, 'bold'),
                                   bg='black', fg='red', padx=10, pady=5)
        self.update_alerts()
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_build_panel_tab()
        self.create_saved_panels_tab()
        self.create_inventory_tab()
        self.create_history_tab()
        self.create_add_antibody_tab()
    
    def update_alerts(self):
        """Update low stock alerts"""
        low_stock = [ab for ab in self.inventory 
                    if ab['stockVolume'] <= ab['alertThreshold']]
        if low_stock:
            self.alert_label.config(text=f"⚠ {len(low_stock)} Low Stock Alert(s)")
            self.alert_label.pack(side='right', padx=20)
        else:
            self.alert_label.pack_forget()
    
    def create_build_panel_tab(self):
        """Create build panel tab with 3-column antibody grid and right-side summary"""
        frame = tk.Frame(self.notebook, bg='#F9FAFB')
        self.notebook.add(frame, text='Build Panel')

        # ---------------- Top section: Panel info ----------------
        top_frame = tk.Frame(frame, bg='black', padx=20, pady=15)
        top_frame.pack(fill='x', padx=10, pady=10)

        # Panel name
        tk.Label(top_frame, text="Panel Name:", bg='black', font=('Arial', 14, 'bold')).grid(row=0, column=0, sticky='w', pady=5, ipady=10)
        self.panel_name_var = tk.StringVar()
        tk.Entry(top_frame, textvariable=self.panel_name_var, font=('Arial', 14), bg='white', fg='black', width=30).grid(row=0, column=1, padx=10, ipady=6)

        # Cell count
        tk.Label(top_frame, text="Cell Count (millions):", bg='black', font=('Arial', 14, 'bold')).grid(row=0, column=2, sticky='w', padx=(20,0))
        self.cell_count_var = tk.DoubleVar(value=4.0)
        tk.Entry(top_frame, textvariable=self.cell_count_var, font=('Arial', 14), bg='white', fg='black', width=15).grid(row=0, column=3, padx=10, ipady=6)

        tk.Label(top_frame, text="Standard: 1x strength for 4M cells", font=('Arial', 14), bg='black', fg='white').grid(row=1, column=0, columnspan=4, sticky='w', pady=(5,0))

        # ---------------- Search bar ----------------
        search_frame = tk.Frame(frame, bg='black')
        search_frame.pack(fill='x', padx=15, pady=(0,10))
    
        tk.Label(search_frame, text="🔍", bg='black', font=('Arial', 14)).pack(side='left', padx=(0,5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh_antibody_list())
        tk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 14), bg='white', fg='black', width=50).pack(side='left')
        tk.Label(search_frame, text="Search by antigen, metal, or clone", font=('Arial', 14), bg='black', fg='white').pack(side='left', padx=10)

         # ---------------- Main horizontal frame ----------------
        # ---------------- Main horizontal frame ----------------
        main_frame = tk.Frame(frame, bg='#F9FAFB')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ---------------- Antibody panel (left, 80%) ----------------
        antibody_frame = tk.Frame(main_frame, bg='#F9FAFB')
        antibody_frame.grid(row=0, column=0, sticky='nsew')
        
        # Make main frame columns proportional
        main_frame.grid_columnconfigure(0, weight=4)  # antibody panel
        main_frame.grid_columnconfigure(1, weight=0)  # summary panel
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Scroll container for canvas + scrollbar
        scroll_container = tk.Frame(antibody_frame, bg='#F9FAFB')
        scroll_container.pack(fill='both', expand=True)
        
        # Canvas inside container
        canvas = tk.Canvas(scroll_container, bg='#F9FAFB', highlightthickness=0)
        canvas.pack(side='left', fill='both', expand=True)
        
        # Scrollbar to the right of canvas, leaving space from summary panel
        scrollbar = ttk.Scrollbar(scroll_container, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame holding antibody cards
        self.antibody_list_frame = tk.Frame(canvas, bg='#F9FAFB')
        canvas.create_window((0, 0), window=self.antibody_list_frame, anchor='nw')
        
        # Update scroll region dynamically
        self.antibody_list_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        # Configure 3-column grid inside antibody list
        for c in range(3):
            self.antibody_list_frame.grid_columnconfigure(c, weight=1)
        
        # ---------------- Adjust canvas width so scrollbar is left of summary ----------------
        def resize_canvas(event):
            canvas.config(width=event.width - scrollbar.winfo_reqwidth() - 20)  # 20px gap from summary panel
        
        scroll_container.bind('<Configure>', resize_canvas)
        
        # ---------------- Summary panel (right, 20%) ----------------
        self.summary_frame = tk.Frame(
            main_frame,
            bg='black',
            highlightbackground='#10B981',
            highlightthickness=2,
            width=250  # fixed width
        )
        self.summary_frame.grid(row=0, column=1, sticky='ns', padx=(30,0))  # move slightly left from panel edge
        
        # Initial load
        self.refresh_antibody_list()
        self.update_summary()

        
    def refresh_antibody_list(self):
        """Refresh antibody grid + separate Extracellular vs Intracellular"""
    
        # Clear previous cards safely
        for ab_id, frame in list(self.antibody_cards.items()):
            frame.destroy()
            del self.antibody_cards[ab_id]
    
        search = self.search_var.get().lower()
    
        # Filter + sort results
        import re
        def metal_number(ab):
            m = re.match(r"(\d+)", ab['metal'])
            return int(m.group(1)) if m else 0
    
        filtered = [ab for ab in self.inventory if
                    search in ab['antigen'].lower() or
                    search in ab['metal'].lower() or
                    search in ab['clone'].lower()]
        filtered.sort(key=lambda x: (x['antigen'].lower(), metal_number(x)))
    
        # Separate Extracellular vs Intracellular
        extracellular = [ab for ab in filtered if ab.get("stainType", "Extracellular") == "Extracellular"]
        intracellular = [ab for ab in filtered if ab.get("stainType", "Extracellular") == "Intracellular"]
    
        columns = 3
        row_ptr = 0
    
        # ░░ Extracellular Section ░░
        if extracellular:
            tk.Label(self.antibody_list_frame,
                     text="Extracellular Antibodies",
                     font=('Arial', 16, 'bold'),
                     bg='#F9FAFB', fg='black').grid(row=row_ptr, column=0,
                                                     columnspan=columns, pady=(0, 10))
            row_ptr += 1
    
            for i, ab in enumerate(extracellular):
                r = row_ptr + (i // columns)
                c = i % columns
                self.create_antibody_card(ab, row=r, col=c)
    
            row_ptr += (len(extracellular) + columns - 1) // columns  # ceil division
    
        # ░░ Intracellular Section ░░
        if intracellular:
            tk.Label(self.antibody_list_frame,
                     text="Intracellular Antibodies (0.2x)",
                     font=('Arial', 16, 'bold'),
                     bg='#F9FAFB', fg='firebrick').grid(row=row_ptr, column=0,
                                                        columnspan=columns, pady=(20, 5))
            row_ptr += 1
    
            for i, ab in enumerate(intracellular):
                r = row_ptr + (i // columns)
                c = i % columns
                self.create_antibody_card(ab, row=r, col=c)


    def create_antibody_card(self, antibody, row=0, col=0):
        """Create or update an antibody card in the 3-column grid"""
        card_id = antibody['id']

        # If card already exists, just update it
        if card_id in self.antibody_cards:
            self.update_antibody_card(antibody)
            return

        # Create card frame
        frame = tk.Frame(self.antibody_list_frame, highlightthickness=3, padx=15, pady=10)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='n')  # Grid placement

        # Store for later updates
        self.antibody_cards[card_id] = frame

        # Build inner card UI
        self.update_antibody_card(antibody)

    def update_antibody_card(self, antibody):
        """Update card UI instead of rebuilding full list"""
        frame = self.antibody_cards.get(antibody["id"])
        if frame is None:
            return  # safety fallback

        # Determine state
        is_selected = any(s['id'] == antibody['id'] for s in self.selected_panel)
        is_low_stock = antibody['stockVolume'] <= antibody['alertThreshold']

        # Update frame appearance
        frame.configure(
            bg='#DDD6FE' if is_selected else 'black',
            highlightbackground='red' if is_low_stock else '#D1D5DB',
            highlightthickness=3
        )

        # ---- Clear and rebuild card interior (but not the whole widget) ----
        for widget in frame.winfo_children():
            widget.destroy()

        # --- Checkbox toggle ---
        var = tk.BooleanVar(value=is_selected)

        def toggle():
            if var.get():
                if not any(s['id'] == antibody['id'] for s in self.selected_panel):
                    self.selected_panel.append(antibody)
            else:
                self.selected_panel = [s for s in self.selected_panel if s['id'] != antibody['id']]

            # 🔥 Only update this one card + summary
            self.update_antibody_card(antibody)
            self.update_summary()

        chk = tk.Checkbutton(frame, variable=var, command=toggle, bg=frame['bg'])
        chk.pack(side='right')

        # --- Header ---
        header_frame = tk.Frame(frame, bg=frame['bg'])
        header_frame.pack(fill='x')

        tk.Label(header_frame,
                 text=f"{antibody['antigen']} - {antibody['metal']}",
                 font=('Arial', 18, 'bold'), bg=frame['bg'], fg='white').pack(side='left')

        if is_low_stock:
            tk.Label(header_frame, text="LOW STOCK", bg='red', fg='white',
                     font=('Arial', 12, 'bold'), padx=5, pady=2).pack(side='left', padx=10)

        # --- Details ---
        details_frame = tk.Frame(frame, bg=frame['bg'])
        details_frame.pack(fill='x', pady=(5, 0))

        details = [
            f"Clone: {antibody['clone']}",
            f"Concentration: {antibody['concentration']} mg/mL",
            f"Stock: {antibody['stockVolume']:.1f} µL",
            f"Vol/Test: {antibody['volumePerTest']} µL",
            f"Date: {antibody['dateConjugated']}"
        ]

        for i, detail in enumerate(details):
            tk.Label(details_frame, text=detail, font=('Arial', 9),
                     bg=frame['bg'], fg='white').grid(row=i//2, column=i%2, sticky='w', padx=(0,20))

        # --- Notes (if present) ---
        if antibody['notes']:
            tk.Label(frame, text=antibody['notes'], font=('Arial', 9, 'italic'),
                     bg=frame['bg'], fg='white').pack(anchor='w', pady=(5,0))

    def update_summary(self):
        """Update panel summary"""
        # Clear previous summary widgets
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        if not self.selected_panel:
            return

        # Title
        tk.Label(self.summary_frame, 
                 text=f"Panel Summary ({len(self.selected_panel)} antibodies selected)",
                 font=('Arial', 14, 'bold'), bg='black', fg='white'
                ).grid(row=0, column=0, columnspan=2, sticky='w', padx=15, pady=10)

        # List selected antibodies
        for i, ab in enumerate(self.selected_panel, start=1):
            volume = self.calculate_volume(ab)
            item_frame = tk.Frame(self.summary_frame, bg='white', padx=10, pady=5)
            item_frame.grid(row=i, column=0, columnspan=2, sticky='ew', padx=15, pady=2)

            tk.Label(item_frame, text=f"{ab['antigen']} - {ab['metal']}", 
                     font=('Arial', 14), bg='white', fg='black').pack(side='left')
            tk.Label(item_frame, text=f"{volume:.2f} µL will be used",
                     font=('Arial', 14, 'bold'), bg='white', fg='#4F46E5').pack(side='right')

        # Buttons
        button_frame = tk.Frame(self.summary_frame, bg='black')
        button_frame.grid(row=i+1, column=0, columnspan=2, sticky='ew', padx=15, pady=10)

        tk.Button(button_frame, text="💾 Save Panel", command=self.save_panel,
                  bg='white', fg='black', font=('Arial', 11, 'bold'),
                  padx=20, pady=8, cursor='hand2').pack(side='left', padx=5)

        tk.Button(button_frame, text="✓ Execute Panel", command=self.execute_panel,
                  bg='white', fg='black', font=('Arial', 11, 'bold'),
                  padx=20, pady=8, cursor='hand2').pack(side='left', padx=5)
        
    def calculate_volume(self, antibody):
        """Volume scales with cell count — intracellular uses 0.2x volume"""
        base = antibody['volumePerTest']
        ratio = self.cell_count_var.get()/4.0
    
        if antibody.get("stainType","Extracellular")=="Intracellular":
            base *= 0.2     # 🔥 automatic intracellular scaling
    
        return base * ratio

        
    def save_panel(self):
        """Save current panel configuration with name validation"""
        from tkinter import messagebox
        from datetime import datetime
        
        # Must have selected antibodies
        if not self.selected_panel:
            messagebox.showwarning("No Selection", 
                                   "⚠ Please select at least one antibody before saving.")
            return
    
        entered_name = self.panel_name_var.get().strip()
    
        # 🔴 No name entered
        if not entered_name:
            messagebox.showwarning("Missing Panel Name",
                                   "⚠ You must enter a panel name before saving.")
            return
    
        # 🔴 Check duplicate name in saved_panels
        existing_names = [p['name'].lower() for p in self.saved_panels]
        if entered_name.lower() in existing_names:
            messagebox.showerror("Duplicate Name",
                                 f"🚫 A panel named '{entered_name}' already exists.\n"
                                 "Please choose a different name.")
            return
    
        # Passed validation → save panel
        panel = {
            'id': int(datetime.now().timestamp() * 1000),
            'name': entered_name,
            'antibodyIds': [ab['id'] for ab in self.selected_panel],
            'createdBy': self.current_user,
            'createdAt': datetime.now().isoformat()
        }
    
        self.saved_panels.append(panel)
        self.refresh_saved_panels_tab()
    
        messagebox.showinfo("Success",
                            f"💾 Panel \"{entered_name}\" has been saved successfully!")

    def execute_panel(self):
        """Execute panel ONLY if sufficient antibody volume exists and unique in executed panels"""
    
        if not self.selected_panel:
            messagebox.showwarning("No Selection",
                                   "Please select at least one antibody.")
            return
    
        # --- PANEL NAME VALIDATION ---
        entered_name = self.panel_name_var.get().strip()
    
        if not entered_name:
            messagebox.showwarning("Missing Panel Name",
                                   "⚠ You must enter a panel name before executing.")
            return
    
        # Check if name already exists in executed panels only
        existing_names = [h['panelName'].lower() for h in self.panel_history]
        if entered_name.lower() in existing_names:
            messagebox.showerror("Duplicate Name",
                                 f"🚫 A panel named '{entered_name}' has already been executed.\n"
                                 "Please choose a different name before executing.")
            return
    
        # --- STOCK VALIDATION BEFORE EXECUTION ---
        insufficient = []  # store failed antibodies
    
        for ab in self.selected_panel:
            required = self.calculate_volume(ab)
            available = ab["stockVolume"]
    
            if required > available:
                insufficient.append((ab["antigen"], ab["metal"], required, available))
    
        if insufficient:
            msg = "🚨 Not enough antibody for panel execution:\n\n"
            for antigen, metal, req, avail in insufficient:
                msg += f"• {antigen} ({metal}) → Need {req:.2f}µL, Only {avail:.2f}µL available\n"
    
            messagebox.showerror("Execution Blocked", msg)
            return  # NO STOCK IS REMOVED
    
        # --- CONFIRMATION DIALOG ---
        confirm = messagebox.askyesno(
            "Confirm Panel Execution",
            f"Are you sure you want to execute the panel '{entered_name}'?\n"
            "This will reduce antibody stock volumes accordingly."
        )
    
        if not confirm:
            return  # User cancelled execution
    
        # --- EXECUTE PANEL ---
        for item in self.inventory:
            for selected in self.selected_panel:
                if item['id'] == selected['id']:
                    item['stockVolume'] -= self.calculate_volume(selected)
    
        # Record history
        history_entry = {
            'id': int(datetime.now().timestamp() * 1000),
            'timestamp': datetime.now().isoformat(),
            'user': self.current_user,
            'panelName': entered_name,
            'cellCount': self.cell_count_var.get(),
            'antibodies': [{
                'antigen': ab['antigen'],
                'metal': ab['metal'],
                'volumeUsed': self.calculate_volume(ab)
            } for ab in self.selected_panel]
        }
        self.panel_history.insert(0, history_entry)
    
        # Reset UI
        self.selected_panel = []
        self.panel_name_var.set('')
        self.cell_count_var.set(4.0)
    
        self.refresh_antibody_list()
        self.update_summary()
        self.update_alerts()
        self.refresh_inventory_tab()
        self.refresh_history_tab()
    
        messagebox.showinfo("Success", 
                            "Panel executed ✔ Stock volumes updated.")
    


    def create_saved_panels_tab(self):
        self.saved_panels_frame = tk.Frame(self.notebook, bg='#F9FAFB')
        self.notebook.add(self.saved_panels_frame, text='Saved Panels')
    
        # *******************************
        # TOP BAR (STATIC — never destroyed)
        # *******************************
        top_row = tk.Frame(self.saved_panels_frame, bg="#F9FAFB")
        top_row.pack(fill='x', padx=10, pady=(8,4))
    
        tk.Label(top_row, text="Search:", bg="black",
                 font=('Arial', 12)).pack(side='left')
    
        self.saved_search_var = tk.StringVar()
        entry = tk.Entry(top_row, textvariable=self.saved_search_var,
                         font=('Arial', 12), width=30)
        entry.pack(side='left', padx=8)
    
        # Live update on typing
        self.saved_search_var.trace_add(
            "write", lambda *_: self.refresh_saved_panels_tab()
        )
    
        # *********************************
        # LIST AREA (this part refreshes)
        # *********************************
        self.saved_panels_list_frame = tk.Frame(self.saved_panels_frame, bg="#F9FAFB")
        self.saved_panels_list_frame.pack(fill="both", expand=True)
    
        self.refresh_saved_panels_tab()


    def refresh_saved_panels_tab(self):
        """Refresh saved panels display with alphabetical order + search + grid"""
    
        # CLEAR ONLY THE LISTING AREA — ***NOT THE SEARCH BAR***
        for widget in self.saved_panels_list_frame.winfo_children():
            widget.destroy()
    
        # ------------- If none exist -------------
        if not self.saved_panels:
            tk.Label(self.saved_panels_list_frame, text="No saved panels yet",
                     font=('Arial',14), bg='#F9FAFB', fg='#999').pack(pady=20)
            return
    
        # ------------- Scrollable Canvas -------------
        canvas = tk.Canvas(self.saved_panels_list_frame, bg='#F9FAFB', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.saved_panels_list_frame, orient='vertical', command=canvas.yview)
        content_frame = tk.Frame(canvas, bg='#F9FAFB')
    
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0,0), window=content_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))
    
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set)
    
        # ------------- Sort alphabetically -------------
        sorted_panels = sorted(self.saved_panels, key=lambda p: p['name'].lower())
    
        # ------------- Apply search filter -------------
        query = self.saved_search_var.get().lower()
        filtered = [p for p in sorted_panels if query in p['name'].lower()]
    
        if not filtered:
            tk.Label(self.saved_panels_list_frame, text="No panels match search",
                     font=("Arial",13), bg="#F9FAFB", fg="#777").pack(pady=25)
            return
    
        # ------------- Grid render -------------
        NUM_COLS = 3
        for idx, panel in enumerate(filtered):
            row, col = divmod(idx, NUM_COLS)
            self.create_saved_panel_card(content_frame, panel, row, col)

    def create_saved_panel_card(self, parent, panel, row, col):
        """Create a saved panel card (grid-compatible)"""
    
        frame = tk.Frame(
            parent,
            bg='white',
            highlightbackground='#D1D5DB',
            highlightthickness=2,
            padx=15,
            pady=10
        )

        # PLACE CARD IN GRID, NOT PACK
        frame.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

        # ----- Header -----
        header_frame = tk.Frame(frame, bg='white')
        header_frame.pack(fill='x')

        tk.Label(
            header_frame,
            text=panel['name'],
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='black'
        ).pack(side='left')

        date = datetime.fromisoformat(panel['createdAt']).strftime('%d-%m-%Y')

        tk.Label(
            header_frame,
            text=f"Created by {panel['createdBy']} • {date}",
            font=('Arial', 9),
            bg='white',
            fg='#666'
        ).pack(side='left', padx=10)

        # ----- Buttons -----
        btn_frame = tk.Frame(header_frame, bg='white')
        btn_frame.pack(side='right')

        tk.Button(
            btn_frame,
            text="Load",
            command=lambda: self.load_panel(panel),
            bg='white',
            fg='black',
            font=('Arial', 10),
            padx=15,
            pady=5,
            cursor='hand2'
        ).pack(side='left', padx=2)

        tk.Button(
            btn_frame,
            text="🗑",
            command=lambda: self.delete_saved_panel(panel['id']),
            bg='white',
            fg='white',
            font=('Arial', 10),
            padx=8,
            pady=5,
            cursor='hand2'
        ).pack(side='left', padx=2)

        # ----- Antibody details -----
        panel_abs = [ab for ab in self.inventory if ab['id'] in panel['antibodyIds']]
        ab_text = ', '.join([f"{ab['antigen']} - {ab['metal']}" for ab in panel_abs])

        details_frame = tk.Frame(frame, bg='#222222', padx=10, pady=8)
        details_frame.pack(fill='x', pady=(10, 0))

        tk.Label(
            details_frame,
            text=f"Antibodies ({len(panel_abs)}):",
            font=('Arial', 10, 'bold'),
            bg='#222222',
            fg='white'
        ).pack(anchor='w')

        tk.Label(
            details_frame,
            text=ab_text,
            font=('Arial', 9),
            bg='#222222',
            fg='white',
            wraplength=300,   # Adjust to your card width
            justify='left'
        ).pack(anchor='w')

    
    def load_panel(self, panel):
        """Load a saved panel"""
        self.selected_panel = [ab for ab in self.inventory 
                              if ab['id'] in panel['antibodyIds']]
        self.panel_name_var.set(panel['name'])
        self.notebook.select(0)  # Switch to Build Panel tab
        self.refresh_antibody_list()
        self.update_summary()
    
    def delete_saved_panel(self, panel_id):
        """Delete a saved panel"""
        if messagebox.askyesno("Confirm Delete",
                              "Are you sure you want to delete this saved panel?"):
            self.saved_panels = [p for p in self.saved_panels if p['id'] != panel_id]
            self.refresh_saved_panels_tab()


    def create_inventory_tab(self):
        """Create inventory management tab"""
        self.inventory_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.inventory_frame, text='Manage Inventory')

        # Search and filter variables
        self.inventory_search_var = tk.StringVar()
        self.show_low_stock_only = tk.BooleanVar(value=False)

        # Header
        header = tk.Frame(self.inventory_frame, bg='white')
        header.pack(fill='x', padx=10, pady=10)

        tk.Label(header, text="Current Inventory", font=('Arial', 20, 'bold'),
                 bg='white', fg='black').pack()

        tk.Button(header, text="📥 Export to CSV", command=self.export_inventory,
                  bg='white', fg='black', font=('Arial', 10, 'bold'),
                  padx=15, pady=5, cursor='hand2').pack(side='right')

        # Search and filter row
        filter_frame = tk.Frame(self.inventory_frame, bg='#F9FAFB')
        filter_frame.pack(fill='x', padx=10, pady=(0, 10))

        search_container = tk.Frame(filter_frame, bg='black')
        search_container.pack(side='left', fill='x', expand=True)

        tk.Label(search_container, text="🔍", bg='black', font=('Arial', 12)).pack(side='left', padx=(0, 5))
        search_entry = tk.Entry(search_container, textvariable=self.inventory_search_var,
                                font=('Arial', 10), width=40, bg='white', fg='black')
        search_entry.pack(side='left')

        tk.Label(search_container, text="Search by antigen or metal",
                 font=('Arial', 9), bg='black', fg='white').pack(side='left', padx=10)

        # Low stock filter button
        low_stock_btn = tk.Button(
            filter_frame,
            text="⚠ Show Low Stock Only",
            command=lambda: self.show_low_stock_only.set(not self.show_low_stock_only.get()),
            bg='black', fg='black',
            font=('Arial', 10, 'bold'),
            padx=15, pady=5, cursor='hand2'
        )
        low_stock_btn.pack(side='right', padx=(10, 0))

        # Trace changes to refresh table only
        self.inventory_search_var.trace('w', lambda *args: self.refresh_inventory_tab())
        self.show_low_stock_only.trace('w', lambda *args: self.refresh_inventory_tab())

        # Table container (persistent)
        self.inventory_table_frame = tk.Frame(self.inventory_frame)
        self.inventory_table_frame.pack(fill='both', expand=True, padx=10, pady=(2, 10))

        # Initial table load
        self.refresh_inventory_tab()

    def refresh_inventory_tab(self):
        """Refresh inventory table with in-place editing and delete button."""
        
        # Clear previous table
        for widget in self.inventory_table_frame.winfo_children():
            widget.destroy()
    
        # Filter inventory
        search_term = self.inventory_search_var.get().lower()
        filtered_inventory = []
        for ab in self.inventory:
            search_match = (search_term == '' or
                            search_term in ab['antigen'].lower() or
                            search_term in ab['metal'].lower())
            is_low_stock = ab['stockVolume'] <= ab['alertThreshold']
            low_stock_match = not self.show_low_stock_only.get() or is_low_stock
    
            if search_match and low_stock_match:
                filtered_inventory.append(ab)
            
        # Sort alphabetically by antigen
        filtered_inventory.sort(key=lambda x: x['antigen'].lower())
    
        # Table columns
        columns = ('Antigen', 'Metal', 'Clone', 'Conc', 'Stock',
                   'Vol/Test', 'Date', 'Notes')
    
        tree = ttk.Treeview(self.inventory_table_frame, columns=columns, show='headings', height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100 if col != 'Notes' else 200)
    
        # Populate table
        for ab in filtered_inventory:
            values = (
                ab['antigen'], ab['metal'], ab['clone'], ab['concentration'],
                f"{ab['stockVolume']:.1f}", ab['volumePerTest'], ab['dateConjugated'], ab['notes']
            )
            tags = ('low_stock',) if ab['stockVolume'] <= ab['alertThreshold'] else ()
            tree.insert('', 'end', values=values, tags=tags)
    
        tree.tag_configure('low_stock', background='red')
    
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.inventory_table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
        # ----------------- In-place editing -----------------
        def on_double_click(event):
            item_id = tree.identify_row(event.y)
            column = tree.identify_column(event.x)
            if not item_id or not column:
                return
    
            col_idx = int(column.replace("#", "")) - 1
            x, y, width, height = tree.bbox(item_id, column)
            value = tree.set(item_id, column)
    
            entry = tk.Entry(tree)
            entry.place(x=x, y=y, width=width, height=height)
            entry.insert(0, value)
            entry.focus_set()
    
            def save_edit(event=None):
                new_value = entry.get()
                tree.set(item_id, column, new_value)
                # Update underlying inventory
                idx = tree.index(item_id)
                ab = filtered_inventory[idx]
                if col_idx == 0:  # Antigen
                    ab['antigen'] = new_value
                elif col_idx == 1:  # Metal
                    ab['metal'] = new_value
                elif col_idx == 2:  # Clone
                    ab['clone'] = new_value
                elif col_idx == 3:  # Conc
                    try: ab['concentration'] = float(new_value)
                    except ValueError: pass
                elif col_idx == 4:  # Stock
                    try: ab['stockVolume'] = float(new_value)
                    except ValueError: pass
                elif col_idx == 5:  # Vol/Test
                    try: ab['volumePerTest'] = float(new_value)
                    except ValueError: pass
                elif col_idx == 6:  # Date
                    ab['dateConjugated'] = new_value
                elif col_idx == 7:  # Notes
                    ab['notes'] = new_value
                entry.destroy()
                self.refresh_inventory_tab()
    
            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", lambda e: entry.destroy())
    
        tree.bind("<Double-1>", on_double_click)
    
        # ----------------- Delete Button -----------------
        btn_frame = tk.Frame(self.inventory_table_frame, bg="#F9FAFB")
        btn_frame.pack(fill='x', pady=5)
    
        tk.Button(btn_frame, text="Delete Selected", bg="#ff5c5c", fg="black",
                  command=lambda: self.delete_selected_antibody(tree, filtered_inventory)).pack(side='left', padx=5)
    
    def delete_selected_antibody(self, tree, visible_inventory):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an antibody to delete.")
            return
    
        idx = tree.index(selected[0])
        ab = visible_inventory[idx]
    
        if messagebox.askyesno("Delete Antibody",
                               f"Remove {ab['antigen']} ({ab['metal']}) from inventory?"):
            self.inventory.remove(ab)
        self.refresh_inventory_tab()


    def export_inventory(self):
        """Export inventory to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='antibody_inventory.csv'
        )
        
        if filename:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Antigen', 'Clone', 'Metal', 'Concentration (mg/mL)',
                               'Antibody per Test (µg)', 'Volume per Test (µL)',
                               'Stock Volume (µL)', 'Alert Threshold (µL)',
                               'Date Conjugated', 'Notes'])
                
                for ab in self.inventory:
                    writer.writerow([
                        ab['antigen'], ab['clone'], ab['metal'],
                        ab['concentration'], ab['antibodyPerTest'],
                        ab['volumePerTest'], f"{ab['stockVolume']:.2f}",
                        ab['alertThreshold'], ab['dateConjugated'], ab['notes']
                    ])
            
            messagebox.showinfo("Success", f"Inventory exported to {filename}")
    
    def create_history_tab(self):
        """Create history tab"""
        self.history_frame = tk.Frame(self.notebook, bg='#F9FAFB')
        self.notebook.add(self.history_frame, text='History')
        self.refresh_history_tab()
    
    def refresh_history_tab(self):
        """Display history in 3-column grid, sorted alphabetically"""
        for widget in self.history_frame.winfo_children():
            widget.destroy()
    
        # Header row
        header = tk.Frame(self.history_frame, bg='#F9FAFB')
        header.pack(fill='x', padx=10, pady=10)
    
        tk.Label(header, text="Panel Execution History",
                 font=('Arial', 18, 'bold'), bg='#F9FAFB', fg='black').pack(side='left')
    
        if self.panel_history:
            tk.Button(header, text="📥 Export to CSV", command=self.export_history,
                      bg='white', fg='black', relief='raised',
                      font=('Arial', 10), padx=12, pady=5).pack(side='right')
    
        if not self.panel_history:
            tk.Label(self.history_frame, text="No panels executed yet",
                     font=('Arial', 14), bg='#F9FAFB', fg='#999').pack(expand=True)
            return
    
        # SCROLL CANVAS
        canvas = tk.Canvas(self.history_frame, bg='#F9FAFB', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.history_frame, orient='vertical', command=canvas.yview)
        content = tk.Frame(canvas, bg='#F9FAFB')
    
        content.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win = canvas.create_window((0,0), window=content, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
    
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set)
    
        # 🟦 Display in 3-column grid
        NUM_COLS = 3
        sorted_history = sorted(self.panel_history, key=lambda x: x['panelName'].lower())
    
    # in refresh_history_tab
        for i, entry in enumerate(sorted_history):
            r, c = divmod(i, NUM_COLS)
            self.create_history_card(content, entry).grid(row=r, column=c, padx=10, pady=10, sticky='nsew')
            content.grid_columnconfigure(c, weight=1)
    
    def create_history_card(self, parent, entry):
        frame = tk.Frame(parent, bg='white', width=300, height=180, padx=12, pady=10,
                         highlightbackground='#D1D5DB', highlightthickness=1)

    
        ## TITLE ROW
        top = tk.Frame(frame, bg='white')
        top.pack(fill='x')
    
        tk.Label(top, text=entry['panelName'], font=('Arial', 18, 'bold'),
                 bg='white', fg='#111').pack(side='left')
    
        timestamp = datetime.fromisoformat(entry['timestamp'])
        tk.Label(top, text=timestamp.strftime("%d %b %Y • %H:%M"),
                 font=('Arial',9), bg='white', fg='#666').pack(side='left', padx=8)
    
        # ↩ Undo + Delete
        btns = tk.Frame(top, bg='white')
        btns.pack(side='right')
    
        tk.Button(btns, text="↩ Undo", command=lambda e=entry:self.undo_panel(e),
                  bg='white', fg='black', font=('Arial',9,'bold'), width=6).pack(side='left', padx=3)
    
        tk.Button(btns, text="🗑", command=lambda e=entry:self.delete_history_panel(e),
                  bg='white', fg='black', font=('Arial',9,'bold'), width=4).pack(side='left', padx=3)
    
        # --- ANTIBODY GRID (2-col) ---
        body = tk.Frame(frame, bg='white')
        body.pack(fill='x', pady=(5,0))
    
        for i, ab in enumerate(entry['antibodies']):
            r,c = divmod(i,2)
            cell = tk.Frame(body, bg='#F4F6F8', padx=5, pady=2)
            cell.grid(row=r, column=c, sticky='ew', padx=4, pady=3)
    
            tk.Label(cell, text=f"{ab['antigen']} ({ab['metal']})",
                     font=('Arial',9), bg='#F4F6F8', fg='black').pack(side='left')
    
            tk.Label(cell, text=f"{ab['volumeUsed']:.2f} µL",
                     font=('Arial',9,'bold'), bg='#F4F6F8', fg='#0A74DA').pack(side='right')
    
        # Total Volume
        total = sum(a['volumeUsed'] for a in entry['antibodies'])
        tk.Label(frame, text=f"Total: {total:.2f} µL", font=('Arial',10,'bold'),
                 bg='white', fg='#0A74DA').pack(pady=(8,0))
    
        return frame

        
    def delete_history_panel(self, entry):
        """Remove a panel from history without changing stock"""
        if messagebox.askyesno("Confirm Delete", f"Delete panel '{entry['panelName']}'?"):
            self.panel_history = [e for e in self.panel_history if e['id'] != entry['id']]
            self.refresh_history_tab()

    
    def undo_panel(self, panel):
        """Undo an executed panel, restoring antibody stock volumes"""
        if not messagebox.askyesno("Undo Panel",
                                   f"Are you sure you want to undo '{panel['panelName']}'?"):
            return
        
        # Restore stock volumes
        for ab_used in panel['antibodies']:
            for ab in self.inventory:
                if ab['antigen'] == ab_used['antigen'] and ab['metal'] == ab_used['metal']:
                    ab['stockVolume'] += ab_used['volumeUsed']
        
        # Remove from history
        self.panel_history = [p for p in self.panel_history if p['id'] != panel['id']]
        
        # Refresh tabs
        self.refresh_history_tab()
        self.refresh_inventory_tab()
        self.update_summary()
        self.update_alerts()
        
        messagebox.showinfo("Undo Successful", f"Panel '{panel['panelName']}' has been undone.")

    def export_history(self):
        """Export history to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='panel_history.csv'
        )
        
        if filename:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'User', 'Panel Name',
                               'Cell Count (millions)', 'Antibodies Used',
                               'Total Volume (µL)'])
                
                for entry in self.panel_history:
                    timestamp = datetime.fromisoformat(entry['timestamp'])
                    ab_list = '; '.join([f"{ab['antigen']}({ab['metal']})" 
                                        for ab in entry['antibodies']])
                    total_vol = sum(ab['volumeUsed'] for ab in entry['antibodies'])
                    
                    writer.writerow([
                        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        entry['user'],
                        entry['panelName'],
                        entry['cellCount'],
                        ab_list,
                        f"{total_vol:.2f}"
                    ])
            
            messagebox.showinfo("Success", f"History exported to {filename}")
    
    def create_add_antibody_tab(self):
        """Create Add Antibody tab with 2-column grid"""
        frame = tk.Frame(self.notebook, bg='black')
        self.notebook.add(frame, text='Add Antibody')
        
        tk.Label(frame, text="Add New Antibody", font=('Arial', 20, 'bold'),
                 bg='black', fg='white').pack(pady=20)
        
        form_frame = tk.Frame(frame, bg='black', padx=30, pady=20)
        form_frame.pack(padx=50, fill='both', expand=True)
        
        # Entry fields in 2-column grid
        self.new_ab_vars = {}
        fields = [
            ('antigen', 'Antigen *', 0, 0),
            ('clone', 'Clone', 0, 1),
            ('metal', 'Metal', 1, 0),
            ('concentration', 'Concentration (mg/mL)', 1, 1),
            ('antibodyPerTest', 'Antibody per Test (µg)', 2, 0),
            ('volumePerTest', 'Volume per Test (µL)', 2, 1),
            ('stockVolume', 'Stock Volume (µL) *', 3, 0),
            ('alertThreshold', 'Alert Threshold (µL)', 3, 1),
            ('dateConjugated', 'Date of Conjugation', 4, 0)
        ]
        
        for field, label, row, col in fields:
            tk.Label(form_frame, text=label, font=('Arial', 20, 'bold'),
                     bg='black').grid(row=row*2, column=col, sticky='w', padx=10, pady=(10, 2))
            
            var = tk.StringVar()
            if field == 'alertThreshold':
                var.set('50')
            
            entry = tk.Entry(form_frame, textvariable=var, font=('Arial', 20),
                             bg='white', fg='black', width=35)
            entry.grid(row=row*2+1, column=col, sticky='ew', padx=10)
            self.new_ab_vars[field] = var
    
        # ──────────────────────────────
        # Stain Type Dropdown (full width)
        # ──────────────────────────────
        # Date Conjugated (left column, row 4) already exists in your fields
        
        # Stain Type (right column, row 4)
        tk.Label(form_frame, text="Stain Type", font=('Arial', 20, 'bold'),
                 bg='black', fg='white').grid(row=8, column=1, sticky='w', padx=10, pady=(10, 2))
        
        self.stain_type_var = tk.StringVar(value="Extracellular")
        stain_menu = ttk.Combobox(
            form_frame,
            textvariable=self.stain_type_var,
            values=["Extracellular", "Intracellular"],
            font=('Arial', 18),
            state="readonly",
            width=35
        )
        stain_menu.grid(row=9, column=1, sticky='ew', padx=10, pady=5)

        
        # Notes (full width)
        tk.Label(form_frame, text="Notes", font=('Arial', 20, 'bold'),
                 bg='black').grid(row=12, column=0, columnspan=2, sticky='w', padx=10, pady=(10, 2))
        
        self.notes_text = tk.Text(form_frame, height=4, font=('Arial', 20),
                                  bg='white', fg='black', width=70)
        self.notes_text.grid(row=13, column=0, columnspan=2, sticky='ew', padx=10, pady=(0, 10))
        
        # Add Button
        tk.Button(form_frame, text="➕ Add Antibody", command=self.add_antibody,
                  bg='black', fg='white', font=('Arial', 12, 'bold'),
                  padx=30, pady=10, cursor='hand2').grid(row=14, column=0, columnspan=2, pady=20)


    
    def add_antibody(self):
        """Add new antibody to inventory"""
        antigen = self.new_ab_vars['antigen'].get().strip()
        stock = self.new_ab_vars['stockVolume'].get().strip()
        
        if not antigen or not stock:
            messagebox.showwarning("Missing Information",
                                  "Please fill in at least Antigen and Stock Volume")
            return
        
        try:
            new_antibody = {
                'id': int(datetime.now().timestamp() * 1000),
                'antigen': antigen,
                'clone': self.new_ab_vars['clone'].get(),
                'metal': self.new_ab_vars['metal'].get(),
                'concentration': float(self.new_ab_vars['concentration'].get() or 0),
                'antibodyPerTest': float(self.new_ab_vars['antibodyPerTest'].get() or 0),
                'volumePerTest': float(self.new_ab_vars['volumePerTest'].get() or 0),
                'stockVolume': float(stock),
                'alertThreshold': float(self.new_ab_vars['alertThreshold'].get() or 50),
                'dateConjugated': self.new_ab_vars['dateConjugated'].get(),
                'notes': self.notes_text.get('1.0', 'end-1c'),
                'stainType': self.stain_type_var.get() 
            }
            
            self.inventory.append(new_antibody)
            
            # Clear form
            for var in self.new_ab_vars.values():
                var.set('')
            self.new_ab_vars['alertThreshold'].set('50')
            self.notes_text.delete('1.0', 'end')
            
            self.refresh_antibody_list()
            self.refresh_inventory_tab()
            self.update_alerts()
            
            self.notebook.select(0)  # Switch to Build Panel tab
            messagebox.showinfo("Success", f"Antibody {antigen} added successfully!")
            
        except ValueError:
            messagebox.showerror("Invalid Input",
                               "Please enter valid numbers for numeric fields")


def main():
    root = tk.Tk()
    app = AntibodyPanelManager(root)
    root.mainloop()


if __name__ == '__main__':
    main()


# In[ ]:





# In[ ]:




