import os
import sys
import threading
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import main

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
DATA_PATH = os.path.join(BASE_DIR, "data", "gap_results.csv")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class IntelliNicheApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IntelliNiche — Market Gap Detector with Embedded Visuals")
        self.geometry("1100x700")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.fig, self.ax = None, None
        self.canvas = None
        self.df = None

        self._build_widgets()
        self.load_data_if_exists()

    def _build_widgets(self):
        header = ctk.CTkFrame(self, corner_radius=0, height=65, fg_color="#1E293B")
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header, text="✨ IntelliNiche — Market Gap Detector",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"), text_color="#F8FAFC"
        )
        title_label.grid(row=0, column=0, padx=24, pady=16, sticky="w")

        self.upload_btn = ctk.CTkButton(
            header, text="📁 Upload CSV Data", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#10B981", hover_color="#059669", text_color="white",
            corner_radius=8, height=38, command=self.upload_and_process
        )
        self.upload_btn.grid(row=0, column=1, padx=24, pady=16, sticky="e")

        left_frame = ctk.CTkFrame(self, width=320, corner_radius=12, fg_color="#0F172A")
        left_frame.grid(row=1, column=0, padx=(20, 10), pady=16, sticky="nsew")
        left_frame.grid_rowconfigure(1, weight=1)

        cat_title = ctk.CTkLabel(
            left_frame, text="Top Ranked Categories",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color="#94A3B8"
        )
        cat_title.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        self.scroll_frame = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        right_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#1E293B")
        right_frame.grid(row=1, column=1, padx=(10, 20), pady=16, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)

        self.detail_title = ctk.CTkLabel(
            right_frame, text="Select a category or Upload CSV to view visual gaps",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"), text_color="#38BDF8", anchor="w"
        )
        self.detail_title.pack(fill="x", padx=20, pady=(16, 8))

        scores_frame = ctk.CTkFrame(right_frame, fg_color="#0F172A", corner_radius=10)
        scores_frame.pack(fill="x", padx=20, pady=6)
        scores_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.demand_card = self._create_score_card(scores_frame, "Demand Score", "-", 0)
        self.supply_card = self._create_score_card(scores_frame, "Supply Score", "-", 1)
        self.gap_card = self._create_score_card(scores_frame, "Gap Score", "-", 2)

        self.graph_container = ctk.CTkFrame(right_frame, fg_color="#0F172A", corner_radius=10, height=220)
        self.graph_container.pack(fill="x", padx=20, pady=10)
        self.graph_container.pack_propagate(False)

        ev_title = ctk.CTkLabel(
            right_frame, text="Supporting Customer Evidence:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#94A3B8", anchor="w"
        )
        ev_title.pack(fill="x", padx=20, pady=(8, 4))

        self.evidence_box = ctk.CTkTextbox(
            right_frame, font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#0F172A", text_color="#E2E8F0", corner_radius=10, wrap="word", height=90
        )
        self.evidence_box.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def _create_score_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, fg_color="transparent")
        card.grid(row=0, column=col, padx=12, pady=8)
        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="#64748B")
        lbl_title.pack()
        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=16, weight="bold"), text_color="#F8FAFC")
        lbl_val.pack()
        return lbl_val

    def upload_and_process(self):
        file_path = filedialog.askopenfilename(
            title="Select Review CSV", 
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return

        self.upload_btn.configure(state="disabled", text="⏳ Processing...")
        messagebox.showinfo("Processing", "File uploaded! Processing dataset in background...")

        def run_in_background():
            try:
                main.run_pipeline_for_file(file_path)
                self.after(0, self._on_process_complete)
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda: self._on_process_error(err_msg))

        threading.Thread(target=run_in_background, daemon=True).start()

    def _on_process_complete(self):
        self.upload_btn.configure(state="normal", text="📁 Upload CSV Data")
        self.load_data_if_exists()
        messagebox.showinfo("Success", "Analysis complete! Results & Graphs loaded successfully.")

    def _on_process_error(self, err_msg):
        self.upload_btn.configure(state="normal", text="📁 Upload CSV Data")
        messagebox.showerror("Error", f"Processing failed:\n{err_msg}")

    def load_data_if_exists(self):
        if os.path.exists(DATA_PATH):
            try:
                self.df = pd.read_csv(DATA_PATH)
                for widget in self.scroll_frame.winfo_children():
                    widget.destroy()

                top_df = self.df.head(50)

                for idx, row in top_df.iterrows():
                    btn = ctk.CTkButton(
                        self.scroll_frame, 
                        text=f"#{row['rank']}  {row['category']} (Gap: {row['gap_score']:.2f})",
                        font=ctk.CTkFont(family="Segoe UI", size=11),
                        fg_color="#1E293B", hover_color="#334155", text_color="#E2E8F0",
                        anchor="w", height=36, corner_radius=6,
                        command=lambda r=row: self._show_details(r)
                    )
                    btn.pack(fill="x", pady=3, padx=2)

                self.render_graph(self.df.head(5))
                if not top_df.empty:
                    self._show_details(top_df.iloc[0])
            except Exception as e:
                print(f"Error loading CSV: {e}")
        else:
            self.df = None

    def render_graph(self, top_data):
        for widget in self.graph_container.winfo_children():
            widget.destroy()

        if top_data is None or top_data.empty:
            return

        fig, ax = plt.subplots(figsize=(6.5, 2.0), dpi=100)
        fig.patch.set_facecolor("#0F172A")
        ax.set_facecolor("#0F172A")

        categories = top_data['category'].astype(str).str[:12].tolist()
        gap_scores = top_data['gap_score'].tolist()

        bars = ax.barh(categories[::-1], gap_scores[::-1], color="#38BDF8", height=0.5)
        ax.set_xlim(0, 1.0)
        ax.tick_params(colors="#94A3B8", labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#334155')
        ax.spines['bottom'].set_color('#334155')
        ax.set_title("Top 5 Market Gap Score Analysis", color="#F8FAFC", fontsize=10, pad=4)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _show_details(self, row):
        self.detail_title.configure(text=f"#{row['rank']}  {row['category']}")
        self.demand_card.configure(text=f"{row['demand_score']:.2f}")
        self.supply_card.configure(text=f"{row['supply_score']:.2f}")
        self.gap_card.configure(text=f"{row['gap_score']:.2f}")

        evidence_text = f"• \"{row['evidence_1']}\"\n\n• \"{row['evidence_2']}\"" if pd.notna(row.get("evidence_2")) and row["evidence_2"] else f"• \"{row['evidence_1']}\""
        
        self.evidence_box.delete("1.0", "end")
        self.evidence_box.insert("1.0", evidence_text)

if __name__ == "__main__":
    app = IntelliNicheApp()
    app.mainloop()