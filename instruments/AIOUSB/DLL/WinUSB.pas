unit WinUSB;

interface

uses
  Windows;

type
  USB_INTERFACE_DESCRIPTOR = packed record
    bLength,
    bDescriptorType,
    bInterfaceNumber,
    bAlternateSetting,
    bNumEndpoints,
    bInterfaceClass,
    bInterfaceSubClass,
    bInterfaceProtocol,
    iInterface: Byte;
  end;
  PUSB_INTERFACE_DESCRIPTOR = ^USB_INTERFACE_DESCRIPTOR;

  //USBD_PIPE_TYPE = (UsbdPipeTypeControl, UsbdPipeTypeIsochronous, UsbdPipeTypeBulk, UsbdPipeTypeInterrupt);

  WINUSB_PIPE_INFORMATION = packed record
    PipeType: LongWord;
    PipeId: Byte;
    MaximumPacketSize: Word;
    Interval: Byte;
  end;
  PWINUSB_PIPE_INFORMATION = ^WINUSB_PIPE_INFORMATION;

  TWinUSBSetupPacket = packed record
    RequestType,
    Request: Byte;
    Value,
    Index,
    DataLength: Word;
  end;

  TWinUsb_Initialize             = function (DeviceHandle: THandle; var InterfaceHandle: THandle): BOOL; stdcall;
  TWinUsb_Free                   = function (InterfaceHandle: THandle): BOOL; stdcall;
  TWinUsb_ControlTransfer        = function (InterfaceHandle: THandle; SetupPacket: TWinUSBSetupPacket; Buffer: PByte; BufferLength: LongWord; var LengthTransferred: LongWord; Overlapped: POverlapped): BOOL; stdcall;
  TWinUsb_GetDescriptor          = function (InterfaceHandle: THandle; DescriptorType: Byte; Index: Byte; LanguageID: Word; Buffer: Pointer; BufferLength: LongWord; var LengthTransferred: LongWord): BOOL; stdcall;
  TWinUsb_QueryInterfaceSettings = function (InterfaceHandle: THandle; AlternateSettingNumber: Byte; UsbAltInterfaceDescriptor: PUSB_INTERFACE_DESCRIPTOR): BOOL; stdcall;
  TWinUsb_QueryPipe              = function (InterfaceHandle: THandle; AlternateInterfaceNumber, PipeIndex: Byte; PipeInformation: PWINUSB_PIPE_INFORMATION): BOOL; stdcall;
  TWinUsb_TransferPipe           = function (InterfaceHandle: THandle; PipeID: Byte; Buffer: PByte; BufferLength: LongWord; var LengthTransferred: LongWord; pOverlapped: Pointer): BOOL; stdcall;

var
  bWinUSBLoaded: Boolean;

  WinUsb_Initialize            : TWinUsb_Initialize            ;
  WinUsb_Free                  : TWinUsb_Free                  ;
  WinUsb_ControlTransfer       : TWinUsb_ControlTransfer       ;
  WinUsb_GetDescriptor         : TWinUsb_GetDescriptor         ;
  WinUsb_QueryInterfaceSettings: TWinUsb_QueryInterfaceSettings;
  WinUsb_QueryPipe             : TWinUsb_QueryPipe             ;
  WinUsb_WritePipe             : TWinUsb_TransferPipe          ;
  WinUsb_ReadPipe              : TWinUsb_TransferPipe          ;



implementation

procedure LoadWinUSB;
var
  hWinUSB: THandle;

begin
  bWinUSBLoaded := False;
  hWinUSB := LoadLibrary('WinUSB.dll');
  if (hWinUSB = 0) or (hWinUSB = INVALID_HANDLE_VALUE) then Exit;

  WinUsb_Initialize             := GetProcAddress(hWinUSB, 'WinUsb_Initialize'            );
  WinUsb_Free                   := GetProcAddress(hWinUSB, 'WinUsb_Free'                  );
  WinUsb_ControlTransfer        := GetProcAddress(hWinUSB, 'WinUsb_ControlTransfer'       );
  WinUsb_GetDescriptor          := GetProcAddress(hWinUSB, 'WinUsb_GetDescriptor'         );
  WinUsb_QueryInterfaceSettings := GetProcAddress(hWinUSB, 'WinUsb_QueryInterfaceSettings');
  WinUsb_QueryPipe              := GetProcAddress(hWinUSB, 'WinUsb_QueryPipe'             );
  WinUsb_WritePipe              := GetProcAddress(hWinUSB, 'WinUsb_WritePipe'             );
  WinUsb_ReadPipe               := GetProcAddress(hWinUSB, 'WinUsb_ReadPipe'              );

  bWinUSBLoaded := True;
end;

initialization
  LoadWinUSB;
end.
