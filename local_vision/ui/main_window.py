import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import queue
import configparser
import os
import pyperclipimg
import tempfile
from tkinterdnd2 import DND_FILES, TkinterDnD


from local_vision.logic.llm_manager import LLM_Manager
from local_vision.data.history_manager import HistoryManager
from local_vision.logic.image_processor import ImageProcessor
from local_vision.logic.tts_manager import TTSManager


# Apply the theme as soon as the app starts
config = configparser.ConfigParser()
config.read('config.ini')
theme = config.get('Accessibility', 'Theme', fallback='system')
ctk.set_appearance_mode(theme)


def make_accessible(widget, text, tts_manager=None):
    """
    Makes a CustomTkinter widget accessible by:
    1. Enabling focus (takefocus=True) on internal components
    2. Binding FocusIn event for TTS
    3. Binding Enter (hover) event for TTS
    """
    if tts_manager is None:
        from local_vision.logic.tts_manager import TTSManager
        tts_manager = TTSManager()

    try:
        # Enable focus on the widget's internal parts
        # This fixes the issue where CTk widgets aren't focusable by default
        if hasattr(widget, "_canvas"):
            widget._canvas.configure(takefocus=1)
        if hasattr(widget, "_entry"):
            widget._entry.configure(takefocus=1)
        if hasattr(widget, "_textbox"):
            widget._textbox.configure(takefocus=1)
            
        try:
            widget.configure(takefocus=1)
        except:
            pass

        def on_focus(event):
            tts_manager.speak(text)
            
        def on_hover(event):
            tts_manager.speak(text)

        # Bind events using add="+" to preserve existing bindings
        widget.bind("<FocusIn>", on_focus, add="+")
        widget.bind("<Enter>", on_hover, add="+")

        if isinstance(widget, ctk.CTkButton):
            def invoke_command(event):
                if widget._command:
                    widget._command()
            
            widget.bind("<Return>", invoke_command, add="+")
            widget.bind("<space>", invoke_command, add="+")
        
    except Exception as e:
        print(f"Error making widget accessible: {e}")


class LoginWindow(ctk.CTkToplevel):
    """
    A window that prompts the user for a nickname.
    """
    def __init__(self, master):
        super().__init__(master)
        self.title("Welcome to Local Vision")
        self.geometry("300x150")
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.nickname = None
        self.tts = TTSManager()

        self.label = ctk.CTkLabel(self, text="Please enter your nickname:")
        self.label.pack(pady=10)

        self.entry = ctk.CTkEntry(self)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self._on_submit)
        
        make_accessible(self.entry, "Enter your nickname", self.tts)

        self.button = ctk.CTkButton(self, text="Start", command=self._on_submit)
        self.button.pack(pady=10)
        make_accessible(self.button, "Start button", self.tts)

        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack()

        self.entry.focus()
        
        self.after(500, lambda: self.tts.speak("Welcome to Local Vision. Please enter your nickname and press Enter."))

    def _on_submit(self, event=None):
        nickname = self.entry.get().strip()
        if nickname:
            self.nickname = nickname
            self.destroy()
        else:
            error_msg = "Nickname cannot be empty."
            self.error_label.configure(text=error_msg)
            self.tts.speak(error_msg)

    def _on_close(self):
        """Handles the window close event."""
        self.nickname = None
        self.master.destroy() # Close the main app if a login is cancelled

    def get_nickname(self):
        """Waits for the window to close and returns the nickname."""
        self.master.wait_window(self)
        return self.nickname

class ConfirmationDialog(ctk.CTkToplevel):
    """A simple confirmation dialog."""
    def __init__(self, master, title="Confirm", message="Are you sure?"):
        super().__init__(master)
        self.title(title)
        self.geometry("300x120")
        self.transient(master)
        self.grab_set()

        self.result = False

        self.label = ctk.CTkLabel(self, text=message)
        self.label.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        self.ok_button = ctk.CTkButton(self.button_frame, text="OK", command=self.on_ok)
        self.ok_button.pack(side="left", padx=10)
        make_accessible(self.ok_button, "OK button")

        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side="right", padx=10)
        make_accessible(self.cancel_button, "Cancel button")

    def on_ok(self):
        self.result = True
        self.destroy()

    def on_cancel(self):
        self.result = False
        self.destroy()

    def get_result(self):
        self.master.wait_window(self)
        return self.result

