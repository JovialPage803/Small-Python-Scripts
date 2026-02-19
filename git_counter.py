import os
import threading
from pathlib import Path
from pynput.keyboard import Key, Listener, KeyCode

#To make this file an executable, open command prompt, navigate to your folder_path
#using cd XXXXX         ex: cd Desktop/Scripts/Counters
#run the below command
#pyinstaller.py --onefile --distpath "dist" git_counter.py
#                                           ^^^^^^^^^^^^^^ file name if you change it


class SimpleCounter:
    def __init__(self):
        #Setup the paths using pathlab
        #change the path below to wherever your desired folder is
        #only the part after the '/' needs to be changed.
        self.folder_path = Path.home()/"Desktop"/"Scripts"/"Counters"
        #change the path below to what you would like the name of the output file to be
        #only the part after the '/' needs to be changed. This file will be created
        #in the folder_path folder from above.
        self.counter_file = self.folder_path/"git_counter.txt"

        #Initial State (reset to 0 when re-running)
        self.counter_val = 0

        #Change the increment, decrement, or reset values to what you
        #key you would like (The right side of the :)
        self.key_labels = {
            "inc" : "Numpad 7",
            "dec" : "Numpad 4",
            "res" : "Numpad 0"
            }

        #Keycode mapping (currently using numpad. If you have no numpad,
        #                   Change these values to what you would like)
        #Number row values
        #1: 49  |  2: 50  |  3: 51  |  4: 52  |  5: 53
        #6: 54  |  7: 55  |  8: 56  |  9: 57  |  0: 48
        
        self.keys = {
            103: self.increment, #numpad 7
            100: self.decrement, #numpad 4
            96:  self.reset_count#numpad 0
        }

    def load_counter(self):
        #Initialize counter to 0 and save the counter
        self.counter_val = 0
        self.save_counter()

    def save_counter(self):
        #make sure directory exists and save the current value
        try:
            self.folder_path.mkdir(parents = True, exist_ok = True)
            self.counter_file.write_text(f"Count = {self.counter_val}")
        except Exception as e:
            print(f" Error saving file: {e}")

    def increment(self):
        self.counter_val += 1
        self.save_counter()

    def decrement(self):
        if self.counter_val > 0:
            self.counter_val -= 1
            self.save_counter()

    def reset_count(self):
        self.counter_val = 0
        self.save_counter()

    def on_press(self, key):
        #map keys to functions
        vk = getattr(key, 'vk', None)

        if vk in self.keys:
            self.keys[vk]()

        #stop listening if ESC pressed [exit program]
        if key == Key.esc:
            return False

    def start_listening(self):
        #start listening on daemon thread
        listener = Listener(on_press = self.on_press)
        listener.daemon = True #kill thread when program exits
        listener.start()
        return listener

    def cleanup(self):
        if self.counter_file.exists():
            self.counter_file.unlink()
            print("Cleaning counter file...")


if __name__ == "__main__":
    counter = SimpleCounter()

    print("              --- Stream Counter Active ---")
    print(f"Saving to: {counter.counter_file}")
    print(f"\nHotkeys: {counter.key_labels['inc']} = +1  |  {counter.key_labels['dec']} = -1  |  {counter.key_labels['res']} = Reset")
    print("--------------------------------------------------------------")
    print("              Press ESC or ENTER to stop...")
    print("--------------------------------------------------------------")

    counter.load_counter()

    #Start daemonized listener
    listener_thread = counter.start_listening()

    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        #If you want the file deleted when closing the application, uncomment the line below
        #counter.cleanup()
        print("\nCounter Stopped!")
