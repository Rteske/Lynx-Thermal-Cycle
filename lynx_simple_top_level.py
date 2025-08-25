import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import logging
import datetime
from lynx_pa_top_level_test_manager import PaTopLevelTestManager
from logging_utils import configure_logging, log_message, log_queue
from mocked_test_class import MockedTest

class GUIHandler(logging.Handler):
    def __init__(self, log_widget):
        super().__init__()
        self.log_widget = log_widget

    def emit(self, record):
        log_entry = self.format(record)
        self.log_widget.after(0, self.log_widget.update_log, log_entry)

class LynxPaTopLevelGUI:
    def __init__(self, root, sim_mode=False):
        self.root = root
        self.root.title("Lynx PA Top Level GUI")
        self.root.geometry("900x900")
        self.sim_mode = sim_mode

        # Configure main grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Main container frame
        main_container = ttk.Frame(root)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_columnconfigure(0, weight=1)

        # Main Test Section (more compact)
        main_test_frame = ttk.LabelFrame(main_container, text="Main Test", padding="5")
        main_test_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        main_test_frame.grid_columnconfigure(1, weight=1)

        # Serial number entry (more compact)
        tk.Label(main_test_frame, text="Enter Serial Number:").grid(row=0, column=0, sticky="w", pady=2)
        self.sn_entry = tk.Entry(main_test_frame)
        self.sn_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)

        tk.Label(main_test_frame, text="Enter Dir:").grid(row=1, column=0, sticky="w", pady=2)
        self.dir_entry = tk.Entry(main_test_frame)
        self.dir_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)

        # Dropdown menu
        self.options = [
            "Band1_SN1",
            "Band2_SN1",
            "Band3_SN1",
            "Band1_SN2",
            "Band2_SN2",
            "Band3_SN2",
        ]
        self.dropdown_var = tk.StringVar(value=self.options[0])
        tk.Label(main_test_frame, text="Select an option:").grid(row=2, column=0, sticky="w", pady=2)
        self.dropdown_menu = ttk.Combobox(main_test_frame, textvariable=self.dropdown_var, values=self.options, state="readonly", width=40)
        self.dropdown_menu.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)

        # Checkboxes (side by side)
        self.checkbox1_var = tk.BooleanVar()
        self.checkbox2_var = tk.BooleanVar()
        self.checkbox3_var = tk.BooleanVar()
        tk.Checkbutton(main_test_frame, text="CW & OQPSK SIGNAL ANALYZER", variable=self.checkbox1_var).grid(row=3, column=0, sticky="w", pady=2)
        tk.Checkbutton(main_test_frame, text="VSWR GAIN AND PHASE", variable=self.checkbox2_var).grid(row=3, column=1, sticky="w", pady=2)
        tk.Checkbutton(main_test_frame, text="GOLDEN TEST", variable=self.checkbox3_var).grid(row=3, column=2, sticky="w", pady=2)

        # Status label
        self.status_label = tk.Label(main_test_frame, text="Status: Idle", fg="blue")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=2)

        # Submit button
        self.run_button = tk.Button(main_test_frame, text="Run Tests", command=self.start_test_thread)
        self.run_button.grid(row=5, column=0, columnspan=2, pady=5)

        # Scrollable Logger display (reduced height)
        self.log_text = scrolledtext.ScrolledText(main_test_frame, height=6, width=60, state=tk.DISABLED)
        self.log_text.grid(row=6, column=0, columnspan=2, sticky="ew", pady=2)

        # Separator (reduced spacing)
        ttk.Separator(main_container, orient='horizontal').grid(row=1, column=0, sticky="ew", pady=5)

        # Tech Tools Section (more compact)
        tech_tools_frame = ttk.LabelFrame(main_container, text="Tech Tools", padding="5")
        tech_tools_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        tech_tools_frame.grid_columnconfigure(1, weight=1)

        tk.Label(tech_tools_frame, text="Select Path:").grid(row=0, column=0, sticky="w", pady=2)
        self.filepath_var = tk.StringVar()
        self.filepath_dropdown = ttk.Combobox(tech_tools_frame, textvariable=self.filepath_var, values=self.options, state="readonly")
        self.filepath_dropdown.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        tk.Label(tech_tools_frame, text="Select Attenuation Setting:").grid(row=1, column=0, sticky="w", pady=2)
        self.gain_var = tk.StringVar()
        self.gain_dropdown = ttk.Combobox(tech_tools_frame, textvariable=self.gain_var, values=[i for i in range(0, 32, 1)], state="readonly")
        self.gain_dropdown.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        tk.Label(tech_tools_frame, text="Select Measurement Type:").grid(row=2, column=0, sticky="w", pady=2)
        self.measurement_var = tk.StringVar()
        self.measurement_dropdown = ttk.Combobox(tech_tools_frame, textvariable=self.measurement_var, values=["S22", "S21", "S11"], state="readonly")
        self.measurement_dropdown.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)

        # Tech Tools Buttons
        buttons_frame = ttk.Frame(tech_tools_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        self.run_tool_button = tk.Button(buttons_frame, text="Swap to State", command=self.start_tool_thread)
        self.run_tool_button.grid(row=0, column=0, padx=5)

        # Separator for DAQ Controls (reduced spacing)
        ttk.Separator(tech_tools_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # DAQ Controls Section (more compact)
        daq_controls_frame = ttk.LabelFrame(tech_tools_frame, text="DAQ Controls", padding="5")
        daq_controls_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        daq_controls_frame.grid_columnconfigure(0, weight=1)
        daq_controls_frame.grid_columnconfigure(1, weight=1)

        # Enable/Disable RF (more compact)
        self.rf_enable_button = tk.Button(daq_controls_frame, text="Enable RF", command=self.start_enable_rf_thread)
        self.rf_enable_button.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        self.rf_disable_button = tk.Button(daq_controls_frame, text="Disable RF", command=self.start_disable_rf_thread)
        self.rf_disable_button.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # Band selection
        tk.Label(daq_controls_frame, text="Select Band:").grid(row=1, column=0, sticky="w", pady=2)
        self.band_select_var = tk.StringVar(value="NONE")
        self.band_dropdown = ttk.Combobox(daq_controls_frame, textvariable=self.band_select_var, values=["NONE", "L", "M", "H"], state="readonly")
        self.band_dropdown.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        self.band_button = tk.Button(daq_controls_frame, text="Set Band", command=self.start_band_thread)
        self.band_button.grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky="ew")

        # Attenuator controls
        tk.Label(daq_controls_frame, text="Set Gain (10-41 dB):").grid(row=3, column=0, sticky="w", pady=2)
        self.attenuator_var = tk.StringVar(value="Unknown")
        self.attenuator_dropdown = ttk.Combobox(daq_controls_frame, textvariable=self.attenuator_var, values=[i for i in range(0, 31, 1)], state="readonly")
        self.attenuator_dropdown.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        self.attenuator_button = tk.Button(daq_controls_frame, text="Apply Gain", command=self.start_band_attenuator_thread)
        self.attenuator_button.grid(row=4, column=0, columnspan=2, padx=5, pady=2, sticky="ew")

        # Separator for DAQ Status (reduced spacing)
        ttk.Separator(daq_controls_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)

        # DAQ Status Section (more compact)
        tk.Label(daq_controls_frame, text="DAQ Status:").grid(row=6, column=0, sticky="w", pady=2)
        
        # Add refresh button
        self.refresh_status_button = tk.Button(daq_controls_frame, text="Refresh", command=self.start_refresh_status_thread)
        self.refresh_status_button.grid(row=6, column=1, padx=5, pady=2, sticky="e")

        self.daq_enabled_status_var = tk.StringVar(value="Unknown")
        self.daq_enabled_status = tk.Label(daq_controls_frame, textvariable=self.daq_enabled_status_var, fg="black")
        self.daq_enabled_status.grid(row=7, column=0, columnspan=2, pady=1, sticky="ew")

        self.daq_band_status_var = tk.StringVar(value="Unknown")
        self.daq_band_status = tk.Label(daq_controls_frame, textvariable=self.daq_band_status_var, fg="black")
        self.daq_band_status.grid(row=8, column=0, columnspan=2, pady=1, sticky="ew")

        self.daq_attenuator_status_var = tk.StringVar(value="Unknown")
        self.daq_attenuator_status = tk.Label(daq_controls_frame, textvariable=self.daq_attenuator_status_var, fg="black")
        self.daq_attenuator_status.grid(row=9, column=0, columnspan=2, pady=1, sticky="ew")

        self.daq_temp_status_var = tk.StringVar(value="Unknown")
        self.daq_temp_status = tk.Label(daq_controls_frame, textvariable=self.daq_temp_status_var, fg="black")
        self.daq_temp_status.grid(row=10, column=0, columnspan=2, pady=1, sticky="ew")


        # Separator (reduced spacing)
        ttk.Separator(main_container, orient='horizontal').grid(row=3, column=0, sticky="ew", pady=5)

        # SigA Tools Section
        siga_tools_frame = ttk.LabelFrame(main_container, text="SigA Tools", padding="10")
        siga_tools_frame.grid(row=4, column=0, sticky="ew")
        siga_tools_frame.grid_columnconfigure(1, weight=1)

        # Path
        tk.Label(siga_tools_frame, text="Select Path:").grid(row=0, column=0, sticky="w", pady=5)
        self.siga_path_var = tk.StringVar()
        self.siga_path_dropdown = ttk.Combobox(siga_tools_frame, textvariable=self.siga_path_var, values=self.options, state="readonly")
        self.siga_path_dropdown.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Gain Setting
        tk.Label(siga_tools_frame, text="Select Gain Setting:").grid(row=1, column=0, sticky="w", pady=5)
        self.siga_gain_var = tk.StringVar()
        self.siga_gain_dropdown = ttk.Combobox(siga_tools_frame, textvariable=self.siga_gain_var, values=[i for i in range(0, 32)], state="readonly")
        self.siga_gain_dropdown.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Frequency
        tk.Label(siga_tools_frame, text="Select Frequency (GHz):").grid(row=2, column=0, sticky="w", pady=5)
        self.siga_freq_var = tk.StringVar()
        self.siga_freq_dropdown = ttk.Combobox(siga_tools_frame, textvariable=self.siga_freq_var, values=[1.95, 3, 4, 10, 12.5, 15, 25, 28, 31], state="readonly")
        self.siga_freq_dropdown.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Bandwidth
        tk.Label(siga_tools_frame, text="Select Bandwidth (MHz):").grid(row=3, column=0, sticky="w", pady=5)
        self.siga_bw_var = tk.StringVar()
        self.siga_bw_dropdown = ttk.Combobox(siga_tools_frame, textvariable=self.siga_bw_var, values=[10, 200, "harmonic", "wideband"], state="readonly")
        self.siga_bw_dropdown.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Waveform
        tk.Label(siga_tools_frame, text="Select Waveform:").grid(row=4, column=0, sticky="w", pady=5)
        self.siga_waveform_var = tk.StringVar()
        self.siga_waveform_dropdown = ttk.Combobox(siga_tools_frame, textvariable=self.siga_waveform_var, values=["CW", "OQPSK"], state="readonly")
        self.siga_waveform_dropdown.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Run Button
        self.run_siga_button = tk.Button(siga_tools_frame, text="Run SigA Tool", command=self.start_siga_thread)
        self.run_siga_button.grid(row=5, column=0, columnspan=2, pady=10)

        if sim_mode:
            self.mocked_test = MockedTest(42)
        else:
            self.pa_top_level_test_manager = PaTopLevelTestManager(sim=False)
            # Initialize DAQ status display
            self.start_refresh_status_thread()
        
        # Start log monitoring loop
        self.monitor_log_queue()


    # DAQ control threads and functions as methods of LynxPaTopLevelGUI
    def update_daq_status_display(self):
        """Update all DAQ status variables from the actual DAQ status"""
        try:
            rf_on_off, fault_status, bandpath, gain_value, date_string, temp_value = self.pa_top_level_test_manager.daq.read_status_return()
            
            self.daq_enabled_status_var.set(f"RF Status: {rf_on_off}")
            self.daq_band_status_var.set(f"Band: {bandpath}")
            self.daq_attenuator_status_var.set(f"Gain: {gain_value} dB")
            self.daq_temp_status_var.set(f"Temp: {temp_value:.1f}°C")
            
            # Log any faults
            if fault_status != "No Faults":
                log_message(f"DAQ Fault: {fault_status}")
                
        except Exception as e:
            self.daq_enabled_status_var.set(f"Status Error: {e}")
            self.daq_band_status_var.set("Status Error")
            self.daq_attenuator_status_var.set("Status Error")
            self.daq_temp_status_var.set("Status Error")

    def enable_rf(self):
        try:
            result = self.pa_top_level_test_manager.daq.enable_rf()
            log_message(f"DAQ: RF Enable {result}")
            self.update_daq_status_display()  # Update status after operation
        except Exception as e:
            self.daq_enabled_status_var.set(f"Error: {e}")
            log_message(f"DAQ: Enable RF Error: {e}")

    def start_enable_rf_thread(self):
        threading.Thread(target=self.enable_rf, daemon=True).start()

    def disable_rf(self):
        try:
            self.pa_top_level_test_manager.daq.disable_rf()
            log_message("DAQ: RF Disabled")
            self.update_daq_status_display()  # Update status after operation
        except Exception as e:
            self.daq_enabled_status_var.set(f"Error: {e}")
            log_message(f"DAQ: Disable RF Error: {e}")

    def start_disable_rf_thread(self):
        threading.Thread(target=self.disable_rf, daemon=True).start()

    def set_band(self):
        band = self.band_select_var.get()
        try:
            result = self.pa_top_level_test_manager.daq.set_band(band)
            log_message(f"DAQ: Band set to {band}: {result}")
            self.update_daq_status_display()  # Update status after operation
        except Exception as e:
            self.daq_band_status_var.set(f"Error: {e}")
            log_message(f"DAQ: Set Band Error: {e}")

    def start_band_thread(self):
        threading.Thread(target=self.set_band, daemon=True).start()

    def set_attenuator(self):
        try:
            atten = int(self.attenuator_var.get())
            result = self.pa_top_level_test_manager.daq.change_gain(int(atten))
            log_message(f"DAQ: Gain set to {atten} dB: {result}")
            self.update_daq_status_display()  # Update status after operation
        except Exception as e:
            self.daq_attenuator_status_var.set(f"Error: {e}")
            log_message(f"DAQ: Set Gain Error: {e}")

    def start_band_attenuator_thread(self):
        threading.Thread(target=self.set_attenuator, daemon=True).start()

    def start_refresh_status_thread(self):
        threading.Thread(target=self.update_daq_status_display, daemon=True).start()

    def start_siga_thread(self):
        siga_thread = threading.Thread(target=self.run_siga_tool, daemon=True)
        siga_thread.start()

    def run_siga_tool(self):
        self.run_button.config(state="disabled")  # Disable Main Test button while running
        path = self.siga_path_var.get()
        gain = self.siga_gain_var.get()
        freq = self.siga_freq_var.get()
        bw = self.siga_bw_var.get()
        waveform = self.siga_waveform_var.get()

        # Validate selections
        if not all([path, gain, freq, bw, waveform]):
            self.update_log("Error: Please select all SigA Tool options.")
            self.run_button.config(state="normal")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] Running SigA Tool: Path={path}, Gain={gain}, Freq={freq}MHz, BW={bw}MHz, WF={waveform}"
        log_message(msg)

        try:
            bw = float(bw)
        except:
            bw = str(bw)

        frequency = (float(freq) * 1e+9)

        try:
            self.pa_top_level_test_manager.run_state_process(path, gain_setting=int(gain), measurement_type="Signal Analyzer Bandwidth", options= {"frequency":frequency, "bandwidth": bw, "waveform": waveform})
        except Exception as e:
            self.update_log(f"SigA Tool Error: {e}")
        finally:
            self.run_button.config(state="normal")

    def turn_fetts_off(self):
        self.pa_top_level_test_manager.daq.disable_rf()

    def start_turn_fetts_off_thread(self):
        turn_fetts_off_thread = threading.Thread(target=self.turn_fetts_off, daemon=True)
        turn_fetts_off_thread.start()

    def turn_fetts_on(self):
        self.pa_top_level_test_manager.daq.enable_rf()

    def start_turn_fetts_on_thread(self):
        turn_fetts_off_thread = threading.Thread(target=self.turn_fetts_on, daemon=True)
        turn_fetts_off_thread.start()

    def monitor_log_queue(self):
        """ Continuously checks the log queue and updates the GUI log """
        while not log_queue.empty():
            message = log_queue.get()
            self.update_log(message)
        self.root.after(100, self.monitor_log_queue)  # Run this method every 100ms

    def run_tests(self):
        self.run_tool_button.config(state="disabled")  # Disable Tech Tools buttons

        serial_number = self.sn_entry.get().strip()
        if not serial_number:
            self.update_log("Error: Serial Number is required.")
            self.run_tool_button.config(state="normal")  # Re-enable Tech Tools buttons if an error occurs
            return
        
        user_defined_dir = self.dir_entry.get().strip()
        if not user_defined_dir:
            self.update_log("Error: Directory is required.")
            self.run_tool_button.config(state="normal")

        configure_logging(serial_number)
        self.update_status("Running...", "red")
        selected_option = self.dropdown_var.get()
        bin = selected_option.split(" ")
        selected_option = bin[0]
        checkbox1_state = self.checkbox1_var.get()
        checkbox2_state = self.checkbox2_var.get()
        checkbox3_state = self.checkbox3_var.get()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"[{timestamp}] Running tests... SN: {serial_number}, Selected: {selected_option}, Checkbox 1: {checkbox1_state}, Checkbox 2: {checkbox2_state}"
        log_message(message)
        print(message)
        
        if self.sim_mode:
            self.mocked_test.run_tests()
        else:
            # THis is for the results path creation i wanted to see it first to make sure it was working
            self.pa_top_level_test_manager.scribe.new_sno(serial_number, user_defined_dir)
            self.pa_top_level_test_manager.lynx_config.new_sno(serial_number, user_defined_dir)
            self.pa_top_level_test_manager.run_and_process_tests(selected_option, sno=serial_number, sig_a_tests=checkbox1_state, na_tests=checkbox2_state, golden_tests=checkbox3_state)


        log_message("Tests completed.")
        self.update_status("Idle", "blue")
        self.run_tool_button.config(state="normal")  # Re-enable Tech Tools buttons
        print("Tests completed.")

    def start_tool_thread(self):
        tool_thread = threading.Thread(target=self.run_tools, daemon=True)
        tool_thread.start()

    def run_tools(self):
        # This disables the run button so that when the tool is running you cant run a test at the same time
        self.run_button.config(state="disabled")
        selected_option = self.filepath_var.get()
        bin = selected_option.split(" ")
        selected_option = bin[0]
        gain_setting = int(self.gain_var.get())
        measurement_type = self.measurement_var.get()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] Running tools... Selected: {selected_option}, Gain: {gain_setting}, Measurement: {measurement_type}"
        log_message(message)
        self.pa_top_level_test_manager.run_state_process(selected_option, gain_setting, measurement_type)
        # This reenables it
        self.run_button.config(state="normal")

    def start_test_thread(self):
        self.test_thread = threading.Thread(target=self.run_tests, daemon=True)
        self.test_thread.start()

    def update_status(self, text, color):
        self.status_label.config(text=f"Status: {text}", fg=color)
    
    def update_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, str(message) + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)

if __name__ == "__main__":
    import sys
    root = tk.Tk()
    app = LynxPaTopLevelGUI(root)
    root.mainloop()