class HistoryWindow(ctk.CTkToplevel):
    """
    A window for browsing, loading, and deleting conversation history.
    """
    def __init__(self, master, history_manager: HistoryManager):
        super().__init__(master)
        self.title("Conversation History")
        self.geometry("500x500")
        self.transient(master)
        self.grab_set()

        self.history_manager = history_manager
        self.main_app = master

        self.label = ctk.CTkLabel(self, text="Select a conversation:")
        self.label.pack(pady=10)

        self.conversation_list = ctk.CTkScrollableFrame(self)
        self.conversation_list.pack(fill="both", expand=True, padx=10, pady=5)

        self.load_conversations()

    def load_conversations(self):
        """Fetches and displays the list of conversations with delete buttons."""
        for widget in self.conversation_list.winfo_children():
            widget.destroy()

        conversations = self.history_manager.get_conversations()
        if not conversations:
            label = ctk.CTkLabel(self.conversation_list, text="No history found.")
            label.pack()
            return

        for conv in conversations:
            conv_id, timestamp, nickname = conv

            frame = ctk.CTkFrame(self.conversation_list)
            frame.pack(fill="x", pady=2)

            btn_text = f"{nickname} - {timestamp}"
            button = ctk.CTkButton(
                frame,
                text=btn_text,
                command=lambda c=conv_id: self.load_selected_conversation(c)
            )
            button.pack(side="left", fill="x", expand=True, padx=(0, 5))
            make_accessible(button, f"Conversation: {btn_text}", self.main_app.tts)

            delete_button = ctk.CTkButton(
                frame, text="Delete", width=80, fg_color="red",
                command=lambda c=conv_id: self.delete_selected_conversation(c)
            )
            delete_button.pack(side="right")
            make_accessible(delete_button, "Delete conversation button", self.main_app.tts)

    def load_selected_conversation(self, conversation_id):
        """Tells the main app to load the selected conversation."""
        self.main_app.load_conversation_history(conversation_id)
        self.destroy()

    def delete_selected_conversation(self, conversation_id):
        """Deletes a conversation after confirmation."""
        dialog = ConfirmationDialog(self, message="Delete this conversation permanently?")
        if dialog.get_result():
            self.history_manager.delete_conversation(conversation_id)
            self.load_conversations()

