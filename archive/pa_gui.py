import tkinter as tk
from instruments.arduino import ArduinoDAQ

class PaGui:
    def __init__(self, window):
        if isinstance(window, tk.Tk):
            self.window = window
        else:
            raise ValueError()
        
        self.daq = ArduinoDAQ("Arduino")
        
        self.enable_state = True
        self.band_state = 0
        
        self.window.title("Lynx Calibration")
        self.window.geometry('500x500')

        self.frame = tk.Frame(self.window, relief=tk.RAISED)
        self.frame.pack(side=tk.LEFT)

        label_rf_on_off = tk.Label(self.frame, text="RF ON OFF")
        label_rf_on_off.pack()
        self.rf_on_off = tk.Button(self.frame, text=self.enable_state_to_text(), command=self.rf_on_off_signal)
        self.rf_on_off.pack()

        label_set_band = tk.Label(self.frame, text="SET BAND")
        label_set_band.pack()
        self.enable_band_1 = tk.Button(self.frame, text="Enable Band 1", command=lambda: self.enable_band(1))
        self.enable_band_1.pack()
        self.enable_band_2 = tk.Button(self.frame, text="Enable Band 2", command=lambda: self.enable_band(2))
        self.enable_band_2.pack()
        self.enable_band_3 = tk.Button(self.frame, text="Enable Band 3", command=lambda: self.enable_band(3))
        self.enable_band_3.pack()

        label_set_gain = tk.Label(self.frame, text="SET GAIN")
        label_set_gain.pack()
        self.set_gain_spinbox = tk.Spinbox(self.frame, from_=0, to=45)
        self.set_gain_spinbox.pack()
        self.set_gain_button = tk.Button(self.frame, text="SUBMIT")
        self.set_gain_button.pack()

        self.status = tk.Button(self.frame, text="Report Status", command=self.return_status)
        self.status.pack()

        frame2 = tk.Frame(self.window, relief=tk.FLAT)
        frame2.pack(side=tk.RIGHT)
        label_status_return = tk.Label(frame2, text="Return Status")
        label_status_return.pack()

        faults_label = tk.Label(frame2, text="Faults")
        faults_label.pack()
        self.faults_show = tk.Label(frame2, text="NA")
        self.faults_show.pack()

        band_label = tk.Label(frame2, text="Band")
        band_label.pack()
        self.band_show = tk.Label(frame2, text="NA")
        self.band_show.pack()

        gain_value_label = tk.Label(frame2, text="Gain")
        gain_value_label.pack()
        self.gain_value_show = tk.Label(frame2, text="NA")
        self.gain_value_show.pack()

        temp_label = tk.Label(frame2, text="Temp")
        temp_label.pack()
        self.temp_show = tk.Label(frame2, text="NA")
        self.temp_show.pack()

    def enable_state_to_text(self):
        if self.enable_state == True:
            return "Enabled"
        else:
            return "Disabled"

    def rf_on_off_signal(self):
        if self.enable_state:
            self.enable_state = False
        else:
            self.enable_state = True

        self.rf_on_off.configure(text=self.enable_state_to_text())

    def enable_band(self, band):
        self.daq.send_cmd()

    def return_status(self):
        print("External method to return faults, gain value, band, temp")
        self.band_show.configure(text=self.cum)
        self.faults_show.configure(text="FUCk YOU")
        self.gain_value_show.configure(text="gay sex time")
        self.temp_show.configure(text="OBama did nothin wrong")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    window = tk.Tk()
    gui = PaGui(window)
    gui.run()