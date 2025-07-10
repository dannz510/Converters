import customtkinter as ctk
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk
import os
import threading
import tkinter as tk
import json # For saving/loading settings
import shutil # For removing temporary directories
import tempfile # For creating temporary directories
from urllib.parse import urlparse # To check for direct image links

# Import the core conversion functions from the separate file
from converter_core import convert_media, download_media_from_url

class MediaConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ultimate Media Converter")
        self.geometry("850x950") # Increased default height and width for better layout
        self.resizable(True, True) # Make window resizable

        # Configure grid layout for main window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header row - fixed height
        self.grid_rowconfigure(1, weight=1) # Main content row - expands

        # Load assets (icons)
        self.load_assets()

        # Load settings
        self.settings_file = "settings.json"
        self.load_settings()

        # Set default appearance mode and color theme for a modern look
        ctk.set_appearance_mode("Dark") # Force Dark mode for a consistent modern feel
        ctk.set_default_color_theme("blue") # Default blue theme

        # Header Frame - Enhanced Appearance
        self.header_frame = ctk.CTkFrame(self, corner_radius=18, border_width=3, border_color="#555555", fg_color=("#3A3A3A", "#2A2A2A"))
        self.header_frame.grid(row=0, column=0, padx=25, pady=25, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1) # Title
        self.header_frame.grid_columnconfigure(1, weight=0) # Theme switch
        self.header_frame.grid_columnconfigure(2, weight=0) # Settings button

        self.app_title_label = ctk.CTkLabel(
            self.header_frame,
            text="Ultimate Media Converter",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold", slant="italic"),
            text_color="#E0E0E0" # Lighter text for contrast
        )
        self.app_title_label.grid(row=0, column=0, padx=25, pady=15, sticky="w")

        # Theme Switch - Integrated into Header
        self.theme_switch_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.theme_switch_frame.grid(row=0, column=1, padx=(0, 15), pady=10, sticky="e")

        self.theme_label = ctk.CTkLabel(self.theme_switch_frame, text="Theme:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#C0C0C0")
        self.theme_label.grid(row=0, column=0, padx=(0, 5))

        self.theme_option_menu = ctk.CTkOptionMenu(
            self.theme_switch_frame,
            values=["System", "Light", "Dark"],
            command=self.change_theme_event,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            fg_color="#4A4A4A",
            button_color="#6A6A6A",
            button_hover_color="#8A8A8A",
            dropdown_fg_color="#4A4A4A",
            dropdown_hover_color="#6A6A6A"
        )
        self.theme_option_menu.grid(row=0, column=1)
        self.theme_option_menu.set(ctk.get_appearance_mode().capitalize())

        # Settings Button - Enhanced Appearance
        self.settings_button = ctk.CTkButton(
            self.header_frame,
            text="",
            command=self.open_settings,
            width=45, height=45, corner_radius=12,
            image=self.settings_icon,
            fg_color="#444444",
            hover_color="#666666",
            border_width=2, border_color="#666666"
        )
        self.settings_button.grid(row=0, column=2, padx=(0, 25), pady=10, sticky="e")

        # --- Mode Selection Frame - Enhanced Appearance ---
        self.mode_selection_frame = ctk.CTkFrame(self, corner_radius=18, border_width=3, border_color="#555555", fg_color=("#3A3A3A", "#2A2A2A"))
        self.mode_selection_frame.grid(row=1, column=0, padx=25, pady=(0, 25), sticky="nsew")
        self.mode_selection_frame.grid_columnconfigure((0,1,2), weight=1) # Columns expand
        self.mode_selection_frame.grid_rowconfigure(0, weight=0) # Label row
        self.mode_selection_frame.grid_rowconfigure(1, weight=1) # Buttons row - expands

        self.mode_label = ctk.CTkLabel(self.mode_selection_frame, text="Select Conversion Type:", font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), text_color="#E0E0E0")
        self.mode_label.grid(row=0, column=0, columnspan=3, pady=(35, 25))

        # Image Mode Button - Custom Colors & 3D effect
        self.image_mode_button = ctk.CTkButton(
            self.mode_selection_frame,
            text="Image",
            command=lambda: self.select_mode("image"),
            image=self.image_mode_icon,
            compound="top",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            width=180, height=180, corner_radius=20,
            fg_color="#2A7CBA", # Custom color for image button
            hover_color="#3A8CDA",
            border_width=3, border_color="#1F5A8C",
            text_color="#FFFFFF"
        )
        self.image_mode_button.grid(row=1, column=0, padx=25, pady=25, sticky="nsew")

        # Video Mode Button - Custom Colors & 3D effect
        self.video_mode_button = ctk.CTkButton(
            self.mode_selection_frame,
            text="Video",
            command=lambda: self.select_mode("video"),
            image=self.video_mode_icon,
            compound="top",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            width=180, height=180, corner_radius=20,
            fg_color="#E67E22", # Custom color for video button
            hover_color="#F39C12",
            border_width=3, border_color="#B8651B",
            text_color="#FFFFFF"
        )
        self.video_mode_button.grid(row=1, column=1, padx=25, pady=25, sticky="nsew")

        # Audio Mode Button - Custom Colors & 3D effect
        self.audio_mode_button = ctk.CTkButton(
            self.mode_selection_frame,
            text="Audio",
            command=lambda: self.select_mode("audio"),
            image=self.audio_mode_icon,
            compound="top",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            width=180, height=180, corner_radius=20,
            fg_color="#27AE60", # Custom color for audio button
            hover_color="#2ECC71",
            border_width=3, border_color="#1F8C4B",
            text_color="#FFFFFF"
        )
        self.audio_mode_button.grid(row=1, column=2, padx=25, pady=25, sticky="nsew")


        # --- Conversion Options Frame (Initially hidden) - Enhanced Appearance ---
        self.conversion_options_frame = ctk.CTkFrame(self, corner_radius=18, border_width=3, border_color="#555555", fg_color=("#3A3A3A", "#2A2A2A"))
        # This frame will be gridded later when a mode is selected
        self.conversion_options_frame.grid_columnconfigure(0, weight=1) # Input entry column expands
        self.conversion_options_frame.grid_columnconfigure(1, weight=0) # Button column fixed
        # Rows will be dynamically configured in select_mode and start_conversion_thread
        self.conversion_options_frame.grid_rowconfigure(0, weight=0) # Back Button
        self.conversion_options_frame.grid_rowconfigure(1, weight=0) # Input File Label
        self.conversion_options_frame.grid_rowconfigure(2, weight=0) # Input File Entry/Browse
        self.conversion_options_frame.grid_rowconfigure(3, weight=0) # Link Input Label
        self.conversion_options_frame.grid_rowconfigure(4, weight=0) # Link Input Entry/Paste
        self.conversion_options_frame.grid_rowconfigure(5, weight=0) # Output Dir Label
        self.conversion_options_frame.grid_rowconfigure(6, weight=0) # Output Dir Entry/Browse
        self.conversion_options_frame.grid_rowconfigure(7, weight=0) # Output Format Label
        self.conversion_options_frame.grid_rowconfigure(8, weight=0) # Output Format Option
        # Rows 9-13 will be for image/video options, 14 for convert button, 15 for status
        self.conversion_options_frame.grid_rowconfigure(15, weight=1) # Status label row expands

        # Back Button - Enhanced Appearance
        self.back_button = ctk.CTkButton(
            self.conversion_options_frame,
            text="← Back to Modes",
            command=self.back_to_mode_selection,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            width=160, height=35, corner_radius=10,
            fg_color="#555555", hover_color="#777777",
            border_width=2, border_color="#777777"
        )
        self.back_button.grid(row=0, column=0, padx=25, pady=(15, 0), sticky="nw")


        # Input File Section (Browse)
        self.input_label = ctk.CTkLabel(self.conversion_options_frame, text="Input File (Browse):", font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"), text_color="#E0E0E0")
        self.input_label.grid(row=1, column=0, columnspan=2, padx=25, pady=(25, 8), sticky="w")

        self.input_path_entry = ctk.CTkEntry(self.conversion_options_frame, placeholder_text="Select input media file...", height=40, corner_radius=10, font=ctk.CTkFont(size=14), fg_color="#4A4A4A", border_color="#6A6A6A", text_color="#E0E0E0")
        self.input_path_entry.grid(row=2, column=0, padx=25, pady=8, sticky="ew")

        self.browse_input_button = ctk.CTkButton(
            self.conversion_options_frame,
            text="Browse",
            command=self.browse_input_file,
            width=110, height=40, corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            image=self.folder_icon,
            compound="left",
            fg_color="#6A6A6A", hover_color="#8A8A8A", border_width=2, border_color="#8A8A8A"
        )
        self.browse_input_button.grid(row=2, column=1, padx=(0, 25), pady=8, sticky="e")

        # Input File Section (Paste Link - Enabled but with warning)
        self.link_input_label = ctk.CTkLabel(self.conversion_options_frame, text="Input File (Paste Link - Requires yt-dlp for most URLs):", font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"), text_color="#E0E0E0")
        self.link_input_label.grid(row=3, column=0, columnspan=2, padx=25, pady=(20, 8), sticky="w")

        self.link_input_entry = ctk.CTkEntry(self.conversion_options_frame, placeholder_text="Paste direct file URL or video/audio platform link (e.g., YouTube)...", height=40, corner_radius=10, font=ctk.CTkFont(size=14), fg_color="#4A4A4A", border_color="#6A6A6A", text_color="#E0E0E0")
        self.link_input_entry.grid(row=4, column=0, padx=25, pady=8, sticky="ew")

        self.paste_link_button = ctk.CTkButton(
            self.conversion_options_frame,
            text="Paste",
            command=self.paste_link,
            width=110, height=40, corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            image=self.convert_icon, # Reusing convert icon for now
            compound="left",
            fg_color="#6A6A6A", hover_color="#8A8A8A", border_width=2, border_color="#8A8A8A"
        )
        self.paste_link_button.grid(row=4, column=1, padx=(0, 25), pady=8, sticky="e")


        # Output Directory Section
        self.output_dir_label = ctk.CTkLabel(self.conversion_options_frame, text="Output Directory:", font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"), text_color="#E0E0E0")
        self.output_dir_label.grid(row=5, column=0, columnspan=2, padx=25, pady=(20, 8), sticky="w")

        self.output_dir_entry = ctk.CTkEntry(self.conversion_options_frame, placeholder_text="Select output directory...", height=40, corner_radius=10, font=ctk.CTkFont(size=14), fg_color="#4A4A4A", border_color="#6A6A6A", text_color="#E0E0E0")
        self.output_dir_entry.grid(row=6, column=0, padx=25, pady=8, sticky="ew")
        # Pre-fill with default output directory from settings
        self.output_dir_entry.insert(0, self.settings.get("default_output_directory", ""))


        self.browse_output_button = ctk.CTkButton(
            self.conversion_options_frame,
            text="Browse",
            command=self.browse_output_directory,
            width=110, height=40, corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            image=self.folder_icon,
            compound="left",
            fg_color="#6A6A6A", hover_color="#8A8A8A", border_width=2, border_color="#8A8A8A"
        )
        self.browse_output_button.grid(row=6, column=1, padx=(0, 25), pady=8, sticky="e")

        # Output Format Section
        self.format_label = ctk.CTkLabel(self.conversion_options_frame, text="Output Format:", font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"), text_color="#E0E0E0")
        self.format_label.grid(row=7, column=0, columnspan=2, padx=25, pady=(20, 8), sticky="w")

        self.output_format_option = ctk.CTkOptionMenu(
            self.conversion_options_frame,
            values=[], # Will be populated dynamically
            width=220, height=40, corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color="#4A4A4A",
            button_color="#6A6A6A",
            button_hover_color="#8A8A8A",
            dropdown_fg_color="#4A4A4A",
            dropdown_hover_color="#6A6A6A"
        )
        self.output_format_option.grid(row=8, column=0, padx=25, pady=8, sticky="w")
        # No default set here, will be set by select_mode

        # --- Image Specific Options (Initially hidden) ---
        self.image_options_frame = ctk.CTkFrame(self.conversion_options_frame, fg_color="transparent")
        self.image_options_frame.grid_columnconfigure(0, weight=0)
        self.image_options_frame.grid_columnconfigure(1, weight=1)
        self.image_options_frame.grid_columnconfigure(2, weight=0)
        self.image_options_frame.grid_columnconfigure(3, weight=1)
        self.image_options_frame.grid_columnconfigure(4, weight=0) # For percentage label
        self.image_options_frame.grid_rowconfigure((0,1,2), weight=0) # Quality, Rescale Type, Rescale Values

        # Image Quality Slider
        self.quality_label = ctk.CTkLabel(self.image_options_frame, text="Image Quality (1-100):", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), image=self.quality_icon, compound="left", text_color="#E0E0E0")
        self.quality_label.grid(row=0, column=0, padx=(0,15), pady=(20, 8), sticky="w")
        self.quality_slider = ctk.CTkSlider(self.image_options_frame, from_=1, to=100, number_of_steps=99, width=220, corner_radius=10, button_corner_radius=10, fg_color="#6A6A6A", progress_color="#2A7CBA", button_color="#2A7CBA", button_hover_color="#3A8CDA")
        self.quality_slider.set(90) # Default to high quality
        self.quality_slider.grid(row=0, column=1, padx=(0,15), pady=8, sticky="ew")
        self.quality_value_label = ctk.CTkLabel(self.image_options_frame, text="90", font=ctk.CTkFont(size=14), text_color="#E0E0E0")
        self.quality_value_label.grid(row=0, column=2, padx=(0,25), pady=8, sticky="w")
        self.quality_slider.bind("<B1-Motion>", self.update_quality_label)
        self.quality_slider.bind("<ButtonRelease-1>", self.update_quality_label)

        # Image Rescale Options
        self.rescale_label = ctk.CTkLabel(self.image_options_frame, text="Rescale Image:", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), image=self.rescale_icon, compound="left", text_color="#E0E0E0")
        self.rescale_label.grid(row=1, column=0, padx=(0,15), pady=(15, 8), sticky="w")

        self.rescale_mode_var = ctk.StringVar(value="none")
        self.rescale_mode_none_rb = ctk.CTkRadioButton(self.image_options_frame, text="None", variable=self.rescale_mode_var, value="none", command=self.toggle_rescale_inputs, font=ctk.CTkFont(size=14), text_color="#E0E0E0", fg_color="#2A7CBA")
        self.rescale_mode_none_rb.grid(row=1, column=1, padx=(0,15), pady=8, sticky="w")
        self.rescale_mode_percentage_rb = ctk.CTkRadioButton(self.image_options_frame, text="Percentage", variable=self.rescale_mode_var, value="percentage", command=self.toggle_rescale_inputs, font=ctk.CTkFont(size=14), text_color="#E0E0E0", fg_color="#2A7CBA")
        self.rescale_mode_percentage_rb.grid(row=1, column=2, padx=(0,15), pady=8, sticky="w")
        self.rescale_mode_pixels_rb = ctk.CTkRadioButton(self.image_options_frame, text="Pixels", variable=self.rescale_mode_var, value="pixels", command=self.toggle_rescale_inputs, font=ctk.CTkFont(size=14), text_color="#E0E0E0", fg_color="#2A7CBA")
        self.rescale_mode_pixels_rb.grid(row=1, column=3, padx=(0,15), pady=8, sticky="w")

        # Rescale Value Inputs
        self.rescale_value_frame = ctk.CTkFrame(self.image_options_frame, fg_color="transparent")
        self.rescale_value_frame.grid(row=2, column=0, columnspan=5, padx=0, pady=8, sticky="ew")
        self.rescale_value_frame.grid_columnconfigure((0,1,2,3), weight=1) # For inputs

        # Percentage input
        self.percentage_entry = ctk.CTkEntry(self.rescale_value_frame, placeholder_text="e.g., 50", width=90, height=35, corner_radius=10, font=ctk.CTkFont(size=14), fg_color="#4A4A4A", border_color="#6A6A6A", text_color="#E0E0E0")
        self.percentage_label = ctk.CTkLabel(self.rescale_value_frame, text="%", font=ctk.CTkFont(size=14, weight="bold"), text_color="#E0E0E0")

        # Pixel inputs
        self.width_entry = ctk.CTkEntry(self.rescale_value_frame, placeholder_text="Width (px)", width=110, height=35, corner_radius=10, font=ctk.CTkFont(size=14), fg_color="#4A4A4A", border_color="#6A6A6A", text_color="#E0E0E0")
        self.x_label = ctk.CTkLabel(self.rescale_value_frame, text="x", font=ctk.CTkFont(size=14, weight="bold"), text_color="#E0E0E0")
        self.height_entry = ctk.CTkEntry(self.rescale_value_frame, placeholder_text="Height (px)", width=110, height=35, corner_radius=10, font=ctk.CTkFont(size=14), fg_color="#4A4A4A", border_color="#6A6A6A", text_color="#E0E0E0")

        self.toggle_rescale_inputs() # Initialize visibility

        # --- Video Specific Options (Initially hidden) ---
        self.video_options_frame = ctk.CTkFrame(self.conversion_options_frame, fg_color="transparent")
        self.video_options_frame.grid_columnconfigure(0, weight=0)
        self.video_options_frame.grid_columnconfigure(1, weight=1)
        self.video_options_frame.grid_columnconfigure(2, weight=0)
        self.video_options_frame.grid_columnconfigure(3, weight=1)
        self.video_options_frame.grid_rowconfigure((0,1,2,3), weight=0) # Quality, Rescale Type, Rescale Values

        # Video Quality Preset
        self.video_quality_label = ctk.CTkLabel(self.video_options_frame, text="Video Quality Preset:", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), image=self.video_quality_icon, compound="left", text_color="#E0E0E0")
        self.video_quality_label.grid(row=0, column=0, padx=(0,15), pady=(20, 8), sticky="w")
        self.video_quality_option = ctk.CTkOptionMenu(
            self.video_options_frame,
            values=["Default", "1080p", "720p", "480p", "Best Quality (CRF 18)", "Medium Quality (CRF 23)", "Low Quality (CRF 28)"],
            width=220, height=40, corner_radius=10,
            font=ctk.CTkFont(size=14),
            fg_color="#4A4A4A",
            button_color="#6A6A6A",
            button_hover_color="#8A8A8A",
            dropdown_fg_color="#4A4A4A",
            dropdown_hover_color="#6A6A6A"
        )
        self.video_quality_option.grid(row=0, column=1, padx=(0,25), pady=8, sticky="ew")
        self.video_quality_option.set("Default")

        # Video Rescale Options
        self.video_rescale_label = ctk.CTkLabel(self.video_options_frame, text="Rescale Video:", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), image=self.rescale_icon, compound="left", text_color="#E0E0E0")
        self.video_rescale_label.grid(row=1, column=0, padx=(0,15), pady=(15, 8), sticky="w")

        self.video_rescale_mode_var = ctk.StringVar(value="none")
        self.video_rescale_mode_none_rb = ctk.CTkRadioButton(self.video_options_frame, text="None", variable=self.video_rescale_mode_var, value="none", command=self.toggle_video_rescale_inputs, font=ctk.CTkFont(size=14), text_color="#E0E0E0", fg_color="#E67E22")
        self.video_rescale_mode_none_rb.grid(row=1, column=1, padx=(0,15), pady=8, sticky="w")
        self.video_rescale_mode_percentage_rb = ctk.CTkRadioButton(self.video_options_frame, text="Percentage", variable=self.video_rescale_mode_var, value="percentage", command=self.toggle_video_rescale_inputs, font=ctk.CTkFont(size=14), text_color="#E0E0E0", fg_color="#E67E22")
        self.video_rescale_mode_percentage_rb.grid(row=1, column=2, padx=(0,15), pady=8, sticky="w")
        self.video_rescale_mode_pixels_rb = ctk.CTkRadioButton(self.video_options_frame, text="Pixels", variable=self.video_rescale_mode_var, value="pixels", command=self.toggle_video_rescale_inputs, font=ctk.CTkFont(size=14), text_color="#E0E0E0", fg_color="#E67E22")
        self.video_rescale_mode_pixels_rb.grid(row=1, column=3, padx=(0,15), pady=8, sticky="w")

        # Video Rescale Value Inputs
        self.video_rescale_value_frame = ctk.CTkFrame(self.video_options_frame, fg_color="transparent")
        self.video_rescale_value_frame.grid(row=2, column=0, columnspan=5, padx=0, pady=8, sticky="ew")
        self.video_rescale_value_frame.grid_columnconfigure((0,1,2,3), weight=1) # For inputs

        # Video Percentage input
        self.video_percentage_entry = ctk.CTkEntry(self.video_rescale_value_frame, placeholder_text="e.g., 50", width=90, height=35, corner_radius=10, font=ctk.CTkFont(size=14), fg_color="#4A4A4A", border_color="#6A6A6A", text_color="#E0E0E0")
        self.video_percentage_label = ctk.CTkLabel(self.video_rescale_value_frame, text="%", font=ctk.CTkFont(size=14, weight="bold"), text_color="#E0E0E0")

        # Video Pixel inputs
        self.video_width_entry = ctk.CTkEntry(self.video_rescale_value_frame, placeholder_text="Width (px)", width=110, height=35, corner_radius=10, font=ctk.CTkFont(size=14), fg_color="#4A4A4A", border_color="#6A6A6A", text_color="#E0E0E0")
        self.video_x_label = ctk.CTkLabel(self.video_rescale_value_frame, text="x", font=ctk.CTkFont(size=14, weight="bold"), text_color="#E0E0E0")
        self.video_height_entry = ctk.CTkEntry(self.video_rescale_value_frame, placeholder_text="Height (px)", width=110, height=35, corner_radius=10, font=ctk.CTkFont(size=14), fg_color="#4A4A4A", border_color="#6A6A6A", text_color="#E0E0E0")

        self.toggle_video_rescale_inputs() # Initialize visibility


        # Convert Button - Enhanced Appearance
        self.convert_button = ctk.CTkButton(
            self.conversion_options_frame,
            text="Convert Media",
            command=self.start_conversion_thread,
            height=50, corner_radius=15,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            image=self.convert_icon,
            compound="left",
            fg_color="#007ACC", # Windows Blue accent
            hover_color="#005C99",
            border_width=3, border_color="#004A77",
            text_color="#FFFFFF"
        )
        # Initial grid placement, will be adjusted by select_mode
        self.convert_button.grid(row=9, column=0, columnspan=2, padx=25, pady=(30, 15), sticky="ew")

        # Status Message Label - Enhanced Appearance
        self.status_label = ctk.CTkLabel(
            self.conversion_options_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            wraplength=400, # Initial wrap length
            text_color="#E0E0E0"
        )
        # Initial grid placement, will be adjusted by select_2mode
        self.status_label.grid(row=10, column=0, columnspan=2, padx=25, pady=(10, 25), sticky="ew")

        # Bind configure event to update wraplength
        self.conversion_options_frame.bind("<Configure>", self.on_frame_resize)

        # Store current mode
        self.current_mode = None

    def update_quality_label(self, event=None):
        """Updates the image quality value label as the slider is moved."""
        self.quality_value_label.configure(text=f"{int(self.quality_slider.get())}")

    def toggle_rescale_inputs(self):
        """Shows/hides image rescale input fields based on selected mode."""
        mode = self.rescale_mode_var.get()

        # Hide all first
        self.percentage_entry.grid_forget()
        self.percentage_label.grid_forget()
        self.width_entry.grid_forget()
        self.x_label.grid_forget()
        self.height_entry.grid_forget()

        if mode == "percentage":
            self.percentage_entry.grid(row=0, column=0, padx=(0,5), pady=0, sticky="w")
            self.percentage_label.grid(row=0, column=1, padx=(0,20), pady=0, sticky="w")
        elif mode == "pixels":
            self.width_entry.grid(row=0, column=0, padx=(0,5), pady=0, sticky="w")
            self.x_label.grid(row=0, column=1, padx=(0,5), pady=0, sticky="w")
            self.height_entry.grid(row=0, column=2, padx=(0,0), pady=0, sticky="w")
        
        # Ensure the rescale_value_frame is visible only if a mode other than 'none' is selected
        if mode == "none":
            self.rescale_value_frame.grid_remove()
        else:
            self.rescale_value_frame.grid()

    def toggle_video_rescale_inputs(self):
        """Shows/hides video rescale input fields based on selected mode."""
        mode = self.video_rescale_mode_var.get()

        # Hide all first
        self.video_percentage_entry.grid_forget()
        self.video_percentage_label.grid_forget()
        self.video_width_entry.grid_forget()
        self.video_x_label.grid_forget()
        self.video_height_entry.grid_forget()

        if mode == "percentage":
            self.video_percentage_entry.grid(row=0, column=0, padx=(0,5), pady=0, sticky="w")
            self.video_percentage_label.grid(row=0, column=1, padx=(0,20), pady=0, sticky="w")
        elif mode == "pixels":
            self.video_width_entry.grid(row=0, column=0, padx=(0,5), pady=0, sticky="w")
            self.video_x_label.grid(row=0, column=1, padx=(0,5), pady=0, sticky="w")
            self.video_height_entry.grid(row=0, column=2, padx=(0,0), pady=0, sticky="w")
        
        if mode == "none":
            self.video_rescale_value_frame.grid_remove()
        else:
            self.video_rescale_value_frame.grid()


    def on_frame_resize(self, event):
        """Adjusts status label wraplength on frame resize."""
        # Calculate new wraplength based on the frame's width
        new_wraplength = event.width - 50 # 25px padding on each side
        if new_wraplength > 0:
            self.status_label.configure(wraplength=new_wraplength)


    def load_assets(self):
        """Loads image assets for icons."""
        try:
            # Using the new, larger icon sizes for mode buttons (64x64) and others (32x32)
            self.app_icon_img = Image.open("app_icon.png")
            self.app_icon = ctk.CTkImage(light_image=self.app_icon_img, dark_image=self.app_icon_img, size=(40, 40)) # Slightly smaller for header

            self.folder_icon_img = Image.open("folder_icon.png")
            self.folder_icon = ctk.CTkImage(light_image=self.folder_icon_img, dark_image=self.folder_icon_img, size=(25, 25))

            self.convert_icon_img = Image.open("convert_icon.png")
            self.convert_icon = ctk.CTkImage(light_image=self.convert_icon_img, dark_image=self.convert_icon_img, size=(30, 30))

            self.settings_icon_img = Image.open("settings_icon.png")
            self.settings_icon = ctk.CTkImage(light_image=self.settings_icon_img, dark_image=self.settings_icon_img, size=(30, 30))

            # Mode icons (64x64)
            self.image_mode_icon_img = Image.open("image_mode_icon.png")
            self.image_mode_icon = ctk.CTkImage(light_image=self.image_mode_icon_img, dark_image=self.image_mode_icon_img, size=(64, 64))

            self.video_mode_icon_img = Image.open("video_mode_icon.png")
            self.video_mode_icon = ctk.CTkImage(light_image=self.video_mode_icon_img, dark_image=self.video_mode_icon_img, size=(64, 64))

            self.audio_mode_icon_img = Image.open("audio_mode_icon.png")
            self.audio_mode_icon = ctk.CTkImage(light_image=self.audio_mode_icon_img, dark_image=self.audio_mode_icon_img, size=(64, 64))

            # New icons for quality and rescale (32x32)
            self.quality_icon_img = Image.open("quality_icon.png")
            self.quality_icon = ctk.CTkImage(light_image=self.quality_icon_img, dark_image=self.quality_icon_img, size=(25, 25))

            self.rescale_icon_img = Image.open("rescale_icon.png")
            self.rescale_icon = ctk.CTkImage(light_image=self.rescale_icon_img, dark_image=self.rescale_icon_img, size=(25, 25))

            self.video_quality_icon_img = Image.open("video_quality_icon.png")
            self.video_quality_icon = ctk.CTkImage(light_image=self.video_quality_icon_img, dark_image=self.video_quality_icon_img, size=(25, 25))


        except FileNotFoundError:
            print("Error: One or more icon files not found. Please ensure 'icon_generate.py' has been run and the PNGs are in the same directory.")
            # Create dummy images to prevent errors if icons are missing
            self.app_icon = None
            self.folder_icon = None
            self.convert_icon = None
            self.settings_icon = None
            self.image_mode_icon = None
            self.video_mode_icon = None
            self.audio_mode_icon = None
            self.quality_icon = None
            self.rescale_icon = None
            self.video_quality_icon = None
        except Exception as e:
            print(f"Error loading assets: {e}")
            # Fallback to None for all icons if any error occurs
            self.app_icon = None
            self.folder_icon = None
            self.convert_icon = None
            self.settings_icon = None
            self.image_mode_icon = None
            self.video_mode_icon = None
            self.audio_mode_icon = None
            self.quality_icon = None
            self.rescale_icon = None
            self.video_quality_icon = None


    def load_settings(self):
        """Loads settings from settings.json or creates default settings."""
        default_settings = {
            "default_output_directory": os.path.join(os.path.expanduser("~"), "ConvertedMedia"),
            "show_verbose_ffmpeg_output": False
        }
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    self.settings = json.load(f)
            except json.JSONDecodeError:
                print("Error reading settings.json, using default settings.")
                self.settings = default_settings
        else:
            self.settings = default_settings
            self.save_settings() # Save defaults if file doesn't exist

    def save_settings(self):
        """Saves current settings to settings.json."""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def change_theme_event(self, new_theme: str):
        """Changes the CustomTkinter theme."""
        ctk.set_appearance_mode(new_theme)

    def select_mode(self, mode: str):
        """Switches from mode selection to conversion options for the selected mode."""
        self.current_mode = mode
        self.mode_selection_frame.grid_forget() # Hide mode selection
        self.conversion_options_frame.grid(row=1, column=0, padx=25, pady=(0, 25), sticky="nsew") # Show conversion options

        # Hide all optional frames first, regardless of their current visibility
        self.image_options_frame.grid_forget()
        self.video_options_frame.grid_forget()

        # Update title and output formats based on mode
        if mode == "image":
            self.app_title_label.configure(text="Image Converter")
            # Added more image formats
            self.output_format_option.configure(values=["png", "jpg", "jpeg", "webp", "gif", "bmp", "ico", "tiff", "psd", "eps", "avif", "icns"])
            self.output_format_option.set("png")
            self.browse_input_button.configure(text="Browse Image")
            # Show image specific options
            self.image_options_frame.grid(row=9, column=0, columnspan=2, padx=25, pady=(20, 10), sticky="ew")
            # Adjust grid rows for convert button and status label
            self.convert_button.grid(row=14, column=0, columnspan=2, padx=25, pady=(30, 15), sticky="ew")
            self.status_label.grid(row=15, column=0, columnspan=2, padx=25, pady=(10, 25), sticky="ew")
        elif mode == "video":
            self.app_title_label.configure(text="Video Converter")
            # Added more video formats
            self.output_format_option.configure(values=["mp4", "mov", "avi", "mkv", "webm", "3gp", "3g2", "3gpp", "cavs", "dv", "dvr", "flv", "m2ts", "m4v", "mpeg", "mpg", "mts", "mxf", "ogg", "rm", "rmvb"])
            self.output_format_option.set("mp4")
            self.browse_input_button.configure(text="Browse Video")
            # Show video specific options
            self.video_options_frame.grid(row=9, column=0, columnspan=2, padx=25, pady=(20, 10), sticky="ew")
            # Adjust grid rows for convert button and status label
            self.convert_button.grid(row=14, column=0, columnspan=2, padx=25, pady=(30, 15), sticky="ew")
            self.status_label.grid(row=15, column=0, columnspan=2, padx=25, pady=(10, 25), sticky="ew")
        elif mode == "audio":
            self.app_title_label.configure(text="Audio Converter")
            # Added more audio formats
            self.output_format_option.configure(values=["mp3", "wav", "aac", "flac", "ogg", "aif", "aiff", "aifc", "amr", "au", "caf", "dss", "m4a", "m4b", "oga", "voc", "weba", "wma", "ac3"])
            self.output_format_option.set("mp3")
            self.browse_input_button.configure(text="Browse Audio")
            # Adjust grid rows for convert button and status label when no specific options are shown
            self.convert_button.grid(row=9, column=0, columnspan=2, padx=25, pady=(30, 15), sticky="ew")
            self.status_label.grid(row=10, column=0, columnspan=2, padx=25, pady=(10, 25), sticky="ew")

        self.update_status(f"Mode set to {mode.capitalize()} conversion.")

    def back_to_mode_selection(self):
        """Returns to the initial mode selection screen."""
        self.conversion_options_frame.grid_forget()
        self.mode_selection_frame.grid(row=1, column=0, padx=25, pady=(0, 25), sticky="nsew")
        self.app_title_label.configure(text="Ultimate Media Converter")
        self.update_status("Select a conversion type.")
        # Clear entries when going back
        self.input_path_entry.delete(0, ctk.END)
        self.link_input_entry.delete(0, ctk.END)
        self.output_dir_entry.delete(0, ctk.END)
        self.status_label.configure(text="") # Clear status message
        
        # Reset image options when going back
        self.rescale_mode_var.set("none")
        self.toggle_rescale_inputs()
        self.quality_slider.set(90)
        self.update_quality_label()

        # Reset video options when going back
        self.video_quality_option.set("Default")
        self.video_rescale_mode_var.set("none")
        self.toggle_video_rescale_inputs()


    def browse_input_file(self):
        """Opens a file dialog for input media selection, filtered by current mode."""
        filetypes = [("All Files", "*.*")]
        if self.current_mode == "image":
            filetypes.insert(0, ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.ico *.tiff *.psd *.eps *.avif *.icns"))
        elif self.current_mode == "video":
            filetypes.insert(0, ("Video Files", "*.mp4 *.mov *.avi *.mkv *.webm *.3gp *.3g2 *.3gpp *.cavs *.dv *.dvr *.flv *.m2ts *.m4v *.mpeg *.mpg *.mts *.mxf *.ogg *.rm *.rmvb"))
        elif self.current_mode == "audio":
            filetypes.insert(0, ("Audio Files", "*.mp3 *.wav *.aac *.flac *.ogg *.aif *.aiff *.aifc *.amr *.au *.caf *.dss *.m4a *.m4b *.oga *.voc *.weba *.wma *.ac3"))
        file_path = filedialog.askopenfilename(
            title=f"Select Input {self.current_mode.capitalize()} File",
            filetypes=filetypes
        )
        if file_path:
            self.input_path_entry.delete(0, ctk.END)
            self.input_path_entry.insert(0, file_path)
            self.link_input_entry.delete(0, ctk.END) # Clear link field if file is selected
            self.update_status("Input file selected from folder.")

    def browse_output_directory(self):
        """Opens a directory dialog for output path selection."""
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir_entry.delete(0, ctk.END)
            self.output_dir_entry.insert(0, dir_path)
            self.update_status("Output directory selected.")

    def paste_link(self):
        """Attempts to paste content from clipboard to link entry."""
        try:
            clipboard_content = self.clipboard_get()
            self.link_input_entry.delete(0, ctk.END)
            self.link_input_entry.insert(0, clipboard_content)
            self.input_path_entry.delete(0, ctk.END) # Clear file field if link is pasted
            self.update_status("URL pasted. Click 'Convert Media' to download and convert (requires yt-dlp).", "blue")
        except tk.TclError:
            self.update_status("Could not access clipboard. Please copy a URL first.", "error")
        except Exception as e:
            self.update_status(f"Error pasting link: {e}", "error")


    def open_settings(self):
        """Opens a new Toplevel window for settings."""
        if hasattr(self, "settings_window") and self.settings_window.winfo_exists():
            self.settings_window.focus() # Bring to front if already open
            return

        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.title("Settings")
        self.settings_window.geometry("480x350") # Adjusted size
        self.settings_window.transient(self) # Make it appear on top of the main window
        self.settings_window.grab_set() # Make it modal (block interaction with main window)
        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings) # Handle close button
        self.settings_window.configure(fg_color=("#3A3A3A", "#2A2A2A")) # Match main app background

        self.settings_window.grid_columnconfigure(0, weight=1)
        self.settings_window.grid_columnconfigure(1, weight=0) # For browse button

        # Default Output Directory Setting
        self.default_output_label = ctk.CTkLabel(self.settings_window, text="Default Output Folder:", font=ctk.CTkFont(size=15, weight="bold"), text_color="#E0E0E0")
        self.default_output_label.grid(row=0, column=0, padx=25, pady=(25, 8), sticky="w")

        self.default_output_entry = ctk.CTkEntry(self.settings_window, placeholder_text="Select default output folder...", width=320, height=35, corner_radius=10, font=ctk.CTkFont(size=14), fg_color="#4A4A4A", border_color="#6A6A6A", text_color="#E0E0E0")
        self.default_output_entry.grid(row=1, column=0, padx=25, pady=8, sticky="ew")
        self.default_output_entry.insert(0, self.settings.get("default_output_directory", "")) # Load current default

        self.browse_default_output_button = ctk.CTkButton(
            self.settings_window,
            text="Browse",
            command=self.browse_default_output_directory_settings,
            width=90, height=35, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#6A6A6A", hover_color="#8A8A8A", border_width=2, border_color="#8A8A8A"
        )
        self.browse_default_output_button.grid(row=1, column=1, padx=(0, 25), pady=8, sticky="e")

        # Verbose FFmpeg Output (Placeholder)
        self.verbose_label = ctk.CTkLabel(self.settings_window, text="Show Verbose FFmpeg Output:", font=ctk.CTkFont(size=15, weight="bold"), text_color="#E0E0E0")
        self.verbose_label.grid(row=2, column=0, columnspan=2, padx=25, pady=(20, 8), sticky="w")

        self.verbose_checkbox = ctk.CTkCheckBox(self.settings_window, text="Enable detailed logs (Future feature)", state="disabled", font=ctk.CTkFont(size=14), text_color="#E0E0E0", fg_color="#007ACC")
        self.verbose_checkbox.grid(row=3, column=0, columnspan=2, padx=25, pady=8, sticky="w")
        # You would load/save the state of this checkbox here if it were functional
        # if self.settings.get("show_verbose_ffmpeg_output", False):
        #     self.verbose_checkbox.select()

        self.settings_save_button = ctk.CTkButton(
            self.settings_window,
            text="Save Settings",
            command=self.save_settings_and_close,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=12,
            height=45,
            fg_color="#007ACC", hover_color="#005C99", border_width=2, border_color="#004A77"
        )
        self.settings_save_button.grid(row=4, column=0, columnspan=2, padx=25, pady=35, sticky="ew")

        self.settings_window.wait_window() # Wait for settings window to close

    def browse_default_output_directory_settings(self):
        """Opens a directory dialog for default output path selection in settings."""
        dir_path = filedialog.askdirectory(title="Select Default Output Directory")
        if dir_path:
            self.default_output_entry.delete(0, ctk.END)
            self.default_output_entry.insert(0, dir_path)

    def save_settings_and_close(self):
        """Saves settings and closes the settings window."""
        self.settings["default_output_directory"] = self.default_output_entry.get()
        # self.settings["show_verbose_ffmpeg_output"] = self.verbose_checkbox.get() # For future
        self.save_settings()
        self.update_status("Settings saved successfully!", "success")
        self.close_settings()

    def close_settings(self):
        """Closes the settings window and releases grab."""
        self.settings_window.grab_release()
        self.settings_window.destroy()

    def update_status(self, message, color="default"):
        """Updates the status label with a message."""
        if color == "success":
            self.status_label.configure(text_color="green")
        elif color == "error":
            self.status_label.configure(text_color="red")
        elif color == "blue":
            self.status_label.configure(text_color="blue")
        else:
            self.status_label.configure(text_color="#E0E0E0") # Default text color
        self.status_label.configure(text=message)
        self.update_idletasks()

    def start_conversion_thread(self):
        """Starts the conversion process in a separate thread."""
        input_path = self.input_path_entry.get()
        output_dir = self.output_dir_entry.get()
        output_format = self.output_format_option.get()
        link_input = self.link_input_entry.get()

        # Image specific options
        image_quality = None
        image_scale_width = None
        image_scale_height = None
        image_scale_percentage = None

        # Video specific options
        video_quality_preset = None
        video_scale_width = None
        video_scale_height = None
        video_scale_percentage = None


        if self.current_mode == "image":
            image_quality = int(self.quality_slider.get())
            rescale_mode = self.rescale_mode_var.get()
            if rescale_mode == "percentage":
                try:
                    image_scale_percentage = float(self.percentage_entry.get())
                    if not (0 < image_scale_percentage <= 1000): # Allow up to 10x scaling
                        self.update_status("Error: Percentage must be between 0 and 1000.", "error")
                        return
                except ValueError:
                    self.update_status("Error: Invalid percentage value for image.", "error")
                    return
            elif rescale_mode == "pixels":
                try:
                    width_str = self.width_entry.get()
                    height_str = self.height_entry.get()
                    if width_str:
                        image_scale_width = int(width_str)
                    if height_str:
                        image_scale_height = int(height_str)
                    
                    if (image_scale_width is None and image_scale_height is None) or \
                       (image_scale_width is not None and image_scale_width <= 0) or \
                       (image_scale_height is not None and image_scale_height <= 0):
                        self.update_status("Error: Enter valid positive pixel dimensions (width or height) for image.", "error")
                        return
                except ValueError:
                    self.update_status("Error: Invalid pixel dimension for image (must be an integer).", "error")
                    return
        elif self.current_mode == "video":
            video_quality_preset = self.video_quality_option.get()
            rescale_mode = self.video_rescale_mode_var.get()
            if rescale_mode == "percentage":
                try:
                    video_scale_percentage = float(self.video_percentage_entry.get())
                    if not (0 < video_scale_percentage <= 1000): # Allow up to 10x scaling
                        self.update_status("Error: Percentage must be between 0 and 1000 for video.", "error")
                        return
                except ValueError:
                    self.update_status("Error: Invalid percentage value for video.", "error")
                    return
            elif rescale_mode == "pixels":
                try:
                    width_str = self.video_width_entry.get()
                    height_str = self.video_height_entry.get()
                    if width_str:
                        video_scale_width = int(width_str)
                    if height_str:
                        video_scale_height = int(height_str)
                    
                    if (video_scale_width is None and video_scale_height is None) or \
                       (video_scale_width is not None and video_scale_width <= 0) or \
                       (video_scale_height is not None and video_scale_height <= 0):
                        self.update_status("Error: Enter valid positive pixel dimensions (width or height) for video.", "error")
                        return
                except ValueError:
                    self.update_status("Error: Invalid pixel dimension for video (must be an integer).", "error")
                    return


        if not output_dir:
            self.update_status("Error: Please select an output directory.", "error")
            return

        if link_input:
            # Handle URL download and then conversion
            self.update_status("Downloading media from URL... (This may take a while)", "blue")
            self.convert_button.configure(state="disabled", text="Downloading...")
            threading.Thread(
                target=self._run_url_conversion,
                args=(link_input, output_dir, output_format, image_quality, image_scale_width, image_scale_height, image_scale_percentage,
                      video_quality_preset, video_scale_width, video_scale_height, video_scale_percentage)
            ).start()
        elif input_path:
            # Handle local file conversion
            self.update_status("Conversion started... Please wait.", "blue")
            self.convert_button.configure(state="disabled", text="Converting...")
            threading.Thread(
                target=self._run_local_conversion,
                args=(input_path, output_dir, output_format, image_quality, image_scale_width, image_scale_height, image_scale_percentage,
                      video_quality_preset, video_scale_width, video_scale_height, video_scale_percentage)
            ).start()
        else:
            self.update_status("Error: Please select an input file or paste a URL.", "error")


    def _run_local_conversion(self, input_path, output_dir, output_format,
                               image_quality=None, scale_width=None, scale_height=None, scale_percentage=None,
                               video_quality_preset=None, video_scale_width=None, video_scale_height=None, video_scale_percentage=None):
        """Internal method to run local file conversion and update GUI."""
        success, message = convert_media(
            input_path, output_dir, output_format, self.update_status,
            image_quality=image_quality, scale_width=scale_width, scale_height=scale_height, scale_percentage=scale_percentage,
            video_quality_preset=video_quality_preset, video_scale_width=video_scale_width, video_scale_height=video_scale_height, video_scale_percentage=video_scale_percentage
        )

        if success:
            self.update_status(f"Conversion complete! Output: {message}", "success")
        else:
            self.update_status(f"Conversion failed: {message}", "error")

        self.convert_button.configure(state="normal", text="Convert Media")

    def _run_url_conversion(self, url, output_dir, output_format,
                            image_quality=None, scale_width=None, scale_height=None, scale_percentage=None,
                            video_quality_preset=None, video_scale_width=None, video_scale_height=None, video_scale_percentage=None):
        """Internal method to download from URL, then convert, and clean up."""
        temp_download_dir = None
        try:
            # Create a temporary directory for the downloaded file
            temp_download_dir = tempfile.mkdtemp(prefix="media_converter_download_")
            self.update_status(f"Downloading to temporary folder: {temp_download_dir}", "blue")

            # Download the media
            download_success, downloaded_file_path = download_media_from_url(url, temp_download_dir, self.current_mode, self.update_status)

            if not download_success:
                self.update_status(f"Download failed: {downloaded_file_path}", "error")
                return # Exit if download failed

            self.update_status(f"Download complete. Converting {os.path.basename(downloaded_file_path)}...", "blue")
            # Now convert the downloaded file
            conversion_success, conversion_message = convert_media(
                downloaded_file_path, output_dir, output_format, self.update_status,
                image_quality=image_quality, scale_width=scale_width, scale_height=scale_height, scale_percentage=scale_percentage,
                video_quality_preset=video_quality_preset, video_scale_width=video_scale_width, video_scale_height=video_scale_height, video_scale_percentage=video_scale_percentage
            )

            if conversion_success:
                self.update_status(f"Conversion complete! Output: {conversion_message}", "success")
            else:
                self.update_status(f"Conversion failed: {conversion_message}", "error")

        except Exception as e:
            self.update_status(f"An unexpected error occurred during URL processing: {e}", "error")
        finally:
            # Clean up the temporary directory
            if temp_download_dir and os.path.exists(temp_download_dir):
                try:
                    shutil.rmtree(temp_download_dir)
                    self.update_status("Temporary download files cleaned up.", "blue")
                except Exception as e:
                    self.update_status(f"Error cleaning up temporary files: {e}", "error")
            self.convert_button.configure(state="normal", text="Convert Media")
            self.link_input_entry.delete(0, ctk.END) # Clear link field after attempt
            self.input_path_entry.delete(0, ctk.END) # Clear local path as well


if __name__ == "__main__":
    app = MediaConverterApp()
    app.mainloop()
