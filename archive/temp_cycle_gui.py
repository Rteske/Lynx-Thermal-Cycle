import temp_cycle_manager as temp_cycle_manager 
import tkinter as tk
from tkinter import Toplevel, messagebox
from configs.calibration import Calibration
import threading
from tkinter import ttk
import time
from queue import Queue

class TempCycleGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Temp Cycle GUI")
        self.window.geometry("800x600")
        self.window.configure(bg="lightblue")
        self.cal_loaded = True
        self._cal = Calibration()

        self.temp_profile = [
            {"temperature": 71, "time_per_band": 10, "voltage": 28, "dwell_time": 60, "temp_controller_offset": 10},
            {"temperature": -34, "time_per_band": 10, "voltage": 28, "dwell_time": 60, "temp_controller_offset": -5},
            {"temperature": 71, "time_per_band": 10, "voltage": 34, "dwell_time": 60, "temp_controller_offset": 10},
            {"temperature": -34, "time_per_band": 10, "voltage": 34, "dwell_time": 60, "temp_controller_offset": -5}
        ]

        self.test_runner = temp_cycle_manager.TempCycle(self._cal, sim=False)

        self.serial_number_frame = tk.Frame(self.window)
        self.serial_number_frame.pack(pady=10)

        self.serial_number_label = tk.Label(self.serial_number_frame, text="Serial Number:")
        self.serial_number_label.pack(side=tk.LEFT, padx=10)

        self.serial_number_entry = tk.Entry(self.serial_number_frame)
        self.serial_number_entry.pack(side=tk.LEFT, padx=10)

        self.confirm_button = tk.Button(self.serial_number_frame, text="Confirm", bg="blue", fg="white", command=self.confirm_serial_number)
        self.confirm_button.pack(side=tk.RIGHT, pady=20)

        # self.cal_button_frame = tk.Frame(self.window)
        # self.cal_button_frame.pack(pady=20)

        # self.take_cal_data_button = tk.Button(self.cal_button_frame, text="Take New Calibration Data", bg="blue", fg="white", command=self.take_new_cal_data)
        # self.take_cal_data_button.pack(side=tk.LEFT, padx=10)
        self.text_editor_button = tk.Button(self.window, text="Open Temp Profile Editor", bg="blue", fg="white", command=self.open_temp_profile_editor)
        self.text_editor_button.pack(pady=10)

        self.connection_status_frame = tk.Frame(self.window)
        self.connection_status_frame.pack(pady=20)

        if self.test_runner.instruments_connection["rfpm1"] == False:
            self.rfpm1 = tk.Label(self.connection_status_frame, text="RFPM1", bg="red", fg="white")
        else:
            self.rfpm1 = tk.Label(self.connection_status_frame, text="RFPM1", bg="green", fg="white")

        self.rfpm1.pack(side=tk.LEFT, padx=10)

        if self.test_runner.instruments_connection["rfpm2"] == False:
            self.rfpm2 = tk.Label(self.connection_status_frame, text="RFPM2", bg="red", fg="white")
        else:
            self.rfpm2 = tk.Label(self.connection_status_frame, text="RFPM2", bg="green", fg="white")

        self.rfpm2.pack(side=tk.LEFT, padx=10)

        if self.test_runner.instruments_connection["rfpm3"] == False:
            self.rfpm3 = tk.Label(self.connection_status_frame, text="RFPM3", bg="red", fg="white")
        else:
            self.rfpm3 = tk.Label(self.connection_status_frame, text="RFPM3", bg="green", fg="white")

        self.rfpm3.pack(side=tk.LEFT, padx=10)

        if self.test_runner.instruments_connection["rfsg"] == False:
            self.rfsg = tk.Label(self.connection_status_frame, text="RFSG", bg="red", fg="white")
        else:
            self.rfsg = tk.Label(self.connection_status_frame, text="RFSG", bg="green", fg="white")

        self.rfsg.pack(side=tk.LEFT, padx=10)

        if self.test_runner.instruments_connection["temp_probe"] == False:
            self.temp_probe = tk.Label(self.connection_status_frame, text="Temp Probe", bg="red", fg="white")
        else:
            self.temp_probe = tk.Label(self.connection_status_frame, text="Temp Probe", bg="green", fg="white")
        
        self.temp_probe.pack(side=tk.LEFT, padx=10)

        if self.test_runner.instruments_connection["daq"] == False:
            self.daq = tk.Label(self.connection_status_frame, text="DAQ", bg="red", fg="white")
        else:
            self.daq = tk.Label(self.connection_status_frame, text="DAQ", bg="green", fg="white")
        
        self.daq.pack(side=tk.LEFT, padx=10)

        if self.test_runner.instruments_connection["temp_controller"] == False:
            self.temp_controller = tk.Label(self.connection_status_frame, text="Temp Controller", bg="red", fg="white")
        else:
            self.temp_controller = tk.Label(self.connection_status_frame, text="Temp Controller", bg="green", fg="white")

        self.temp_controller.pack(side=tk.LEFT, padx=10)

        button = tk.Button(self.window, text="Run Tests", bg="blue", fg="white", command=self.run_tests)
        button.pack(pady=20)

        self.current_values_frame = tk.Frame(self.window)
        self.current_values_frame.pack(side=tk.LEFT,pady=30, padx=30)

        self.rfpm1_value = tk.StringVar()
        self.rfpm1_label = tk.Label(self.current_values_frame, textvariable=self.rfpm1_value).grid(row=0, column=0, pady=10)

        self.rfpm2_value = tk.StringVar()
        self.rfpm2_label = tk.Label(self.current_values_frame, textvariable=self.rfpm2_value).grid(row=0, column=1, pady=10)

        self.rfpm3_value = tk.StringVar()
        self.rfpm3_label = tk.Label(self.current_values_frame, textvariable=self.rfpm3_value).grid(row=0, column=2, pady=10)

        self.psu_value = tk.StringVar()
        self.psu_label = tk.Label(self.current_values_frame, textvariable=self.psu_value).grid(row=2, column=0, pady=10)

        self.temp_probe_value = tk.StringVar()
        self.temp_probe_label = tk.Label(self.current_values_frame, textvariable=self.temp_probe_value).grid(row=4, column=0, pady=10)

        self.temp_plate_value = tk.StringVar()
        self.temp_plate_label = tk.Label(self.current_values_frame, textvariable=self.temp_plate_value).grid(row=4, column=1, pady=10)

        self.dut_status_label = tk.Label(self.current_values_frame, text="DUT Status").grid(row=5, column=0, pady=10)

        self.dut_enabled = tk.StringVar()
        self.dut_enabled_label = tk.Label(self.current_values_frame, textvariable=self.dut_enabled).grid(row=5, column=1, pady=10)

        self.dut_fault = tk.StringVar()
        self.dut_fault_label = tk.Label(self.current_values_frame, textvariable=self.dut_fault).grid(row=5, column=2, pady=10)

        self.dut_bandpath = tk.StringVar()
        self.dut_bandpath_label = tk.Label(self.current_values_frame, textvariable=self.dut_bandpath).grid(row=5, column=3, pady=10)

        self.dut_gain = tk.StringVar()
        self.dut_gain_label = tk.Label(self.current_values_frame, textvariable=self.dut_gain).grid(row=5, column=4, pady=10)

        self.dut_temp = tk.StringVar()
        self.dut_temp_label = tk.Label(self.current_values_frame, textvariable=self.dut_temp).grid(row=5, column=5, pady=10)

        self.rfpm1_value.set("RFPM1" + "n/a" + " dB")
        self.rfpm2_value.set("RFPM2" + "n/a" + " dB")
        self.psu_value.set(f"V n/a A n/a")
        self.rfpm3_value.set("RFPM3" + "n/a" + " dB")
        self.dut_enabled.set("n/a")
        self.dut_fault.set("FAULTS: " + "n/a")
        self.dut_bandpath.set("BANDPATH: " + "n/a")
        self.dut_gain.set("GAIN SETTING" + "n/a")
        self.dut_temp.set("DUT TEMP" + "n/a" + "C")
        self.temp_probe_value.set("TEMP PROBE" + "n/a")
        self.temp_plate_value.set("TEMP PLATE" + "n/a")

    def open_temp_profile_editor(self):
        self.text_editor_window = tk.Toplevel(self.window)
        self.text_editor_window.title("Text Editor")
        self.text_editor_window.geometry("600x600")

        self.text_editor = tk.Text(self.text_editor_window, height=30, width=50)
        self.text_editor.insert(tk.END, f"{self.temp_profile}")
        self.text_editor.pack(pady=10)

        self.save_button = tk.Button(self.text_editor_window, text="Save", bg="blue", fg="white", command=self.save_temp_profile_editor)
        self.save_button.pack(pady=10)

    def save_temp_profile_editor(self):
        text = self.text_editor.get("1.0", tk.END)
        self.temp_profile = eval(text)
        self.test_runner.set_temp_profile(self.temp_profile)

        self.text_editor_window.destroy()

    def save_temp_profile(self):
        print("Saving Temp Profile")
        
    def confirm_serial_number(self):
        serial_number = self.serial_number_entry.get()
        self.confirm_button.destroy()
        self.serial_number_entry.config(state='disabled')
        self.test_runner.sno = serial_number
        messagebox.showinfo("Confirmation", f"Serial Number: {serial_number} confirmed!")

    def confirm_cal_data(self):
        self.cal_gui.destroy()
        self.cal_loaded = True
        self.cal_button_frame.destroy()
        messagebox.showinfo("Confirmation", "Calibration Data Loaded!")

    def run_tests(self):    
        if self.cal_loaded:
            self.run_tests_in_thread()

    def run_tests_in_thread(self):
        talking_bucket = Queue()
        self.test_runner.run_tests(talking_bucket)

        
        # while thread.is_alive():
        #     while not talking_bucket.empty():
        #         self.update_test_state(talking_bucket)

    def update_test_state(self, talking_bucket):
        # frame = [rfpm1_dBm, rfpm2_dBm, psu_voltage, psu_current, rfpm3_dBm, rf_on_off, fault_status, bandpath, date_string, gain_value, dut_temp_value, probe_temp_value, temp_plate_value]
        
        array = talking_bucket.get()
        self.rfpm1_value.set("RFPM1: " + array[1] + " dB")
        self.rfpm2_value.set("RFPM2: " + array[2] + " dB")
        self.psu_value.set(f"V {array[3]} A {array[4]}")
        self.rfpm3_value.set("RFPM3: " + array[5] + " dB")
        self.dut_enabled.set(array[6])
        self.dut_fault.set("FAULTS: " + array[7])
        self.dut_bandpath.set("BANDPATH: " + array[9])
        self.dut_gain.set("GAIN SETTING: " + array[10])
        self.dut_temp.set("DUT TEMP: " + array[11] + "C")
        self.temp_probe_value.set("TEMP PROBE: " + array[12])
        self.temp_plate_value.set("TEMP PLATE: " + array[13])

    def take_new_cal_data(self):
        self.cal_gui = Toplevel(self.window)
        self.cal_gui.title("Calibration Data")
        self.cal_gui.geometry("400x400")

        self.j3_input_loss_label = tk.Label(self.cal_gui, text="J3 Input Loss").grid(row=0, column=0)
        self.j3_input_loss_value = tk.StringVar()
        self.j3_entry = tk.Entry(self.cal_gui, textvariable=self.j3_input_loss_value).grid(row=0, column=1)

        self.j4_input_loss_label = tk.Label(self.cal_gui, text="J4 Input Loss").grid(row=1, column=0)
        self.j4_input_loss_value = tk.StringVar()
        self.j4_entry = tk.Entry(self.cal_gui, textvariable=self.j4_input_loss_value).grid(row=1, column=1)

        self.j5_input_loss_label = tk.Label(self.cal_gui, text="J5 Input Loss").grid(row=2, column=0)
        self.j5_input_loss_value = tk.StringVar()
        self.j5_entry = tk.Entry(self.cal_gui, textvariable=self.j5_input_loss_value).grid(row=2, column=1)

        self.j6_input_loss_label = tk.Label(self.cal_gui, text="J6 Input Loss").grid(row=3, column=0)
        self.j6_input_loss_value = tk.StringVar()
        self.j6_entry = tk.Entry(self.cal_gui, textvariable=self.j6_input_loss_value).grid(row=3, column=1)

        self.j7_input_loss_label = tk.Label(self.cal_gui, text="J7 Input Loss").grid(row=4, column=0)
        self.j7_input_loss_value = tk.StringVar()
        self.j7_entry = tk.Entry(self.cal_gui, textvariable=self.j7_input_loss_value).grid(row=4, column=1)

        self.j8_input_loss_label = tk.Label(self.cal_gui, text="J8 Input Loss").grid(row=5, column=0)
        self.j8_input_loss_value = tk.StringVar()
        self.j8_entry = tk.Entry(self.cal_gui, textvariable=self.j8_input_loss_value).grid(row=5, column=1)

        self.j9_output_loss_label = tk.Label(self.cal_gui, text="J9 Output Loss").grid(row=6, column=0)
        self.j9_output_loss_value = tk.StringVar()
        self.j9_entry = tk.Entry(self.cal_gui, textvariable=self.j9_output_loss_value).grid(row=6, column=1)

        self.j10_output_loss_label = tk.Label(self.cal_gui, text="J10 Output Loss").grid(row=7, column=0)
        self.j10_output_loss_value = tk.StringVar()
        self.j10_entry = tk.Entry(self.cal_gui, textvariable=self.j10_output_loss_value).grid(row=7, column=1)


        self.j11_output_loss_label = tk.Label(self.cal_gui, text="J11 Output Loss").grid(row=8, column=0)
        self.j11_output_loss_value = tk.StringVar()
        self.j11_entry = tk.Entry(self.cal_gui, textvariable=self.j11_output_loss_value).grid(row=8, column=1)


        self.j12_output_loss_label = tk.Label(self.cal_gui, text="J12 Output Loss").grid(row=9, column=0)
        self.j12_output_loss_value = tk.StringVar()
        self.j12_entry = tk.Entry(self.cal_gui, textvariable=self.j12_output_loss_value).grid(row=9, column=1)

        self.j13_output_loss_label = tk.Label(self.cal_gui, text="J13 Output Loss").grid(row=10, column=0)
        self.j13_output_loss_value = tk.StringVar()
        self.j13_entry = tk.Entry(self.cal_gui, textvariable=self.j13_output_loss_value).grid(row=10, column=1)


        self.j14_output_loss_label = tk.Label(self.cal_gui, text="J14 Output Loss").grid(row=11, column=0)
        self.j14_output_loss_value = tk.StringVar()
        self.j14_entry = tk.Entry(self.cal_gui, textvariable=self.j14_output_loss_value).grid(row=11, column=1)

        self.confirm_button = tk.Button(self.cal_gui, text="Confirm", bg="blue", fg="white", command=self.confirm_cal_data).grid(row=12, column=0)

if __name__ == "__main__":
    app = TempCycleGUI()
    app.window.mainloop()