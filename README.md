# RPI-MP3Player
“MP3 player project for Raspberry Pi using Python, Tkinter, and Pygame.”
Installation and Usage Guide for MP3 Player on Raspberry Pi
________________________________________
Step 1: Update Raspberry Pi OS
Before installing the MP3 player, ensure your Raspberry Pi OS is up to date.
1.	Open a terminal on your Raspberry Pi.
2.	Run the following commands: 
sudo apt update && sudo apt upgrade -y
________________________________________
Step 2: Install Required Dependencies
The MP3 player requires several Python libraries, including Tkinter for the GUI and Pygame for audio playback.
1.	Install Python and required packages: 
sudo apt install python3 python3-pip python3-tk -y
2.	Install additional Python libraries: 
pip3 install pygame mutagen
________________________________________
Step 3: Download the MP3 Player Code
1.	Navigate to your preferred directory: 
cd ~
2.	Clone the repository (or download the script manually if it's not in a GitHub repo): 
git clone https://github.com/Shamk74/RPI-MP3Player.git
________________________________________
Step 4: Run the MP3 Player
1.	Ensure you are inside the directory where mp3_player.py is located. 
ls
Ensure you see mp3_player.py in the list of files.
2.	Run the MP3 player: 
python3 mp3_player.py
________________________________________
Step 5: Using the MP3 Player
Once the MP3 player GUI opens, follow these steps:
1.	Click "Load File" to open a single MP3 file.
2.	Click "Load Folder" to load multiple MP3 files from a directory.
•	You only need to select the folder the MP3 files are in it will shuffle between all MP3 files in the folder
3.	Use "Play" to start playback.
4.	Pause, Stop, Rewind, and Fast Forward functions are available.
•	Rewind and Fast Forward functions are in 5 sec intervals.
5.	Adjust volume using the Volume Slider.
6.	Click on the progress bar to jump to a specific part of the song.
________________________________________
Step 6: Enabling Auto-Run on Startup (Optional)
To have the MP3 player launch on boot:
1.	Open the autostart configuration file: 
nano ~/.config/lxsession/LXDE-pi/autostart
2.	Add the following line at the end: 
@python3 /home/pi/ITP258/Project2/src/mp3_player.py
3.	Save and exit (CTRL + X, then Y, then ENTER).
4.	Reboot your Raspberry Pi: 
sudo reboot
________________________________________
Troubleshooting
•	If you get an error regarding missing modules, try reinstalling dependencies: 
pip3 install --upgrade pygame mutagen
•	If the audio doesn't play, ensure your Raspberry Pi's audio output is correctly set: 
raspi-config
Navigate to System Options -> Audio and select the correct output (HDMI or 3.5mm jack).
•	If the GUI does not appear, ensure you are running Raspberry Pi OS with a desktop environment.
________________________________________
Conclusion
You have successfully installed and run the MP3 player on your Raspberry Pi. Enjoy your music!
