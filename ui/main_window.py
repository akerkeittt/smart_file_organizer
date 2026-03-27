import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from typing import List, Optional
from pathlib import Path
from core.ollama_client import OllamaClient
from core.file_handler import FileHandler

class FileRow(ctk.CTkFrame):
    def __init__(self, master, file_data, checkbox_command, **kwargs):
        super().__init__(master, **kwargs)
        self.file_data = file_data
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=2)
        self.grid_columnconfigure(3, weight=2)

        self.checkbox_var = ctk.StringVar(value="off")
        self.checkbox = ctk.CTkCheckBox(
            self, text="", variable=self.checkbox_var, onvalue="on", offvalue="off", 
            width=20, command=lambda: checkbox_command(self)
        )
        self.checkbox.grid(row=0, column=0, padx=(10, 5), pady=10)

        name_str = self.file_data["name"]
        path_str = self.file_data["path"]
        
        self.name_label = ctk.CTkLabel(self, text=name_str, font=("Segoe UI", 12, "bold"), anchor="w")
        self.name_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Basic path truncation for visual cleanliness
        display_path = path_str if len(path_str) < 50 else "..." + path_str[-47:]
        self.path_label = ctk.CTkLabel(self, text=display_path, font=("Segoe UI", 11), text_color="gray", anchor="w")
        self.path_label.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        tags_str = ", ".join(self.file_data["tags"]) if self.file_data["tags"] else "No tags"
        self.tags_label = ctk.CTkLabel(self, text=tags_str, font=("Segoe UI", 12, "italic"), text_color="#3B8EDB", anchor="w")
        self.tags_label.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart File Organizer")
        self.geometry("950x650")
        self.minsize(800, 500)
        
        # Setup CustomTkinter Theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.ollama_client = OllamaClient()
        self.file_handler = FileHandler()

        self.files_data = [] 
        self.file_rows = []

        self._create_ui()
        self._load_existing_files()

    def _create_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top Frame (Header + Search)
        self.top_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self.top_frame, text="Smart File Organizer", font=("Segoe UI", 24, "bold"))
        self.title_label.grid(row=0, column=0, padx=(0, 20))

        self.search_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Search tags...", font=("Segoe UI", 13), width=300)
        self.search_entry.grid(row=0, column=1, sticky="e")
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # List Header 
        self.list_header = ctk.CTkFrame(self, corner_radius=5, height=35)
        self.list_header.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 5))
        self.list_header.grid_columnconfigure(1, weight=1)
        self.list_header.grid_columnconfigure(2, weight=2)
        self.list_header.grid_columnconfigure(3, weight=2)
        
        # Spacer for checkbox column
        ctk.CTkLabel(self.list_header, text="", width=35).grid(row=0, column=0)
        ctk.CTkLabel(self.list_header, text="File Name", font=("Segoe UI", 12, "bold")).grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(self.list_header, text="Path", font=("Segoe UI", 12, "bold")).grid(row=0, column=2, padx=10, sticky="w")
        ctk.CTkLabel(self.list_header, text="Tags", font=("Segoe UI", 12, "bold")).grid(row=0, column=3, padx=10, sticky="w")

        # Scrollable Area
        self.scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=5)
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        # Configure scroll frame inner column for rows
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Bottom Frame (Buttons + Status)
        self.bottom_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(10, 20))
        self.bottom_frame.grid_columnconfigure(2, weight=1)

        self.add_btn = ctk.CTkButton(self.bottom_frame, text="Add Files", font=("Segoe UI", 14, "bold"), command=self._add_files)
        self.add_btn.grid(row=0, column=0, padx=(0, 10))

        self.analyze_btn = ctk.CTkButton(
            self.bottom_frame, text="Analyze & Tag", font=("Segoe UI", 14, "bold"), 
            fg_color="#2FA572", hover_color="#106A43", command=self._analyze_selected
        )
        self.analyze_btn.grid(row=0, column=1)

        self.status_label = ctk.CTkLabel(self.bottom_frame, text="Ready", font=("Segoe UI", 13, "italic"), text_color="gray")
        self.status_label.grid(row=0, column=2, sticky="e", padx=(0, 10))

        self.progress = ctk.CTkProgressBar(self.bottom_frame, mode="indeterminate", width=150)
        self.progress.set(0)

    def _checkbox_command(self, row: FileRow):
        pass

    def _load_existing_files(self):
        for file_path, tags in self.file_handler.file_tags.items():
            if Path(file_path).exists():
                self._add_file_to_list(file_path, tags)

    def _add_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=(
                ("Supported Files", "*.txt *.pdf *.png *.jpg *.jpeg *.docx"),
                ("All Files", "*.*")
            )
        )
        for path in file_paths:
            if not any(f["path"] == path for f in self.files_data):
                tags = self.file_handler.get_tags(path)
                self._add_file_to_list(path, tags)

    def _add_file_to_list(self, file_path: str, tags: List[str]):
        name = Path(file_path).name
        self.files_data.append({"name": name, "path": file_path, "tags": tags})
        self._refresh_list()

    def _refresh_list(self, filter_paths: Optional[List[str]] = None):
        # Clear current rows
        for row in self.file_rows:
            row.destroy()
        self.file_rows.clear()

        # Build new list based on filter
        display_data = self.files_data
        if filter_paths is not None:
            display_data = [f for f in self.files_data if f["path"] in filter_paths]

        for idx, file_data in enumerate(display_data):
            row = FileRow(self.scroll_frame, file_data, self._checkbox_command, fg_color=("gray90", "gray15"))
            row.grid(row=idx, column=0, sticky="ew", pady=2, padx=2)
            self.file_rows.append(row)

    def _on_search(self, event=None):
        query = self.search_entry.get().strip()
        if not query:
            self._refresh_list()
        else:
            matching_paths = self.file_handler.search_files(query)
            self._refresh_list(filter_paths=matching_paths)

    def _analyze_selected(self):
        selected_paths = [row.file_data["path"] for row in self.file_rows if row.checkbox_var.get() == "on"]
        
        if not selected_paths:
            self.status_label.configure(text="Please check files to analyze.")
            return

        self._set_ui_state("disabled")
        self.status_label.configure(text=f"Processing {len(selected_paths)} file(s)...")
        self.progress.grid(row=0, column=2, sticky="e", padx=(0, 150))
        self.progress.start()

        thread = threading.Thread(target=self._process_files, args=(selected_paths,))
        thread.daemon = True
        thread.start()

    def _set_ui_state(self, state: str):
        self.add_btn.configure(state=state)
        self.analyze_btn.configure(state=state)
        self.search_entry.configure(state=state)
        for row in self.file_rows:
            row.checkbox.configure(state=state)

    def _process_files(self, paths: List[str]):
        for path in paths:
            file_name = Path(path).name
            self.status_label.configure(text=f"Extracting: {file_name}")
            
            text = self.file_handler.extract_text(path)
            
            if text and not text.startswith("Error"):
                self.status_label.configure(text=f"Tagging: {file_name}")
                max_chars = 15000 
                if len(text) > max_chars:
                    text = text[:max_chars]

                tags = self.ollama_client.generate_tags(text)
                
                if tags:
                    self.file_handler.save_tags(path, tags)
                    for f in self.files_data:
                        if f["path"] == path:
                            f["tags"] = tags
                            break
            
        self.after(0, self._on_processing_complete)

    def _on_processing_complete(self):
        self.progress.stop()
        self.progress.grid_forget()
        self.status_label.configure(text="Done tagging.")
        self._set_ui_state("normal")
        
        # Deselect all after tagging
        for row in self.file_rows:
            row.checkbox_var.set("off")
            
        # keep search active if it was
        self._on_search()
