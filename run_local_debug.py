# from src.ui.live_view import run_gui
from instruments.power_supply import PowerSupply
from instruments.temp_controller import TempController
from instruments.ztm import ZtmModular
from instruments.signal_generator import E4438CSignalGenerator

# if __name__ == "__main__":
#     run_gui()


power_supply = PowerSupply(visa_address="GPIB0::10::INSTR")

switch = ZtmModular()
switch.init_resource("02402230028")

temp_controller = TempController()

siggen = E4438CSignalGenerator("GPIB0::30::INSTR")

siggen.stop()


switch.reset_all_switches()

power_supply.set_voltage(28)
power_supply.set_current(2.5)
power_supply.set_output_state(True)


voltage = power_supply.get_voltage()
current = power_supply.get_current()

print(f"Voltage: {voltage} V")
print(f"Current: {current} A")

from instruments.daq import RS422_DAQ
daq = RS422_DAQ()
daq.disable_rf()
daq.set_band("NONE")
stuff = daq.read_status_return()
print(f"DAQ Status: {stuff}")

temp_controller.set_setpoint(1, 25)
temp_controller.set_chamber_state(True)
chamber_state = temp_controller.query_chamber_state()
temp = temp_controller.query_actual(1)

print(f"Chamber State: {chamber_state}")
print(f"Temperature: {temp} °C")