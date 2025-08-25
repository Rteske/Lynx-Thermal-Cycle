# Control Mini-Circuits' ZTM & RCM series modular switch systems via USB
# Requirements:
#   1: Python.Net (pip install pythonnet)
#   2: Mini-Circuits' DLL API file (ModularZT_NET45.dll)
#      https://www.minicircuits.com/softwaredownload/ModularZT64_DLL.zip
#      Note: - Windows may block the DLL file after download as a precaution
#            - Right-click on the file, select properties, click "Unblock" (if shown)

import clr # pythonnet
clr.AddReference('ModularZT64')      # Reference the DLL

from ModularZT_NET45 import USB_ZT
sw = USB_ZT()               # Create an instance of the control class

Status = sw.Connect()       # Connect the system (pass the serial number as an argument if required)

if Status > 0:              # The connection was successful

    Responses = sw.Send_SCPI(":SN?", "")        # Read serial number
    print (str(Responses[2]))   # Python interprets the response as a tuple [function return (0 or 1), command parameter, response parameter]

    Responses = sw.Send_SCPI(":MN?", "")        # Read model name
    print (str(Responses[2]))

    # SP4T switches
    Status = sw.Send_SCPI(":SP4T:1:STATE:4", "")    # Set switch 1 state (COM<>4)
    Responses = sw.Send_SCPI(":SP4T:1:STATE?", "")   # Read switch state
    print (str(Responses[2]))

    sw.Disconnect()             # Disconnect at the end of the program

else:
    print ("Could not connect.")
