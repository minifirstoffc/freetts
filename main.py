import os
import threading
import tempfile
import customtkinter as ctk
from gtts import gTTS
from pygame import mixer
import tkinter.messagebox as messagebox
from tkinter import filedialog

class TTSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Text to Speech FREE")
        self.geometry("720x500")
        self.current_file = None
        self.running = True
        
        # Инициализация интерфейса
        self.configure_ui()
        self.init_components()
        
        # Инициализация аудио
        mixer.init()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def configure_ui(self):
        """Настройка внешнего вида приложения"""
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("dark-blue")

    def init_components(self):
        """Инициализация компонентов интерфейса"""
        # Main grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Text input
        self.text_label = ctk.CTkLabel(self, text="Enter Text:", font=("Arial", 14, "bold"))
        self.text_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="nw")

        self.text_input = ctk.CTkTextbox(self, wrap="word", height=180, border_width=2, corner_radius=10)
        self.text_input.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        # Control panel
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # Language selection
        self.lang_label = ctk.CTkLabel(self.control_frame, text="Language:", font=("Arial", 12))
        self.lang_label.pack(side="left", padx=(0, 10))

        self.lang_var = ctk.StringVar(value="en")
        self.lang_menu = ctk.CTkOptionMenu(self.control_frame, 
                                         values=["en", "ru", "es", "fr", "de"],
                                         variable=self.lang_var,
                                         width=80)
        self.lang_menu.pack(side="left")

        # Buttons
        self.btn_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        self.btn_frame.pack(side="right", fill="both", expand=True)

        self.convert_btn = ctk.CTkButton(self.btn_frame, 
                                       text="▶ Convert & Play", 
                                       command=self.thread_convert,
                                       fg_color="#2aa0c4",
                                       hover_color="#227e9c")
        self.convert_btn.pack(side="left", padx=5)

        self.download_btn = ctk.CTkButton(self.btn_frame, 
                                        text="↓ Download MP3", 
                                        command=self.save_file, 
                                        state="disabled",
                                        fg_color="#34a853",
                                        hover_color="#2b8345")
        self.download_btn.pack(side="left", padx=5)

        self.clear_btn = ctk.CTkButton(self.btn_frame, 
                                     text="✖ Clear", 
                                     command=self.clear_text, 
                                     fg_color="#ea4335",
                                     hover_color="#c2382e")
        self.clear_btn.pack(side="left", padx=5)

        # Progress bar
        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", height=8)
        self.progress.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="ew")

        # Status label
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray70")
        self.status_label.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="w")

    def thread_convert(self):
        threading.Thread(target=self.convert_text, daemon=True).start()

    def convert_text(self):
        try:
            self.start_loading()
            text = self.text_input.get("1.0", "end-1c").strip()
            lang = self.lang_var.get()

            if not text:
                messagebox.showwarning("Warning", "Please enter some text!")
                return

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
                temp_path = fp.name

            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_path)
            
            if self.running:
                mixer.music.load(temp_path)
                mixer.music.play()
                self.current_file = temp_path
                self.download_btn.configure(state="normal")
                self.update_status("Ready to play!")

        except Exception as e:
            if self.running:
                messagebox.showerror("Error", f"Conversion failed: {str(e)}")
        finally:
            if self.running:
                self.stop_loading()

    def start_loading(self):
        self.progress.start()
        self.convert_btn.configure(state="disabled")
        self.update_status("Processing text...")

    def stop_loading(self):
        self.progress.stop()
        self.convert_btn.configure(state="normal")

    def update_status(self, message):
        self.status_label.configure(text=message)
        self.after(3000, lambda: self.status_label.configure(text=""))

    def save_file(self):
        if not self.current_file:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")],
            initialfile="tts_output.mp3"
        )
        
        if file_path:
            try:
                with open(self.current_file, "rb") as src, open(file_path, "wb") as dst:
                    dst.write(src.read())
                self.update_status(f"File saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Save failed: {str(e)}")

    def clear_text(self):
        self.text_input.delete("1.0", "end")
        self.download_btn.configure(state="disabled")
        self.update_status("Text cleared")

    def on_close(self):
        self.running = False
        if self.current_file and os.path.exists(self.current_file):
            try:
                os.remove(self.current_file)
            except Exception as e:
                print(f"Error deleting temp file: {e}")
        mixer.quit()
        self.destroy()

if __name__ == "__main__":
    app = TTSApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.on_close()
