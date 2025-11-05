import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
from collections import Counter

class PublicationExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Publications Explorer")
        self.root.geometry("1200x800")
        
        self.df = None
        self.filtered_df = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Top Frame - File Operations
        top_frame = tk.Frame(self.root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        
        tk.Button(top_frame, text="Load CSV", command=self.load_csv, 
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Run Preprocessing", command=self.preprocess_data,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(top_frame, text="No file loaded", fg="gray")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Search Frame
        search_frame = tk.LabelFrame(self.root, text="Search & Filter", padx=10, pady=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Title search
        tk.Label(search_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.title_var, width=30).grid(row=0, column=1, padx=5, pady=2)
        
        # Author search
        tk.Label(search_frame, text="Author:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.author_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.author_var, width=30).grid(row=0, column=3, padx=5, pady=2)
        
        # Year search
        tk.Label(search_frame, text="Year:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.year_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.year_var, width=30).grid(row=1, column=1, padx=5, pady=2)
        
        # Venue search
        tk.Label(search_frame, text="Venue:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.venue_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.venue_var, width=30).grid(row=1, column=3, padx=5, pady=2)
        
        # Action buttons
        button_frame = tk.Frame(search_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        tk.Button(button_frame, text="Apply Filter", command=self.apply_filter,
                 bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear Filter", command=self.clear_filter).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Analyze & Visualize", command=self.visualize,
                 bg="#9C27B0", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Export Results", command=self.export_results,
                 bg="#607D8B", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Results Frame
        results_frame = tk.LabelFrame(self.root, text="Results", padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview
        tree_scroll = tk.Scrollbar(results_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(results_frame, yscrollcommand=tree_scroll.set, 
                                 columns=("Title", "Authors", "Year", "Venue"), show="headings")
        tree_scroll.config(command=self.tree.yview)
        
        self.tree.heading("Title", text="Title")
        self.tree.heading("Authors", text="Authors")
        self.tree.heading("Year", text="Year")
        self.tree.heading("Venue", text="Venue")
        
        self.tree.column("Title", width=400)
        self.tree.column("Authors", width=300)
        self.tree.column("Year", width=80)
        self.tree.column("Venue", width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.result_count_label = tk.Label(results_frame, text="0 results")
        self.result_count_label.pack(pady=5)
    
    def load_csv(self):
        filepath = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.df = pd.read_csv(filepath)
                self.filtered_df = self.df.copy()
                self.status_label.config(text=f"Loaded: {filepath.split('/')[-1]} ({len(self.df)} records)", fg="green")
                self.display_data(self.df)
                messagebox.showinfo("Success", f"Loaded {len(self.df)} publications")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def standardize_author(self, name):
        """Convert author name to First initial + Last name format"""
        if pd.isna(name) or not name.strip():
            return name
        
        name = name.strip()
        parts = name.split()
        
        if len(parts) == 0:
            return name
        
        # Get all initials except last name
        initials = []
        for part in parts[:-1]:
            if part and part[0].isalpha():
                initials.append(part[0].upper() + ".")
        
        # Last name
        last_name = parts[-1]
        
        if initials:
            return " ".join(initials) + " " + last_name
        else:
            return last_name
    
    def standardize_venue(self, venue):
        """Normalize venue names by removing years, conference/journal words"""
        if pd.isna(venue) or not venue.strip():
            return venue
        
        venue = venue.strip()
        
        # Remove years (4 consecutive digits)
        venue = re.sub(r'\b\d{4}\b', '', venue)
        
        # Remove common words
        venue = re.sub(r'\b(Conference|Proceedings|Workshop|Symposium|International|Journal|on|of|the)\b', 
                      '', venue, flags=re.IGNORECASE)
        
        # Remove extra spaces and punctuation
        venue = re.sub(r'[,\-:()]', ' ', venue)
        venue = re.sub(r'\s+', ' ', venue).strip()
        
        return venue.upper() if venue else venue
    
    def preprocess_data(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a CSV file first")
            return
        
        try:
            # Standardize authors
            if 'Authors' in self.df.columns or 'authors' in self.df.columns:
                author_col = 'Authors' if 'Authors' in self.df.columns else 'authors'
                self.df[author_col] = self.df[author_col].apply(
                    lambda x: ', '.join([self.standardize_author(a) for a in str(x).split(',')]) 
                    if pd.notna(x) else x
                )
            
            # Standardize venues
            if 'Venue' in self.df.columns or 'venue' in self.df.columns:
                venue_col = 'Venue' if 'Venue' in self.df.columns else 'venue'
                self.df[venue_col] = self.df[venue_col].apply(self.standardize_venue)
            
            self.filtered_df = self.df.copy()
            self.display_data(self.df)
            messagebox.showinfo("Success", "Preprocessing completed!\n- Author names standardized\n- Venue names normalized")
        except Exception as e:
            messagebox.showerror("Error", f"Preprocessing failed:\n{str(e)}")
    
    def apply_filter(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a CSV file first")
            return
        
        filtered = self.df.copy()
        
        # Get column names (handle case variations)
        title_col = next((c for c in filtered.columns if c.lower() == 'title'), None)
        author_col = next((c for c in filtered.columns if c.lower() == 'authors'), None)
        year_col = next((c for c in filtered.columns if c.lower() == 'year'), None)
        venue_col = next((c for c in filtered.columns if c.lower() == 'venue'), None)
        
        # Apply filters
        if self.title_var.get() and title_col:
            filtered = filtered[filtered[title_col].str.contains(self.title_var.get(), case=False, na=False)]
        
        if self.author_var.get() and author_col:
            filtered = filtered[filtered[author_col].str.contains(self.author_var.get(), case=False, na=False)]
        
        if self.year_var.get() and year_col:
            filtered = filtered[filtered[year_col].astype(str).str.contains(self.year_var.get(), na=False)]
        
        if self.venue_var.get() and venue_col:
            filtered = filtered[filtered[venue_col].str.contains(self.venue_var.get(), case=False, na=False)]
        
        self.filtered_df = filtered
        self.display_data(filtered)
    
    def clear_filter(self):
        self.title_var.set("")
        self.author_var.set("")
        self.year_var.set("")
        self.venue_var.set("")
        if self.df is not None:
            self.filtered_df = self.df.copy()
            self.display_data(self.df)
    
    def display_data(self, df):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if df is None or df.empty:
            self.result_count_label.config(text="0 results")
            return
        
        # Get column names
        title_col = next((c for c in df.columns if c.lower() == 'title'), None)
        author_col = next((c for c in df.columns if c.lower() == 'authors'), None)
        year_col = next((c for c in df.columns if c.lower() == 'year'), None)
        venue_col = next((c for c in df.columns if c.lower() == 'venue'), None)
        
        # Insert data
        for idx, row in df.iterrows():
            title = row[title_col] if title_col and pd.notna(row.get(title_col)) else ""
            authors = row[author_col] if author_col and pd.notna(row.get(author_col)) else ""
            year = row[year_col] if year_col and pd.notna(row.get(year_col)) else ""
            venue = row[venue_col] if venue_col and pd.notna(row.get(venue_col)) else ""
            
            self.tree.insert("", tk.END, values=(title, authors, year, venue))
        
        self.result_count_label.config(text=f"{len(df)} results")
    
    def visualize(self):
        if self.filtered_df is None or self.filtered_df.empty:
            messagebox.showwarning("Warning", "No data to visualize")
            return
        
        # Create visualization window
        viz_window = tk.Toplevel(self.root)
        viz_window.title("Analysis & Visualization")
        viz_window.geometry("1000x800")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Get column names
        year_col = next((c for c in self.filtered_df.columns if c.lower() == 'year'), None)
        author_col = next((c for c in self.filtered_df.columns if c.lower() == 'authors'), None)
        
        # Chart 1: Publications per year
        if year_col:
            year_counts = self.filtered_df[year_col].value_counts().sort_index()
            ax1.plot(year_counts.index, year_counts.values, marker='o', linewidth=2, markersize=6)
            ax1.set_xlabel("Year", fontsize=12)
            ax1.set_ylabel("Number of Publications", fontsize=12)
            ax1.set_title("Publications per Year", fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
        
        # Chart 2: Top 10 most active authors
        if author_col:
            all_authors = []
            for authors in self.filtered_df[author_col].dropna():
                all_authors.extend([a.strip() for a in str(authors).split(',')])
            
            author_counts = Counter(all_authors)
            top_authors = author_counts.most_common(10)
            
            if top_authors:
                authors, counts = zip(*top_authors)
                ax2.barh(range(len(authors)), counts, color='steelblue')
                ax2.set_yticks(range(len(authors)))
                ax2.set_yticklabels(authors)
                ax2.set_xlabel("Number of Publications", fontsize=12)
                ax2.set_ylabel("Author", fontsize=12)
                ax2.set_title("Top 10 Most Active Authors", fontsize=14, fontweight='bold')
                ax2.invert_yaxis()
                ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, viz_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def export_results(self):
        if self.filtered_df is None or self.filtered_df.empty:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.filtered_df.to_csv(filepath, index=False)
                messagebox.showinfo("Success", f"Exported {len(self.filtered_df)} records to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PublicationExplorer(root)
    root.mainloop()