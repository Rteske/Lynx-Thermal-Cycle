unit SetupDi;

interface

uses
  Windows;

const
  DIGCF_DEFAULT         = $00000001;  // only valid with DIGCF_DEVICEINTERFACE
  DIGCF_PRESENT         = $00000002;
  DIGCF_ALLCLASSES      = $00000004;
  DIGCF_PROFILE         = $00000008;
  DIGCF_DEVICEINTERFACE = $00000010;

  USB_DEVICE_DESCRIPTOR_TYPE = 1;

type
  SP_DEVICE_INTERFACE_DATA = record
      cbSize: DWORD;
      InterfaceClassGuid: TGUID;
      Flags: DWORD;
      Reserved: Pointer;
  end;
  PSP_DEVICE_INTERFACE_DATA = ^SP_DEVICE_INTERFACE_DATA;

  SP_DEVINFO_DATA = record
    cbSize: LongWord;
    ClassGUID: TGUID;
    DevInst: LongWord;
    Reserved: Pointer;
  end;
  PSP_DEVINFO_DATA = ^SP_DEVINFO_DATA;

  SP_DEVICE_INTERFACE_DETAIL_DATA = record
    cbSize: LongWord;
    DevicePath: array[0..0] of Char;
  end;
  PSP_DEVICE_INTERFACE_DETAIL_DATA = ^SP_DEVICE_INTERFACE_DETAIL_DATA;

  USB_DEV_DSC = packed record
    bLength     : byte; bDscType  : byte;  bcdUSB      : word;
    bDevCls     : byte; bDevSubCls: byte;  bDevProtocol: byte;
    bMaxPktSize0: byte; idVendor  : word;  idProduct   : word;
    bcdDevice   : word; iMFR      : byte;  iProduct    : byte;
    iSerialNum  : byte; bNumCfg   : byte;
  end;

function SetupDiEnumDeviceInterfaces(DeviceInfoSet: THandle; DeviceInfoData: PSP_DEVINFO_DATA; const InterfaceClassGuid: TGUID; MemberIndex: LongWord; var DeviceInterfaceData: SP_DEVICE_INTERFACE_DATA): BOOL; stdcall; external 'SetupAPI.dll';
function SetupDiDestroyDeviceInfoList(DeviceInfoSet: THandle): BOOL; stdcall; external 'SetupAPI.dll';
function SetupDiGetClassDevs(ClassGuid: PGUID; Enumerator: PChar; hwndParent: THandle; Flags: LongWord): THandle; stdcall; external 'SetupAPI.dll' name 'SetupDiGetClassDevsA';
function SetupDiGetDeviceInterfaceDetail(DeviceInfoSet: THandle; DeviceInterfaceData: PSP_DEVICE_INTERFACE_DATA; DeviceInterfaceDetailData: PSP_DEVICE_INTERFACE_DETAIL_DATA; DeviceInterfaceDetailDataSize: LongWord; pRequiredSize: PLongWord; DeviceInfoData: PSP_DEVINFO_DATA): BOOL; stdcall; external 'SetupAPI.dll' name 'SetupDiGetDeviceInterfaceDetailA';

implementation

end.