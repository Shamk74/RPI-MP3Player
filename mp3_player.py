import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame
import time
import os
import logging
import random

# Set up logging configuration for debugging and troubleshooting.
logging.basicConfig(
    level=logging.DEBUG,  # Log all messages of level DEBUG and higher.
    format="%(asctime)s - %(levelname)s - %(message)s",  # Include time, log level, and message.
    handlers=[
        logging.FileHandler("mp3_player.log"),  # Save logs to a file.
        logging.StreamHandler()  # Also output logs to the console.
    ]
)

# Optionally import mutagen for accurate MP3 duration.
try:
    from mutagen.mp3 import MP3
    use_mutagen = True
except ImportError:
    use_mutagen = False
    logging.warning("Mutagen library not found. Fallback for track length will be used.")


class MP3Player:
    """
    A simple MP3 player built with tkinter for the GUI and pygame for audio playback.

    Features:
      - Load a single MP3 file or a folder containing MP3 files.
      - Build a playlist (shuffled) from the selected folder.
      - Display playback progress and elapsed/total time.
      - Click the progress bar to seek within the track.
      - Click on the volume slider trough to set the volume directly.
      - Playback controls: Play, Pause/Resume, Stop, Rewind (5s), Fast Forward (5s), and Next.
    """

    def __init__(self, root):
        """
        Initialize the MP3Player instance.

        Parameters:
            root (tk.Tk): The root tkinter window.
        """
        self.root = root
        self.root.title("MP3 Player")
        self.root.geometry("800x300")  # Set a widened window size.
        self.root.resizable(False, False)  # Prevent window resizing.

        # Playback state variables.
        self.current_file = None         # Path to the current MP3 file.
        self.playing = False             # True if a track is playing.
        self.paused = False              # True if playback is paused.
        self.track_length = 0            # Duration (in seconds) of the current track.
        self.offset = 0                  # Elapsed time (in seconds) before a pause/seek.
        self.play_start_time = None      # Timestamp when current playback started/resumed.

        # Playlist variables (used when a folder is loaded).
        self.playlist = []               # List of MP3 file paths.
        self.current_index = -1          # Index of the current song in the playlist.

        # Initialize the pygame mixer for audio playback.
        pygame.mixer.init()

        # Create the GUI widgets.
        self.create_widgets()

    def create_widgets(self):
        """
        Create and arrange the GUI elements.
        """
        # Frame for file/folder loading and playback control buttons.
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Button to load a single MP3 file.
        self.load_button = tk.Button(button_frame, text="Load File", width=10, command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=5)

        # Button to load a folder containing MP3 files.
        self.load_folder_button = tk.Button(button_frame, text="Load Folder", width=12, command=self.load_folder)
        self.load_folder_button.grid(row=0, column=1, padx=5)

        # Play button.
        self.play_button = tk.Button(button_frame, text="Play", width=10, command=self.play_music, state=tk.DISABLED)
        self.play_button.grid(row=0, column=2, padx=5)

        # Pause/Resume toggle button.
        self.pause_button = tk.Button(button_frame, text="Pause", width=10, command=self.toggle_pause, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=3, padx=5)

        # Stop button.
        self.stop_button = tk.Button(button_frame, text="Stop", width=10, command=self.stop_music, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=4, padx=5)

        # Volume control: label and slider.
        self.volume_label = tk.Label(self.root, text="Volume (0% - 100%)", font=("Helvetica", 10))
        self.volume_label.pack(pady=5)
        self.volume_scale = tk.Scale(self.root, from_=0, to=100, orient="horizontal",
                                     resolution=1, command=self.set_volume)
        self.volume_scale.set(100)  # Default volume is 100%.
        self.volume_scale.pack(fill='x', padx=20, pady=10)
        # Bind click on the volume slider trough to jump volume to that spot.
        self.volume_scale.bind("<Button-1>", self.jump_volume)

        # Status bar: displays file name and play time.
        self.status_label = tk.Label(self.root, text="Status: Stopped", font=("Helvetica", 12),
                                     relief="sunken", bd=2)
        self.status_label.pack(fill='x', padx=20, pady=5)

        # Progress bar: shows playback progress.
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', padx=20, pady=10)
        # Bind click on the progress bar to allow seeking.
        self.progress_bar.bind("<Button-1>", self.jump_to_position)

        # Navigation controls frame for rewind, fast forward, and next.
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10)
        self.rewind_button = tk.Button(nav_frame, text="Rewind (5s)", width=12,
                                       command=self.rewind_music, state=tk.DISABLED)
        self.rewind_button.grid(row=0, column=0, padx=5)
        self.fast_forward_button = tk.Button(nav_frame, text="Fast Forward (5s)", width=15,
                                             command=self.fast_forward_music, state=tk.DISABLED)
        self.fast_forward_button.grid(row=0, column=1, padx=5)
        # Next button for folder playlists.
        self.next_button = tk.Button(nav_frame, text="Next", width=10,
                                     command=self.play_next_song, state=tk.DISABLED)
        self.next_button.grid(row=0, column=2, padx=5)

    def jump_volume(self, event):
        """
        When the user clicks on the volume slider trough, jump the volume to that spot.

        Parameters:
            event: The tkinter event object containing click coordinates.
        """
        widget_width = event.widget.winfo_width()  # Get slider width.
        new_volume = int((event.x / widget_width) * 100)  # Calculate volume percentage.
        self.volume_scale.set(new_volume)  # Update slider display.
        self.set_volume(new_volume)        # Update the actual volume.

    def load_file(self):
        """
        Open a file dialog to select a single MP3 file.
        Clears any existing folder playlist and loads the chosen file.
        """
        file_path = filedialog.askopenfilename(
            title="Select MP3 File",
            filetypes=[("MP3 Files", "*.mp3")]
        )
        if file_path:
            # Clear any existing folder playlist.
            self.playlist = []
            self.current_index = -1

            self.current_file = file_path
            if file_path.lower().endswith(".mp3"):
                try:
                    # Load the selected MP3 file.
                    pygame.mixer.music.load(self.current_file)
                    self.status_label.config(text=f"Status: Loaded {os.path.basename(self.current_file)}")
                    self.play_button.config(state=tk.NORMAL)
                    self.next_button.config(state=tk.DISABLED)  # No next song in single file mode.
                    logging.info(f"Loaded file: {self.current_file}")

                    # Determine track length using mutagen if available.
                    if use_mutagen:
                        audio = MP3(self.current_file)
                        self.track_length = audio.info.length
                    else:
                        try:
                            sound = pygame.mixer.Sound(self.current_file)
                            self.track_length = sound.get_length()
                        except Exception as e:
                            self.track_length = 0
                            logging.warning("Could not determine track length using fallback.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load the file:\n{e}")
                    logging.error(f"Error loading file: {e}")
                    self.current_file = None
            else:
                messagebox.showwarning("Unsupported File", "Only MP3 files are supported.")
                logging.warning(f"Unsupported file type selected: {file_path}")

    def load_folder(self):
        """
        Open a folder dialog to select a folder containing MP3 files.
        The folder is scanned for files ending in .mp3, a new (shuffled) playlist is created,
        and the first file is loaded and played.
        """
        folder_path = filedialog.askdirectory(title="Select Folder Containing MP3 Files")
        if folder_path:
            # Always stop any current playback.
            if self.playing:
                self.stop_music()

            # Build a new playlist.
            mp3_files = []
            for file in os.listdir(folder_path):
                if file.lower().endswith(".mp3"):
                    full_path = os.path.join(folder_path, file)
                    mp3_files.append(full_path)
                    logging.debug(f"Found file: {full_path}")

            if not mp3_files:
                messagebox.showwarning("No MP3 Files", "No MP3 files found in the selected folder.")
                return

            # Shuffle the list and set as the new playlist.
            self.playlist = mp3_files
            random.shuffle(self.playlist)
            self.current_index = 0
            self.current_file = self.playlist[self.current_index]
            logging.debug(f"New playlist: {self.playlist}")

            try:
                pygame.mixer.music.load(self.current_file)
                self.status_label.config(text=f"Status: Loaded {os.path.basename(self.current_file)}")
                self.play_button.config(state=tk.NORMAL)
                self.next_button.config(state=tk.NORMAL)  # Enable Next in folder mode.
                logging.info(f"Loaded folder: {folder_path} with {len(self.playlist)} files. Starting with: {self.current_file}")

                # Determine track length.
                if use_mutagen:
                    audio = MP3(self.current_file)
                    self.track_length = audio.info.length
                else:
                    try:
                        sound = pygame.mixer.Sound(self.current_file)
                        self.track_length = sound.get_length()
                    except Exception as e:
                        self.track_length = 0
                        logging.warning("Could not determine track length using fallback.")
                # Automatically start playback of the first song.
                self.play_music()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load the file:\n{e}")
                logging.error(f"Error loading file: {e}")
                self.current_file = None

    def play_music(self):
        """
        Start playback of the currently loaded MP3 file.
        Resets timing variables and updates control button states.
        """
        if self.current_file:
            try:
                pygame.mixer.music.play()
                self.offset = 0  # Reset any previous offset.
                self.play_start_time = time.time()  # Record the start time.
                self.playing = True
                self.paused = False
                # Update control buttons.
                self.play_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.NORMAL, text="Pause")
                self.stop_button.config(state=tk.NORMAL)
                self.rewind_button.config(state=tk.NORMAL)
                self.fast_forward_button.config(state=tk.NORMAL)
                if self.playlist:
                    self.next_button.config(state=tk.NORMAL)
                logging.info(f"Started playing: {self.current_file}")
                self.update_progress()  # Begin updating progress.
            except Exception as e:
                messagebox.showerror("Error", f"Failed to play the file:\n{e}")
                logging.error(f"Error playing file: {e}")
        else:
            messagebox.showwarning("No File Selected", "Please load an MP3 file or folder first.")

    def toggle_pause(self):
        """
        Toggle between pausing and resuming playback.
        Updates the pause button text accordingly.
        """
        if self.playing:
            if not self.paused:
                pygame.mixer.music.pause()
                if self.play_start_time is not None:
                    self.offset += time.time() - self.play_start_time
                self.play_start_time = None
                self.paused = True
                self.pause_button.config(text="Resume")
                logging.info(f"Paused playback of: {self.current_file}")
            else:
                pygame.mixer.music.unpause()
                self.play_start_time = time.time()
                self.paused = False
                self.pause_button.config(text="Pause")
                logging.info(f"Resumed playback of: {self.current_file}")

    def stop_music(self):
        """
        Stop playback and reset the player state and control buttons.
        """
        if self.playing:
            pygame.mixer.music.stop()
            self.status_label.config(text="Status: Stopped")
            self.playing = False
            self.paused = False
            self.offset = 0
            self.play_start_time = None
            # Reset control buttons.
            self.play_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED, text="Pause")
            self.stop_button.config(state=tk.DISABLED)
            self.rewind_button.config(state=tk.DISABLED)
            self.fast_forward_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.progress_var.set(0)
            logging.info(f"Stopped playback of: {self.current_file}")

    def set_volume(self, value):
        """
        Set the playback volume.

        Parameters:
            value (str or int): Volume percentage (0 to 100).
        """
        volume_percentage = int(value)
        volume = volume_percentage / 100.0  # Convert to a float between 0.0 and 1.0.
        pygame.mixer.music.set_volume(volume)
        logging.info(f"Set volume to: {volume_percentage}%")

    def format_time(self, seconds):
        """
        Format a time value in seconds to MM:SS.

        Parameters:
            seconds (float): Time in seconds.

        Returns:
            str: Formatted time "MM:SS".
        """
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def update_progress(self):
        """
        Update the progress bar and status label with current playback time.
        If the track finishes (and playback is not paused), auto-play the next track (in folder mode).
        """
        if self.playing and self.track_length > 0:
            if self.paused:
                current_time = self.offset
            else:
                current_time = self.offset + (time.time() - self.play_start_time)
            if current_time > self.track_length:
                current_time = self.track_length
            progress = (current_time / self.track_length) * 100
            self.progress_var.set(min(progress, 100))
            time_str = f"{self.format_time(current_time)} / {self.format_time(self.track_length)}"
            base_status = "Paused" if self.paused else "Playing"
            self.status_label.config(text=f"Status: {base_status} {os.path.basename(self.current_file)} [{time_str}]")
            
            # If playback has finished (and is not paused), auto-play the next track (if in folder mode).
            if not pygame.mixer.music.get_busy() and not self.paused:
                if self.playlist:
                    self.play_next_song()
                    return
                else:
                    self.stop_music()
                    self.progress_var.set(100)
                    return
            self.root.after(500, self.update_progress)

    def seek(self, delta):
        """
        Seek forward or backward in the current track by delta seconds.

        Parameters:
            delta (float): Seconds to seek (positive for forward, negative for rewind).
        """
        if self.playing and self.track_length > 0:
            if self.paused:
                current_time = self.offset
            else:
                current_time = self.offset + (time.time() - self.play_start_time)
            new_time = current_time + delta
            if new_time < 0:
                new_time = 0
            elif new_time > self.track_length:
                new_time = self.track_length - 1  # Slightly before the end.
            was_paused = self.paused
            pygame.mixer.music.play(start=new_time)
            self.offset = new_time
            if not was_paused:
                self.play_start_time = time.time()
                logging.info(f"Seeked to {new_time:.2f} seconds in {self.current_file}")
            else:
                pygame.mixer.music.pause()
                self.play_start_time = None
                logging.info(f"Seeked (paused) to {new_time:.2f} seconds in {self.current_file}")

    def jump_to_position(self, event):
        """
        Jump to a new playback position based on a click in the progress bar.

        Parameters:
            event: The tkinter event object containing click coordinates.
        """
        if self.playing and self.track_length > 0:
            widget_width = event.widget.winfo_width()
            fraction = event.x / widget_width
            new_time = fraction * self.track_length
            if self.paused:
                current_time = self.offset
            else:
                current_time = self.offset + (time.time() - self.play_start_time)
            delta = new_time - current_time
            self.seek(delta)

    def rewind_music(self):
        """
        Rewind the current track by 5 seconds.
        """
        self.seek(-5)

    def fast_forward_music(self):
        """
        Fast forward the current track by 5 seconds.
        """
        self.seek(5)

    def play_next_song(self):
        """
        Advance to the next song in the playlist and start playback.
        Loops back to the beginning if at the end.
        """
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.current_file = self.playlist[self.current_index]
            try:
                pygame.mixer.music.load(self.current_file)
                if use_mutagen:
                    audio = MP3(self.current_file)
                    self.track_length = audio.info.length
                else:
                    try:
                        sound = pygame.mixer.Sound(self.current_file)
                        self.track_length = sound.get_length()
                    except Exception as e:
                        self.track_length = 0
                        logging.warning("Could not determine track length using fallback.")
                pygame.mixer.music.play()
                self.offset = 0
                self.play_start_time = time.time()
                self.status_label.config(text=f"Status: Playing {os.path.basename(self.current_file)}")
                self.playing = True
                self.paused = False
                self.play_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.NORMAL, text="Pause")
                self.stop_button.config(state=tk.NORMAL)
                self.rewind_button.config(state=tk.NORMAL)
                self.fast_forward_button.config(state=tk.NORMAL)
                self.next_button.config(state=tk.NORMAL)
                logging.info(f"Playing next song: {self.current_file}")
                self.update_progress()
            except Exception as e:
                logging.error(f"Error playing next song: {e}")


def main():
    """
    Main function to create the tkinter root window and run the MP3Player application.
    """
    root = tk.Tk()
    app = MP3Player(root)
    root.mainloop()


if __name__ == "__main__":
    main()
