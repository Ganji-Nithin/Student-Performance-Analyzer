import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class StudentAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Performance Analyzer")
        self.root.geometry("800x600")
        self.root.configure(bg="#e8f0fe")

        self.data = None

        header = tk.Label(root, text="Student Performance Analyzer", 
                          font=("Helvetica", 24, "bold"), bg="#e8f0fe", fg="#2c3e50")
        header.pack(pady=15)

        ttk.Style().configure('TButton', font=('Helvetica', 13))
        ttk.Button(root, text="Upload CSV File", command=self.load_csv).pack(pady=10)

        self.student_var = tk.StringVar()
        self.student_dropdown = ttk.Combobox(root, textvariable=self.student_var, state="readonly", font=('Helvetica', 12))
        self.student_dropdown.pack(pady=10)
        self.student_dropdown.set("Select Student ID")

        btn_frame = tk.Frame(root, bg="#e8f0fe")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="📈 Overall Summary", width=22, command=self.show_summary).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="📊 Subject-wise Average", width=22, command=self.show_subject_average).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="📉 Student Performance Trends", width=22, command=self.show_student_trends).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="🎯 Student Performance Summary", width=22, command=self.show_student_performance_summary).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="🏆 Class Rank Dashboard", width=22, command=self.show_class_ranks).grid(row=2, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="📋 Subjects wise Summary", width=22, command=self.show_lagging_subjects).grid(row=2, column=1, padx=10, pady=5)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.data = pd.read_csv(file_path)

                if "Student_ID" not in self.data.columns:
                    raise ValueError("CSV must contain 'Student_ID' column.")

                if self.data["Student_ID"].isnull().any():
                    raise ValueError("Student_ID column contains empty values.")
                if self.data["Student_ID"].duplicated().any():
                    raise ValueError("Student_ID column contains duplicate values.")

                self.data["Student_ID"] = self.data["Student_ID"].astype(str)
                self.student_dropdown["values"] = self.data["Student_ID"].unique().tolist()
                self.student_dropdown.set("Select Student ID")

                messagebox.showinfo("Success", "Data loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV:\n{e}")

    def show_summary(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please upload data first.")
            return

        numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
        if "Student_ID" in numeric_cols:
            numeric_cols.remove("Student_ID")
        if not numeric_cols:
            messagebox.showinfo("Info", "No numeric columns found for summary.")
            return
        
        summary = self.data[numeric_cols].describe().round(2)
        self.show_text_window("Overall Summary Statistics", summary.to_string())

    def show_subject_average(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please upload data first.")
            return

        numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
        if "Student_ID" in numeric_cols:
            numeric_cols.remove("Student_ID")
        if not numeric_cols:
            messagebox.showinfo("Info", "No numeric columns found for averages.")
            return
        
        averages = self.data[numeric_cols].mean()

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(averages.index, averages.values, color="#3498db")
        ax.set_title("Subject-wise Average Scores", fontsize=18, weight='bold')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.tick_params(left=False, bottom=False)
        ax.set_yticklabels([])

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1, f"{height:.1f}", ha='center', fontsize=11)

        plt.tight_layout()
        plt.show()

    def show_student_trends(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please upload data first.")
            return
        
        selected_id = self.student_var.get()
        if selected_id == "Select Student ID":
            messagebox.showinfo("Info", "Please select a Student ID.")
            return
        
        student_data = self.data[self.data["Student_ID"] == selected_id]
        if student_data.empty:
            messagebox.showerror("Error", "Student ID not found.")
            return
        
        numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
        if "Student_ID" in numeric_cols:
            numeric_cols.remove("Student_ID")
        if not numeric_cols:
            messagebox.showinfo("Info", "No numeric columns found for trend analysis.")
            return
        
        scores = student_data[numeric_cols].iloc[0]
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(numeric_cols, scores.values, marker='o', color="#e67e22", linewidth=3)
        ax.fill_between(numeric_cols, scores.values, color="#f39c12", alpha=0.2)
        ax.set_title(f"Performance Trend for Student ID: {selected_id}", fontsize=18, weight='bold')

        # Clean style
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.tick_params(left=False, bottom=False)
        ax.set_yticklabels([])

        for i, v in enumerate(scores.values):
            ax.text(numeric_cols[i], v + 1, f"{v}", ha='center', fontsize=11)

        plt.tight_layout()
        plt.show()

    def show_student_performance_summary(self):
        """Summary showing lagging subjects and improvements for selected student"""
        if self.data is None:
            messagebox.showwarning("Warning", "Please upload data first.")
            return

        selected_id = self.student_var.get()
        if selected_id == "Select Student ID":
            messagebox.showinfo("Info", "Please select a Student ID.")
            return

        student_data = self.data[self.data["Student_ID"] == selected_id]
        if student_data.empty:
            messagebox.showerror("Error", "Student ID not found.")
            return

        numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
        if "Student_ID" in numeric_cols:
            numeric_cols.remove("Student_ID")
        if not numeric_cols:
            messagebox.showinfo("Info", "No numeric columns found for analysis.")
            return
        
        scores = student_data[numeric_cols].iloc[0]

        threshold = 50
        lagging_subjects = scores[scores < threshold].index.tolist()
        strong_subjects = scores[scores >= threshold].index.tolist()

        summary_text = f"Performance Summary for Student ID: {selected_id}\n\n"
        if lagging_subjects:
            summary_text += "Subjects lagging behind (below 50):\n"
            for sub in lagging_subjects:
                summary_text += f" - {sub}: {scores[sub]}\n"
            summary_text += "\nImprovement Suggestions:\n"
            for sub in lagging_subjects:
                summary_text += f" • Focus more on {sub}. Consider additional practice or tutoring.\n"
        else:
            summary_text += "Great job! No subjects lagging behind.\n"

        self.show_text_window("Student Performance Summary", summary_text)

    def show_class_ranks(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please upload data first.")
            return
        
        numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
        if "Student_ID" in numeric_cols:
            numeric_cols.remove("Student_ID")
        if not numeric_cols:
            messagebox.showinfo("Info", "No numeric columns found for ranking.")
            return

        self.data["Total_Score"] = self.data[numeric_cols].sum(axis=1)
        self.data["Rank"] = self.data["Total_Score"].rank(method='min', ascending=False).astype(int)

        rank_df = self.data[["Student_ID", "Total_Score", "Rank"]].sort_values("Rank")

        top_ranks = rank_df.head(10)

        self.show_text_window("Top 10 Student Ranks", top_ranks.to_string(index=False))

    def show_lagging_subjects(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please upload data first.")
            return

        numeric_cols = self.data.select_dtypes(include='number').columns.tolist()
        if "Student_ID" in numeric_cols:
            numeric_cols.remove("Student_ID")
        if not numeric_cols:
            messagebox.showinfo("Info", "No numeric columns found for lagging subject analysis.")
            return

        threshold = 50
        lagging_counts = (self.data[numeric_cols] < threshold).sum().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(lagging_counts.index, lagging_counts.values, color="#e74c3c")
        ax.set_title("Number of Students Lagging per Subject (Score < 50)", fontsize=18, weight='bold')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.tick_params(left=False, bottom=False)
        ax.set_yticklabels([])

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1, f"{int(height)}", ha='center', fontsize=11)

        plt.tight_layout()
        plt.show()

    def show_text_window(self, title, content):
        top = tk.Toplevel(self.root)
        top.title(title)
        top.geometry("600x450")
        text = tk.Text(top, wrap=tk.WORD, font=("Courier", 11))
        text.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)
        text.insert(tk.END, content)
        text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentAnalyzerApp(root)
    root.mainloop()
