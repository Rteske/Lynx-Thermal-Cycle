
from configs.calibration import Calibration
import temp_cycle_manager as temp_cycle_manager 
import time
import os

cal = Calibration()

temp_profile = [
    {"temperature": 71, "time_per_band": 10, "voltage": 28, "dwell_time": 60, "temp_controller_offset": 10},
    {"temperature": -34, "time_per_band": 10, "voltage": 28, "dwell_time": 60, "temp_controller_offset": -5},
    {"temperature": 71, "time_per_band": 10, "voltage": 34, "dwell_time": 60, "temp_controller_offset": 10},
    {"temperature": -34, "time_per_band": 10, "voltage": 34, "dwell_time": 60, "temp_controller_offset": -5}
]

rfpm1_cal_factor_table = {
    3e+9: 99.03,
    1.25e+10: 97.25,
    2.8e+10: 94.13
}

rfpm2_cal_factor_table = {
    3e+9: 99.3,
    1.25e+10: 97.4,
    2.8e+10: 94.8
}

rfpm3_cal_factor_table = {
    3e+9: 99.03,
    1.25e+10: 97.9,
    2.8e+10: 97
}

test_runner = temp_cycle_manager.TempCycle(cal, temp_profile=temp_profile, sim=False)

test_runner.temp_profile = temp_profile

print("INITIALIZING TEST")

time.sleep(1)

os.system('cls')
print("\n")
print("STARTING TEST")
print("\n")
time.sleep(1)
os.system('cls') 

res = input("Enter sno: ")

test_runner.test.set_sno(res)

test_runner.run_tests()

