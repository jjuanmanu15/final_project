import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk
from logic import Competition



class Registration(tk.Toplevel):
    """The model of the registration window."""
    def __init__(self, parent, logic):
        super().__init__(parent)
        self.title("Register athlete")
        self.geometry("400x400")
        self.configure(bg='midnight blue')
        self.logic = logic
        self.widgets()

    def widgets(self):
        tk.Label(self, text='Athlete registration', font=('Times New Roman', 16), fg='white', background='midnight blue').pack(pady=10)

        frame = tk.Frame(self)
        frame.pack(pady=10)
        frame.configure(bg='midnight blue')

        tk.Label(frame, text="Name:", fg='white', background='midnight blue').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.name_entry = tk.Entry(frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tests = ['Resistence', 'Strength', 'Velocity']
        self.score_entries = []

        for i, test in enumerate(tests, start=1): #loop for every entry related to each test
            tk.Label(frame, text=f"{test}:", fg='white', background='midnight blue').grid(row=i, column=0, sticky='e', padx=5, pady=5)
            entry = tk.Entry(frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.score_entries.append(entry)

        tk.Button(self, text="Register", command=self.register_athlete).pack(pady=20)

    def register_athlete(self):
        """Gets entries of each participant's entries."""
        name = self.name_entry.get().strip()

        try:
            scores = [float(entry.get()) for entry in self.score_entries]
            if any(score < 0 or score > 100 for score in scores):
                raise ValueError("Scores must be between 0 and 100")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        if not name:
            messagebox.showerror("Input Error", "Name cannot be empty")
            return

        try:
            final_score, qualified = self.logic.register_athlete(name, *scores)
            messagebox.showinfo(
                "Success",
                f"Athlete Registered!\n"
                f"Name: {name}\n"
                f"Final Score: {final_score}\n"
                f"Status: {'QUALIFIED' if qualified else 'Not Qualified'}\n\n"
                f"Data saved to {self.logic.csv_file}"
            )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save participant:\n{str(e)}\n\n"
                "Participant was not registered.")

#Treeview https://www.geeksforgeeks.org/python-tkinter-treeview-scrollbar/
class Report(tk.Toplevel):
    """The model of the general report."""
    def __init__(self, parent, logic):
        super().__init__(parent)
        self.title("General report")
        self.geometry("800x600")
        self.logic = logic
        self.widgets()
    
    def widgets(self):
        data = self.logic.get_general_report_data()
        
        if not data:
            tk.Label(self, text="There's not registered athletes.").pack(pady=50)
            return
        
        df, stats = data
        
        main_frame = tk.Frame(self)
        main_frame.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(main_frame) #Canvas is to create a scrollable area for the report https://www.geeksforgeeks.org/python-tkinter-create-different-type-of-lines-using-canvas-class/
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))) #Allows the scrollbar adjust to the size of the window
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill='both', expand=True)
        scrollbar.pack(side="right", fill='y')
        
        tk.Label(scrollable_frame, text="General Report", font=('Times New Roman', 16)).pack(pady=10)

        table = tk.Frame(scrollable_frame) #The table with the information of every athlete
        table.pack(fill='x', padx=10, pady=5)
        
        headers = ["Name", "Final Score", "Qualified"]
        for col, header in enumerate(headers):
            tk.Label(table, text=header, font=('Times New Roman', 10, 'bold'),
                    relief='ridge', width=20).grid(row=0, column=col, sticky='ew')
        
        for row_idx, row in df.iterrows():
            tk.Label(table, text=row['Name'], relief='ridge',
                    width=20).grid(row=row_idx+1, column=0, sticky='ew')
            tk.Label(table, text=row['Final scores'], relief='ridge',
                    width=20).grid(row=row_idx+1, column=1, sticky='ew')
            tk.Label(table, text=row['Qualified'], relief='ridge',
                    width=20).grid(row=row_idx+1, column=2, sticky='ew')
        
        tk.Label(scrollable_frame, text="Statistics:", font=('Times New Roman', 12)).pack(pady=5, anchor='w')

        stats_text = (f"Average punctuation: {stats['average_score']:.2f}\n"
                     f"Qualified athletes: {stats['qualified_count']}\n"
                     f"Non-qualified participants: {stats['not_qualified_count']}")
        
        tk.Label(scrollable_frame, text=stats_text, justify='left').pack(anchor='w', padx=10)
        
        pie_image = ImageTk.PhotoImage(stats['pie_chart'])
        pie_label = tk.Label(scrollable_frame, image=pie_image)
        pie_label.image = pie_image
        pie_label.pack()

        tk.Label(scrollable_frame, text="Correlation Matrix:", font=('Times New Roman', 12)).pack(pady=5, anchor='w')
        
        corr_image = ImageTk.PhotoImage(stats['correlation_plot'])
        corr_label = tk.Label(scrollable_frame, image=corr_image)
        corr_label.image = corr_image
        corr_label.pack(pady=10)
