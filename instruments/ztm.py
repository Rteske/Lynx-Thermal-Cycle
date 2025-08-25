class ZtmModular:
    def __init__(self):
        self.sn = None 
        self.resource = None

    def init_resource(self, sno):
        import time
        import clr # pythonnet
        clr.AddReference('C:\\Users\\lcl-caballerom\\lynx\\instruments\\ModularZT64_DLL\\ModularZT_NET45.dll')    # Reference the DLL
        from ModularZT_NET45 import USB_ZT
        self.resource = USB_ZT()
        # self.resource.Connect()
        shit = ""
        # res = self.resource.Get_Available_SN_List(shit)
        if sno == "02402230028":
            self.resource.Connect(sno)
            
            self.switches = [
                SP4T(switch_number=1),SP6T(switch_number=2),SP6T(switch_number=3),SP4T(switch_number=4),SP4T(switch_number=5),SP4T(switch_number=6)
            ]
        elif sno == "01905230039":
            self.resource.Connect(sno)
            self.switches = [
                SP4T(switch_number=1),SP4T(switch_number=2),SP4T(switch_number=3),SP4T(switch_number=4),SP4T(switch_number=5)            ]

    def get_sn(self):
        return self.resource.Send_SCPI(":SN?", "")[2]
    
    def set_switch_state(self, switch_number, state):
        switch = self.get_switch(switch_number)

        if isinstance(switch, SP4T):
            self.resource.Send_SCPI(f":SP4T:{switch_number}:STATE:{state}", "")
            check = self.resource.Send_SCPI(f":SP4T:{switch_number}:STATE?", "")
            if int(check[2]) == state:
                switch.set_state(state)
            else:
                raise ValueError("Switch state not set")
        elif isinstance(switch, SP6T):
            self.resource.Send_SCPI(f":SP6T:{switch_number}:STATE:{state}", "")
            check = self.resource.Send_SCPI(f":SP6T:{switch_number}:STATE?", "")
            if int(check[2]) == state:
                switch.set_state(state)
            else:
                raise ValueError("Switch state not set")
            print("SHE")
        else:
            raise ValueError("Tried to set switch state but not correct Class")
        
        print(switch_number, state)
        
    def set_all_switches(self, states):
        for switch, state in enumerate(states):
            self.set_switch_state(switch + 1, state)
        
    def reset_all_switches(self):
        for i in range(1, len(self.switches) + 1):
            print(i)
            self.set_switch_state(i, 0)
            time.sleep(.5)

    def get_switch(self, num):
        for switch in self.switches:
            if switch.switch_number == num:
                print(switch)
                return switch
            
        
    def __repr__(self) -> str:
        print(f"ZtmModular({self.sn})")
        print(f"Switches: {self.switches}")        

class SP4T:
    def __init__(self, switch_number):
        self.state = 0
        self.switch_number = switch_number

    def set_state(self, state):
        if state not in [0, 1, 2, 3, 4]:
            raise ValueError("Invalid state")
        else:
            self.state = state
            
class SP6T:
    def __init__(self, switch_number):
        self.state = 0
        self.switch_number = switch_number

    def set_state(self, state):
        if state not in [0, 1, 2, 3, 4, 5, 6]:
            raise ValueError("Invalid state")
        else:
            self.state = state

import time

if __name__ == '__main__':
    ztm = ZtmModular()
    sno =  "02402230028"
    ztm.init_resource(sno)
    print(ztm.get_sn())
    ztm.reset_all_switches()

    sno2 =  "01905230039"
    ztm2 = ZtmModular()
    ztm2.init_resource(sno2)
    ztm2.reset_all_switches()

    ztm.set_all_switches([1,2,0,0,0,2])
    ztm2.set_all_switches([0,0,0,2,2])

    ztm.resource.Disconnect()
    ztm2.resource.Disconnect()