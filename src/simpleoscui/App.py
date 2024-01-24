import pycromanager
import customtkinter
import os
from PIL import Image
import tkinter as tk
from customtkinter import CTk,CTkButton
import datetime
import time

def init_pycromanager(timeout=20_000) -> (pycromanager.Core, pycromanager.Studio):
    """Initialize pycromanager and return the core and studio objects."""
    core = pycromanager.Core()
    studio = pycromanager.Studio()
    core.set_timeout_ms(timeout)
    return core,studio

def add_timestamp(func):
    def wrapper(*args, **kwargs):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ", end="")
        return func(*args, **kwargs)
    return wrapper

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("600x400")

        # Create a button
        self.button1 = customtkinter.CTkButton(self, 
                                               width=250,
                                               text_color='black',
                                               text="Initialize pycromanager", 
                                               command=self.on_button1_click,
                                               anchor=customtkinter.CENTER)
        self.button1.pack(pady=10,padx=10,anchor='nw')

        # Create a label
        self.label = customtkinter.CTkLabel(self, text="DCC", font=("Arial", 16))
        self.label.pack(pady=10,padx=10,anchor='nw')

        # Create a RESET button
        self.button2 = customtkinter.CTkButton(self, 
                                               width=250,
                                               text_color='black',
                                               text="RESET", 
                                               command=self.dcc_reset,
                                               anchor=customtkinter.CENTER)
        
        self.button2.pack(pady=10,padx=10,anchor='nw')
        ## delayed loop
        self.after_id = None
        #self.after(0, self.dcc_status_request_loop)
        
        
        
    def __del__(self):
        if self.after_id is not None:
            self.after_cancel(self.after_id)
        if self.core:
            self.core.__del__()
        

    def on_button1_click(self):
        self.core,self.studio = init_pycromanager()
        self.dcc_status_request_loop()

    def dcc_status_request_loop(self):        
        response = self.core.get_property("DCCModule1","C3_Overloaded")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = f"{timestamp} - DCC Overloaded: {response}"

        cfd =self.core.get_property("OSc-LSM","BH-TCSPC-RateCounter-CFD")
        cfd = float(cfd)
        if cfd<200:
            self.dcc_reset()
            print("CFD is low, resetting DCC")
        print(f"{response} : {cfd}")
        self.label.configure(text=response)
        self.after_id =self.after(1000, self.dcc_status_request_loop)
    

    def dcc_reset(self):
        if self.core:
            self.core.set_property("DCCModule1","ClearOverloads","")
            #mmc.setProperty("DCCModule1","ClearOverloads","");
            self.core.set_property("DCCModule1","EnableOutputs","Off")
            time.sleep(0.25)  # Wait for 2 seconds

            self.core.set_property("DCCModule1","EnableOutputs","On")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response = f"{timestamp} - DCC Reset"
            print(f"{response}")
            self.label.configure(text=response)



if __name__ == "__main__":
    app = App()
    app.mainloop()