class SettingsWindow(ctk.CTkToplevel):
    """
    A window for application settings, including model selection and accessibility.
    """
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("500x400")
        self.transient(master)
        self.grab_set()

        self.main_app = master

        self.model_frame = ctk.CTkFrame(self)
        self.model_frame.pack(fill="x", padx=10, pady=10)

        self.model_label = ctk.CTkLabel(self.model_frame, text="LLM Model Management")
        self.model_label.pack()

        self.current_model_label = ctk.CTkLabel(self.model_frame, text=f"Current Model: {self.main_app.model_identifier}", wraplength=480)
        self.current_model_label.pack(pady=5)

        self.current_model_label.pack(pady=5)

        self.model_entry_frame = ctk.CTkFrame(self.model_frame)
        self.model_entry_frame.pack(pady=10, fill="x", padx=10)

        self.model_entry = ctk.CTkEntry(self.model_entry_frame, placeholder_text="Enter model identifier (e.g., org/repo)")
        self.model_entry.insert(0, self.main_app.model_identifier)
        self.model_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        make_accessible(self.model_entry, "Model identifier input", self.main_app.tts)

        self.save_model_button = ctk.CTkButton(self.model_entry_frame, text="Save", width=80, command=self.save_model_identifier)
        self.save_model_button.pack(side="left")
        make_accessible(self.save_model_button, "Save model button", self.main_app.tts)


        make_accessible(self.save_model_button, "Save model button", self.main_app.tts)


        self.accessibility_frame = ctk.CTkFrame(self)
        self.accessibility_frame.pack(fill="x", padx=10, pady=10)

        self.accessibility_label = ctk.CTkLabel(self.accessibility_frame, text="Accessibility")
        self.accessibility_label.pack()

        self.theme_menu = ctk.CTkOptionMenu(self.accessibility_frame, values=["System", "Light", "Dark"],
                                            command=self.change_theme)
        self.theme_menu.set(self.main_app.theme.capitalize())
        self.theme_menu.pack(pady=10)
        make_accessible(self.theme_menu, "Theme selection menu", self.main_app.tts)

        self.font_frame = ctk.CTkFrame(self.accessibility_frame)
        self.font_frame.pack(pady=5)

        self.font_label = ctk.CTkLabel(self.font_frame, text="Font Size:")
        self.font_label.pack(side="left", padx=5)

        self.decrease_font_button = ctk.CTkButton(self.font_frame, text="-", width=30, command=self.main_app.decrease_font_size)
        self.decrease_font_button.pack(side="left")
        make_accessible(self.decrease_font_button, "Decrease font size button", self.main_app.tts)

        self.increase_font_button = ctk.CTkButton(self.font_frame, text="+", width=30, command=self.main_app.increase_font_size)
        self.increase_font_button.pack(side="left", padx=5)
        make_accessible(self.increase_font_button, "Increase font size button", self.main_app.tts)

        make_accessible(self.increase_font_size_button, "Increase font size button", self.main_app.tts)

        self.voice_frame = ctk.CTkFrame(self.accessibility_frame)
        self.voice_frame.pack(pady=10, fill="x")
        
        self.voice_label = ctk.CTkLabel(self.voice_frame, text="Text-to-Speech:")
        self.voice_label.pack(side="left", padx=5)
        
        self.voice_switch = ctk.CTkSwitch(self.voice_frame, text="Enable Voice", command=self.toggle_voice)
        from local_vision.logic.tts_manager import TTSManager
        if TTSManager().enabled:
            self.voice_switch.select()
        else:
            self.voice_switch.deselect()
        self.voice_switch.pack(side="right", padx=5)
        self.voice_switch.pack(side="right", padx=5)
        make_accessible(self.voice_switch, "Voice toggle switch", self.main_app.tts)

        make_accessible(self.voice_switch, "Voice toggle switch", self.main_app.tts)

        self.discord_frame = ctk.CTkFrame(self)
        self.discord_frame.pack(fill="x", padx=10, pady=10)

        self.discord_label = ctk.CTkLabel(self.discord_frame, text="Discord Integration")
        self.discord_label.pack()

        self.token_entry = ctk.CTkEntry(self.discord_frame, placeholder_text="Discord Bot Token")
        self.token_entry.insert(0, self.main_app.discord_token or "")
        self.token_entry.pack(fill="x", padx=5, pady=5)
        make_accessible(self.token_entry, "Discord Token Input", self.main_app.tts)

        self.discord_button_frame = ctk.CTkFrame(self.discord_frame, fg_color="transparent")
        self.discord_button_frame.pack(fill="x", pady=5)

        self.save_token_button = ctk.CTkButton(self.discord_button_frame, text="Save Token", width=80, command=self.save_discord_token)
        self.save_token_button.pack(side="left", padx=5)
        make_accessible(self.save_token_button, "Save Discord Token Button", self.main_app.tts)

        self.toggle_bot_button = ctk.CTkButton(self.discord_button_frame, text="Start Bot", width=80, command=self.toggle_discord_bot)
        self.toggle_bot_button.pack(side="right", padx=5)
        
        self.toggle_bot_button.pack(side="right", padx=5)
        
        if self.main_app.discord_bot and self.main_app.discord_bot.is_running:
             self.toggle_bot_button.configure(text="Stop Bot", fg_color="red")
        
        make_accessible(self.toggle_bot_button, "Toggle Discord Bot Button", self.main_app.tts)

    def save_discord_token(self):
        token = self.token_entry.get().strip()
        if token:
            self.main_app.update_discord_token(token)
            self.main_app.tts.speak("Discord token saved")
        else:
            self.main_app.tts.speak("Token cannot be empty")

    def toggle_discord_bot(self):
        if self.main_app.discord_bot and self.main_app.discord_bot.is_running:
            self.main_app.stop_discord_bot()
            self.toggle_bot_button.configure(text="Start Bot", fg_color=["#3B8ED0", "#1F6AA5"])
            self.main_app.tts.speak("Discord bot stopped")
        else:
            if not self.main_app.discord_token:
                self.main_app.tts.speak("Please save a token first")
                return
            
            self.main_app.start_discord_bot()
            self.toggle_bot_button.configure(text="Stop Bot", fg_color="red")
            self.main_app.tts.speak("Discord bot started")

    def toggle_voice(self):
        """Toggles the TTS engine."""
        from local_vision.logic.tts_manager import TTSManager
        tts = TTSManager()
        if self.voice_switch.get():
            tts.enabled = True
            tts.speak("Voice enabled")
        else:
            tts.speak("Voice disabled")
            tts.enabled = False 

    def save_model_identifier(self):
        """Saves the new model identifier from the entry field."""
        new_identifier = self.model_entry.get().strip()
        if new_identifier:
            self.main_app.update_model_identifier(new_identifier)
            self.current_model_label.configure(text=f"Current Model: {new_identifier}")

    def change_theme(self, new_theme):
        """Changes the application theme."""
        self.main_app.update_theme(new_theme.lower())