#Tk.Toplevel, to pop up individual and general report window 
#https://www-geeksforgeeks-org.translate.goog/python-tkinter-toplevel-widget/?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc
class IndividualReport(tk.Toplevel):
    """The model of the individual report."""
    def __init__(self, parent, logic):
        super().__init__(parent)
        self.title("Individual Report")
        self.geometry("800x600")
        self.logic = logic
        self.widgets()
    
    def widgets(self):
        tk.Label(self, text="Individual Report", font=('Times New Roman', 16)).pack(pady=10)
        
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Athlete name:").pack(side='left')
        self.name_entry = tk.Entry(search_frame)
        self.name_entry.pack(side='left', padx=5)
        tk.Button(search_frame, text="Search", command=self.show_report).pack(side='left')
        
        self.report_frame = tk.Frame(self)
        self.report_frame.pack(fill='both', expand=True)
    
    def show_report(self):
        name = self.name_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Enter a name")
            return
            
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        report_data = self.logic.get_individual_report_data(name)
        
        if not report_data:
            tk.Label(self.report_frame, text="Athlete not found").pack(pady=50)
            return
        
        info_frame = tk.Frame(self.report_frame)
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text=f"Name: {report_data['name']}", font=('Times New Roman', 12)).pack(anchor='w')
        tk.Label(info_frame, text=f"Final punctuation: {report_data['final_score']}", 
                font=('Times New Roman', 12)).pack(anchor='w')
        tk.Label(info_frame, text=f"Qualified: {'Yes' if report_data['qualified'] else 'No'}", 
                font=('Times New Roman', 12)).pack(anchor='w')
        
        hist_image = ImageTk.PhotoImage(report_data['histograms'])
        hist_label = tk.Label(self.report_frame, image=hist_image)
        hist_label.image = hist_image
        hist_label.pack(pady=10)

class Root(tk.Tk):
    """The model of the main window"""
    def __init__(self):
        super().__init__()
        self.title('Performance management system')
        self.geometry('600x300')
        self.logic = Competition()
        self.configure(bg='midnight blue')
        self.widgets()

    def registration(self):
        Registration(self, self.logic)

    def report(self):
        Report(self, self.logic)

    def individual_report(self):
        IndividualReport(self, self.logic)

    def widgets(self):
        tk.Label(self, text='Performance Management System in Sports Events', font=('Times New Roman', 16), fg='white', background='midnight blue').pack(pady=20)

        buttons_frame = tk.Frame(self)
        buttons_frame.pack(expand=True)
        buttons_frame.configure(bg='midnight blue')

        tk.Button(buttons_frame, text='Register athlete', command=self.registration, width=25).pack(pady=5)
        tk.Button(buttons_frame, text="General report", command=self.report, width=25).pack(pady=5)
        tk.Button(buttons_frame, text="Individual report", command=self.individual_report, width=25).pack(pady=5)
        tk.Button(buttons_frame, text="Close", command=self.destroy, width=25).pack(pady=5)

Root().mainloop()