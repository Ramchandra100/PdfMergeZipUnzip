import os
import zipfile
import re
import shutil
import subprocess
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfMerger

def natural_sort_key(s):
    """Sorts strings with numbers correctly (Unit-1, Unit-2, Unit-10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

class PDFApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Book Maker Pro")
        self.geometry("700x500")
        
        # Responsive Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- Robust Icon Loading ---
        self.icon_name = "logo.ico"
        if os.path.exists(self.icon_name):
            try:
                self.iconbitmap(self.icon_name)
            except Exception:
                pass # Silently fail if icon format is invalid

        # --- UI Components ---
        self.label = ctk.CTkLabel(self, text="📚 Automated PDF Book Merger", font=ctk.CTkFont(size=22, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=20)

        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)

        self.path_entry = ctk.CTkEntry(self.path_frame, placeholder_text="Select folder containing your block zips...")
        self.path_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.browse_btn = ctk.CTkButton(self.path_frame, text="Browse", width=100, command=self.browse_folder)
        self.browse_btn.grid(row=0, column=1, padx=(5, 10), pady=10)

        self.start_btn = ctk.CTkButton(self, text="GENERATE COMPLETE PDF", height=45, fg_color="#27ae60", hover_color="#219150", 
                                       font=ctk.CTkFont(weight="bold"), command=self.start_processing)
        self.start_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.log_text = ctk.CTkTextbox(self, state="disabled", corner_radius=10, border_width=1)
        self.log_text.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"> {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def start_processing(self):
        raw_path = self.path_entry.get().strip().replace('"', '')
        if not raw_path or not os.path.exists(raw_path):
            messagebox.showwarning("Path Error", "The selected folder path does not exist.")
            return
        
        self.start_btn.configure(state="disabled")
        self.log("🚀 Initializing...")
        threading.Thread(target=self.process_logic, args=(raw_path,), daemon=True).start()

    def process_logic(self, root_folder):
        # Create a unique temp folder inside the target
        temp_dir = os.path.join(root_folder, "_temp_extraction_process")
        
        try:
            folder_name = os.path.basename(os.path.normpath(root_folder))
            output_pdf = os.path.join(root_folder, f"{folder_name}_Final_Book.pdf")
            merger = PdfMerger()

            # Cleanup old temp folders if they exist
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            os.makedirs(temp_dir, exist_ok=True)

            # Find and Sort Zip Files
            zips = sorted([f for f in os.listdir(root_folder) if f.lower().endswith('.zip')], key=natural_sort_key)
            
            if not zips:
                self.log("❌ No ZIP files found in this folder.")
                return

            for z_file in zips:
                self.log(f"📦 Extracting: {z_file}")
                z_path = os.path.join(root_folder, z_file)
                
                try:
                    with zipfile.ZipFile(z_path, 'r') as z_ref:
                        target_subfolder = os.path.join(temp_dir, z_file.replace('.zip', ''))
                        z_ref.extractall(target_subfolder)

                        # Find all PDFs in this block
                        pdfs_in_block = []
                        for root, _, files in os.walk(target_subfolder):
                            for f in files:
                                if f.lower().endswith(".pdf"):
                                    pdfs_in_block.append(os.path.join(root, f))
                        
                        # Sort units (Unit-1, Unit-2...)
                        pdfs_in_block.sort(key=natural_sort_key)
                        for pdf in pdfs_in_block:
                            self.log(f"   📄 Merging: {os.path.basename(pdf)}")
                            merger.append(pdf)

                except zipfile.BadZipFile:
                    self.log(f"⚠️ SKIPPED: '{z_file}' is corrupted.")
                except Exception as e:
                    self.log(f"⚠️ Error in {z_file}: {str(e)}")

            # Final Save with Lock Check
            try:
                merger.write(output_pdf)
                merger.close()
            except PermissionError:
                messagebox.showerror("Permission Denied", f"Could not save PDF.\nIs '{os.path.basename(output_pdf)}' open in another program?")
                return

            self.log(f"\n✅ COMPLETE: {os.path.basename(output_pdf)}")
            messagebox.showinfo("Success", "The PDF book has been created successfully.")
            subprocess.run(['explorer', '/select,', os.path.normpath(output_pdf)])

        except Exception as e:
            self.log(f"🛑 Critical Failure: {str(e)}")
            messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}")
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            self.start_btn.configure(state="normal")

if __name__ == "__main__":
    app = PDFApp()
    app.mainloop()