import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

class InterfaceGrafica(ctk.CTk, TkinterDnD.DnDWrapper):
    """
    The main graphical interface for the Local Vision application.
    """
    def __init__(self, history_manager: HistoryManager):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Local Vision Chat")
        self.geometry("800x600")

        self.history_manager = history_manager
        self.conversation_id = None
        
        self.tts = TTSManager()

        self._load_config()

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self._on_drop)

        logging.info("Starting initialization...")
        self.withdraw()

        logging.debug("Prompting for nickname...")
        self.nickname = self._prompt_for_nickname()
        if not self.nickname:
            logging.info("No nickname provided, exiting...")
            return

        logging.info(f"Got nickname: {self.nickname}")
        self._start_new_conversation()

        logging.debug("Creating widgets...")
        try:
            self._create_widgets()
            logging.debug("Widgets created successfully")
        except Exception as e:
            logging.error(f"Error creating widgets: {e}", exc_info=True)
            raise
        
        logging.debug("Showing window...")
        self.deiconify()
        self.title(f"Local Vision Chat - {self.nickname}")

        self.result_queue = queue.Queue()
        
        # LLM Manager - initialize after UI is ready to display errors
        self.llm_manager = None
        logging.info("Initializing LLM Manager...")
        try:
            self.llm_manager = LLM_Manager(model_identifier=self.model_identifier)
            logging.info("LLM Manager initialized successfully")
        except Exception as e:
            error_msg = f"Failed to connect to LM Studio: {e}\n\nPlease ensure LM Studio is running and a model is loaded."
            self._add_message(f"System Error: {error_msg}", is_system=True)
            logging.error(f"LLM initialization error: {e}", exc_info=True)

        self.discord_bot = None
        self.discord_token = self.config.get('Settings', 'DiscordToken', fallback=None)
        if self.discord_token:
             logging.info("Discord token found in config.")

        logging.debug("Starting queue check...")
        self.after(100, self._check_queue)
        logging.debug("Updating fonts...")
        self.update_all_fonts()
        logging.info("Initialization complete!")
        
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Start heartbeat to verify mainloop is running
        self._heartbeat_count = 0
        self.after(1000, self._heartbeat)
        
    def _heartbeat(self):
        """Periodic heartbeat to verify mainloop is running."""
        self._heartbeat_count += 1
        
        
        # Only log if window is NOT normal or every 60 seconds
        state = self.state()
        if state != 'normal' or self._heartbeat_count % 60 == 0:
            logging.debug(f"Heartbeat {self._heartbeat_count} - Window state: {state}, Visible: {self.winfo_viewable()}")
        
        if state == 'withdrawn':
            logging.warning("Window is withdrawn! Attempting to show...")
            self.deiconify()
        
        try:
            self.after(1000, self._heartbeat)
        except Exception as e:
            logging.error(f"Heartbeat failed: {e}")
        
    def _on_window_close(self):
        """Handle window close event."""
        logging.info("Window close requested")
        self.destroy()


    def _create_widgets(self):
        """Creates and places all widgets in the main window."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.history_frame = ctk.CTkScrollableFrame(self)
        self.history_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        self.input_frame.grid_columnconfigure(1, weight=1)

        self.menu_frame = ctk.CTkFrame(self.input_frame)
        self.menu_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.history_button = ctk.CTkButton(self.menu_frame, text="History", width=80, command=self._open_history)
        self.history_button.pack(side="left", padx=(0,5))
        make_accessible(self.history_button, "History button", self.tts)

        self.settings_button = ctk.CTkButton(self.menu_frame, text="Settings", width=80, command=self._open_settings)
        self.settings_button.pack(side="left")
        make_accessible(self.settings_button, "Settings button", self.tts)

        self.attach_button = ctk.CTkButton(self.input_frame, text="Attach Image", width=120, command=self._on_attach_click)
        self.attach_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        make_accessible(self.attach_button, "Attach Image button", self.tts)

        self.paste_button = ctk.CTkButton(self.input_frame, text="Paste Image", width=120, command=self._on_paste)
        self.paste_button.grid(row=0, column=1, padx=(130, 5), pady=5, sticky="w")
        make_accessible(self.paste_button, "Paste Image button", self.tts)


        self.text_input = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message...")
        self.text_input.grid(row=0, column=1, sticky="ew", padx=(260, 5), pady=5)
        self.text_input.bind("<Return>", self._on_send_text)
        make_accessible(self.text_input, "Message input", self.tts)


        self.send_button = ctk.CTkButton(self.input_frame, text="Send", width=80, command=self._on_send_text)
        self.send_button.grid(row=0, column=2, padx=5, pady=5)
        make_accessible(self.send_button, "Send button", self.tts)

    def _load_config(self):
        """Loads settings from config.ini."""
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.model_identifier = self.config.get('Settings', 'ModelIdentifier', fallback='local-model')
        self.theme = self.config.get('Accessibility', 'Theme', fallback='system')
        self.font_size = self.config.getint('Accessibility', 'FontSize', fallback=12)
        
        voice_enabled = self.config.getboolean('Accessibility', 'VoiceEnabled', fallback=True)
        self.tts.enabled = voice_enabled

        ctk.set_appearance_mode(self.theme)


    def _save_config(self):
        """Saves current settings to config.ini."""
        if 'Settings' not in self.config:
            self.config['Settings'] = {}
        if 'Accessibility' not in self.config:
            self.config['Accessibility'] = {}

        self.config['Settings']['ModelIdentifier'] = self.model_identifier
        if self.discord_token:
            self.config['Settings']['DiscordToken'] = self.discord_token
        self.config['Accessibility']['Theme'] = self.theme
        self.config['Accessibility']['FontSize'] = str(self.font_size)
        self.config['Accessibility']['VoiceEnabled'] = str(self.tts.enabled)


        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def update_model_identifier(self, new_identifier):
        """Updates the model identifier and saves it."""
        self.model_identifier = new_identifier
        self._save_config()
        try:
            self.llm_manager = LLM_Manager(model_identifier=self.model_identifier)
            logging.info(f"Model updated to: {self.model_identifier}")
            self._add_message(f"System: Model updated successfully to {self.model_identifier}", is_system=True)
            self.tts.speak("Model updated successfully")
        except Exception as e:
            self.llm_manager = None
            error_msg = f"Failed to connect with new model: {e}"
            self._add_message(f"System Error: {error_msg}", is_system=True)
            logging.error(f"Model update error: {e}")
            self.tts.speak("Failed to update model")

    def update_discord_token(self, token):
        self.discord_token = token
        self._save_config()

    def start_discord_bot(self):
        if not self.discord_token:
            return
        
        if not self.llm_manager:
            self._add_message("System Error: Cannot start Discord bot without LLM Manager.", is_system=True)
            return

        try:
            from local_vision.logic.discord_bot import DiscordBot
            self.discord_bot = DiscordBot(self.discord_token, self.llm_manager)
            self.discord_bot.start_bot()
            self._add_message("System: Discord Bot started.", is_system=True)
        except Exception as e:
            self._add_message(f"System Error: Failed to start Discord Bot: {e}", is_system=True)

    def stop_discord_bot(self):
        if self.discord_bot:
            self.discord_bot.stop_bot()
            self.discord_bot = None
            self._add_message("System: Discord Bot stopped.", is_system=True)

    def update_theme(self, new_theme):
        """Updates the theme and saves it."""
        self.theme = new_theme
        ctk.set_appearance_mode(self.theme)
        self._save_config()

    def increase_font_size(self):
        self.font_size += 1
        self.update_all_fonts()
        self._save_config()

    def decrease_font_size(self):
        self.font_size = max(8, self.font_size - 1) # Minimum font size of 8
        self.update_all_fonts()
        self._save_config()

    def update_all_fonts(self):
        """Iterates through all widgets and updates their font size."""
        try:
            logging.debug(f"Updating fonts to size {self.font_size}")
            new_font = (None, self.font_size)
            ctk.CTkFont(size=self.font_size)

            # Update existing widgets - make a copy of children list to avoid modification during iteration
            children = list(self.winfo_children())
            for widget in children:
                try:
                    self._update_widget_font(widget, new_font)
                except Exception as e:
                    logging.debug(f"Error updating font for widget {widget}: {e}")
            logging.debug("Fonts updated successfully")
        except Exception as e:
            logging.error(f"Error in update_all_fonts: {e}", exc_info=True)

    def _update_widget_font(self, widget, font):
        """Recursively update font for a widget and its children."""
        try:
            if not widget.winfo_exists():
                return
                
            widget.configure(font=font)
        except Exception:
            pass

        try:
            # Make a copy of children list to avoid modification during iteration
            children = list(widget.winfo_children())
            for child in children:
                self._update_widget_font(child, font)
        except Exception as e:
            logging.debug(f"Error iterating widget children: {e}")


    def _prompt_for_nickname(self):
        """Creates the login window and gets the user's nickname."""
        login_win = LoginWindow(self)
        return login_win.get_nickname()

    def _start_new_conversation(self):
        """Creates a new conversation in the database."""
        self.conversation_id = self.history_manager.create_conversation(self.nickname)

    def _on_send_text(self, event=None):
        """Handles sending a text message."""
        message = self.text_input.get().strip()
        if not message:
            return

        self._add_message(f"{self.nickname}: {message}")
        self.history_manager.save_interaction(self.conversation_id, "user", "text", content=message)
        self.text_input.delete(0, "end")

        if self.llm_manager:
            history = self.history_manager.get_conversation_history(self.conversation_id, as_dict=True)
            self.llm_manager.get_text_response(message, history, self.result_queue)
            self._add_message("System: Processing...", is_system=True)
        else:
            self._add_message("System Error: LLM not connected. Please check LM Studio.", is_system=True)


    def _on_attach_click(self):
        """Handles the attach image button click."""
        filepath = filedialog.askopenfilename(
            title="Select an image",
            filetypes=(("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*"))
        )
        if filepath:
            self._process_image_submission(filepath)

    def _on_drop(self, event):
        """Handles a file being dropped on the window."""
        # The event data is a string of file paths, potentially with spaces and braces
        filepath = self.tk.splitlist(event.data)[0]
        if filepath:
            self._process_image_submission(filepath)

    def _on_paste(self):
        """Handles pasting an image from the clipboard."""
        temp_path = None
        try:
            img = pyperclipimg.paste()
            if img:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    img.save(temp_file, "PNG")
                    temp_path = temp_file.name

                self._process_image_submission(temp_path)
            else:
                self._add_message("System: No image found on clipboard.", is_system=True)
        except Exception as e:
            self._add_message(f"System: Error pasting image: {e}", is_system=True)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    def _process_image_submission(self, filepath):
        """Shared logic for processing an image from any source."""
        supported_formats = ('.png', '.jpg', '.jpeg')
        if not filepath.lower().endswith(supported_formats):
            self._add_message("System: Formato de arquivo não suportado. Use JPEG, PNG, etc.", is_system=True)
            return

        self._add_message(f"{self.nickname} (image):")
        self.history_manager.save_interaction(self.conversation_id, "user", "image", image_path=filepath)

        if not self._add_image(filepath):
            return

        if self.llm_manager:
            self._add_message("System: Processing...", is_system=True)
            self.llm_manager.get_image_description(filepath, self.result_queue)
        else:
            self._add_message("System Error: LLM not connected. Cannot process image.", is_system=True)


    def _check_queue(self):
        """Checks the result queue for new messages and updates the UI."""
        try:
            response = self.result_queue.get_nowait()
            response_type = response.get("type")
            content = response.get("content", "No content received.")

            children = self.history_frame.winfo_children()
            if children:
                children[-1].destroy()

            self._add_message(f"System: {content}", is_system=True)
            
            self.tts.speak(content)

            if response_type == "description":
                self.history_manager.save_interaction(self.conversation_id, "system", "description", content=content)
            elif response_type == "text_response":
                self.history_manager.save_interaction(self.conversation_id, "system", "text", content=content)
            elif response_type == "error":
                 pass

        except queue.Empty:
            pass # No message yet
        except Exception as e:
            logging.error(f"Error in _check_queue: {e}", exc_info=True)

        # Always reschedule the next check
        try:
            self.after(100, self._check_queue)
        except Exception as e:
            logging.error(f"Error scheduling next queue check: {e}")

    def _open_history(self):
        """Opens the conversation history window."""
        HistoryWindow(self, self.history_manager)

    def _open_settings(self):
        """Opens the settings window."""
        SettingsWindow(self)

    def load_conversation_history(self, conversation_id):
        """Loads and displays a selected conversation from history."""
        # Clear the current chat display
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        self.conversation_id = conversation_id
        interactions = self.history_manager.get_conversation_history(conversation_id)

        # Get the nickname for this historic conversation
        conv_details = [c for c in self.history_manager.get_conversations() if c[0] == conversation_id]
        historic_nickname = conv_details[0][2] if conv_details else "user"


        for interaction in interactions:
            actor = interaction[3]
            interaction_type = interaction[4]
            content = interaction[5]
            image_path = interaction[6]

            if actor == "user":
                if interaction_type == "text":
                    self._add_message(f"{historic_nickname}: {content}")
                elif interaction_type == "image":
                    self._add_message(f"{historic_nickname} (image):")
                    self._add_image(image_path)
            elif actor == "system":
                self._add_message(f"System: {content}", is_system=True)



    def _add_message(self, message, is_system=False):
        """Adds a text message to the history frame."""
        # Determine colors based on system/user
        text_color = None
        
        if is_system:
            text_color = "orange" if "Error" in message else "gray"
        
        # Use CTkLabel for better text formatting (wrapping)
        msg_label = ctk.CTkLabel(
            self.history_frame, 
            text=message, 
            anchor="w", 
            justify="left",
            wraplength=600, # Allow text to wrap
            text_color=text_color,
            # fg_color="transparent" # Default is transparent
        )
        msg_label.pack(fill="x", padx=5, pady=5)
        
        # Bind focus event to read the message
        make_accessible(msg_label, message, self.tts)
        
        # Add click event to speak message (since Label doesn't have command)
        msg_label.bind("<Button-1>", lambda e: self.tts.speak(message))

    def _add_image(self, filepath):
        """
        Adds an image to the history frame. Returns True on success, False on failure.
        """
        ctk_image = ImageProcessor.process_and_resize(filepath)
        if ctk_image:
            # Use CTkButton for accessibility
            img_button = ctk.CTkButton(
                self.history_frame, 
                image=ctk_image, 
                text="",
                fg_color="transparent",
                hover_color="gray20",
                height=ctk_image.cget("size")[1] + 10,
                command=lambda: self.tts.speak("Image sent")
            )
            img_button.pack(padx=5, pady=5)
            make_accessible(img_button, "Image sent", self.tts)
            return True
        else:
            # As per the sequence diagram for "falha no carregamento"
            self._add_message("System: Falha ao carregar a imagem. Tente novamente.", is_system=True)
            return False


    def run(self):
        """Starts the main application loop."""
        if self.nickname:
            try:
                logging.info("Starting mainloop...")
                self.mainloop()
                logging.info("Mainloop exited normally")
            except Exception as e:
                logging.critical(f"FATAL ERROR in mainloop: {e}", exc_info=True)
                input("Press Enter to close...")
        else:
            logging.info("No nickname, not starting mainloop")
