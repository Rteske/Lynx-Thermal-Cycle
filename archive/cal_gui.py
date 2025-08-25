import tkinter as tk

window = tk.Tk()

def get_input_loss(port):
    print("shit")
    print(port)

def get_output_loss():
    print("CUm")

buttons_frame = tk.Frame(window)
buttons_frame.pack(side=tk.LEFT)

horizontal_buttons_label = tk.Label(buttons_frame, text="Horizontal Input Losses")
horizontal_buttons_label.pack()
j3_input_loss = tk.Button(buttons_frame, text="J3 3 GHz", command=lambda: get_input_loss('j3'))
j3_input_loss.pack()
j5_input_loss = tk.Button(buttons_frame, text= "J5 12.5 GHz", command=lambda: get_input_loss('j5'))
j5_input_loss.pack()
j7_input_loss = tk.Button(buttons_frame, text= "J7 28 GHz", command=lambda: get_input_loss('j7'))
j7_input_loss.pack()

vertical_buttons_label = tk.Label(buttons_frame, text="Vertical Input Losses")
vertical_buttons_label.pack()
j4_input_loss = tk.Button(buttons_frame, text="J4 3 GHz", command=lambda: get_input_loss('j4'))
j4_input_loss.pack()
j6_input_loss = tk.Button(buttons_frame, text="J6 12.5 GHz", command=lambda: get_input_loss('j6'))
j6_input_loss.pack()
j8_input_loss = tk.Button(buttons_frame, text="J8 30 GHz", command=lambda: get_input_loss('j8'))
j8_input_loss.pack()

output_loss = tk.Button(window, text="Output Loss", command=get_output_loss)
output_loss.pack(side=tk.RIGHT)

window.title("Lynx Calibration")
window.geometry('520x500')
window.mainloop()