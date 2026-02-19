import re
import threading
from pathlib import Path
from pynput.keyboard import Key, Listener

#To make this file an executable, open command prompt, navigate to your folder_path
#using cd XXXXX         ex: cd Desktop/Scripts/Counters
#run the below command
#pyinstaller.py --onefile --distpath "dist" git_game_tracker.py
#                                           ^^^^^^^^^^^^^^^^^^^ file name if you change it

class GameTracker:
    def __init__(self):
        #Setup paths using pathlib
        #change the path below to wherever your desired folder is
        #only the part after the '/' needs to be changed.
        #This will be located on the C: Drive by default.
        self.folder_path = Path.home()/"Desktop"/"Scripts"/"Counters"
        #change the path below to what you would like the name of the output file to be
        #only the part after the '/' needs to be changed. This file will be created
        #in the folder_path folder from above.
        self.counter_file = self.folder_path/"winLossTracker.txt"

        #Initial stats (Will be reloaded when program is re-launched)
        #Use the reset_stats key to set everything back to 0
        self.win_val = 0
        self.loss_val = 0
        self.avg_val = 0


        #Change the increment, decrement, or reset values to what you
        #key you would like (The right side of the : and inside the "")
        self.key_labels = {
            "Win+" : "Numpad 9",
            "Win-" : "Numpad 8",
            "Loss+" : "Numpad 6",
            "Loss-" : "Numpad 5",
            "Reset" : "Numpad 0"
            }

        #Keycode mapping (currently using numpad. If you have no numpad,
        #                   Change these values to what you would prefer)
        #Number row values
        #1: 49  |  2: 50  |  3: 51  |  4: 52  |  5: 53
        #6: 54  |  7: 55  |  8: 56  |  9: 57  |  0: 48
        
        #Numpad values start at 96 (0) and end at 105 (9)
        #Edit the left value (the numbers) to your preferred key to CHANGE THE HOTKEYS
        #list of all VK codes can be found online for further customization. 
        self.keys = {
            105: self.inc_w,      #numpad 9
            104: self.dec_w,      #numpad 8
            102: self.inc_l,      #numpad 6
            101: self.dec_l,      #numpad 5
            96:  self.reset_stats #numpad 0
        }



    def load_counter(self):
        #Read existing file to resume progress using Regex
        if self.counter_file.exists():
            try:
                content = self.counter_file.read_text()
                w_match = re.search(r"W = (\d+)", content)
                l_match = re.search(r"L = (\d+)", content)

                if w_match: self.win_val = int(w_match.group(1))
                if l_match: self.loss_val = int(l_match.group(1))

                self.avg_count() #calculate the average of the loaded stats
            except Exception as e:
                print(f"Could not load previous stats: {e}")


    def save_counter(self):
        #Save Wins, Losses, and Avg % to the file
        try:
            self.folder_path.mkdir(parents = True, exist_ok = True)
            output = (
                f"W = {self.win_val}\n"
                f"L = {self.loss_val}\n"
                f"A = {self.avg_val:.1f}%"
            )
            self.counter_file.write_text(output)
        except Exception as e:
            print(f"Error saving file: {e}")



    #Increment, Decrement, and Reset functions
    def inc_w(self):
        self.win_val += 1
        self.avg_count()

    def dec_w(self):
        if self.win_val > 0:
            self.win_val -= 1
        self.avg_count()

    def inc_l(self):
        self.loss_val += 1
        self.avg_count()

    def dec_l(self):
        if self.loss_val > 0:
            self.loss_val -= 1
        self.avg_count()

    def reset_stats(self):
        self.win_val = 0
        self.loss_val = 0
        self.avg_val = 0.0
        self.save_counter()

    def avg_count(self):
        #calculate the win % and save to file
        total_games = self.win_val + self.loss_val
        if total_games == 0:
            self.avg_val = 0.0
        else:
            self.avg_val = (self.win_val / total_games) * 100
        self.save_counter()


        
    def on_press(self, key):
        vk = getattr(key, 'vk', None)
        if vk in self.keys:
            self.keys[vk]()


    def start_listening(self):
        #start listening to keyboard in a daemon thread
        listener = Listener(on_press = self.on_press)
        listener.daemon = True
        listener.start()
        return Listener



if __name__ == "__main__":
    tracker = GameTracker()
    tracker.load_counter()  #resume progress from file
    print("          ---Game Tracker Counter Active---")
    print(f"Saving to: {tracker.counter_file}\n")
    print(f"Hotkeys: {tracker.key_labels['Win+']} = W+   |   {tracker.key_labels['Win-']} = W-")
    print(f"         {tracker.key_labels['Loss+']} = L+   |   {tracker.key_labels['Loss-']} = L-")
    print(f"         {tracker.key_labels['Reset']} = Reset Stats\n")
    print("------------------------------------------------")
    print("             Press ENTER to stop...")
    print("------------------------------------------------")

    listener_thread = tracker.start_listening()

    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n             Tracker Stopped!")

