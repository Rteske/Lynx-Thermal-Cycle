from instruments.signal_analyzer import MXASignalAnalyzer
from matplotlib import pyplot

import matplotlib.pyplot as plt

def plot_array(freqs, trace, title="Array Plot", xlabel="Index", ylabel="Value"):
    plt.figure(figsize=(10, 5))
    plt.plot(freqs, trace)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.show()



mxa = MXASignalAnalyzer("TCPIP0::K-N90X0A-000005.local::hislip0::INSTR")

bandwidth = 10000000.0
center = 1950000000.0
start, stop = 1e+9, 8e+9

freqs, trace = mxa.get_channel_power_data(center=center, span=bandwidth, points=401, avg=100)

plot_array(freqs, trace)

freqs, trace = mxa.get_sa_bandwidth_trace(start=start, stop=stop)

plot_array(freqs, trace)

