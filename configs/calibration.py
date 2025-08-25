import time
import csv
import datetime
import os
import sys

class Calibration:
    def __init__(self):
        self.input_horizontal_loss = {"J3": 0, "J5": 0, "J7": 0}
        self.output_horizontal_loss = {"J9": 0, "J11": 0, "J13": 0}
        self.input_vertical_loss = {"J4": 0, "J6": 0, "J8": 0}
        self.output_vertical_loss = {"J10": 0, "J12": 0, "J14": 0}
        dt = datetime.datetime.now()
        date_string = dt.strftime("%d_%m_%Y_%H_%M_%S")
        dir_name = os.getcwd()

        self.cal_data_filepath = dir_name + "\\calibration" + "\\" + f"cal_{date_string}" + ".csv"

        self.cal_file = "calibration.csv"

    def insert_losses(self, input_horizontal, output_horizontal, input_vertical, output_vertical):
        self.input_horizontal_loss = input_horizontal
        self.output_horizontal_loss = output_horizontal
        self.input_vertical_loss = input_vertical
        self.output_vertical_loss = output_vertical

    def write2file(self, data):
        with open(self.cal_data_filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            file.close()

    def save_calibration(self):
        self.write2file(["J3", "J5", "J7", "J9", "J11", "J13", "J4", "J6", "J8", "J10", "J12", "J14"])
        self.write2file([self.input_horizontal_loss["J3"], self.input_horizontal_loss["J5"], self.input_horizontal_loss["J7"],
                         self.output_horizontal_loss["J9"], self.output_horizontal_loss["J11"], self.output_horizontal_loss["J13"],
                         self.input_vertical_loss["J4"], self.input_vertical_loss["J6"], self.input_vertical_loss["J8"],
                         self.output_vertical_loss["J10"], self.output_vertical_loss["J12"], self.output_vertical_loss["J14"]])

    def get_input_loss(self, jack):
        jack = jack.lower()
        if jack == 'j3_j4':
            return self.input_horizontal_loss["J3"], self.input_vertical_loss["J4"]
        elif jack == 'j5_j6':
            return self.input_horizontal_loss["J5"], self.input_vertical_loss["J6"]
        elif jack == 'j7_j8':
            return self.input_horizontal_loss["J7"], self.input_vertical_loss["J8"]
        else:
            raise ValueError()
        
    def get_output_loss(self, jack):
        print(jack)
        jack = jack.lower()
        if jack == 'j9_j10':
            return self.output_horizontal_loss["J9"], self.output_vertical_loss["J10"]
        elif jack == 'j11_j12':
            return self.output_horizontal_loss["J11"], self.output_vertical_loss["J12"]
        elif jack == 'j13_j14':
            return self.output_horizontal_loss["J13"], self.output_vertical_loss["J14"]
        else:
            raise ValueError()
        
    def get_output_loss_at_frequency(self, frequency):
        if frequency == 3e+9:
            return self.output_horizontal_loss["J9"], self.output_vertical_loss["J10"]
        elif frequency == 1.25e+10:
            return self.output_horizontal_loss["J11"], self.output_vertical_loss["J12"]
        elif frequency == 2.8e+10:
            return self.output_horizontal_loss["J13"], self.output_vertical_loss["J14"]
        else:
            raise ValueError()

    def get_input_loss_at_frequency(self, frequency):
        if frequency == 3e+9:
            return self.input_horizontal_loss["J3"], self.input_vertical_loss["J4"]
        elif frequency == 1.25e+10:
            return self.input_horizontal_loss["J5"], self.input_vertical_loss["J6"]
        elif frequency == 2.8e+10:
            return self.input_horizontal_loss["J7"], self.input_vertical_loss["J8"]
        else:
            raise ValueError()