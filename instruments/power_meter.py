from pyvisa import ResourceManager
import time

class E4418BPowerMeter:
	"""Class for interfacing with Agilent E4418B"""
	def __init__(self, adrress, name):
		rm = ResourceManager()
		self._name = name
		self._cable_loss = 0
		self._res = rm.open_resource(adrress)
		self._res.timeout = 25000
		self._res.write("*CLS")
		self._res.write("*WAI")
		self._res.write("*RST")
		time.sleep(3)
		# self._res.read_termination = '\n'
		# self._res.write_termination = '\n'
		# self._res.write(":CONF1:POW:AC  DEF,3,(@1)")             
		# self._res.write(":TRIG1:SOUR IMM")                       
		# self._res.write(":TRIG1:DEL:AUTO ON")                    
		# self._res.write(":SENS1:AVER:STAT ON")           
		# self._res.write(":SENS1:AVER:COUN:1024") 
		# self._res.write("SENSe:SPEed 40")
		self.freqs_to_factors = {}
		print("Power meter has been validated")

	def set_frequency(self, frequency):
		"""Set the frequency of the power meter"""
		self._res.write(f"SENSe1:FREQuency {frequency}Hz")
		# self._res.write(f"SENSe1:CORRection:CFAC {self.freqs_to_factors[frequency]}")
		print(f'Setting frequency = {frequency}')

	def get_power_measurement(self):
		print('Obtaining power measurement')
		self._res.write(':INIT1:CONT ON')
		time.sleep(1)
		measurement_taken = False
		while measurement_taken == False:
			try:
				reading = self._res.query(":FETCH1:POW:AC? DEF,3,(@1)")
				measurement_taken = True
			except:
				time.sleep(3)
				print("measurement not taken")
			
			reading = float(reading)
			reading = round(reading, 2)

		return reading
			
class GigatronixPowerMeter: 
	def __init__(self, address):
			rm = ResourceManager()
			self._res = rm.open_resource(address)
			self._res.timeout = 25000
			self._res.write("*CLS")
			self._res.write("*WAI")
			self._res.write("*RST")
			time.sleep(3)

	def set_frequency(self):
		self._res.write()

	def get_power_measurement(self):
		self._res.write()