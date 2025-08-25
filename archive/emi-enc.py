from temp_probe import Agilent34401A
import csv
import time
import datetime
import os
import sys
import shutil
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

dt = datetime.datetime.now()
session_date_string = dt.strftime("%d_%m_%Y_%H_%M_%S")
dir_name = os.getcwd()
filepath = dir_name + "\\data\\emi_raw_data\\" + session_date_string + "_emi.csv"

ll_ylim_rfpm1 = input("INPUT DBM SCALE LOWER LIMIT> ")
ul_ylim_rfpl1 = input("INPUT DBM SCALE UPPER LIMIT> ")

from daq import RS422_DAQ

try:
    daq = RS422_DAQ()
except:
    print("Failed to connect to daq")

from power_meter import E4418BPowerMeter

rfpm1_cal_factor_table = {
    3e+9: 99.3,
    1.25e+10: 97.25,
    2.8e+10: 94.83
}

try:
    rfpm1 = E4418BPowerMeter("GPIB0::15::INSTR", name="rfpm1")
    rfpm1.freqs_to_factors = rfpm1_cal_factor_table
except:
    print("Failed to connect to rfpm1")

def make_a_copy(filepath):
    dt = datetime.datetime.now()
    date_string = dt.strftime("%d_%m_%Y_%H_%M_%S")
    path = dir_name + "\\data\\emi_accessible_data\\" + date_string + "_emi.csv"

    shutil.copy(filepath, path)

start_time = time.time()

global dates, rfpm1_readings, dut_temps
dates, rfpm1_readings, dut_temps = [], [], []

fig, ax1 = plt.subplots()

def refresh_plot():
    ax1.clear()
    ax2 = ax1.twinx()
    
    # Plotting RFPM1 and RFPM2 readings
    ax1.plot(dates, rfpm1_readings, 'g-', label='RFPM1')
    ax1.set_xlabel('Datetime')
    ax1.set_ylabel('Power Meter Readings (dBm)', color='g')
    ax1.tick_params(axis='y', labelcolor='k')
    ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    ax1.set_ylim(float(ll_ylim_rfpm1), float(ul_ylim_rfpl1))
    
    # Plotting DUT temperature
    ax2.plot(dates, dut_temps, 'b-', label="TEMP")
    ax2.set_ylabel('DUT Temperature (°C)', color='b')
    ax2.tick_params(axis='y', labelcolor='b')
    ax2.set_ylim(10, 80)
    
    fig.tight_layout()
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.draw()

try:
    while True:
        rf_on_off, fault_status, bandpath, gain_value, date_string, dut_temp_value = daq.read_status_return()
        rfpm1_power = rfpm1.get_power_measurement()
        dt = datetime.datetime.now()
        print(f"RF On/Off: {rf_on_off}")
        print(f"Fault Status: {fault_status}")
        print(f"Bandpath: {bandpath}")
        print(f"Gain Value: {gain_value}")
        print(f"Date String: {date_string}")
        print(f"DUT Temp Value: {dut_temp_value}")
        print(f"RFPM1: {rfpm1_power}")

        frame = [dt, rf_on_off, fault_status, bandpath, gain_value, date_string, dut_temp_value, rfpm1_power]

        dates.append(dt)
        rfpm1_readings.append(rfpm1_power)
        dut_temps.append(dut_temp_value)

        if len(dates) % 10 == 0:  # Update plot every 10 data points
            refresh_plot()
            plt.pause(0.1)

        with open(filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(frame)
    
        if time.time() - start_time > 5 * 60:
            make_a_copy(filepath)
            start_time = time.time()

        os.system('cls')

except KeyboardInterrupt:
    print("END OF TEST")
    sys.exit()
