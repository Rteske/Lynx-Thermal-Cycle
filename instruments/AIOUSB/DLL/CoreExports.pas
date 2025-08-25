unit CoreExports;

interface

uses
  Windows;

type
  TDACEntry = packed record
    Channel: Word;
    Value: Word;
  end;
  PDACEntry = ^TDACEntry;

procedure LoadDriverLinks;

//Global.
function GetDevices: LongWord; cdecl;
function QueryDeviceInfo(DeviceIndex: LongWord; pPID: PLongWord; pNameSize: PLongWord; pName: PAnsiChar; pDIOBytes, pCounters: PLongWord): LongWord; cdecl;
function ClearDevices: LongWord; cdecl;
function AIOUSB_CloseDevice(DeviceIndex: LongWord): LongWord; cdecl;
function AIOUSB_ReloadDeviceLinks: LongWord; cdecl;
function GetDeviceUniqueStr(DeviceIndex: LongWord; pIIDSize: PLongWord; pIID: PAnsiChar): LongWord; cdecl;
function GetDeviceSerialNumber(DeviceIndex: LongWord; var pSerialNumber: Int64): LongWord; cdecl;
function GetDeviceByEEPROMByte(Data: Byte): LongWord; cdecl;
function GetDeviceByEEPROMData(StartAddress, DataSize: LongWord; pData: PByte): LongWord; cdecl;
function ResolveDeviceIndex(DeviceIndex: LongWord): LongWord; cdecl;
function GetDeviceBySerialNumber(const pSerialNumber: Int64): LongWord; cdecl;
function CustomEEPROMRead(DeviceIndex: LongWord; StartAddress: LongWord; var DataSize: LongWord; Data: Pointer): LongWord; cdecl;
function CustomEEPROMWrite(DeviceIndex: LongWord; StartAddress: LongWord; DataSize: LongWord; Data: Pointer): LongWord; cdecl;
function AIOUSB_FlashRead(DeviceIndex: LongWord; StartAddress: LongWord; var DataSize: LongWord; Data: Pointer): LongWord; cdecl;
function AIOUSB_FlashWrite(DeviceIndex: LongWord; StartAddress: LongWord; DataSize: LongWord; Data: Pointer): LongWord; cdecl;
function AIOUSB_FlashEraseSector(DeviceIndex: LongWord; Sector: Integer): LongWord; cdecl;
function GenericVendorRead(DeviceIndex: LongWord; Request: Byte; Value, Index: Word; var DataSize: LongWord; pData: Pointer): LongWord; cdecl;
function GenericVendorWrite(DeviceIndex: LongWord; Request: Byte; Value, Index: Word; DataSize: LongWord; pData: Pointer): LongWord; cdecl;
function AWU_GenericBulkIn(DeviceIndex: LongWord; PipeID: LongWord; pData: Pointer; DataSize: LongWord; var BytesRead: LongWord): LongWord; cdecl;
function AWU_GenericBulkOut(DeviceIndex: LongWord; PipeID: LongWord; pData: Pointer; DataSize: LongWord; var BytesWritten: LongWord): LongWord; cdecl;

function AIOUSB_ClearFIFO(DeviceIndex: LongWord; TimeMethod: LongWord): LongWord; cdecl;
function AIOUSB_GetStreamStatus(DeviceIndex: LongWord; var Status: LongWord): LongWord; cdecl;
function AIOUSB_SetStreamingBlockSize(DeviceIndex, BlockSize: LongWord): LongWord; cdecl;
function AIOUSB_ResetChip(DeviceIndex: LongWord): LongWord; cdecl;
function AIOUSB_AbortPipe(DeviceIndex: LongWord; PipeID: Byte): LongWord; cdecl;
function AIOUSB_UploadD15LoFirmwaresByPID(pFirmScript: PAnsiChar): LongWord; cdecl;

//FWE 2.0 PNP in general.
function AIOUSB_QuerySimplePNPData(DeviceIndex: LongWord; pPNPData: Pointer; pPNPDataBytes: PLongWord): LongWord; cdecl;

//Load-time defaults.
function AIOUSB_SaveStateAsDefaults(DeviceIndex: LongWord): LongWord; cdecl;
function AIOUSB_RestoreFactoryDefaults(DeviceIndex: LongWord): LongWord; cdecl;
function AIOUSB_SetDefaultsTable(DeviceIndex: LongWord; pDefTable: Pointer; pDefTableBytes: PLongWord): LongWord; cdecl;
function AIOUSB_GetDefaultsTable(DeviceIndex: LongWord; pDefTable: Pointer; pDefTableBytes: PLongWord): LongWord; cdecl;

//Global tick.
function AIOUSB_SetGlobalTickRate(DeviceIndex: LongWord; pHz: PDouble): LongWord; cdecl;



//DIO.
function DIO_Configure(DeviceIndex: LongWord; Tristate: ByteBool; pOutMask: Pointer; pData: Pointer): LongWord; cdecl;
function DIO_ConfigureEx(DeviceIndex: LongWord; pOutMask: Pointer; pData: Pointer; pTristateMask: Pointer): LongWord; cdecl;
function DIO_ConfigurationQuery(DeviceIndex: LongWord; pOutMask: Pointer; pTristateMask: Pointer): LongWord; cdecl;
function DIO_ConfigureMasked(DeviceIndex: LongWord; pOuts: Pointer; pOutsMask: Pointer; pData: Pointer; pDataMask: Pointer; pTristates: Pointer; pTristatesMask: Pointer): LongWord; cdecl;
function DIO_Write1(DeviceIndex, BitIndex: LongWord; Data: ByteBool): LongWord; cdecl;
function DIO_Write8(DeviceIndex, ByteIndex: LongWord; Data: Byte): LongWord; cdecl;
function DIO_WriteAll(DeviceIndex: LongWord; pData: Pointer): LongWord; cdecl;
function DIO_Read1(DeviceIndex, BitIndex: LongWord; Buffer: PByte): LongWord; cdecl;
function DIO_Read8(DeviceIndex, ByteIndex: LongWord; Buffer: PByte): LongWord; cdecl;
function DIO_ReadAll(DeviceIndex: LongWord; pData: Pointer): LongWord; cdecl;

function DIO_StreamOpen(DeviceIndex: LongWord; bIsRead: LongBool): LongWord; cdecl;
function DIO_StreamClose(DeviceIndex: LongWord): LongWord; cdecl;
function DIO_StreamFrame(DeviceIndex, FramePoints: LongWord; pFrameData: PWord; var BytesTransferred: LongWord): LongWord; cdecl;
function DIO_StreamSetClocks(DeviceIndex: LongWord; var ReadClockHz, WriteClockHz: Double): LongWord; cdecl;

function DIO_SPI_Write(DeviceIndex: LongWord; Address, Reg, Value: Byte): LongWord; cdecl;
function DIO_SPI_Read(DeviceIndex: LongWord; Address, Reg: Byte; pValue: PByte): LongWord; cdecl;

//DIO automapping.
function DIO_Automap_ClearTable(DeviceIndex: LongWord): LongWord; cdecl;
function DIO_Automap_SetTable(DeviceIndex: LongWord; pMapTable: Pointer; pMapTableBytes: PLongWord): LongWord; cdecl;
function DIO_Automap_AddEntry(DeviceIndex: LongWord; pMapEntry: PWord): LongWord; cdecl;
function DIO_Automap_SetTickDivisor(DeviceIndex: LongWord; pDivisor: PByte): LongWord; cdecl;
//function DIO_Automap_GetTable(DeviceIndex: LongWord; pMapTable: Pointer; pMapTableBytes: PLongWord): LongWord; cdecl;

//DIO PWM.
function DIO_PWM_Start(DeviceIndex: LongWord; pPWMTable: Pointer; pPWMTableBytes: PLongWord): LongWord; cdecl;

//function DIO_PWM_GetAll(DeviceIndex: LongWord; pDutyCycles: Pointer; pDutyCyclesBytes: PLongWord): LongWord; cdecl;
//function DIO_PWM_SetAll(DeviceIndex: LongWord; pDivisor: PByte; pPWMTable: Pointer; pPWMTableBytes: PLongWord): LongWord; cdecl;
//function DIO_PWM_Clear(DeviceIndex: LongWord): LongWord; cdecl;
//function DIO_PWM_Add(DeviceIndex: LongWord; BitIndex: LongWord; DutyCycle: LongWord): LongWord; cdecl;
//function PWM_SetGlobalTicksPerPWMPeriod(DeviceIndex: LongWord; ): LongWord; cdecl;

//DIO latching.
function DIO_Latch_SetDivisor(DeviceIndex: LongWord; pDivisor: PByte): LongWord; cdecl;
function DIO_Latch_Reset(DeviceIndex: LongWord): LongWord; cdecl;
function DIO_Latch_Read(DeviceIndex: LongWord; pLowLatches, pHighLatches, pNoLatches: PByte; pLatchesBytes: PLongWord): LongWord; cdecl;

//DIO debounce.
function DIO_Deb_SetConfig(DeviceIndex: LongWord; pDebTable: Pointer; pDebTableBytes: PLongWord): LongWord; cdecl;
function DIO_Deb_ReadAll(DeviceIndex: LongWord; pDebData: PByte): LongWord; cdecl;



//Counters.
function CTR_8254Mode(DeviceIndex, BlockIndex, CounterIndex, Mode: LongWord): LongWord; cdecl;
function CTR_8254Load(DeviceIndex, BlockIndex, CounterIndex: LongWord; LoadValue: Word): LongWord; cdecl;
function CTR_8254ModeLoad(DeviceIndex, BlockIndex, CounterIndex, Mode: LongWord; LoadValue: Word): LongWord; cdecl;
function CTR_8254ReadModeLoad(DeviceIndex, BlockIndex, CounterIndex, Mode: LongWord; LoadValue: Word; pReadValue: PWord): LongWord; cdecl;
function CTR_8254Read(DeviceIndex, BlockIndex, CounterIndex: LongWord; pReadValue: PWord): LongWord; cdecl;
function CTR_8254ReadStatus(DeviceIndex, BlockIndex, CounterIndex: LongWord; pReadValue: PWord; pStatus: PByte): LongWord; cdecl;
function CTR_8254ReadAll(DeviceIndex: LongWord; pData: PWord): LongWord; cdecl;
function CTR_StartOutputFreq(DeviceIndex, BlockIndex: LongWord; pHz: PDouble): LongWord; cdecl;
function CTR_8254ReadLatched(DeviceIndex: LongWord; pData: PWord): LongWord; cdecl;
function CTR_8254SelectGate(DeviceIndex, GateIndex: LongWord): LongWord; cdecl;

function CTR_SetWaitGates(DeviceIndex: LongWord; A, B: Byte): LongWord; cdecl;
function CTR_EndWaitGates(DeviceIndex: LongWord): LongWord; cdecl;
function CTR_WaitForGate(DeviceIndex: LongWord; GateIndex: Byte; var Content: Word): LongWord; cdecl;

function CTR_StartMeasuringPulseWidth(DeviceIndex: LongWord): LongWord; cdecl;
function CTR_StopMeasuringPulseWidth(DeviceIndex: LongWord): LongWord; cdecl;
function CTR_GetPulseWidthMeasurement(DeviceIndex, BlockIndex, CounterIndex: LongWord; pReadValue: PWord): LongWord; cdecl;



//A/D.
function ADC_GetConfig(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord): LongWord; cdecl;
function ADC_SetConfig(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord): LongWord; cdecl;
function ADC_RangeAll(DeviceIndex: LongWord; pGainCodes: PByte; bDifferential: LongBool): LongWord; cdecl;
function ADC_Range1(DeviceIndex, ADChannel: LongWord; GainCode: Byte; bDifferential: LongBool): LongWord; cdecl;
function ADC_ADMode(DeviceIndex: LongWord; TriggerMode, CalMode: Byte): LongWord; cdecl;
function ADC_SetScanLimits(DeviceIndex, StartChannel, EndChannel: LongWord): LongWord; cdecl;
function ADC_SetOversample(DeviceIndex: LongWord; Oversample: Byte): LongWord; cdecl;
function ADC_QueryCal(DeviceIndex: LongWord): LongWord; cdecl;
function ADC_SetCal(DeviceIndex: LongWord; CalFileName: PAnsiChar): LongWord; cdecl;
function ADC_SetCalAndSave(DeviceIndex: LongWord; CalFileName, SaveCalFileName: PAnsiChar): LongWord; cdecl;
function ADC_Initialize(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord; CalFileName: PAnsiChar): LongWord; cdecl;
function ADC_Start(DeviceIndex: LongWord): LongWord; cdecl;
function ADC_Stop(DeviceIndex: LongWord): LongWord; cdecl;
function ADC_BulkAcquire(DeviceIndex: LongWord; BufSize: LongWord; pBuf: Pointer): LongWord; cdecl;
function ADC_BulkPoll(DeviceIndex: LongWord; var BytesLeft: LongWord): LongWord; cdecl;
function ADC_BulkAbort(DeviceIndex: LongWord): LongWord; cdecl;
function ADC_BulkMode(DeviceIndex, BulkMode: LongWord): LongWord; cdecl;
function ADC_BulkContinuousCallbackStart(DeviceIndex: LongWord; BufSize: LongWord; BaseBufCount: LongWord; Context: LongWord; pCallback: Pointer): LongWord; cdecl;
function ADC_BulkContinuousCallbackStartClocked(DeviceIndex: LongWord; BufSize: LongWord; BaseBufCount: LongWord; Context: LongWord; pCallback: Pointer; var Hz: Double): LongWord; cdecl;
function ADC_BulkContinuousRingStart(DeviceIndex: LongWord; RingBufferSize: LongWord; PacketsPerBlock: LongWord): LongWord; cdecl;
function ADC_BulkContinuousEnd(DeviceIndex: LongWord; pIOStatus: PLongWord): LongWord; cdecl;
function ADC_BulkContinuousDebug(DeviceIndex: LongWord; var Blanks, Accessings, GotDatas: LongWord): LongWord; cdecl;
function ADC_GetImmediate(DeviceIndex, Channel: LongWord; pBuf: PWord): LongWord; cdecl;
function ADC_GetScan(DeviceIndex: LongWord; pBuf: PWord): LongWord; cdecl;
function ADC_GetScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; cdecl;
function ADC_GetTrigScan(DeviceIndex: LongWord; pBuf: PWord; TimeoutMS: LongInt): LongWord; cdecl;
function ADC_GetTrigScanV(DeviceIndex: LongWord; pBuf: PDouble; TimeoutMS: LongInt): LongWord; cdecl;
function ADC_GetChannelV(DeviceIndex, ChannelIndex: LongWord; pBuf: PDouble): LongWord; cdecl;
function ADC_GetCalRefV(DeviceIndex, CalRefIndex: LongWord; var pRef: Double): LongWord; cdecl;
function ADC_GetBuf(DeviceIndex: LongWord; out pData: Pointer; out BufSize: LongWord; pReserved: Pointer; Timeout: Double): LongWord; cdecl;
function ADC_ReadData(DeviceIndex: LongWord; pConfigBuf: Pointer; var ScansToRead: LongWord; pData: PDouble; Timeout: Double): LongWord; cdecl;
function ADC_FullStartRing(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord; CalFileName: PAnsiChar; pCounterHz: PDouble; RingBufferSize: LongWord; PacketsPerBlock: LongWord): LongWord; cdecl;



//D/A.
function DACDirect(DeviceIndex: LongWord; Channel: Word; Value: Word): LongWord; cdecl;
function DACMultiDirect(DeviceIndex: LongWord; pDACData: PDACEntry; DACDataCount: LongWord): LongWord; cdecl;
function DACSetBoardRange(DeviceIndex: LongWord; RangeCode: LongWord): LongWord; cdecl;
function DACSetChannelCal(DeviceIndex: LongWord; Channel: LongWord; CalFileName: PAnsiChar): LongWord; cdecl;
function DACOutputOpen(DeviceIndex: LongWord; var ClockHz: Double): LongWord; cdecl;
function DACOutputAbort(DeviceIndex: LongWord): LongWord; cdecl;
function DACOutputClose(DeviceIndex: LongWord; bWait: LongBool): LongWord; cdecl;
function DACOutputCloseNoEnd(DeviceIndex: LongWord; bWait: LongBool): LongWord; cdecl;
function DACOutputSetCount(DeviceIndex, NewCount: LongWord): LongWord; cdecl;
function DACOutputFrame(DeviceIndex, FramePoints: LongWord; FrameData: PWord): LongWord; cdecl;
function DACOutputFrameRaw(DeviceIndex, FramePoints: LongWord; FrameData: PWord): LongWord; cdecl;
function DACOutputStatus(DeviceIndex: LongWord): LongWord; cdecl;
function DACOutputStart(DeviceIndex: LongWord): LongWord; cdecl;
function DACOutputSetInterlock(DeviceIndex: LongWord; bInterlock: LongBool): LongWord; cdecl;
function DACOutputSetClock(DeviceIndex: LongWord; var ClockHz: Double): LongWord; cdecl;

function DACOutputProcess(DeviceIndex: LongWord; var ClockHz: Double; Samples: LongWord; pSampleData: PWord): LongWord; cdecl;
function DACOutputLoadProcess(DeviceIndex: LongWord; var ClockHz: Double; Samples: LongWord; pSampleData: PWord): LongWord; cdecl;



//Watchdog.
function WDG_SetConfig(DeviceIndex: LongWord; pTimeoutSeconds: PDouble; pWDGTable: Pointer; pWDGTableBytes: PLongWord): LongWord; cdecl;
function WDG_GetStatus(DeviceIndex: LongWord; pStatus: Pointer; pStatusBytes: PLongWord): LongWord; cdecl;
function WDG_Pet(DeviceIndex: LongWord; PetFlag: LongWord): LongWord; cdecl;
//function WDG_SetTimeout(DeviceIndex: LongWord; pTimeoutSeconds: PDouble): LongWord; cdecl;
//function WDG_GetTimeout(DeviceIndex: LongWord; pTimeoutSeconds: PDouble): LongWord; cdecl;


function AIOUSB_OfflineWrite1(DeviceIndex: LongWord; SampleIndex: LongWord; Buf: Word): LongWord; cdecl;
function AIOUSB_OfflineRead1(DeviceIndex: LongWord; SampleIndex: LongWord; pBuf: PWord): LongWord; cdecl;



//Custom.
function ADC_InitFastITScanV(DeviceIndex: LongWord): LongWord; cdecl;
function ADC_ResetFastITScanV(DeviceIndex: LongWord): LongWord; cdecl;
function ADC_SetFastITScanVChannels(DeviceIndex, NewChannels: LongWord): LongWord; cdecl;
function ADC_GetFastITScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; cdecl;
function ADC_GetITScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; cdecl;
function DIO_CSA_DoSync(DeviceIndex: LongWord; var BaseRateHz, DurAms, DurBms, DurCms: Double): LongWord; cdecl;
function DIO_CSA_DebounceSet(DeviceIndex, DebounceCounts: LongWord): LongWord; cdecl;
function DIO_CSA_DebounceReadAll(DeviceIndex: LongWord; pData: Pointer): LongWord; cdecl;
function DAC_CSA_SetRangeLimits(DeviceIndex: LongWord; pData: Pointer): LongWord; cdecl;
function DAC_CSA_ClearRangeLimits(DeviceIndex: LongWord): LongWord; cdecl;
function DIO_CSA_ReadAllString(DeviceIndex: LongWord; pData: Pointer; pDataBytes: PLongWord): LongWord; cdecl;
function ADC_CSA_GetScanOversamples(DeviceIndex: LongWord; pBuf: PWord): LongWord; cdecl;

function ADC_CSA_InitFastScanV(DeviceIndex: LongWord): LongWord; cdecl;
function ADC_CSA_ResetFastScanV(DeviceIndex: LongWord): LongWord; cdecl;
function ADC_CSA_GetFastScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; cdecl;

function DACDIO_WriteAll(DeviceIndex: LongWord; pDACCounts: PWord; pDIOData: PByte): LongWord; cdecl;




//Debug / engineering.
function GetPipes(DeviceIndex: LongWord; var PipeCount: LongWord; pPipeData: PLongWord): LongWord; cdecl;
function GetDeviceHandle(DeviceIndex: LongWord; pData: PHandle): LongWord; cdecl;
function AIOUSB_UploadFirmware(DeviceIndex: LongWord; FirmBuf: PAnsiChar; BufLen: LongWord): LongWord; cdecl;

function DEB_BulkIn(DeviceIndex: LongWord): LongWord; cdecl;
function DEB_BulkOut(DeviceIndex, TargetPipe: LongWord; pBuf: Pointer; BufLen: LongWord): LongWord; cdecl;
function DEB_SetInterface(DeviceIndex: LongWord; TargetInterface: Word): LongWord; cdecl;

function DEB_BufTest(DeviceIndex: LongWord; VR: Byte; VI: LongWord; pData: PByte; DataSize: LongWord): LongWord; cdecl;





implementation

uses
  Math,
  SysUtils, Classes,
  SetupDi, WinUSB,
  ContBufThreads,
  TheseUtils;

const
  ERROR_DEVICE_REMOVED = 1617;
  ERROR_DEVICE_NOT_CONNECTED = 1167; //Observed on an actual motherboard, probably typoed from ERROR_DEVICE_REMOVED.
  ERROR_NO_SUCH_DEVICE = 433;

  FILE_DEVICE_UNKNOWN = $0022;
  METHOD_BUFFERED = 0;
  METHOD_NEITHER  = 3;
  FILE_ANY_ACCESS = 0;

  IOCTL_ADAPT_INDEX = $0000;
  IOCTL_CY_BASE = LongWord(FILE_DEVICE_UNKNOWN shl 16) or (FILE_ANY_ACCESS shl 14);
  IOCTL_ADAPT_GET_DRIVER_VERSION        = IOCTL_CY_BASE or ((IOCTL_ADAPT_INDEX   ) shl 2) or METHOD_BUFFERED;
  IOCTL_ADAPT_SELECT_INTERFACE          = IOCTL_CY_BASE or ((IOCTL_ADAPT_INDEX+ 3) shl 2) or METHOD_BUFFERED;
  IOCTL_ADAPT_SEND_EP0_CONTROL_TRANSFER = IOCTL_CY_BASE or ((IOCTL_ADAPT_INDEX+ 8) shl 2) or METHOD_BUFFERED;
  IOCTL_ADAPT_ABORT_PIPE                = IOCTL_CY_BASE or ((IOCTL_ADAPT_INDEX+17) shl 2) or METHOD_BUFFERED;
  IOCTL_ADAPT_SEND_NON_EP0_DIRECT       = IOCTL_CY_BASE or ((IOCTL_ADAPT_INDEX+18) shl 2) or METHOD_NEITHER;
  IOCTL_ADAPT_GET_DEVICE_SPEED          = IOCTL_CY_BASE or ((IOCTL_ADAPT_INDEX+19) shl 2) or METHOD_BUFFERED;

  AIOWinUSBClassGUID: TGUID = (D1: $88D87F5A; D2: $EA16; D3: $93FC; D4: ($21, $65, $39, $C9, $1C, $36, $C9, $6E) );
  AIOCyUSBClassGUID:  TGUID = (D1: $D52D27E3; D2: $CF76; D3: $25EB; D4: ($72, $EA, $59, $6F, $22, $34, $C0, $E1) );
  D15LoClassGUID:     TGUID = (D1: $AE18AA60; D2: $7F6A; D3: $11D4; D4: ($97, $DD, $00, $01, $02, $29, $B9, $59) );

  CyBaseTimeout = 42; //It's an integer, and all the .PDF says is it's the value you'd expect divided by 1000.
  DACDIOStreamImmHz = 1024*1024; //`@ Should maybe be faster?

type
  TCySetupPacket = packed record
    bRequestType: Byte;
    bRequest: Byte;
    Value,
    Index,
    Len: Word;
    ulTimeOut: LongWord;
  end;

  TCyIsoAdvParams = packed record
    IsoId: Word;
    IsoCmd: Word;
    ULParam1: LongWord;
    ULParam2: LongWord;
  end;

  TCySingleTransfer = packed record
    SetupPacket: TCySetupPacket;

    reserved: Byte;

    ucEndpointAddress: Byte;
    NtStatus,
    UsbdStatus,
    IsoPacketOffset,
    IsoPacketLength,
    BufferOffset,
    BufferLength: LongWord;
  end;
  TPCySingleTransfer = ^TCySingleTransfer;

  TCyControlTransfer = TCySingleTransfer;
  TPCyControlTransfer = ^TCyControlTransfer;

  TCyBulkTransfer = TCySingleTransfer;
  TPCyBulkTransfer = ^TCyBulkTransfer;

  TCy2IsoTransfer = TCySingleTransfer;
  TPCy2IsoTransfer = ^TCy2IsoTransfer;

  TCy3IsoTransfer = packed record
    IsoAdvParams: TCyIsoAdvParams;

    reserved: Byte;

    ucEndpointAddress: Byte;
    NtStatus,
    UsbdStatus,
    IsoPacketOffset,
    IsoPacketLength,
    BufferOffset,
    BufferLength: LongWord;
  end;
  TPCy3IsoTransfer = ^TCy3IsoTransfer;

  TStringArray = array of AnsiString;

  TWordArray = array of Word;

  TDIO16ClockData = packed record
    Disables: Byte;
    WriteOctDac, ReadOctDac: Word;
  end;

  TGenericBulk = function (DeviceIndex: LongWord; PipeID: LongWord; pData: Pointer; DataSize: LongWord; var BytesTransferred: LongWord): LongWord; cdecl;



const
  AUR_DIO_WRITE           = $10;
  AUR_DIO_READ            = $11;
  AUR_DIO_CONFIG          = $12;
  AUR_DIO_CONFIG_QUERY    = $13;
  AUR_DIO_LATCH_READ      = $14;
  AUR_DIO_DEB_READ        = $15;
  AUR_DIO_ADVANCED        = $18;
  AUR_DIO_CONFIG_MASKED   = $1F;
  AUR_CTR_READ            = $20;
  AUR_CTR_MODE            = $21;
  AUR_CTR_LOAD            = $22;
  AUR_CTR_MODELOAD        = $23;
  AUR_CTR_SELGATE         = $24;
  AUR_CTR_READALL         = $25;
  AUR_CTR_READLATCHED     = $26;
  AUR_CTR_COS_BULK_GATE2  = $27;
  AUR_CTR_COS_BULK_ABORT  = $29;
  {
  AUR_CTR_PUR_FIRST       = $28; //Not used with device, for index offsetting
  AUR_CTR_PUR_OFRQ        = $28; //Set up to output frequency
  AUR_CTR_PUR_MFRQ        = $2C; //Set up to measure frequency
  AUR_CTR_PUR_EVCT        = $2D; //Set up to count events
  AUR_CTR_PUR_MPUL        = $2E; //Set up to measure pulse width
  }
  AUR_WDG_STATUS          = $2E;
  AUR_DIO_WDG16_DEPREC    = $2F;
  AUR_GEN_CLEAR_FIFO_NEXT = $34;
  AUR_GEN_CLEAR_FIFO      = $35;
  AUR_GEN_CLEAR_FIFO_WAIT = $36;
  AUR_GEN_ABORT_AND_CLEAR = $38;
  AUR_SET_GPIF_MODE       = $39;
  AUR_GEN_REGISTER        = $3C;
  AUR_PCIE_WDG            = $40;
  AUR_WDG                 = $44;
  AUR_OFFLINE_READWRITE   = $50;
  AUR_DACDIO_WRITEALL     = $8C;
  //                        $90; //First index assigned to self-tests.
  AUR_SELF_TEST_1         = $91;
  //                        $9F; //Last index assigned to self-tests.
  AUR_DAC_CONTROL         = $B0;
  AUR_DAC_DATAPTR         = $B1;
  AUR_DAC_DIVISOR         = $B2;
  AUR_DAC_IMMEDIATE       = $B3;
  AUR_GEN_STREAM_STATUS   = $B4;
  AUR_FLASH_READWRITE     = $B5;
  AUR_DAC_RANGE           = $B7;
  AUR_PROBE_CALFEATURE    = $BA;
  //                        $BB;
  //                        $BC;
  AUR_DIO_SETCLOCKS       = $BD;
  AUR_ADC_SET_CONFIG      = $BE;
  AUR_ADC_IMMEDIATE       = $BF;
  AUR_DIO_SPI_WRITE       = $C0;
  AUR_DIO_SPI_READ        = $C1;
  AUR_SET_CUSTOM_CLOCKS   = $C4;
  AUR_ADC_GET_CONFIG      = $D2;
  AUR_DEBUG_DEBUG         = $D4;
  AUR_DEBUG_FLASH_1TO1    = $F0;
  AUR_DEBUG_FLASH_ERASE   = $FC;

  //Cypress FX2 vendor requests.
  CUR_RAM_READ            = $A3;



type
  TDACWorker = class(TStartableThread)
    public
      Index: Integer;
    protected
      procedure Execute; override;
  end;

  TDACData = AnsiString;

  TBCStyle = (bsADC, bsDIO);
  TBCStyles = set of TBCStyle;

  TADCWorker = class(TStartableThread)
  public
    DI: LongWord;
    TargetPipe: LongWord;
    BytesLeft: LongInt;
    pTar: PWord;
    BCStyle: TBCStyle;
    BlockSize: LongWord;
    bAbort: Boolean;
  protected
    ADBuf: array of Byte;

    procedure Execute; override;
  end;

  PContCallback = procedure (pBuf: PWord; BufSize, Flags, Context: LongWord); cdecl;
  TADCContAcqWorker = class;
  TADCContBufWorker = class;

  TADCContAcqWorker = class(TStartableThread)
  public
    DI: LongWord;
    TargetPipe: LongWord;
    bCounterControl: Boolean;
    DivisorA, DivisorB: Word;
    //BytesPerBC,
    IOStatus: LongWord;
    BCStyle: TBCStyle;
    MyBufThread: TADCContBufWorker;
    hStartEvent: THandle;
  protected
    procedure Execute; override;
  end;

  TADCContBufWorker = class(TStartableThread)
  public
    BytesPerBuf: LongWord;
    hBufMutex, hBlankBufSem, hDataBufSem, hKillSem: THandle;
    MyAcqThread: TADCContAcqWorker;
    BufBuf: array of PContBuf;
    NextIndexIn, NextIndexOut: Integer;
    Callback: PContCallback;
    CallbackContext: LongWord;

    procedure GetDebugStats(var Blanks, Accessings, GotDatas: LongWord);
  protected
    procedure Execute; override;
    function GetBlankBuf(Flags: LongWord): PContBuf;
    procedure PutDataBuf(pNewBuf: PContBuf);
    function GetDataBuf(Timeout: LongWord = INFINITE): PContBuf;
    function GetDataBufOrKilled: PContBuf;
    procedure PutBlankBuf(pNewBuf: PContBuf);
    function ExtraBuf: PContBuf;
  end;

  TRingAcqData = record
    RingBuffer: array of Word;
    iNextRead, iNextWrite: LongWord;
    hSem: THandle;
  end;
  TPRingAcqData = ^TRingAcqData;

  TCtrMonitorThread = class(TStartableThread)
  public
    DI: LongWord;
    hListMutex: THandle;
    MeasuredPulseWidth: array of Word;
  protected
    procedure Execute; override;
  end;

  TUSBDriverType = (dtNone, dtWinUSB, dtCyUSB2, dtCyUSB3);
  TUSBSpeed = (usUnknown, usLowFull, usHigh);

  TPNPData = packed record
    PNPSize: Byte;
    Rev: Word;
    nADCConfigBytes,
    nDIOControlBytes,
    nDIOBytes,
    nCounterBlocks,
    nDACWords,
    HasDeb,
    HasLatch,
    PWMTableMaxLen,
    MapTableMaxLen,
    MapHighSrcBit,
    MapHighDstBit,
    HasDIOWrite1: Byte;
  end;

  TDeviceData = record
    bOpen, bDeviceWasHere, bGotHandle: Boolean;
    hHandleTableMutex: THandle;
    HandleTable: array of record
      ThreadID: LongWord;
      hDevice: THandle;
    end;
    ExpandFromOldHandle, hWinUSBFile: THandle;
    USBDriverType: TUSBDriverType;
    DevPath: AnsiString;
    DIOBytes, DIOConfigBits: LongWord;
    LastDIOData: array of Byte;
    Counters: LongWord;
    Tristates: LongWord;
    bGateSelectable: Boolean;
    RootClock: Double;
    //LastPurpose: Byte;
    LastEventCount: Word;
    PID: LongWord;
    CtrDivisor: Word;
    bGetName: Boolean;
    ConfigBytes: LongWord;

    ImmDACs, ImmADCs: LongWord;
    ImmADCPostScale: Double;

    bDACBoardRange, bDACChannelCal, bDACStream, bDACDIOStream, bDACSlowWaveStream: Boolean;
    DACsUsed: Integer;
    bDACOpen, bDACClosing, bDACAborting, bDACStarted: Boolean;
    DACData: array of TDACData;
    hDACDataMutex, hDACDataSem: THandle;
    PendingDACData: TDACData;
    WorkerThread: TDACWorker;

    CtrMonitorThread: TCtrMonitorThread;

    bADCBulk, bADCDIOStream: Boolean;
    ADCChannels, ADCMUXChannels: LongWord;
    ADCWorker: TADCWorker;
    ADCContAcqWorker: TADCContAcqWorker;
    ADCContBufWorker: TADCContBufWorker;
    pRingAcqData: TPRingAcqData;
    RangeShift: Byte;
    FastITConfig, FastITBakConfig: array of Byte;
    CSA_FastConfig, CSA_FastBakConfig: array of Byte;

    bDIOStream, bDIOOpen, bDIORead: Boolean;

    StreamingBlockSize, StreamingBlockSizeFloor: LongWord;

    bDIODebounce, bDIOSPI: Boolean;

    bSetCustomClocks: Boolean;

    WDGBytes: LongWord;

    bClearFIFO: Boolean;

    FlashSectors: Integer;

    bFirmware20: Boolean;
    USBSpeed: TUSBSpeed;
    PNPData: TPNPData;
  end;
  PDeviceData = ^TDeviceData;

const
  diNone = $FFFFFFFF;
  diFirst = $FFFFFFFE;
  diOnly = $FFFFFFFD;
  diLoadAndOnly = $FFFFFFFC;

var
  bLoaded: Boolean = False;
  Dev: array[0..31] of TDeviceData;

function ADC_GetScan_Inner(var DeviceIndex: LongWord; var Config: array of Byte; var ADBuf: TWordArray; var StartChannel, EndChannel: Byte; TimeoutMS: LongInt): LongWord; forward;

function Validate(var DeviceIndex: LongWord): LongWord;
var
  I: Integer;
  bGotOne, bOnly: Boolean;

begin
  if DeviceIndex = diLoadAndOnly then begin
    for I := 0 to High(Dev) do AIOUSB_CloseDevice(I);
    LoadDriverLinks;
    DeviceIndex := diOnly;
  end;

  if (DeviceIndex = diOnly) or (DeviceIndex = diFirst) then begin
    bOnly := DeviceIndex = diOnly;
    bGotOne := False;
    for I := 0 to High(Dev) do begin
      if Dev[I].bGotHandle then begin
        if bGotOne then begin
          Result := ERROR_DUP_NAME;
          Exit;
        end;
        DeviceIndex := I;
        if not bOnly then begin
          Result := ERROR_SUCCESS;
          Exit;
        end;
        bGotOne := True;
      end;
    end;
    if DeviceIndex < LongWord(Length(Dev)) then
      Result := ERROR_SUCCESS
    else
      Result := ERROR_FILE_NOT_FOUND
    ;
  end
  else if DeviceIndex >= LongWord(Length(Dev)) then begin
    Result := ERROR_INVALID_INDEX;
  end
  else
    Result := ERROR_SUCCESS;
  ;
end;

function AIOUSB_CloseDevice(DeviceIndex: LongWord): LongWord; cdecl;
var
  I: Integer;

begin
  try
  Result := Validate(DeviceIndex);
  if Result <> ERROR_SUCCESS then Exit;

  with Dev[DeviceIndex] do begin
    if not bGotHandle then begin
      if bDeviceWasHere then begin
        bDeviceWasHere := False;
        Result := ERROR_SUCCESS;
      end
      else
        Result := ERROR_INVALID_HANDLE
      ;
      Exit;
    end;

    try
      bDeviceWasHere := False;
      case USBDriverType of
        dtWinUSB: begin
          WaitForSingleObject(hHandleTableMutex, INFINITE);
          for I := 0 to High(HandleTable) do
            WinUSB_Free(HandleTable[I].hDevice)
          ;
          SetLength(HandleTable, 0);
          ReleaseMutex(hHandleTableMutex);

          CloseHandle(hWinUSBFile);
        end;
        else begin
          WaitForSingleObject(hHandleTableMutex, INFINITE);
          for I := 0 to High(HandleTable) do
            CloseHandle(HandleTable[I].hDevice)
          ;
          SetLength(HandleTable, 0);
          ReleaseMutex(hHandleTableMutex);
        end;
      end;
      Result := ERROR_SUCCESS;
    except
      Result := GetLastError;
      if Result = ERROR_SUCCESS then Result := ERROR_GEN_FAILURE;
    end;
    bGotHandle := False;
    hWinUSBFile := 0;
  end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function GetThreadHandleForDevice(DeviceIndex: LongWord): THandle;
var
  I: Integer;
  ThreadID: LongWord;

begin
  with Dev[DeviceIndex] do
    case USBDriverType of
      dtCyUSB2, dtCyUSB3: begin
        ThreadID := GetCurrentThreadId;

        WaitForSingleObject(hHandleTableMutex, INFINITE);
          Result := INVALID_HANDLE_VALUE;
          for I := 0 to High(HandleTable) do
            if HandleTable[I].ThreadID = ThreadID then begin
              Result := HandleTable[I].hDevice;
              Break;
            end
          ;
          if Result = INVALID_HANDLE_VALUE then begin
            I := Length(HandleTable);
            SetLength(HandleTable, I+1);
            HandleTable[I].ThreadID := ThreadID;
            HandleTable[I].hDevice := CreateFileA(PAnsiChar(DevPath), GENERIC_WRITE or GENERIC_READ, FILE_SHARE_WRITE or FILE_SHARE_READ, nil, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, 0);
            Result := HandleTable[I].hDevice;
          end;
        ReleaseMutex(hHandleTableMutex);
      end;
      dtWinUSB: begin
        WaitForSingleObject(hHandleTableMutex, INFINITE);
          if Length(HandleTable) <> 0 then
            Result := HandleTable[0].hDevice
          else begin
            SetLength(HandleTable, 1);
            HandleTable[0].ThreadID := 0;
            WinUSB_Initialize(hWinUSBFile, HandleTable[0].hDevice);
            Result := HandleTable[0].hDevice;
          end;
        ReleaseMutex(hHandleTableMutex);
      end;
      else begin
        Result := INVALID_HANDLE_VALUE; //`@
      end;
    end
  ;
end;

procedure AddThreadHandleForDevice(DeviceIndex: LongWord; hDevice: THandle);
var
  I: Integer;

begin
  with Dev[DeviceIndex] do begin
    WaitForSingleObject(hHandleTableMutex, INFINITE);
      I := Length(HandleTable);
      SetLength(HandleTable, I+1);
      HandleTable[I].ThreadID := GetCurrentThreadId;
      HandleTable[I].hDevice := hDevice;
    ReleaseMutex(hHandleTableMutex);
  end;
end;

{$IFDEF Debug}
function AnsiMessageBox(Text, Caption: AnsiString; uType: UINT): Integer;
begin
  Result := MessageBoxA(0, PAnsiChar(Text), PAnsiChar(Caption), uType);
  Text := '';
  Caption := '';
end;
{$ENDIF}

function GetCyUSBDriverType(hDevice: THandle): TUSBDriverType;
var
  CyUSBVer, BytesReturned: LongWord;

begin
  CyUSBVer := 0;
  BytesReturned := 0;
  DeviceIoControl(hDevice, IOCTL_ADAPT_GET_DRIVER_VERSION, @CyUSBVer, SizeOf(CyUSBVer), @CyUSBVer, SizeOf(CyUSBVer), BytesReturned, nil);
  //AnsiMessageBox(AnsiString(IntToHex(CyUSBVer, 1)), 'CyUSB Version', MB_ICONINFORMATION); //`@
  case CyUSBVer of
    $1020100, $10303E7: Result := dtCyUSB3;
    else Result := dtCyUSB2;
  end;
end;

function GetDevicePaths(const ClassGUID: TGUID): TStringArray;
var
  DevInterfaceData: SP_DEVICE_INTERFACE_DATA;
  MemberIndex: Integer;
  hDevInfo: THandle;

  L: LongWord;
  pDetailData: PSP_DEVICE_INTERFACE_DETAIL_DATA;

  Buf: AnsiString;
  I, RL: Integer;

begin
  RL := 0;
  SetLength(Result, RL);

  hDevInfo := SetupDiGetClassDevs(@ClassGUID, nil, 0, DIGCF_PRESENT or DIGCF_DEVICEINTERFACE);
  if hDevInfo = 0 then Exit;

  DevInterfaceData.cbSize := sizeof(DevInterfaceData);
  MemberIndex := 0;
  while SetupDiEnumDeviceInterfaces(hDevInfo, nil, ClassGUID, MemberIndex, DevInterfaceData) do begin
    L := 0;
    SetupDiGetDeviceInterfaceDetail(hDevInfo, @DevInterfaceData, nil, 0, @L, nil);

    GetMem(pDetailData, L);
    if SizeOf(Pointer) = 8 then
      pDetailData.cbSize := 8 //The fixed portion is 4. Dunno where 8 comes from.
    else
      pDetailData.cbSize := 5 //The fixed portion is 4. Dunno where 5 comes from.
    ;

    if not SetupDiGetDeviceInterfaceDetail(hDevInfo, @DevInterfaceData, pDetailData, L, nil, nil) then begin
      FreeMem(pDetailData);
      Inc(MemberIndex);
      Continue;
    end;

    SetString(Buf, PAnsiChar(@pDetailData.DevicePath[0]), L - 4);
    FreeMem(pDetailData);
    I := Pos(AnsiChar(#0), Buf);
    if I <> 0 then SetLength(Buf, I - 1);

    SetLength(Result, RL + 1);
    Result[RL] := Buf;
    Inc(RL);
    Buf := '';

    Inc(MemberIndex);
  end;
  SetupDiDestroyDeviceInfoList(hDevInfo);
end;

procedure LoadCyUSBLinks(const ByGUID: TGUID);
var
  DevicePath: TStringArray;
  ThisPath: AnsiString;
  PI, DI: Integer;
  hFile: THandle;
  bFull: Boolean;

begin
  DevicePath := GetDevicePaths(ByGUID);
  for PI := 0 to High(DevicePath) do begin
    ThisPath := DevicePath[PI];
    for DI := 0 to High(Dev) do
      if Dev[DI].bGotHandle then
        if Dev[DI].DevPath = ThisPath then begin
          ThisPath := '';
          Break;
        end
    ;
    if Length(ThisPath) = 0 then Continue;

    hFile := CreateFileA(PAnsiChar(ThisPath), GENERIC_WRITE or GENERIC_READ, FILE_SHARE_WRITE or FILE_SHARE_READ, nil, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, 0);
    ThisPath := '';
    if hFile = INVALID_HANDLE_VALUE then hFile := 0;
    if hFile = 0 then Continue;

    bFull := True;
    for DI := 0 to High(Dev) do with Dev[DI] do
      if (not bGotHandle) and not bDeviceWasHere then begin
        AddThreadHandleForDevice(DI, hFile);
        bGotHandle := True;
        hWinUSBFile := 0;
        USBDriverType := GetCyUSBDriverType(hFile);
        DevPath := DevicePath[PI];

        bOpen := False;
        bDACOpen := False;
        bDACClosing := False;

        bFull := False;
        Break;
      end
    ;
    if bFull then begin
      CloseHandle(hFile);
      Break;
    end;
  end;
  SetLength(DevicePath, 0);
end;

procedure LoadWinUSBLinks(const ByGUID: TGUID);
var
  DevicePath: TStringArray;
  PI, DI: Integer;
  hFile, hWinUSB: THandle;
  bFull: Boolean;

begin
  if bWinUSBLoaded then begin
    DevicePath := GetDevicePaths(ByGUID);
    for PI := 0 to High(DevicePath) do begin
      hFile := CreateFileA(PAnsiChar(DevicePath[PI]), GENERIC_WRITE or GENERIC_READ, 0, nil, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, 0);
      DevicePath[PI] := '';
      if hFile = INVALID_HANDLE_VALUE then hFile := 0;
      if hFile = 0 then Continue;

      if not WinUSB_Initialize(hFile, hWinUSB) then begin
        CloseHandle(hFile);
        Continue;
      end;

      {
      if not CheckVID(hWinUSB) then begin
        WinUSB_Free(hWinUSB);
        CloseHandle(hFile);
        Continue;
      end;

      SetupData.RequestType := $C0;
      SetupData.Request := $A2;
      SetupData.Value := $1DF8;
      SetupData.Index := 0;
      SetupData.DataLength := SizeOf(ThisSN);
      if (not WinUSB_ControlTransfer(hWinUSB, SetupData, @ThisSN, SizeOf(ThisSN), BytesRead, nil)) or (BytesRead <> SizeOf(ThisSN)) then begin
        WinUSB_Free(hWinUSB);
        CloseHandle(hFile);
        Continue;
      end;
      }

      bFull := True;
      DI := 0;
      while DI < Length(Dev) do with Dev[DI] do
        if (not bGotHandle) and not bDeviceWasHere then begin
          AddThreadHandleForDevice(DI, hWinUSB);
          bGotHandle := True;
          hWinUSBFile := hFile;
          USBDriverType := dtWinUSB;

          bOpen := False;
          bDACOpen := False;
          bDACClosing := False;

          bFull := False;
          Break;
        end
        else
          Inc(DI)
      ;
      if bFull then begin
        WinUSB_Free(hWinUSB);
        CloseHandle(hFile);
        Break;
      end;
    end;
    SetLength(DevicePath, 0);
  end;
end;

procedure LoadDriverLinks;
begin
  //May want to alter these to not open handles until GetThreadHandleForDevice.

  LoadCyUSBLinks(AIOCyUSBClassGUID);

  LoadWinUSBLinks(AIOWinUSBClassGUID);
end;

function GetMappedFailure(DeviceIndex: LongWord): LongWord;
begin
  Result := GetLastError;
  case Result of
    ERROR_INVALID_HANDLE, ERROR_DEVICE_REMOVED, ERROR_DEVICE_NOT_CONNECTED, ERROR_NO_SUCH_DEVICE, ERROR_FILE_NOT_FOUND: begin
      AIOUSB_CloseDevice(DeviceIndex);
      Dev[DeviceIndex].bDeviceWasHere := True;

      Dev[DeviceIndex].bOpen := False;
      Dev[DeviceIndex].bDACOpen := False;
      Dev[DeviceIndex].bDACClosing := False;
      Result := ERROR_DEVICE_REMOVED;
    end;
    ERROR_SUCCESS: Result := ERROR_GEN_FAILURE;
  end;
end;

function _Cy_GenericRead(DeviceIndex: LongWord; RequestType, Request: Byte; Value, Index: Word; var DataSize: LongWord; pData: Pointer): LongWord; register; forward;

function CheckFirmware20(DeviceIndex: LongWord): LongWord;
var
  L: LongWord;
  MemFlags: array[0..2] of Byte;

begin
  if Dev[DeviceIndex].bFirmware20 then begin
    Result := ERROR_SUCCESS;
    Exit;
  end;

  //Read out the first chunk of "memory" flags.
  L := Length(MemFlags);
  Result := _Cy_GenericRead(DeviceIndex, $C0, CUR_RAM_READ, $8000, 1, L, @MemFlags[0]);
  if Result <> ERROR_SUCCESS then Exit;
  Result := ERROR_NOT_SUPPORTED;
  if LongInt(L) < Length(MemFlags) then Exit;
  if MemFlags[0] = $FF then Exit;
  if MemFlags[0] < 3 then Exit;

  if (MemFlags[2] and $02) = 0 then Exit;

  Result := ERROR_SUCCESS;
  Dev[DeviceIndex].bFirmware20 := True;
end;

function CheckPNPData(DeviceIndex: LongWord): LongWord;
var
  PNPSize: LongWord;

begin
  with Dev[DeviceIndex] do begin
    PNPData.PNPSize := 0;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    PNPSize := SizeOf(PNPData);
    Result := _Cy_GenericRead(DeviceIndex, $C0, $3F, 0, 0, PNPSize, @PNPData);
    if Result <> ERROR_SUCCESS then begin
      PNPData.PNPSize := 0;
      Exit;
    end;
    if PNPData.PNPSize = $FF then PNPData.PNPSize := 0;
  end;
end;

function bDevHasPNPByte(const PNPEntry): Boolean;
var
  I: Integer;

begin
  I := Cardinal(@PNPEntry) - Cardinal(@Dev[0]);
  I := I div SizeOf(Dev[0]);
  Result := Dev[I].PNPData.PNPSize > (Cardinal(@PNPEntry) - Cardinal(@Dev[I].PNPData));
end;

function CheckUSBSpeed(DeviceIndex: LongWord): TUSBSpeed;
var
  L, SpeedCode: LongWord;

begin
  with Dev[DeviceIndex] do begin
    Result := USBSpeed;
    if Result <> usUnknown then Exit;

    L := 0;
    SpeedCode := 0;
    if not DeviceIOControl(GetThreadHandleForDevice(DeviceIndex), IOCTL_ADAPT_GET_DEVICE_SPEED, @SpeedCode, SizeOf(SpeedCode), @SpeedCode, SizeOf(SpeedCode), L, nil) then Exit;
    if L <> SizeOf(SpeedCode) then Exit;

    case SpeedCode of
      $1: USBSpeed := usLowFull;
      $2: USBSpeed := usHigh;
      else Exit;
    end;
    Result := USBSpeed;
  end;
end;

function EnsureOpen(const DeviceIndex: LongWord): LongWord;
var
  Device: PDeviceData;
  DeviceInfo: USB_DEV_DSC;
  dwBytesReturned: LongWord;

begin
  Device := @Dev[DeviceIndex];

  if not Device.bGotHandle then begin
    if Device.bDeviceWasHere then
      Result := ERROR_DEVICE_REMOVED
    else
      Result := ERROR_FILE_NOT_FOUND
    ;
    Exit;
  end;

  if Device.bOpen then begin
    Result := ERROR_SUCCESS;
    Exit;
  end;

  Device.PID := $FFFFFFFF;
  case Device.USBDriverType of
    dtCyUSB2, dtCyUSB3: begin
      dwBytesReturned := SizeOf(DeviceInfo);
      Result := _Cy_GenericRead(DeviceIndex, $80, $06, $0100, $0000, dwBytesReturned, @DeviceInfo);
      if dwBytesReturned < SizeOf(DeviceInfo) then Result := ERROR_READ_FAULT;
      if Result <> ERROR_SUCCESS then Exit;
      Device.PID := DeviceInfo.idProduct;
    end;
    dtWinUSB: begin
      dwBytesReturned := 0;
      if WinUSB_GetDescriptor(GetThreadHandleForDevice(DeviceIndex), USB_DEVICE_DESCRIPTOR_TYPE, 0, $0409, @DeviceInfo, SizeOf(DeviceInfo), dwBytesReturned) then
        Device.PID := DeviceInfo.idProduct
      else begin
        Result := GetMappedFailure(DeviceIndex);
        Exit;
      end;
    end;
    else begin
      Device.PID := 0; //`@
    end;
  end;

  Device.DIOBytes := 0;
  Device.DIOConfigBits := 0;
  Device.Counters := 0;
  Device.RootClock := 0;
  Device.Tristates := 0;
  Device.bGetName := False;
  Device.ConfigBytes := 0;
  Device.bGateSelectable := False;
  Device.bDACBoardRange := False;
  Device.bDACChannelCal := False;
  Device.ImmDACs := 0;
  Device.ImmADCs := 0;
  Device.ImmADCPostScale := 1;
  Device.ADCChannels := 0;
  Device.ADCMUXChannels := 0;
  Device.ADCWorker := nil;
  Device.ADCContAcqWorker := nil;
  Device.ADCContBufWorker := nil;
  Device.pRingAcqData := nil;
  Device.bDACStream := False;
  Device.bDACDIOStream := False;
  Device.bDACSlowWaveStream := False;
  Device.bADCBulk := False;
  Device.bADCDIOStream := False;
  Device.RangeShift := 0;
  Device.bDIOStream := False;
  Device.StreamingBlockSize := 31*1024;
  Device.StreamingBlockSizeFloor := 0;
  Device.bDIODebounce := False;
  Device.bDIOSPI := False;
  Device.bClearFIFO := False;
  Device.FlashSectors := 0;
  Device.WDGBytes := 0;
  Device.bSetCustomClocks := False;
  Device.USBSpeed := usUnknown;

  case Device.PID of
    $8001: begin //USB-DIO-32
      Device.DIOBytes := 4;
      Device.Tristates := 1;
      Device.Counters := 3;
      Device.RootClock := 3000000;
      Device.bGetName := True;
      Device.bSetCustomClocks := True;
      Device.bDIODebounce := True;
    end;
    $8004: begin //USB-DIO-32I
      Device.DIOBytes := 4;
      Device.DIOConfigBits := 32;
      Device.Tristates := 1;
      Device.bGetName := True;
      Device.bSetCustomClocks := True;
    end;
    $8005: begin //USB-DIO-24
      Device.DIOBytes := 3;
      Device.DIOConfigBits := 4;
      Device.Tristates := 1;
      Device.bGetName := True;
      Device.bDIODebounce := True;
    end;
    $8006: begin //USB-DIO-24-CTR6
      Device.DIOBytes := 3;
      Device.DIOConfigBits := 4;
      Device.Tristates := 1;
      Device.Counters := 2;
      Device.RootClock := 10000000;
      Device.bGetName := True;
      Device.bSetCustomClocks := True;
      Device.bDIODebounce := True;
    end;
    $8002: begin //USB-DIO-48
      Device.DIOBytes := 6;
      Device.Tristates := 1;
      Device.bGetName := True;
    end;
    $8003: begin //USB-DIO-96
      Device.DIOBytes := 12;
      Device.Tristates := 1;
      Device.bGetName := True;
    end;
    $8008, $8009, $800A: begin //USB-DIO16A family, old revs
      Device.DIOBytes := 1;
      Device.bGetName := True;
      Device.bDIOStream := True;
      Device.bDIOSPI := True;
      Device.bClearFIFO := True;
    end;
    $800C, $800D, $800E, $800F: begin //USB-DIO16A family, current revs
      Device.DIOBytes := 4;
      Device.Tristates := 2;
      Device.bGetName := True;
      Device.bDIOStream := True;
      Device.bDIOSPI := True;
      Device.bClearFIFO := True;
      Device.bDACDIOStream := True;
      Device.ImmDACs := 1;
    end;
    $8068: begin //USB-AO-ARB1
      Device.DIOBytes := 2;
      Device.Tristates := 1;
      Device.bGetName := True;
      Device.bDIOStream := True;
      Device.bClearFIFO := True;
      Device.bDACDIOStream := True;
      Device.ImmDACs := 1;
    end;
    $8010, $8011, $8012, $8014, $8015, $8016, //USB-IIRO-16 family
    $8018,        $801A, $801C,        $801E, //USB-IDIO-16 family
    $8019, $801D, $801F: begin //USB-II-16-OEM family
      Device.DIOBytes := 4;
      Device.Tristates := 1;
      Device.bGetName := True;
      Device.WDGBytes := 2;
    end;
    $4001, $4002: begin //USB-DA12-8A
      Device.bGetName := False;
      Device.bDACStream := True;
      Device.ImmDACs := 8;
      Device.DACsUsed := 5;
      Device.bGetName := True;
    end;
    $4003: begin //USB-DA12-8E (no streaming)
      Device.bGetName := False;
      Device.ImmDACs := 8;
      Device.bGetName := True;
    end;
    $8020: begin //USB-CTR-15
      Device.Counters := 5;
      Device.bGateSelectable := True;
      Device.RootClock := 10000000;
      Device.bGetName := True;
    end;
    $8030, $8031: begin //USB-IIRO4-2SM, USB-IIRO4-COM
      Device.DIOBytes := 2;
      Device.Tristates := 1;
      Device.bGetName := True;
    end;
    $8032: begin //USBP-DIO16RO8
      Device.DIOBytes := 3;
      Device.Tristates := 1;
      Device.bGetName := True;
    end;
    $8033: begin //PICO-DIO16RO8
      Device.DIOBytes := 3;
      Device.Tristates := 1;
      Device.bGetName := True;
    end;
    $8036: begin //USBP-II8IDO4
      Device.DIOBytes := 2;
      Device.Tristates := 1;
      Device.bGetName := True;
      Device.ImmADCs := 2;
      Device.ImmADCPostScale := 4.096/5;
    end;
    $8037: begin //PICO-II8IDO4
      Device.DIOBytes := 2;
      Device.Tristates := 1;
      Device.bGetName := True;
      Device.ImmADCs := 2;
      Device.ImmADCPostScale := 4.096/5;
    end;
    $803C, $803D, $803E: begin //USB-DIO48DO24, USB-DIO24DO12, ACCES USB-DO24
      Device.DIOBytes := 9;
      Device.Tristates := 1;
      Device.bGetName := True;
    end;
    $8040..$8044, $805F, $8140..$8144, $815F: begin //USB-AI(O)16-16 and USB-AI(O)16-16F family
      Device.DIOBytes := 2;
      Device.Tristates := 1;
      Device.Counters := 1;
      Device.RootClock := 10000000;
      Device.bGetName := True;
      Device.bADCBulk := True;
      Device.ADCChannels := 16;
      Device.ADCMUXChannels := 16;
      Device.ConfigBytes := 20;
      Device.RangeShift := 0;
      Device.bClearFIFO := True;
      if (Device.PID and $0100) <> 0 then begin
        Device.bDACBoardRange := True;
        Device.ImmDACs := 4;
      end;
    end;
    $8045..$8049, $8145..$8149: begin //USB-AI(O)16-64M family
      Device.DIOBytes := 2;
      Device.Tristates := 1;
      Device.Counters := 1;
      Device.RootClock := 10000000;
      Device.bGetName := True;
      Device.bADCBulk := True;
      Device.ADCChannels := 16;
      Device.ADCMUXChannels := 64;
      Device.ConfigBytes := 21;
      Device.RangeShift := 2;
      Device.bClearFIFO := True;
      if (Device.PID and $0100) <> 0 then begin
        Device.bDACBoardRange := True;
        Device.ImmDACs := 4;
      end;
    end;
    $804A..$805E, $814A..$815E: begin //USB-AI(O)16-32+ family
      Device.DIOBytes := 2;
      Device.Tristates := 1;
      Device.Counters := 1;
      Device.RootClock := 10000000;
      Device.bGetName := True;
      Device.bADCBulk := True;
      Device.ADCChannels := 16;
      Device.ADCMUXChannels := 32 * ((((Device.PID - $804A) and not $0100) div 5) + 1);
      Device.ConfigBytes := 21;
      Device.RangeShift := 3;
      Device.bClearFIFO := True;
      if (Device.PID and $0100) <> 0 then begin
        Device.bDACBoardRange := True;
        Device.ImmDACs := 4;
      end;
    end;
    $8060, $8070..$807F: begin //USB-AO16-16A family
      Device.DIOBytes := 2;
      Device.Tristates := 1;
      Device.bGetName := True;
      Device.FlashSectors := 32;
      Device.bDACBoardRange := True;
      Device.bDACChannelCal := True;
      //Device.bClearFIFO := True;
      case Device.PID and $6 of
        $0: Device.ImmDACs := 16;
        $2: Device.ImmDACs := 12;
        $4: Device.ImmDACs := 8;
        $6: Device.ImmDACs := 4;
      end;
      if (Device.PID and 1) = 0 then Device.ImmADCs := 2;
      Device.bDACSlowWaveStream := True; //Add a new-style DAC streaming
      Device.DACsUsed := Device.ImmDACs;
    end;
    $8180: begin //USB-AI16-2A
      Device.DIOBytes := 2;
      Device.RootClock := 1000000;
      Device.bGetName := True;
      Device.bDIOStream := True;
      Device.bADCDIOStream := True;
      Device.ADCChannels := 2;
      Device.ADCMUXChannels := 2;
      Device.ConfigBytes := 2;
      Device.bClearFIFO := True;
    end;
    else begin
      //Device.bADCStream := True; Result := ERROR_SUCCESS;
      //Device.bDIOStream := True; Result := ERROR_SUCCESS;
      //Device.bDIOSPI := True; Result := ERROR_SUCCESS;
      Device.bGetName := False;
    end;
  end;
  if Device.DIOConfigBits = 0 then Device.DIOConfigBits := Device.DIOBytes;

  SetLength(Device.LastDIOData, Device.DIOBytes);

  if Device.bGetName then CheckPNPData(DeviceIndex);

  Device.bOpen := True;
  Result := ERROR_SUCCESS;
end;

function ValidateAndEnsureOpen(var DeviceIndex: LongWord): LongWord;
begin
  Result := Validate(DeviceIndex);
  if Result <> ERROR_SUCCESS then Exit;

  Result := EnsureOpen(DeviceIndex);
end;

function WriteGlobalTick(DeviceIndex: LongWord; pHz: PDouble): LongWord;
const
  CPUHz = 12000000;

var
  Hz, fDivisor: Double;
  Divisor: Word;

begin
  Hz := pHz^;
  if Hz = 0 then begin
    Divisor := $FFFF; //Will load 0 into the counter.
    pHz^ := 0;
  end
  else begin
    fDivisor := CPUHz / Hz;
    if fDivisor <= 0 then
      Divisor := 0
    else if fDivisor >= $FFFF then
      Divisor := $FFFF
    else
      Divisor := Round(fDivisor)
    ;
    pHz^ := CPUHz / Divisor;
  end;

  Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $FFFF - Divisor, $8001, 0, nil);
end;





function _GenericVendorRead(DeviceIndex: LongWord; Request: Byte; Value, Index: Word; var DataSize: LongWord; pData: Pointer): LongWord; cdecl;
var
  SetupData: TWinUSBSetupPacket;
  Buf: AnsiString;
  BytesReturned: LongWord;
  pCyTransfer: TPCyControlTransfer;

begin
  try
    SetString(Buf, PAnsiChar(pData), DataSize);
  except
    Result := ERROR_NOACCESS;
    Exit;
  end;

  case Dev[DeviceIndex].USBDriverType of
    dtCyUSB2, dtCyUSB3: begin
      Buf := StringOfChar(AnsiChar(#0), SizeOf(pCyTransfer^)) + Buf;
      pCyTransfer := Pointer(PAnsiChar(Buf));
      with pCyTransfer^ do begin
        SetupPacket.bRequestType := $C0;
        SetupPacket.bRequest := Request;
        SetupPacket.Value := Value;
        SetupPacket.Index := Index;
        SetupPacket.Len := DataSize;
        SetupPacket.ulTimeOut := CyBaseTimeout;
        ucEndpointAddress := 0; //EP0.
        BufferOffset := SizeOf(pCyTransfer^);
        BufferLength := SetupPacket.Len;
      end;
      BytesReturned := 0;
      if DeviceIoControl(GetThreadHandleForDevice(DeviceIndex), IOCTL_ADAPT_SEND_EP0_CONTROL_TRANSFER, PAnsiChar(Buf), Length(Buf), PAnsiChar(Buf), Length(Buf), BytesReturned, nil) then begin
        Result := ERROR_SUCCESS;
        BytesReturned := Min(BytesReturned, Length(Buf));
        if BytesReturned <= SizeOf(pCyTransfer^) then
          DataSize := 0
        else
          DataSize := BytesReturned - SizeOf(pCyTransfer^)
        ;
        try
          Move(Buf[1 + SizeOf(pCyTransfer^)], pData^, DataSize);
        except
          Result := ERROR_NOACCESS;
        end;
      end
      else begin
        Result := GetLastError;
        if Result = ERROR_SUCCESS then Result := ERROR_GEN_FAILURE;
        Buf := '';
      end;
    end;
    dtWinUSB: begin
      SetupData.RequestType := $C0;
      SetupData.Request := Request;
      SetupData.Value := Value;
      SetupData.Index := Index;
      SetupData.DataLength := DataSize;
      if WinUSB_ControlTransfer(GetThreadHandleForDevice(DeviceIndex), SetupData, PByte(PAnsiChar(Buf)), DataSize, BytesReturned, nil) then begin
        Result := ERROR_SUCCESS;
        DataSize := Min(BytesReturned, Length(Buf));
        try
          Move(Buf[1], pData^, DataSize);
        except
          Result := ERROR_NOACCESS;
        end;
      end
      else
        Result := GetMappedFailure(DeviceIndex)
      ;
    end;
    else begin
      Result := ERROR_NOT_SUPPORTED;
    end;
  end;
end;

function _GenericVendorWrite(DeviceIndex: LongWord; Request: Byte; Value, Index: Word; DataSize: LongWord; pData: Pointer): LongWord; cdecl;
var
  SetupData: TWinUSBSetupPacket;
  Buf: AnsiString;
  BytesReturned: LongWord;
  pCyTransfer: TPCyControlTransfer;

begin
  try
    SetString(Buf, PAnsiChar(pData), DataSize);
  except
    Result := ERROR_NOACCESS;
    Exit;
  end;

  case Dev[DeviceIndex].USBDriverType of
    dtCyUSB2, dtCyUSB3: begin
      Buf := StringOfChar(AnsiChar(#0), SizeOf(pCyTransfer^)) + Buf;
      pCyTransfer := Pointer(PAnsiChar(Buf));
      with pCyTransfer^ do begin
        SetupPacket.bRequestType := $40;
        SetupPacket.bRequest := Request;
        SetupPacket.Value := Value;
        SetupPacket.Index := Index;
        SetupPacket.Len := DataSize;
        SetupPacket.ulTimeOut := CyBaseTimeout;
        ucEndpointAddress := 0; //EP0.
        BufferOffset := SizeOf(pCyTransfer^);
        BufferLength := SetupPacket.Len;
      end;
      BytesReturned := 0;
      if DeviceIoControl(GetThreadHandleForDevice(DeviceIndex), IOCTL_ADAPT_SEND_EP0_CONTROL_TRANSFER, PAnsiChar(Buf), Length(Buf), PAnsiChar(Buf), Length(Buf), BytesReturned, nil) then
        Result := ERROR_SUCCESS
      else
        Result := GetMappedFailure(DeviceIndex)
      ;
    end;
    dtWinUSB: begin
      SetupData.RequestType := $40;
      SetupData.Request := Request;
      SetupData.Value := Value;
      SetupData.Index := Index;
      SetupData.DataLength := DataSize;
      if WinUSB_ControlTransfer(GetThreadHandleForDevice(DeviceIndex), SetupData, PByte(PAnsiChar(Buf)), DataSize, DataSize, nil) then
        Result := ERROR_SUCCESS
      else
        Result := GetMappedFailure(DeviceIndex)
      ;
    end;
    else begin
      Result := ERROR_NOT_SUPPORTED;
    end;
  end;
end;

function GenericVendorRead(DeviceIndex: LongWord; Request: Byte; Value, Index: Word; var DataSize: LongWord; pData: Pointer): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := _GenericVendorRead(DeviceIndex, Request, Value, Index, DataSize, pData);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function GenericVendorWrite(DeviceIndex: LongWord; Request: Byte; Value, Index: Word; DataSize: LongWord; pData: Pointer): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := _GenericVendorWrite(DeviceIndex, Request, Value, Index, DataSize, pData);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function _Cy_GenericRead(DeviceIndex: LongWord; RequestType, Request: Byte; Value, Index: Word; var DataSize: LongWord; pData: Pointer): LongWord; register;
var
  Buf: AnsiString;
  BytesReturned: LongWord;
  pCyTransfer: TPCyControlTransfer;

begin
  try
    SetString(Buf, PAnsiChar(pData), DataSize);
  except
    Result := ERROR_NOACCESS;
    Exit;
  end;

  Buf := StringOfChar(AnsiChar(#0), SizeOf(pCyTransfer^)) + Buf;
  pCyTransfer := Pointer(PAnsiChar(Buf));
  with pCyTransfer^ do begin
    SetupPacket.bRequestType := RequestType or $80;
    SetupPacket.bRequest := Request;
    SetupPacket.Value := Value;
    SetupPacket.Index := Index;
    SetupPacket.Len := DataSize;
    SetupPacket.ulTimeOut := CyBaseTimeout;
    ucEndpointAddress := 0; //EP0.
    IsoPacketLength := 0;
    BufferOffset := SizeOf(pCyTransfer^);
    BufferLength := SetupPacket.Len;
  end;
  BytesReturned := 0;
  if DeviceIoControl(GetThreadHandleForDevice(DeviceIndex), IOCTL_ADAPT_SEND_EP0_CONTROL_TRANSFER, PAnsiChar(Buf), Length(Buf), PAnsiChar(Buf), Length(Buf), BytesReturned, nil) then begin
    Result := ERROR_SUCCESS;
    BytesReturned := Min(BytesReturned, Length(Buf));
    if BytesReturned <= SizeOf(pCyTransfer^) then
      DataSize := 0
    else
      DataSize := BytesReturned - SizeOf(pCyTransfer^)
    ;
    try
      Move(Buf[1 + SizeOf(pCyTransfer^)], pData^, DataSize);
    except
      Result := ERROR_NOACCESS;
    end;
  end
  else begin
    Result := GetLastError;
    if Result = ERROR_SUCCESS then Result := ERROR_GEN_FAILURE;
    Buf := '';
  end;
end;

function _hCy_GenericVendorWriteStr(hDevice: THandle; Request: Byte; Value, Index: Word; Data: AnsiString): LongWord; cdecl;
var
  DataSize: LongWord;
  BytesReturned: LongWord;
  pCyTransfer: TPCyControlTransfer;

begin
  DataSize := Length(Data);
  Data := StringOfChar(AnsiChar(#0), SizeOf(pCyTransfer^)) + Data;
  pCyTransfer := Pointer(PAnsiChar(Data));
  with pCyTransfer^ do begin
    SetupPacket.bRequestType := $40;
    SetupPacket.bRequest := Request;
    SetupPacket.Value := Value;
    SetupPacket.Index := Index;
    SetupPacket.Len := DataSize;
    SetupPacket.ulTimeOut := CyBaseTimeout;
    ucEndpointAddress := 0; //EP0.
    BufferOffset := SizeOf(pCyTransfer^);
    BufferLength := SetupPacket.Len;
  end;
  BytesReturned := 0;
  if DeviceIoControl(hDevice, IOCTL_ADAPT_SEND_EP0_CONTROL_TRANSFER, PAnsiChar(Data), Length(Data), PAnsiChar(Data), Length(Data), BytesReturned, nil) then
    Result := ERROR_SUCCESS
  else begin
    Result := GetLastError;
    if Result = ERROR_SUCCESS then Result := ERROR_GEN_FAILURE;
  end;
end;

function _GenericBulk(DeviceIndex: LongWord; PipeID: LongWord; pData: Pointer; DataSize: LongWord; var BytesTransferred: LongWord): LongWord;
var
  CT: TCyBulkTransfer;
  WinUsb_TransferPipe: TWinUsb_TransferPipe;

begin
  case Dev[DeviceIndex].USBDriverType of
    dtCyUSB2, dtCyUSB3: begin
      FillChar(CT, SizeOf(CT), 0);
      CT.SetupPacket.ulTimeOut := CyBaseTimeout;
      CT.ucEndpointAddress := PipeID;
      if Dev[DeviceIndex].USBDriverType = dtCyUSB3 then begin
        CT.BufferOffset := 0;
        CT.BufferLength := DataSize;
      end;
      if DeviceIoControl(GetThreadHandleForDevice(DeviceIndex), IOCTL_ADAPT_SEND_NON_EP0_DIRECT, @CT, SizeOf(CT), pData, DataSize, BytesTransferred, nil) then begin
        Result := ERROR_SUCCESS;
        if BytesTransferred > DataSize then BytesTransferred := DataSize;
      end
      else
        Result := GetMappedFailure(DeviceIndex)
      ;
    end;
    dtWinUSB: begin
      if (PipeID and $80) <> 0 then
        WinUsb_TransferPipe := WinUsb_ReadPipe
      else
        WinUsb_TransferPipe := WinUsb_WritePipe
      ;
      SetLastError(ERROR_GEN_FAILURE);
      if WinUsb_TransferPipe(GetThreadHandleForDevice(DeviceIndex), PipeID, pData, DataSize, BytesTransferred, nil) then
        Result := ERROR_SUCCESS
      else
        Result := GetMappedFailure(DeviceIndex)
      ;
    end;
    else begin
      Result := ERROR_NOT_SUPPORTED;
    end;
  end;
end;

function AWU_GenericBulkIn(DeviceIndex: LongWord; PipeID: LongWord; pData: Pointer; DataSize: LongWord; var BytesRead: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    PipeID := PipeID or $80;
    Result := _GenericBulk(DeviceIndex, PipeID, pData, DataSize, BytesRead);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AWU_GenericBulkOut(DeviceIndex: LongWord; PipeID: LongWord; pData: Pointer; DataSize: LongWord; var BytesWritten: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    PipeID := PipeID and not $80;
    Result := _GenericBulk(DeviceIndex, PipeID, pData, DataSize, BytesWritten);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;



function GetDevices: LongWord; cdecl;
var
  I: Integer;

begin
  LoadDriverLinks;

  Result := 0;
  for I := 0 to High(Dev) do
    if EnsureOpen(I) = ERROR_SUCCESS then
      Result := Result or (1 shl I)
  ;
end;

function QueryDeviceInfo(DeviceIndex: LongWord; pPID: PLongWord; pNameSize: PLongWord; pName: PAnsiChar; pDIOBytes, pCounters: PLongWord): LongWord; cdecl;
var
  Content: AnsiString;
  wContent: WideString;
  DeviceInfo: USB_DEV_DSC;
  L, L2: LongWord;

begin
  try
    Result := Validate(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    if not Dev[DeviceIndex].bGotHandle then LoadDriverLinks;

    Result := EnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    if pPID      <> nil then pPID     ^ := Dev[DeviceIndex].PID     ;
    if pDIOBytes <> nil then pDIOBytes^ := Dev[DeviceIndex].DIOBytes;
    if pCounters <> nil then pCounters^ := Dev[DeviceIndex].Counters;
    if pNameSize <> nil then begin
      if not Dev[DeviceIndex].bGetName then begin //Old ASM firmwares do not support get-string
        pNameSize^ := 0;
      end
      else begin
        L := SizeOf(DeviceInfo);
        Result := GenericVendorRead(DeviceIndex, $06, $0100, 0, L, @DeviceInfo); //Cypress get-descriptor
        if Result <> ERROR_SUCCESS then Exit;

        if L < SizeOf(DeviceInfo) then begin
          Result := ERROR_HANDLE_EOF;
          Exit;
        end;

        if DeviceInfo.iProduct = 0 then
          DeviceInfo.iProduct := 2
        ;

        SetString(wContent, nil, pNameSize^ + 1);
        L := Length(wContent) * SizeOf(wContent[1]);
        Result := GenericVendorRead(DeviceIndex, $06, $0300 or DeviceInfo.iProduct, 0, L, PWChar(wContent)); //Cypress get-string
        if Result <> ERROR_SUCCESS then Exit;

        L2 := Byte(wContent[1]) div 2;
        if L2 <> 0 then begin
          Dec(L2);
          if pName <> nil then begin
            L := Min(pNameSize^, L2+1);
            wContent := Copy(wContent, 2, L2) + #0;
            Content := AnsiString(wContent);
            Move(Content[1], pName^, L);
          end;
        end;
        Result := ERROR_SUCCESS;
        pNameSize^ := L2;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ResolveDeviceIndex(DeviceIndex: LongWord): LongWord; cdecl;
begin
  try
    Result := Validate(DeviceIndex);
    SetLastError(Result);
    if Result = ERROR_SUCCESS then begin
      Result := DeviceIndex;
    end
    else begin
      Result := diNone;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ClearDevices: LongWord; cdecl;
var
  I: Integer;
  wContent: WideString;
  L: LongWord;
  ErrorCode: LongWord;

begin
  for I := High(Dev) downto 0 do begin
    if Dev[I].bGotHandle then begin
      if not Dev[I].bGetName then begin
        //Old ASM firmwares do not support get-string
      end
      else begin
        ErrorCode := EnsureOpen(I);
        if ErrorCode = ERROR_SUCCESS then begin
          SetString(wContent, nil, 257);
          L := Length(wContent) * SizeOf(wContent[1]);
          ErrorCode := GenericVendorRead(I, $06, $0302, 0, L, PWChar(wContent));

          if ErrorCode <> ERROR_SUCCESS then
            GetMappedFailure(I)
          ;
        end;
      end;
    end
    else begin
      Dev[I].bDeviceWasHere := False;
    end;
  end;
  Result := ERROR_SUCCESS;
end;

function GetDeviceBySerialNumber(const pSerialNumber: Int64): LongWord; cdecl;
var
  I: Integer;
  ThisSerialNumber: Int64;
  Status: LongWord;

begin
  for I := 0 to High(Dev) do begin
    Status := GetDeviceSerialNumber(I, ThisSerialNumber);
    if Status <> ERROR_SUCCESS then Continue;
    if ThisSerialNumber <> pSerialNumber then Continue;

    Result := I;
    Exit;
  end;

  Result := diNone;
end;

function GetDeviceByEEPROMByte(Data: Byte): LongWord; cdecl;
var
  ThisData: Byte;
  Status, ThisDataSize, MyLastError: LongWord;
  I: Integer;

begin
  try
    Result := diNone;
    MyLastError := ERROR_FILE_NOT_FOUND;

    for I := 0 to High(Dev) do begin
      ThisDataSize := 1;
      Status := CustomEEPROMRead(I, 0, ThisDataSize, @ThisData);
      if Status <> ERROR_SUCCESS then Continue;
      if ThisDataSize <> 1 then Continue;
      if ThisData <> Data then Continue;

      if Result = diNone then begin
        Result := I;
        MyLastError := ERROR_SUCCESS;
      end
      else begin
        MyLastError := ERROR_DUP_NAME;
      end;
    end;
    SetLastError(MyLastError);
  except
    Result := diNone;
    SetLastError(ERROR_INTERNAL_ERROR);
  end;
end;

function GetDeviceByEEPROMData(StartAddress, DataSize: LongWord; pData: PByte): LongWord; cdecl;
var
  ipData: PByte;
  ThisData: array of Byte;
  Status, ThisDataSize, MyLastError: LongWord;
  I, J: Integer;
  bMatch: Boolean;

begin
  try
    Result := diNone;
    MyLastError := ERROR_FILE_NOT_FOUND;

    if DataSize > $100 then begin
      SetLastError(ERROR_BAD_LENGTH);
      Exit;
    end;

    if DataSize = 0 then begin
      Result := ResolveDeviceIndex(diFirst);
      Exit;
    end;

    SetLength(ThisData, DataSize);
    for I := 0 to High(Dev) do begin
      ThisDataSize := DataSize;
      Status := CustomEEPROMRead(I, StartAddress, ThisDataSize, @ThisData[0]);
      if Status <> ERROR_SUCCESS then Continue;
      if ThisDataSize <> DataSize then Continue;

      bMatch := True;
      ipData := pData;
      for J := 0 to DataSize - 1 do begin
        if ThisData[J] <> ipData^ then begin
          bMatch := False;
          Break;
        end;
        Inc(ipData);
      end;
      if not bMatch then Continue;

      if Result = diNone then begin
        Result := I;
        MyLastError := ERROR_SUCCESS;
      end
      else begin
        MyLastError := ERROR_DUP_NAME;
      end;
    end;
    SetLastError(MyLastError);
  except
    Result := diNone;
    SetLastError(ERROR_INTERNAL_ERROR);
  end;
end;

function AIOUSB_ReloadDeviceLinks: LongWord; cdecl;
var
  I: Integer;

begin
  try
    Result := ERROR_SUCCESS;
    for I := 0 to High(Dev) do
      AIOUSB_CloseDevice(I)
    ;
    LoadDriverLinks;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;





function CustomEEPROMRead(DeviceIndex: LongWord; StartAddress: LongWord; var DataSize: LongWord; Data: Pointer): LongWord; cdecl;
begin
  if StartAddress > $FF then begin
    Result := ERROR_SEEK;
    Exit;
  end;
  if DataSize > (LongWord($100) - StartAddress) then begin
    Result := ERROR_BAD_LENGTH;
    Exit;
  end;

  Result := GenericVendorRead(DeviceIndex, $A2, $1E00 + StartAddress, 0, DataSize, Data);
end;

function CustomEEPROMWrite(DeviceIndex: LongWord; StartAddress: LongWord; DataSize: LongWord; Data: Pointer): LongWord; cdecl;
const
  BlockSize = 32;

begin
  try
    if StartAddress > $FF then begin
      Result := ERROR_SEEK;
      Exit;
    end;
    if DataSize > (LongWord($100) - StartAddress) then begin
      Result := ERROR_BAD_LENGTH;
      Exit;
    end;

    while DataSize > BlockSize do begin
      Result := GenericVendorWrite(DeviceIndex, $A2, $1E00 + StartAddress, 0, BlockSize, Data);
      if Result <> ERROR_SUCCESS then Exit;
      Inc(StartAddress, BlockSize);
      Dec(DataSize, BlockSize);
      Inc(PByte(Data), BlockSize);
    end;
    Result := GenericVendorWrite(DeviceIndex, $A2, $1E00 + StartAddress, 0, DataSize, Data);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_FlashRead(DeviceIndex: LongWord; StartAddress: LongWord; var DataSize: LongWord; Data: Pointer): LongWord; cdecl;
const
  BlockSize = 4096;

var
  ReadSize: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if FlashSectors = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if StartAddress >= $200000 then begin
        Result := ERROR_SEEK;
        Exit;
      end;
      if DataSize > (LongWord($200000) - StartAddress) then begin
        Result := ERROR_BAD_LENGTH;
        Exit;
      end;
      if (DataSize and 1) <> 0 then begin
        DataSize := DataSize and $FFFFFFFE;
      end;

      while DataSize > BlockSize do begin
        ReadSize := BlockSize;
        Result := GenericVendorRead(DeviceIndex, AUR_FLASH_READWRITE, StartAddress shr 1, StartAddress shr 17, ReadSize, Data);
        if Result <> ERROR_SUCCESS then Exit;
        Inc(StartAddress, ReadSize);
        Dec(DataSize, ReadSize);
        Inc(PByte(Data), ReadSize);
      end;
      Result := GenericVendorRead(DeviceIndex, AUR_FLASH_READWRITE, StartAddress shr 1, StartAddress shr 17, DataSize, Data);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_FlashWrite(DeviceIndex: LongWord; StartAddress: LongWord; DataSize: LongWord; Data: Pointer): LongWord; cdecl;
const
  BlockSize = 4096;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if FlashSectors = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if StartAddress >= $200000 then begin
        Result := ERROR_SEEK;
        Exit;
      end;
      if DataSize > (LongWord($200000) - StartAddress) then begin
        Result := ERROR_BAD_LENGTH;
        Exit;
      end;
      if (DataSize and 1) <> 0 then begin
        DataSize := DataSize and $FFFFFFFE;
      end;

      while DataSize > BlockSize do begin
        Result := GenericVendorWrite(DeviceIndex, AUR_FLASH_READWRITE, StartAddress shr 1, StartAddress shr 17, BlockSize, Data);
        if Result <> ERROR_SUCCESS then Exit;
        Inc(StartAddress, BlockSize);
        Dec(DataSize, BlockSize);
        Inc(PByte(Data), BlockSize);
      end;
      Result := GenericVendorWrite(DeviceIndex, AUR_FLASH_READWRITE, StartAddress shr 1, StartAddress shr 17, DataSize, Data);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_FlashEraseSector(DeviceIndex: LongWord; Sector: Integer): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if FlashSectors = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if Sector >= FlashSectors then begin
        Result := ERROR_SEEK;
        Exit;
      end;

      Result := GenericVendorWrite(DeviceIndex, AUR_DEBUG_FLASH_ERASE, 0, Sector, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function GetPipes(DeviceIndex: LongWord; var PipeCount: LongWord; pPipeData: PLongWord): LongWord; cdecl;
var
  bSuc: Boolean;
  InterfaceDescriptor: USB_INTERFACE_DESCRIPTOR;
  I, L: Integer;
  PipeInfo: WINUSB_PIPE_INFORMATION;
  pIPipeData: PLongWord;
  hDevice: THandle;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    case Dev[DeviceIndex].USBDriverType of
      dtCyUSB2, dtCyUSB3: begin
        Result := ERROR_NOT_SUPPORTED; //To generate the hint.
        Result := ERROR_NOT_SUPPORTED;
        Exit;
      end;
      dtWinUSB: begin
        hDevice := GetThreadHandleForDevice(DeviceIndex);
        SetLastError(ERROR_GEN_FAILURE);
        bSuc := WinUsb_QueryInterfaceSettings(hDevice, 0, @InterfaceDescriptor);
        if not bSuc then begin
          Result := GetMappedFailure(DeviceIndex);
          PipeCount := 0;
          Exit;
        end;

        if PipeCount < InterfaceDescriptor.bNumEndpoints then
          L := PipeCount
        else
          L := InterfaceDescriptor.bNumEndpoints
        ;
        PipeCount := InterfaceDescriptor.bNumEndpoints;

        pIPipeData := pPipeData;
        for I := 0 to L - 1 do begin
          pIPipeData^ := $FFFFFFFF;
          Inc(pIPipeData);
        end;

        pIPipeData := pPipeData;
        for I := 0 to L - 1 do begin
          bSuc := WinUsb_QueryPipe(hDevice, 0, I, @PipeInfo);
          if not bSuc then begin
            Result := GetMappedFailure(DeviceIndex);
            Exit;
          end;

          pIPipeData^ := PipeInfo.PipeId or (PipeInfo.PipeType shl 8);

          Inc(pIPipeData);
        end;
      end;
    end;

    Result := ERROR_SUCCESS;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function GetDeviceHandle(DeviceIndex: LongWord; pData: PHandle): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    pData^ := GetThreadHandleForDevice(DeviceIndex);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_UploadFirmware(DeviceIndex: LongWord; FirmBuf: PAnsiChar; BufLen: LongWord): LongWord; cdecl;
begin
  Result := ERROR_NOT_SUPPORTED;
end;

function StrToLines(S: AnsiString): TStringArray;
var
  Count, Capacity, iC, oC,
  L: Integer;

begin
  Count := 0;
  Capacity := 8;
  SetLength(Result, Capacity);
  S := S + #13;
  L := Length(S);
  iC := 1;
  oC := 1;
  while iC <= L do begin
    if (S[iC] = #13) or (S[iC] = #10) then begin
      if Count >= Capacity then begin
        Capacity := Capacity * 2;
        SetLength(Result, Capacity);
      end;
      Result[Count] := Copy(S, oC, iC - oC);
      Inc(Count);

      if (iC < L) and (S[iC] = #13) and (S[iC+1] = #10) then Inc(iC);
      oC := iC+1;
    end;
    Inc(iC);
  end;
  SetLength(Result, Count);
end;

function AIOUSB_UploadD15LoFirmwaresByPID(pFirmScript: PAnsiChar): LongWord; cdecl;
type
  THexChunk = record
    Addr: Word;
    Data: AnsiString;
  end;
  THexChunks = array of THexChunk;

  TPIDFirmData = record
    PID: Word;
    FirmContent: THexChunks;
  end;

  function ParseHex(HexStrs: TStringArray): THexChunks;
  var
    iLine, iChunk: Integer;
    ThisAddr, ThisData: AnsiString;

  begin
    //Validate hex file.
    SetLength(Result, 0);
    for iLine := 0 to High(HexStrs) do begin
      ThisData := HexStrs[iLine];
      if ThisData = '' then Continue;
      if ThisData[1] <> ':' then Exit;
      if not IsHex(Copy(ThisData, 2, MAXINT)) then Exit;
      if (Length(ThisData) and 1) = 0 then Exit; //If source line is even(has colon plus odd nybbles), reject as invalid.
    end;

    SetLength(Result, Length(HexStrs));
    iChunk := 0;
    for iLine := 0 to High(HexStrs) do begin
      ThisData := HexStrs[iLine];
      if ThisData = '' then Continue;
      if Copy(ThisData, 8, 2) <> '00' then Continue; //We only care about type 00 records.

      ThisAddr := Copy(ThisData, 4, 4);
      ThisData := Copy(ThisData, 10, Length(ThisData) - 11);

      Result[iChunk].Addr := HexToInt(ThisAddr);
      Result[iChunk].Data := HexToStr(ThisData);
      Inc(iChunk);
    end;
    SetLength(Result, iChunk);
  end;

var
  PFD: array of TPIDFirmData; //Loading the script would be a bit faster with pointers, but that's not much of an improvement, so safety is more important.
  iPF, iLine, iPath, iFirmware,
  I: Integer;
  ThisLine, PIDStr, FirmStr: AnsiString;
  DevicePath, FirmScript: TStringArray;
  FirmHex: THexChunks;
  hCyFile: THandle;
  Status: LongWord;
  ThisPID: Word;

begin
  try
    Result := 0;
    try
      FirmScript := StrToLines(pFirmScript);
      iPF := -1;
      for iLine := 0 to High(FirmScript) do begin
        ThisLine := FirmScript[iLine];
        if ThisLine = '' then Continue;
        if ThisLine[1] = ';' then Continue;

        SplitStr(ThisLine, '=', PIDStr, FirmStr);
        if PIDStr = '' then Continue;
        if FirmStr = '' then Continue;
        if not IsHex(PIDStr) then Continue;
        if not FileExists(String(FirmStr)) then Continue;

        try
          FirmStr := DumpFileToString(FirmStr);
          FirmStr := AnsiString(UpperCase(Trim(String(FirmStr))));
          FirmHex := ParseHex(StrToLines(FirmStr));
          if Length(FirmHex) = 0 then Continue;
        except
          Continue;
        end;

        Inc(iPF);
        SetLength(PFD, iPF+1);
        with PFD[iPF] do begin
          PID := HexToInt(PIDStr) and $7FFF;
          FirmContent := FirmHex;
        end;
      end;

      DevicePath := GetDevicePaths(D15LoClassGUID);
      for iPath := 0 to High(DevicePath) do begin
        ThisLine := DevicePath[iPath];

        I := Pos('PID_', UpperCase(String(ThisLine)));
        if I = 0 then Continue;
        PIDStr := Copy(ThisLine, I + 4, 4);
        {$IFDEF Debug}
          if not IsHex(PIDStr) then AnsiMessageBox('Device PID ' + PIDStr + ' not hex!', 'AIOUSB_UploadD15LoFirmwaresByPID', MB_ICONEXCLAMATION);
        {$ENDIF}
        if not IsHex(PIDStr) then Continue;
        ThisPID := HexToInt(PIDStr) and $7FFF;
        iFirmware := High(PFD);
        while (iFirmware >= 0) and (PFD[iFirmware].PID <> ThisPID) do Dec(iFirmware);
        {$IFDEF Debug}
          if iFirmware < 0 then AnsiMessageBox('Device PID ' + AnsiString(IntToHex(ThisPID, 4)) + ' not recognized!', 'AIOUSB_UploadD15LoFirmwaresByPID', MB_ICONEXCLAMATION);
        {$ENDIF}
        if iFirmware < 0 then Continue; //PID not recognized, don't bother.

        hCyFile := CreateFileA(PAnsiChar(ThisLine), GENERIC_WRITE or GENERIC_READ, FILE_SHARE_WRITE or FILE_SHARE_READ, nil, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, 0);
        ThisLine := '';
        if hCyFile = INVALID_HANDLE_VALUE then hCyFile := 0;
        {$IFDEF Debug}
          if hCyFile = 0 then AnsiMessageBox('Unable to open CyUSB device!', 'AIOUSB_UploadD15LoFirmwaresByPID', MB_ICONEXCLAMATION);
        {$ENDIF}
        if hCyFile = 0 then Continue;

        //Transfer the hex file.

        //Put CPU into reset.
        Status := _hCy_GenericVendorWriteStr(hCyFile, $A0, $E600, 0, #$01);
        if Status = ERROR_SUCCESS then begin
          //Transfer each line.
          for iLine := 0 to High(PFD[iFirmware].FirmContent) do
            with PFD[iFirmware].FirmContent[iLine] do
              _hCy_GenericVendorWriteStr(hCyFile, $A0, Addr, 0, Data)
          ;
          //take CPU out of reset.
          _hCy_GenericVendorWriteStr(hCyFile, $A0, $E600, 0, #$00);
          Inc(Result);
        end
        else begin
          {$IFDEF Debug}
            AnsiMessageBox('Error ' + AnsiString(IntToStr(Status)) + ' putting CPU into reset!', 'AIOUSB_UploadD15LoFirmwaresByPID', MB_ICONEXCLAMATION);
          {$ENDIF}
        end;

        CloseHandle(hCyFile);
      end;
      SetLastError(ERROR_SUCCESS);
    except
      SetLastError(ERROR_INTERNAL_ERROR);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DEB_BufTest(DeviceIndex: LongWord; VR: Byte; VI: LongWord; pData: PByte; DataSize: LongWord): LongWord; cdecl;
var
  Data: AnsiString;

begin
  try
    LoadCyUSBLinks(D15LoClassGUID);

    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not (USBDriverType in [dtCyUSB2, dtCyUSB3]) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      try
        SetString(Data, PAnsiChar(pData), DataSize);
      except
        Result := ERROR_NOACCESS;
        Exit;
      end;

      Result := ERROR_NOT_SUPPORTED;
      //Result := _GenericVendorWrite(DeviceIndex, VR, VI, VI shr 16, DataSize, pData);
      //Result := _hCy_GenericVendorWriteStr(GetThreadHandleForDevice(DeviceIndex), VR, VI, VI shr 16, Data);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function GetDeviceSerialNumber(DeviceIndex: LongWord; var pSerialNumber: Int64): LongWord; cdecl;
var
  L: LongWord;
  Content: Int64;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    L := SizeOf(Content);
    Result := GenericVendorRead(DeviceIndex, $A2, $1DF8, 0, L, @Content);

    if (Result = ERROR_SUCCESS) and (L = SizeOf(Content)) then begin
      if Content = 0 then Content := -1;
      pSerialNumber := Content;
      if Content = -1 then Result := ERROR_NOT_SUPPORTED;
    end
    else begin
      Result := GetMappedFailure(DeviceIndex);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function GetDeviceUniqueStr(DeviceIndex: LongWord; pIIDSize: PLongWord; pIID: PAnsiChar): LongWord; cdecl;
var
  Content: Int64;

begin
  try
    Result := GetDeviceSerialNumber(DeviceIndex, Content);
    if Result <> ERROR_SUCCESS then Exit;

    Move(Content, pIID^, Min(SizeOf(Content), pIIDSize^));
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function OctDacFromFreq(var ClockHz: Double): Word;
var
  Octave, Offset: Integer;

begin
  if ClockHz = 0 then begin
    Result := 0;
    Exit;
  end;
  if ClockHz > 40000000 then ClockHz := 40000000;
  //if ClockHz > 66000000 then ClockHz := 66000000;
  Octave := Floor(3.322 * Log10(ClockHz / 1039));
  if Octave < 0 then begin //Don't bother with upper limit, we already covered it and then some above.
    Octave := 0;
    Offset := 0;
    Result := $0000;
  end
  else begin
    Offset := Round(2048 - (LDExp(2078, 10 + Octave)/ClockHz)); //Don't bother with limits, we covered that when calculating the octave.
    Result := (Octave shl 12) or (Offset shl 2);
    Result := MotorolaWord(Result);
  end;
  ClockHz := (2078 shl Octave) / (2 - Offset / 1024);
end;





function DACDirect(DeviceIndex: LongWord; Channel: Word; Value: Word): LongWord; cdecl;
var
  DACStreamData: LongWord;
  ClockHz: Double;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin

      if ImmDACs = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if (bDACStream or bDACDIOStream or bDACSlowWaveStream) and (bDACOpen or bDACClosing) then begin
        Result := ERROR_TOO_MANY_OPEN_FILES;
        Exit;
      end;

      if Channel >= ImmDACs then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      if bDACDIOStream then begin
        DACStreamData := Value * $00010001;
        ClockHz := DACDIOStreamImmHz;
        Result := DACOutputProcess(DeviceIndex, ClockHz, 2, @DACStreamData);
      end
      else begin
        Result := GenericVendorWrite(DeviceIndex, AUR_DAC_IMMEDIATE, Value, Channel, 0, nil);
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACMultiDirect(DeviceIndex: LongWord; pDACData: PDACEntry; DACDataCount: LongWord): LongWord; cdecl;
var
  Content: AnsiString;
  pDE: PDACEntry;
  pDB, pMB: PByte;
  I, J: Integer;
  L: LongWord;
  DACStreamData: LongWord;
  ClockHz: Double;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if ImmDACs = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if (bDACStream or bDACDIOStream or bDACSlowWaveStream) and (bDACOpen or bDACClosing) then begin
        Result := ERROR_TOO_MANY_OPEN_FILES;
        Exit;
      end;

      if DACDataCount = 0 then Exit; //If length is zero, it's a nop

      pDE := pDACData;
      L := 0;
      for I := 0 to DACDataCount - 1 do begin
        if pDE.Channel > L then L := pDE.Channel;
        Inc(pDE);
      end;
      //L is now highest channel

      if L >= ImmDACs then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      if bDACDIOStream then begin
        pDE := pDACData;
        Inc(pDE, DACDataCount - 1);
        DACStreamData := pDE.Value * $00010001;
        ClockHz := DACDIOStreamImmHz;
        Result := DACOutputProcess(DeviceIndex, ClockHz, 2, @DACStreamData);
      end
      else begin
        L := (L div 8) + 1; //Number of blocks of 8 DACs

        Content := StringOfChar(AnsiChar(#0), L * 17);

        pDB := PByte(PAnsiChar(Content));
        pDE := pDACData;
        for I := 0 to DACDataCount - 1 do begin
          J := pDE.Channel;
          pMB := pDB;
          Inc(pMB, J * 2 + (J div 8) + 1);
          PWord(pMB)^ := pDE.Value;

          pMB := pDB;
          Inc(pMB, (J div 8) * 17);
          pMB^ := pMB^ or (1 shl (J and 7));

          Inc(pDE);
        end;

        Result := GenericVendorWrite(DeviceIndex, AUR_DAC_IMMEDIATE, 0, 0, Length(Content), PAnsiChar(Content));
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACSetBoardRange(DeviceIndex: LongWord; RangeCode: LongWord): LongWord; cdecl;
var
  ConfigData: array[0..1] of Byte;
  DataSize: LongWord;
  DACData: Word;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    if Dev[DeviceIndex].bDACDIOStream then begin
      //Read the jumper.
      DataSize := 2;
      Result := GenericVendorRead(DeviceIndex, $B7, 0, 0, DataSize, @ConfigData[0]);
      if Result <> ERROR_SUCCESS then Exit;

      if ConfigData[0] >= 2 then begin
        if ConfigData[1] <> 0 then
          DACData := $8000 //Bipolar counts for zero volts.
        else
          DACData := $0000 //Unipolar counts for zero volts.
        ;
        Result := DACDirect(DeviceIndex, 0, DACData);
        if Result <> ERROR_SUCCESS then Exit;
      end;

      //Enable the reference.
      Result := GenericVendorWrite(DeviceIndex, $B7, 0, 0, 0, nil);
      Exit;
    end;

    if not Dev[DeviceIndex].bDACBoardRange then begin
      //`@ If the board has channel range, then channel range in a loop.
      Result := ERROR_BAD_TOKEN_TYPE;
      Exit;
    end;

    Result := GenericVendorWrite(DeviceIndex, AUR_DAC_RANGE, RangeCode, 0, 0, nil);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function StringReplaceC(const S: AnsiString; const OldChar, NewChar: AnsiChar): AnsiString;
var
  I: Integer;

begin
  Result := S;
  for I := 1 to Length(Result) do
    if Result[I] = OldChar then
      Result[I] := NewChar
  ;
end;

function DACSetChannelCal(DeviceIndex: LongWord; Channel: LongWord; CalFileName: PAnsiChar): LongWord; cdecl;
var
  CalTable: array of Word;
  Suc: Boolean;
  L, L2: LongWord;
  hFil: THandle;
  InterBuf: AnsiString;
  I, J, K: Integer;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if (FlashSectors = 0) or not bDACChannelCal then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if Channel >= ImmDACs then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      if (CalFileName = ':1TO1:') or (CalFileName = ':NONE:') then begin
        Result := AIOUSB_FlashEraseSector(DeviceIndex, Channel * 2);
        if Result <> ERROR_SUCCESS then Exit;
        Result := AIOUSB_FlashEraseSector(DeviceIndex, Channel * 2 + 1);
        if Result <> ERROR_SUCCESS then Exit;

        Result := GenericVendorWrite(DeviceIndex, AUR_DEBUG_FLASH_1TO1, 0, Channel, 0, nil);
      end
      else begin

        hFil := CreateFileA(CalFileName, GENERIC_READ, FILE_SHARE_READ or FILE_SHARE_WRITE, nil, OPEN_EXISTING, 0, 0);
        if (hFil = 0) or (hFil = INVALID_HANDLE_VALUE) then begin
          Result := GetLastError;
          if Result = ERROR_SUCCESS then Result := ERROR_GEN_FAILURE;
          Exit;
        end;
        L := GetFileSize(hFil, nil);
        Result := GetLastError;
        if Result <> ERROR_SUCCESS then begin
          CloseHandle(hFil);
          Exit;
        end;
        L := Min(L, $08000000); //Cap for RAM reasons. Even a 0x-based file should be $80000 bytes.
        try
          SetString(InterBuf, nil, L + 1);
          InterBuf[L + 1] := #13; //Terminate for the read-out logic.
        except
          CloseHandle(hFil);
          Result := ERROR_OUTOFMEMORY;
          Exit;
        end;
        Suc := ReadFile(hFil, InterBuf[1], L, L2, nil);
        Result := GetLastError;
        if (Result = ERROR_SUCCESS) and not Suc then Result := ERROR_GEN_FAILURE;
        if (Result = ERROR_SUCCESS) and (L2 < L) then begin
          Result := GetLastError;
          if Result = ERROR_SUCCESS then Result := ERROR_GEN_FAILURE;
        end;
        CloseHandle(hFil);
        if Result <> ERROR_SUCCESS then Exit;

        SetLength(CalTable, $10000);
        try
          InterBuf := StringReplaceC(InterBuf, #10, #13);
          J := 1;
          for I := 0 to High(CalTable) do begin
            repeat
              K := InStrC(#13, InterBuf, J);
              if K = 0 then begin
                Result := ERROR_HANDLE_EOF;
                SetLength(CalTable, 0);
                Exit;
              end
              else if K = J then begin
                Inc(J);
              end
              else begin
  {$IFDEF VER130}  // Delphi 5
                CalTable[I] := StrToInt(Trim(Copy(InterBuf, J, K - J)));
  {$ELSE}
                CalTable[I] := StrToInt(Trim(UnicodeString(Copy(InterBuf, J, K - J))));
  {$ENDIF}

                J := K + 1;
                Break;
              end;
            until False;
          end;
        except
          SetLength(CalTable, 0);
          Result := ERROR_INVALID_DATA;
          Exit;
        end;

        Result := AIOUSB_FlashEraseSector(DeviceIndex, Channel * 2);
        if Result <> ERROR_SUCCESS then Exit;
        Result := AIOUSB_FlashEraseSector(DeviceIndex, Channel * 2 + 1);
        if Result <> ERROR_SUCCESS then Exit;

        Result := AIOUSB_FlashWrite(DeviceIndex, Channel * $20000, Length(CalTable) * SizeOf(CalTable[0]), @CalTable[0]);
        SetLength(CalTable, 0);

      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;



function DACOutputOpen(DeviceIndex: LongWord; var ClockHz: Double): LongWord; cdecl;
var
  DCD: TDIO16ClockData;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin

      if not (bDACStream or bDACDIOStream or bDACSlowWaveStream) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if bDACOpen or bDACClosing then begin
        Result := ERROR_TOO_MANY_OPEN_FILES;
        Exit;
      end;

      if bDACDIOStream then begin
        if bDACOpen or bDACClosing or bDIOOpen then begin
          Result := ERROR_TOO_MANY_OPEN_FILES;
          Exit;
        end;

        Result := DIO_StreamOpen(DeviceIndex, False);
        if Result <> ERROR_SUCCESS then Exit;

        DCD.Disables := $00;
        DCD.WriteOctDac := OctDacFromFreq(ClockHz);
        DCD.ReadOctDac := $0000;
        Result := GenericVendorWrite(DeviceIndex, AUR_DIO_SETCLOCKS, 0, 0, SizeOf(DCD), @DCD);
        if Result <> ERROR_SUCCESS then begin
          DIO_StreamClose(DeviceIndex);
          Exit;
        end;

        bDACOpen := True;
      end
      else if bDACSlowWaveStream then begin
        Result := GenericVendorWrite(DeviceIndex, $C7, $01, 0, 0, nil);
        if Result <> ERROR_SUCCESS then Exit;

        Result := WriteGlobalTick(DeviceIndex, @ClockHz);
        if Result <> ERROR_SUCCESS then Exit;

        bDACOpen := True;
      end
      else begin
        //DoSetIFace(Handle, $100);

        Result := GenericVendorWrite(DeviceIndex, AUR_DAC_CONTROL, $80, 0, 0, nil); //Reset
        if Result <> ERROR_SUCCESS then Exit;

        Result := GenericVendorWrite(DeviceIndex, AUR_DAC_DATAPTR, $00, 0, 0, nil); //DataPtr << 0
        if Result <> ERROR_SUCCESS then Exit;

        CtrDivisor := Round(12000000 / ClockHz);
        ClockHz := 12000000 / CtrDivisor;

        Result := GenericVendorWrite(DeviceIndex, AUR_DAC_DIVISOR, 0, CtrDivisor, 0, nil); //Set divisor
        if Result <> ERROR_SUCCESS then Exit;

        hDACDataMutex := CreateMutex(nil, False, nil);
        hDACDataSem := CreateSemaphore(nil, 0, $FFFF, nil);

        WorkerThread := TDACWorker.Create(True);
        WorkerThread.FreeOnTerminate := False;
        WorkerThread.Index := DeviceIndex;
        WorkerThread.Start;
      end;

      bDACOpen := True;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACOutputAbort(DeviceIndex: LongWord): LongWord; cdecl;
begin
  Result := ERROR_NOT_SUPPORTED; //To generate the hint.
  Result := ERROR_NOT_SUPPORTED; //`@
end;

function DACOutputClose(DeviceIndex: LongWord; bWait: LongBool): LongWord; cdecl;
var
  L, L2, Releases: Integer;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not (bDACStream or bDACDIOStream or bDACSlowWaveStream) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bDACOpen then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      if bDACDIOStream then begin
        Result := DIO_StreamClose(DeviceIndex);
        if Result <> ERROR_SUCCESS then Exit;

        bDACOpen := False;
      end
      else if bDACSlowWaveStream then begin
        Result := ERROR_SUCCESS; //`@
        Result := ERROR_SUCCESS;

        bDACOpen := False;
      end
      else begin
        bDACOpen := False;

        //Flush pending data to worker buffer, adding EOM($8000), and release semaphore one extra time.
        WaitForSingleObject(hDACDataMutex, INFINITE);
          L := Length(DACData);
          if L = 0 then begin
            SetLength(DACData, 1);
            L2 := Length(PendingDACData);
            if L2 <> 0 then begin //No buffered buffers but we have pending data, so we'll buffer and use that.
              PendingDACData[L2] := AnsiChar(Byte(PendingDACData[L2]) or $80);
              DACData[0] := PendingDACData;
              Releases := 2;
            end
            else begin //No buffered buffers and no pending data, so buffer a little buffer so we can add EOM.
              DACData[0] := #$00#$E0; //`@
              Releases := 2;
            end;
          end
          else begin
            L2 := Length(PendingDACData);
            if L2 <> 0 then begin //Some buffered buffers, but we have pending data, so we'll buffer and use the pending data.
              SetLength(DACDAta, L + 1);
              PendingDACData[L2] := AnsiChar(Byte(PendingDACData[L2]) or $80);
              DACData[L] := PendingDACData;
              Releases := 2;
            end
            else begin //Some buffered buffers and no pending data, so we'll use the last buffer.
              Dec(L);
              L2 := Length(DACData[L]);
              DACData[L][L2] := AnsiChar(Byte(DACData[L][L2]) or $80);
              Releases := 1;
            end;
          end;
        ReleaseMutex(hDACDataMutex);
        PendingDACData := '';

        bDACClosing := True;
        ReleaseSemaphore(hDACDataSem, Releases, nil);
        {
        while WaitForSingleObject(hDACDataSem, 0) <> WAIT_TIMEOUT do
          ReleaseSemaphore(hDACDataSem, 1, nil)
        ;
        }

        {
        if bWait then begin
          //Once worker thread has drained its buffer, it checks bDACOpen, and if false it closes and reports back to us.
          //`@
        end;
        }

        WorkerThread.Terminate;
        WorkerThread.Free;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACOutputCloseNoEnd(DeviceIndex: LongWord; bWait: LongBool): LongWord; cdecl;
var
  L, L2, Releases: Integer;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not (bDACStream or bDACDIOStream or bDACSlowWaveStream) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bDACOpen then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      if bDACDIOStream then begin
        Result := DIO_StreamClose(DeviceIndex);
        if Result <> ERROR_SUCCESS then Exit;

        bDACOpen := False;
      end
      else if bDACSlowWaveStream then begin
        Result := ERROR_SUCCESS; //`@
        Result := ERROR_SUCCESS;

        bDACOpen := False;
      end
      else begin
        bDACOpen := False;

        //Flush pending data to worker buffer, and release semaphore one extra time.
        WaitForSingleObject(hDACDataMutex, INFINITE);
          L2 := Length(PendingDACData);
          if L2 <> 0 then begin
            L := Length(DACData);
            SetLength(DACDAta, L + 1);
            DACData[L] := PendingDACData;
            Releases := 2;
          end
          else begin //No pending data, so just release the semaphore to signal end.
            Releases := 1;
          end;
        ReleaseMutex(hDACDataMutex);
        PendingDACData := '';

        bDACClosing := True;
        ReleaseSemaphore(hDACDataSem, Releases, nil);

        {
        if bWait then begin
          //Once worker thread has drained its buffer, it checks bDACOpen, and if false it closes and reports back to us.
          //`@
        end;
        }

        WorkerThread.Terminate;
        WorkerThread.Free;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACOutputSetCount(DeviceIndex, NewCount: LongWord): LongWord; cdecl;
var
  MaxCount: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not (bDACStream or bDACDIOStream or bDACSlowWaveStream) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bDACOpen then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      if NewCount = 0 then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      if bDACDIOStream then //`@ Move to TDeviceData as StreamDACs or something.
        MaxCount := 1
      else if bDACSlowWaveStream then
        MaxCount := ImmDACs
      else
        MaxCount := 8
      ;
      if NewCount > MaxCount then begin
        Result := ERROR_OUTOFMEMORY;
        Exit;
      end;

      DACsUsed := NewCount;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACOutputFrame(DeviceIndex, FramePoints: LongWord; FrameData: PWord): LongWord; cdecl;
const
  FrameBufferSize = 8192; //Bytes per buffer, bloody ass band-aid.

var
  I, L, Ch: Integer;
  FrameSamples, FrameBytes, FrameBuffers: Integer;
  NewDACData: TDACData;
  pSample: PWord;
  pBuffer: PAnsiChar;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bDACDIOStream or bDACSlowWaveStream then begin
        Result := DACOutputFrameRaw(DeviceIndex, FramePoints, FrameData); //There are no non-raw control bits to manipulate.
        Exit;
      end;

      if not bDACStream then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bDACOpen then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      if FramePoints <= 0 then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      if FramePoints > 6400 then begin
        Result := ERROR_OUTOFMEMORY;
        Exit;
      end;

      WaitForSingleObject(hDACDataMutex, INFINITE);
        L := Length(DACData);
      ReleaseMutex(hDACDataMutex);

      if L > 32 then begin
        Result := ERROR_NOT_READY;
        Exit;
      end;

      try
        FrameSamples := Integer(FramePoints) * DACsUsed;
        SetString(NewDACData, PAnsiChar(FrameData), FrameSamples * SizeOf(Word));
      except
        Result := ERROR_NOACCESS;
        Exit;
      end;

      pSample := PWord(PAnsiChar(NewDACData));
      Ch := 0;
      for I := 0 to FrameSamples - 1 do begin
        pSample^ := pSample^ and $0FFF;
        Inc(Ch);
        if Ch = DACsUsed then begin
          pSample^ := pSample^ or $2000;
          Ch := 0;
        end;
        Inc(pSample);
      end;
      Dec(pSample);
      pSample^ := pSample^ or $4000;

      NewDACData := PendingDACData + NewDACData;
      FrameBytes := Length(NewDACData);
      FrameBuffers := FrameBytes div FrameBufferSize;
      pBuffer := PAnsiChar(NewDACData);

      WaitForSingleObject(hDACDataMutex, INFINITE);
        L := Length(DACData);
        SetLength(DACData, L + FrameBuffers);
        for I := 0 to FrameBuffers - 1 do begin
          SetString(DACData[L + I], pBuffer, FrameBufferSize);
          Inc(pBuffer, FrameBufferSize);
        end;
      ReleaseMutex(hDACDataMutex);
      ReleaseSemaphore(hDACDataSem, FrameBuffers, nil);

      FrameBytes := FrameBytes mod FrameBufferSize;
      if FrameBytes <> 0 then
        SetString(PendingDACData, pBuffer, FrameBytes)
      else
        PendingDACData := ''
      ;

      NewDACData := '';
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACOutputFrameRaw(DeviceIndex, FramePoints: LongWord; FrameData: PWord): LongWord; cdecl;
const
  FrameBufferSize = 8192; //Bytes per buffer, bloody ass band-aid.

var
  I, L: Integer;
  FrameSamples, FrameBytes, FrameBuffers: Integer;
  NewDACData: TDACData;
  pBuffer: PAnsiChar;
  BytesPerPoint, BytesTransferred, WordsTransferred: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not (bDACStream or bDACDIOStream or bDACSlowWaveStream) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bDACOpen then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      if FramePoints <= 0 then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      if bDACDIOStream then begin
        repeat
          BytesTransferred := 0;
          Result := DIO_StreamFrame(DeviceIndex, FramePoints, FrameData, BytesTransferred);
          if Result <> ERROR_SUCCESS then begin
            DIO_StreamClose(DeviceIndex); //`@ Why?
            Exit;
          end;

          WordsTransferred := BytesTransferred div 2;
          if WordsTransferred >= FramePoints then Break;

          Inc(FrameData, WordsTransferred);
          Dec(FramePoints, WordsTransferred);
        until False;
      end
      else if bDACSlowWaveStream then begin
        BytesPerPoint := 2 * DACsUsed;
        repeat
          BytesTransferred := 0;
          Result := AWU_GenericBulkOut(DeviceIndex, $06, FrameData, FramePoints*BytesPerPoint, BytesTransferred);
          if Result <> ERROR_SUCCESS then Break;

          WordsTransferred := BytesTransferred div 2;
          if WordsTransferred >= FramePoints then Break;

          Inc(FrameData, WordsTransferred);
          Dec(FramePoints, WordsTransferred);
        until False;
      end
      else begin
        if FramePoints > 6400 then begin
          Result := ERROR_OUTOFMEMORY;
          Exit;
        end;

        WaitForSingleObject(hDACDataMutex, INFINITE);
          L := Length(DACData);
        ReleaseMutex(hDACDataMutex);

        if L > 32 then begin
          Result := ERROR_NOT_READY;
          Exit;
        end;

        try
          FrameSamples := Integer(FramePoints) * DACsUsed;
          SetString(NewDACData, PAnsiChar(FrameData), FrameSamples * SizeOf(Word));
        except
          Result := ERROR_NOACCESS;
          Exit;
        end;

        NewDACData := PendingDACData + NewDACData;
        FrameBytes := Length(NewDACData);
        FrameBuffers := FrameBytes div FrameBufferSize;
        pBuffer := PAnsiChar(NewDACData);

        WaitForSingleObject(hDACDataMutex, INFINITE);
          L := Length(DACData);
          SetLength(DACData, L + FrameBuffers);
          for I := 0 to FrameBuffers - 1 do begin
            SetString(DACData[L + I], pBuffer, FrameBufferSize);
            Inc(pBuffer, FrameBufferSize);
          end;
        ReleaseMutex(hDACDataMutex);
        ReleaseSemaphore(hDACDataSem, FrameBuffers, nil);

        FrameBytes := FrameBytes mod FrameBufferSize;
        if FrameBytes <> 0 then
          SetString(PendingDACData, pBuffer, FrameBytes)
        else
          PendingDACData := ''
        ;

        NewDACData := '';
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACOutputStatus(DeviceIndex: LongWord): LongWord; cdecl;
begin
  Result := ERROR_NOT_SUPPORTED; //`@
end;

function DACOutputStart(DeviceIndex: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bDACStream then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bDACOpen then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      if bDACStarted then begin
        Result := ERROR_ALREADY_EXISTS;
        Exit;
      end;

      Result := GenericVendorWrite(DeviceIndex, AUR_DAC_CONTROL, $01, 0, 0, nil);

      if Result = ERROR_SUCCESS then bDACStarted := True;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACOutputSetInterlock(DeviceIndex: LongWord; bInterlock: LongBool): LongWord; cdecl;
var
  Value: Byte;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bDACStream then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bDACOpen then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      if bInterlock then Value := $20 else Value := $00;
      Result := GenericVendorWrite(DeviceIndex, AUR_DAC_CONTROL, Value, 0, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACOutputSetClock(DeviceIndex: LongWord; var ClockHz: Double): LongWord; cdecl;
var
  DCD: TDIO16ClockData;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin

      if not (bDACStream or bDACDIOStream or bDACSlowWaveStream) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if bDACDIOStream then begin
        DCD.Disables := $00;
        DCD.WriteOctDac := OctDacFromFreq(ClockHz);
        DCD.ReadOctDac := $0000;
        Result := GenericVendorWrite(DeviceIndex, AUR_DIO_SETCLOCKS, 0, 0, SizeOf(DCD), @DCD);
      end
      else if bDACSlowWaveStream then begin
        Result := WriteGlobalTick(DeviceIndex, @ClockHz);
      end
      else begin
        CtrDivisor := Round(12000000 / ClockHz);
        ClockHz := 12000000 / CtrDivisor;

        Result := GenericVendorWrite(DeviceIndex, AUR_DAC_DIVISOR, 0, CtrDivisor, 0, nil); //Set divisor
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;




function DACOutputLoadProcess(DeviceIndex: LongWord; var ClockHz: Double; Samples: LongWord; pSampleData: PWord): LongWord; cdecl;
const
  BlockSamples = 31*512;

var
  TargetPipe: LongWord;
  L: LongWord;
  DCD: TDIO16ClockData;
  BytesTransferred, WordsTransferred: LongWord;
  BakDACs: Integer;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not (bDACStream or bDACDIOStream or bDACSlowWaveStream) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if bDACOpen or bDACClosing then begin
        Result := ERROR_TOO_MANY_OPEN_FILES;
        Exit;
      end;

      if bDACDIOStream then begin
            if bDACOpen or bDACClosing or bDIOOpen then begin
                Result := ERROR_TOO_MANY_OPEN_FILES;
                Exit;
            end;

            Result := DIO_StreamOpen(DeviceIndex, False);
            if Result <> ERROR_SUCCESS then Exit;

            DCD.Disables := $00;
            DCD.WriteOctDac := OctDacFromFreq(ClockHz);
            DCD.ReadOctDac := $0000;
            Result := GenericVendorWrite(DeviceIndex, AUR_DIO_SETCLOCKS, 0, 0, SizeOf(DCD), @DCD);
            if Result <> ERROR_SUCCESS then Exit;

            repeat
                BytesTransferred := 0;
                Result := DIO_StreamFrame(DeviceIndex, Samples, pSampleData, BytesTransferred);
                if Result <> ERROR_SUCCESS then begin
                  DIO_StreamClose(DeviceIndex);
                  Exit;
                end;

                WordsTransferred := BytesTransferred div 2;
                if WordsTransferred >= Samples then Break;

                Inc(pSampleData, WordsTransferred);
                Dec(Samples, WordsTransferred);
            until False;

            Result := DIO_StreamClose(DeviceIndex);
      end
      else if bDACSlowWaveStream then begin
            Result := DACOutputOpen(DeviceIndex, ClockHz);
            if Result <> ERROR_SUCCESS then Exit;

            BakDACs := DACsUsed;
            try
              DACsUsed := 1;
              Result := DACOutputFrameRaw(DeviceIndex, Samples, pSampleData);
            finally
              DACsUsed := BakDACs;
            end;
            if Result <> ERROR_SUCCESS then begin
              DACOutputClose(DeviceIndex, True);
            end
            else begin
              Result := DACOutputClose(DeviceIndex, True);
            end;
      end
      else begin
            if Samples >= 128*1024 then begin
              Result := ERROR_OUTOFMEMORY;
              Exit;
            end;

            //Result := DoSetIFace(Handle, $100);
            //if Result <> ERROR_SUCCESS then begin Result := GetMappedFailure(DeviceIndex); Exit; end;

            Result := GenericVendorWrite(DeviceIndex, AUR_DAC_CONTROL, $80, 0, 0, nil); //Reset
            if Result <> ERROR_SUCCESS then Exit;

            Result := GenericVendorWrite(DeviceIndex, AUR_DAC_DATAPTR, $00, 0, 0, nil); //DataPtr << 0
            if Result <> ERROR_SUCCESS then Exit;

            CtrDivisor := Round(12000000 / ClockHz);
            ClockHz := 12000000 / CtrDivisor;

            Result := GenericVendorWrite(DeviceIndex, AUR_DAC_DIVISOR, 0, CtrDivisor, 0, nil); //Set divisor
            if Result <> ERROR_SUCCESS then Exit;

            //Transfer data
            TargetPipe := $02;
            while Samples > BlockSamples do begin
              L := 0;
              Result := AWU_GenericBulkOut(DeviceIndex, TargetPipe, pSampleData, BlockSamples * 2, L);
              if Result <> ERROR_SUCCESS then Exit;
              Inc(pSampleData, BlockSamples);
              Dec(Samples, BlockSamples);
            end;
            L := 0;
            Result := AWU_GenericBulkOut(DeviceIndex, TargetPipe, pSampleData, Samples * 2, L);
            if Result <> ERROR_SUCCESS then Exit;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DACOutputProcess(DeviceIndex: LongWord; var ClockHz: Double; Samples: LongWord; pSampleData: PWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := DACOutputLoadProcess(DeviceIndex, ClockHz, Samples, pSampleData);
    if Result <> ERROR_SUCCESS then Exit;

    if Dev[DeviceIndex].bDACDIOStream then
    else if Dev[DeviceIndex].bDACSlowWaveStream then
    else if Dev[DeviceIndex].bDACStream then begin
      Result := GenericVendorWrite(DeviceIndex, AUR_DAC_CONTROL, $01, 0, 0, nil); //Start
      //if Result <> ERROR_SUCCESS then Exit;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;



function DEB_SetInterface(DeviceIndex: LongWord; TargetInterface: Word): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    //Result := DoSetIFace(Dev[DeviceIndex].Handle, TargetInterface);
    Result := ERROR_NOT_SUPPORTED;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DEB_BulkIn(DeviceIndex: LongWord): LongWord; cdecl;
begin
  Result := ERROR_NOT_SUPPORTED;
end;

function DEB_BulkOut(DeviceIndex, TargetPipe: LongWord; pBuf: Pointer; BufLen: LongWord): LongWord; cdecl;
begin
  Result := AWU_GenericBulkOut(DeviceIndex, TargetPipe, pBuf, BufLen, BufLen);
end;

{ TDACWorker }

procedure TDACWorker.Execute;
var
  {I,} L, Intro: Integer;
  DACData: TDACData;
  TargetPipe, nBytes: LongWord;
  bExit: Boolean;
  //DataPtr: LongWord;
  //BufferSends: LongInt;
  //hDevice: THandle;

begin
  Intro := (128 + 32)*1024; //After one and a quarter 128KB SRAMs, issue the start, if the user hasn't issued it first.
  //BufferSends := 0;
  TargetPipe := $02;
  //DataPtr := 0;

  //hDevice := Dev[Index].Handle;

  bExit := False;
  repeat
    try
      WaitForSingleObject(Dev[Index].hDACDataSem, INFINITE);

      if Dev[Index].bDACAborting then Break;

      WaitForSingleObject(Dev[Index].hDACDataMutex, INFINITE);
        L := Length(Dev[Index].DACData);
        if L = 0 then begin
          if Dev[Index].bDACClosing then bExit := True;
        end
        else begin
          DACData := Dev[Index].DACData[0];
          Dec(L);
          if L <> 0 then begin
            Dev[Index].DACData[0] := Dev[Index].DACData[L]; //For garbage collection
            Move(Dev[Index].DACData[1], Dev[Index].DACData[0], L * 4);
          end;
          SetLength(Dev[Index].DACData, L);
        end;
      ReleaseMutex(Dev[Index].hDACDataMutex);
      if bExit then Break;

      L := Length(DACData);
      {
      for I := 1 to L do
        if ((I and 1) = 0) and ((Byte(DACData[I]) and $80) <> 0) then
          Beep
      ;
      }
      AWU_GenericBulkOut(Index, TargetPipe, PAnsiChar(DACData), L, nBytes);
      DACData := '';

      //Inc(BufferSends);
      //Inc(DataPtr, L);
      if Intro <> 0 then begin
        Dec(Intro, L);
        if Intro <= 0 then begin
          Intro := 0;

          {
          VRD.Request := AUR_DAC_CONTROL; //Reset
          VRD.Value := $80;
          VRD.Index := 0;
          nBytes := 0;
          DeviceIoControl(hDevice, IOCTL_AIOUSB_WRITE, @VRD, SizeOf(VRD), nil, 0, nBytes, nil);

          VRD.Request := AUR_DAC_DIVISOR; //Set divisor
          VRD.Value := 0;
          VRD.Index := Dev[Index].CtrDivisor;
          nBytes := 0;
          DeviceIoControl(hDevice, IOCTL_AIOUSB_WRITE, @VRD, SizeOf(VRD), nil, 0, nBytes, nil);
          }

          DACOutputStart(Index);
        end;
      end;

      {
      VRD.Request := AUR_DAC_DATAPTR; //Set DataPtr to proper value - debug
      VRD.Value := (DataPtr shr 6) and $0700;
      VRD.Index := DataPtr and $3FFF;
      nBytes := 0;
      DeviceIoControl(hDevice, IOCTL_AIOUSB_WRITE, @VRD, SizeOf(VRD), nil, 0, nBytes, nil);
      }
    except
      Break;
    end;
  until Terminated;

  WaitForSingleObject(Dev[Index].hDACDataMutex, INFINITE);
    SetLength(Dev[Index].DACData, 0);
  ReleaseMutex(Dev[Index].hDACDataMutex);

  //if BufferSends <> 0 then BufferSends := 0;

  //CloseHandle(hDevice);
  CloseHandle(Dev[Index].hDACDataMutex);
  CloseHandle(Dev[Index].hDACDataSem);
  Dev[Index].bDACClosing := False;
  Dev[Index].bDACAborting := False;
  Dev[Index].bDACStarted := False;
end;

function DACOutputInvade(DeviceIndex, InvasionType: LongWord; InvasionData: PLongWord): LongWord; cdecl;
begin
  Result := ERROR_NOT_SUPPORTED;
end;





function ADC_GetConfig(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord): LongWord; cdecl;
var
  Content: AnsiString;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if ConfigBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ConfigBufSize < ConfigBytes then begin
        Result := ERROR_INSUFFICIENT_BUFFER;
        ConfigBufSize := ConfigBytes;
        Exit;
      end;

      if pConfigBuf = nil then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      SetString(Content, PAnsiChar(pConfigBuf), ConfigBytes); //Probe buffer

      L := ConfigBytes;
      Result := GenericVendorRead(DeviceIndex, AUR_ADC_GET_CONFIG, 0, 0, L, pConfigBuf);
      if Result = ERROR_SUCCESS then ConfigBufSize := ConfigBytes;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_SetConfig(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord): LongWord; cdecl;
var
  Content: AnsiString;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if ConfigBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ConfigBufSize < ConfigBytes then begin
        Result := ERROR_INSUFFICIENT_BUFFER;
        ConfigBufSize := ConfigBytes;
        Exit;
      end;

      if pConfigBuf = nil then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      SetString(Content, PAnsiChar(pConfigBuf), ConfigBytes); //Probe buffer

      Result := GenericVendorWrite(DeviceIndex, AUR_ADC_SET_CONFIG, 0, 0, ConfigBytes, pConfigBuf);

      if Result = ERROR_SUCCESS then ConfigBufSize := ConfigBytes;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_RangeAll(DeviceIndex: LongWord; pGainCodes: PByte; bDifferential: LongBool): LongWord; cdecl;
var
  ConfigStr: AnsiString;
  L: LongWord;
  I: Integer;
  pRC: PByte;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if (ADCChannels = 0) or not (bADCBulk or bADCDIOStream) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if pGainCodes = nil then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      pRC := pGainCodes;
      for I := 1 to ADCChannels do begin
        if (pRC^ and $F8) <> 0 then begin
          Result := ERROR_INVALID_DATA;
          Exit;
        end;
        Inc(pRC);
      end;

      if bADCBulk then begin
        L := ConfigBytes;
        SetString(ConfigStr, nil, L);

        Result := GenericVendorRead(DeviceIndex, AUR_ADC_GET_CONFIG, 0, 0, L, PAnsiChar(ConfigStr));
        if Result <> ERROR_SUCCESS then Exit;

        pRC := pGainCodes;
        for I := 1 to ADCChannels do begin
          ConfigStr[I] := AnsiChar(pRC^ or (Ord(bDifferential) shl 3));
          Inc(pRC);
        end;

        Result := GenericVendorWrite(DeviceIndex, AUR_ADC_SET_CONFIG, 0, 0, Length(ConfigStr), PAnsiChar(ConfigStr));
      end
      else if bADCDIOStream then begin
        SetString(ConfigStr, PAnsiChar(pGainCodes), ConfigBytes);

        Result := GenericVendorWrite(DeviceIndex, AUR_ADC_SET_CONFIG, 0, 0, Length(ConfigStr), PAnsiChar(ConfigStr));
      end
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_Range1(DeviceIndex, ADChannel: LongWord; GainCode: Byte; bDifferential: LongBool): LongWord; cdecl;
var
  ConfigStr: AnsiString;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not (bADCBulk or bADCDIOStream) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ADChannel >= ADCChannels then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      if (GainCode and $F8) <> 0 then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      L := ConfigBytes;
      SetString(ConfigStr, nil, L);

      Result := GenericVendorRead(DeviceIndex, AUR_ADC_GET_CONFIG, 0, 0, L, PAnsiChar(ConfigStr));
      if Result <> ERROR_SUCCESS then Exit;

      ConfigStr[1 + (ADChannel mod ADCChannels)] := AnsiChar(GainCode or (Ord(bDifferential) shl 3));

      Result := GenericVendorWrite(DeviceIndex, AUR_ADC_SET_CONFIG, 0, 0, Length(ConfigStr), PAnsiChar(ConfigStr));
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_ADMode(DeviceIndex: LongWord; TriggerMode, CalMode: Byte): LongWord; cdecl;
var
  ConfigStr: AnsiString;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not CalMode in [$00, $01, $03, $05, $07] then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      L := ConfigBytes;
      SetString(ConfigStr, nil, L);

      Result := GenericVendorRead(DeviceIndex, AUR_ADC_GET_CONFIG, 0, 0, L, PAnsiChar(ConfigStr));
      if Result <> ERROR_SUCCESS then Exit;

      ConfigStr[1 + $10] := AnsiChar(CalMode);
      ConfigStr[1 + $11] := AnsiChar(TriggerMode);

      Result := GenericVendorWrite(DeviceIndex, AUR_ADC_SET_CONFIG, 0, 0, Length(ConfigStr), PAnsiChar(ConfigStr));
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_SetScanLimits(DeviceIndex, StartChannel, EndChannel: LongWord): LongWord; cdecl;
var
  ConfigStr: AnsiString;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if (StartChannel > EndChannel) or (EndChannel > ADCMUXChannels) then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      L := ConfigBytes;
      SetString(ConfigStr, nil, L);

      Result := GenericVendorRead(DeviceIndex, AUR_ADC_GET_CONFIG, 0, 0, L, PAnsiChar(ConfigStr));
      if Result <> ERROR_SUCCESS then Exit;

      if ConfigBytes < $15 then
        ConfigStr[1 + $12] := AnsiChar(StartChannel or (EndChannel shl 4))
      else begin
        ConfigStr[1 + $12] := AnsiChar((StartChannel and $0F) or (EndChannel shl 4));
        ConfigStr[1 + $14] := AnsiChar((StartChannel shr 4) or (EndChannel and $F0));
      end;

      Result := GenericVendorWrite(DeviceIndex, AUR_ADC_SET_CONFIG, 0, 0, Length(ConfigStr), PAnsiChar(ConfigStr));
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;


function ADC_SetOversample(DeviceIndex: LongWord; Oversample: Byte): LongWord; cdecl;
var
  ConfigStr: AnsiString;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      L := ConfigBytes;
      SetString(ConfigStr, nil, L);

      Result := GenericVendorRead(DeviceIndex, AUR_ADC_GET_CONFIG, 0, 0, L, PAnsiChar(ConfigStr));
      if Result <> ERROR_SUCCESS then Exit;

      ConfigStr[1 + $13] := AnsiChar(Oversample);

      Result := GenericVendorWrite(DeviceIndex, AUR_ADC_SET_CONFIG, 0, 0, Length(ConfigStr), PAnsiChar(ConfigStr));
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_QueryCal(DeviceIndex: LongWord): LongWord; cdecl;
var
  L: LongWord;
  DataByte: Byte;
  Status: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      DataByte := $FF;
      L := SizeOf(DataByte);
      Status := GenericVendorRead(DeviceIndex, AUR_PROBE_CALFEATURE, 0, 0, L, @DataByte);
      if Status <> ERROR_SUCCESS then begin
        Result := Status;
        Exit;
      end;
      if (L <> SizeOf(DataByte)) or (DataByte <> $BB) then begin
        Result := ERROR_NOT_SUPPORTED;
        Exit;
      end;

      Result := ERROR_SUCCESS;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_SetCal(DeviceIndex: LongWord; CalFileName: PAnsiChar): LongWord; cdecl;
begin
  Result := ADC_SetCalAndSave(DeviceIndex, CalFileName, nil);
end;

//This function is huge and sprawling. OO would help.
function ADC_SetCalAndSave(DeviceIndex: LongWord; CalFileName, SaveCalFileName: PAnsiChar): LongWord; cdecl;
var
  CalTable: array of Word;
  oConfig, nConfig: array of Byte;
  Suc: Boolean;
  PacketWords, PacketsMask, ChunkSize: LongWord;

  procedure DoLoadCalTable;
  var
    bFirstChunkDouble: Boolean;
    TargetPipe: LongWord;
    SRAMIndex: Integer;
    L, L2: LongWord;

  begin
    bFirstChunkDouble := True;
    TargetPipe := $02;
    SRAMIndex := 0;
    repeat
      L2 := (Length(CalTable) - SRAMIndex);
      if L2 > ChunkSize then L2 := ChunkSize;
      L := 0;
      Suc := AWU_GenericBulkOut(DeviceIndex, TargetPipe, @CalTable[SRAMIndex], SizeOf(CalTable[0]) * L2, L) = ERROR_SUCCESS;
      if not Suc then Break;

      GenericVendorWrite(DeviceIndex, $BB, SRAMIndex, L2, 0, nil);

      L := L div 2; //Entries
      L := L and PacketsMask; //Entries in complete packets
      Inc(SRAMIndex, L);
      if bFirstChunkDouble then begin
        bFirstChunkDouble := False;
        SRAMIndex := 0;
      end;
    until (SRAMIndex = $10000);
  end;

  function ConfigureAndBulkAcquire: Double;
  var
    L: LongWord;
    I: Integer;
    ADData: TWordArray;
    Status, ADTot: LongWord;
    StartChannel, EndChannel: Byte;

  begin
    L := Length(nConfig);
    ADC_SetConfig(DeviceIndex, @nConfig[0], L);

    Status := ADC_GetScan_Inner(DeviceIndex, nConfig, ADData, StartChannel, EndChannel, 0);
    if Status <> ERROR_SUCCESS then begin
      Result := Status;
      Exit;
    end;

    ADTot := 0;
    for I := 0 to nConfig[$13] do Inc(ADTot, ADData[I]);
    Result := ADTot / (1 + nConfig[$13]);
  end;

  function GetHiRef: Word;
  var
    Status, DataSize: LongWord;

  begin
    DataSize := SizeOf(Result);
    Status := GenericVendorRead(DeviceIndex, $A2, $1DF2, 0, DataSize, @Result);
    if Status <> ERROR_SUCCESS then
      Result := 0
    else if DataSize <> SizeOf(Result) then
      Result := 0
    else if Result = $FFFF then
      Result := 0
    ;
  end;

  function ReadCalTableFromFile(hFil: THandle): LongWord;
  var
    L: LongWord;

  begin
    L := 0;
    SetLastError(ERROR_SUCCESS);
    if ReadFile(hFil, CalTable[0], SizeOf(CalTable[0]) * Length(CalTable), L, nil) then begin
      Result := ERROR_SUCCESS;
      if LongInt(L) < SizeOf(CalTable[0]) * Length(CalTable) then Result := ERROR_HANDLE_EOF;
    end
    else begin
      Result := GetLastError;
      if Result = ERROR_SUCCESS then Result := ERROR_GEN_FAILURE;
    end;
  end;

  function WriteCalTableToFile(hFil: THandle): LongWord;
  var
    L: LongWord;

  begin
    if hFil = 0 then begin //Successfully does nothing.
      Result := ERROR_SUCCESS;
      Exit;
    end;

    L := 0;
    Suc := WriteFile(hFil, CalTable[0], SizeOf(CalTable[0]) * Length(CalTable), L, nil);
    Result := GetLastError;
    if (Result = ERROR_SUCCESS) and not Suc then Result := ERROR_GEN_FAILURE;
    if (Result = ERROR_SUCCESS) and (LongInt(L) < SizeOf(CalTable[0]) * Length(CalTable)) then Result := ERROR_HANDLE_EOF;
  end;

const
  LoRefRef = 0      * 6553.6;
  HiRefRef = 9.9339 * 6553.6;

var
  I, J, K: Integer;
  L: LongWord;
  hFil, hSaveFil: THandle;
  F,
  LoRef,  HiRef,  dRef, ThisRef,
  LoRead, HiRead, dRead: Double;
  DataByte: Byte;
  Status: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      DataByte := $FF;
      L := SizeOf(DataByte);
      Status := GenericVendorRead(DeviceIndex, AUR_PROBE_CALFEATURE, 0, 0, L, @DataByte);
      if Status <> ERROR_SUCCESS then begin
        Result := Status;
        Exit;
      end;
      if (L <> SizeOf(DataByte)) or (DataByte <> $BB) then begin
        Result := ERROR_NOT_SUPPORTED;
        Exit;
      end;

      //Determine packetization and buffering for DoLoadCalTable.
      if CheckUSBSpeed(DeviceIndex) = usHigh then
        PacketWords := $200 div 2
      else
        PacketWords := $40 div 2
      ;
      PacketsMask := $FFFFFFFF * PacketWords;
      ChunkSize := PacketWords * 2;

      if SaveCalFileName = nil then
        hSaveFil := 0
      else begin
        hSaveFil := CreateFileA(SaveCalFileName, GENERIC_READ or GENERIC_WRITE, FILE_SHARE_READ or FILE_SHARE_WRITE, nil, CREATE_ALWAYS, 0, 0);
        if (hSaveFil = 0) or (hSaveFil = INVALID_HANDLE_VALUE) then begin
          Result := GetLastError;
          if Result = ERROR_SUCCESS then Result := ERROR_GEN_FAILURE;
          Exit;
        end;
      end;

      L := ConfigBytes;
      SetLength(oConfig, L);
      SetLength(nConfig, L);
      FillChar(oConfig[0], L, $00);
      FillChar(nConfig[0], L, $00);
      ADC_GetConfig(DeviceIndex, @oConfig[0], L);

      try
        if CalFileName = ':AUTO:' then begin

          LoRef := LoRefRef;
          HiRef := GetHiRef;
          if HiRef = 0 then HiRef := HiRefRef;
          dRef := HiRef - LoRef;

          nConfig[$10] := $05; //Select bip low ref, to select bip cal bank(on banked boards).
          nConfig[$00] := $01; //Select ±10V range for channel 0.
          for K := 0 to 1 do begin
            ADC_SetConfig(DeviceIndex, @nConfig[0], L);

            //Load 1-to-1 to cal against.
            SetLength(CalTable, $10000);
            for I := 0 to High(CalTable) do CalTable[I] := I;
            DoLoadCalTable;

            nConfig[$11] := $04; //scan software-start
            nConfig[$12] := $00; //select 1 channel
            nConfig[$13] := Min($FF, ChunkSize-1); //Max oversample the FX2 can buffer at once

            ThisRef := HiRef;
            if K = 0 then ThisRef := 1/2 * (ThisRef + $10000);
            nConfig[$10] := nConfig[$10] or $02; //cal high ref
            HiRead := ConfigureAndBulkAcquire; //$FE3F;
            if Abs(HiRead - ThisRef) > $1000 then begin
              Result := ERROR_INVALID_DATA;
              Exit;
            end;
            Sleep(10); //Cargo cult.

            ThisRef := LoRef;
            if K = 0 then ThisRef := 1/2 * (ThisRef + $10000);
            nConfig[$10] := nConfig[$10] and not $02; //cal low ref
            LoRead := ConfigureAndBulkAcquire; //$0042;
            if Abs(LoRead - ThisRef) > $100 then begin
              Result := ERROR_INVALID_DATA;
              Exit;
            end;
            Sleep(10); //Cargo cult.

            dRead := HiRead - LoRead;

            SetLength(CalTable, $10000);
            for I := 0 to High(CalTable) do begin
              F := (I - LoRead) / dRead;
              F := LoRef + F * dRef;
              if K = 0 then F := 1/2 * (F + $10000);
              J := Round(F);
              if J <= 0 then
                J := 0
              else if J >= $FFFF then
                J := $FFFF
              ;
              CalTable[I] := J;
            end;

            DoLoadCalTable;

            Result := WriteCalTableToFile(hSaveFil);
            if Result <> ERROR_SUCCESS then Exit;

            nConfig[$10] := $01; //Select unip low ref, to select unip cal bank(on banked boards).
            nConfig[$00] := $00; //Select 0-10V range for channel 0.
          end; //Go around again, with K=1.

        end
        else if (CalFileName = ':NORM:') then begin

          LoRef := LoRefRef;
          HiRef := GetHiRef;
          if HiRef = 0 then HiRef := HiRefRef;
          dRef := HiRef - LoRef;

          LoRead := $0042;
          HiRead := $FE3F;
          dRead := HiRead - LoRead;

          SetLength(CalTable, $10000);
          for I := 0 to High(CalTable) do begin
            F := (I - LoRead) / dRead;
            F := LoRef + F * dRef;
            J := Round(F);
            if J <= 0 then
              J := 0
            else if J >= $FFFF then
              J := $FFFF
            ;
            CalTable[I] := J;
          end;

          nConfig[$10] := $05; //Select bip low ref, to select bip cal bank(on banked boards).
          for K := 0 to 1 do begin
            ADC_SetConfig(DeviceIndex, @nConfig[0], L);

            DoLoadCalTable;

            Result := WriteCalTableToFile(hSaveFil);
            if Result <> ERROR_SUCCESS then Exit;

            nConfig[$10] := $01; //Select unip low ref, to select unip cal bank(on banked boards).
          end;

        end
        else if (CalFileName = ':1TO1:') or (CalFileName = ':NONE:') then begin

          SetLength(CalTable, $10000);
          for I := 0 to High(CalTable) do CalTable[I] := I;

          nConfig[$10] := $05; //Select bip low ref, to select bip cal bank(on banked boards).
          for K := 0 to 1 do begin
            ADC_SetConfig(DeviceIndex, @nConfig[0], L);

            DoLoadCalTable;

            Result := WriteCalTableToFile(hSaveFil);
            if Result <> ERROR_SUCCESS then Exit;

            nConfig[$10] := $01; //Select unip low ref, to select unip cal bank(on banked boards).
          end;

        end
        else if Copy(CalFileName, 1, 1) = ':' then begin

          Result := ERROR_MOD_NOT_FOUND;
          Exit;

        end
        else begin //Not one of the macros, so treat it as a filename.

          hFil := CreateFileA(CalFileName, GENERIC_READ, FILE_SHARE_READ or FILE_SHARE_WRITE, nil, OPEN_EXISTING, 0, 0);
          if (hFil = 0) or (hFil = INVALID_HANDLE_VALUE) then begin
            Result := GetLastError;
            if Result = ERROR_SUCCESS then Result := ERROR_GEN_FAILURE;
            Exit;
          end;
          SetLength(CalTable, $10000);

          I := GetFileSize(hFil, @L);
          Result := GetLastError;
          if (LongWord(I) = INVALID_FILE_SIZE) and (Result <> ERROR_SUCCESS) then begin
            CloseHandle(hFil);
            Exit;
          end;

          if (L <> 0) or (I >= $20000) then begin
            //It's big enough to be a "double" binary cal file.
            nConfig[$10] := $05; //Select bip low ref, to select bip cal bank(on banked boards).
            nConfig[$00] := $01; //Select ±10V range for channel 0.
            for K := 0 to 1 do begin
              ADC_SetConfig(DeviceIndex, @nConfig[0], L);

              Result := ReadCalTableFromFile(hFil);
              if Result <> ERROR_SUCCESS then begin
                CloseHandle(hFil);
                Exit;
              end;

              DoLoadCalTable;

              Result := WriteCalTableToFile(hSaveFil);
              if Result <> ERROR_SUCCESS then begin
                CloseHandle(hFil);
                Exit;
              end;

              nConfig[$10] := $01; //Select unip low ref, to select unip cal bank(on banked boards).
              nConfig[$00] := $00; //Select 0-10V range for channel 0.
            end;
            CloseHandle(hFil);
          end
          else if I >= $10000 then begin
            //It's only a "single" binary cal file.
            Result := ReadCalTableFromFile(hFil);
            CloseHandle(hFil);
            if Result <> ERROR_SUCCESS then Exit;

            DoLoadCalTable;

            Result := WriteCalTableToFile(hSaveFil);
            if Result <> ERROR_SUCCESS then Exit;
          end
          else begin
            Result := ERROR_HANDLE_EOF;
            CloseHandle(hFil);
            Exit;
          end;

        end;
      finally
        L := ConfigBytes;
        ADC_SetConfig(DeviceIndex, @oConfig[0], L);
        SetLength(oConfig, 0);
        SetLength(nConfig, 0);

        SetLength(CalTable, 0);

        if hSaveFil <> 0 then CloseHandle(hSaveFil);
      end;

      if Suc then
        Result := ERROR_SUCCESS
      else
        Result := GetMappedFailure(DeviceIndex)
      ;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_Initialize(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord; CalFileName: PAnsiChar): LongWord; cdecl;
begin
  try
    Result := ERROR_SUCCESS;
    if (pConfigBuf <> nil) and (ConfigBufSize <> 0) then begin
      Result := ADC_SetConfig(DeviceIndex, pConfigBuf, ConfigBufSize);
      if Result <> ERROR_SUCCESS then Exit;
    end;

    if CalFileName <> nil then begin
      Result := ADC_SetCal(DeviceIndex, CalFileName);
      //if Result <> ERROR_SUCCESS then Exit;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_Start(DeviceIndex: LongWord): LongWord; cdecl;
begin
  Result := ERROR_NOT_SUPPORTED;
end;

function ADC_Stop(DeviceIndex: LongWord): LongWord; cdecl;
begin
  Result := ERROR_NOT_SUPPORTED;
end;


{ TADCWorker }

procedure TADCWorker.Execute;
const
  MinBlock = 512;

var
  TransferLen, L, Status: LongWord;
  BCData: LongWord;

begin
  SetThreadPriority(Handle, THREAD_PRIORITY_TIME_CRITICAL);

  TransferLen := Max(MinBlock, Min(BytesLeft, BlockSize));
  SetLength(ADBuf, TransferLen);
  case BCStyle of
    bsADC: begin
      //GenericVendorWrite(DeviceIndex, AUR_SET_GPIF_MODE, 0, $0, 0, nil);
      BCData := $00000005;
      _GenericVendorWrite(DI, $BC, BytesLeft shr 17, BytesLeft shr 1, SizeOf(BCData), @BCData);
    end;
    bsDIO: begin
      _GenericVendorWrite(DI, $BC, $3, 0, 0, nil);
    end;
  end;

  repeat
    if bAbort then begin
      ReturnValue := ERROR_OPERATION_ABORTED;
      BytesLeft := 0;
      Exit;
    end;

    L := 0;
    Status := AWU_GenericBulkIn(DI, TargetPipe, @ADBuf[0], TransferLen, L);

    if Status <> ERROR_SUCCESS then begin
      ReturnValue := Status;
      BytesLeft := 0;
      Exit;
    end;

    if L > LongWord(BytesLeft) then L := BytesLeft;

    Move(ADBuf[0], pTar^, L);
    Inc(pTar, L div 2);
    Dec(BytesLeft, L);

    if (LongWord(BytesLeft) < TransferLen) and (TransferLen <> MinBlock) then
      TransferLen := Max(MinBlock, BytesLeft)
    ;
  until BytesLeft = 0;
  _GenericVendorWrite(DI, $BC, $0, 0, 0, nil);
  ReturnValue := ERROR_SUCCESS;
end;

function ADC_BulkAcquire(DeviceIndex: LongWord; BufSize: LongWord; pBuf: Pointer): LongWord; cdecl;
var
  oADCWorker: TADCWorker;
  oADCContAcqWorker: TADCContAcqWorker;
  oADCContBufWorker: TADCContBufWorker;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bADCBulk or bADCDIOStream then begin
        {
        if not bADCOpen then begin
          Result := ERROR_FILE_NOT_FOUND;
          Exit;
        end;
        }

        oADCWorker := ADCWorker;
        oADCContAcqWorker := ADCContAcqWorker;
        oADCContBufWorker := ADCContBufWorker;
        if ((oADCWorker <> nil) and (oADCWorker.BytesLeft <> 0))
        or (oADCContAcqWorker <> nil) or (oADCContBufWorker <> nil) then begin
          Result := ERROR_TOO_MANY_OPEN_FILES;
          Exit;
        end;

        ADCWorker := TADCWorker.Create(True);
        with ADCWorker do begin
          FreeOnTerminate := False;
          DI := DeviceIndex;
          TargetPipe := $86;
          BytesLeft := BufSize;
          pTar := pBuf;
          if bADCDIOStream then begin
            BCStyle := bsDIO;
            //For historical reasons, DIO streaming block size is in words, ADC streaming block size is in bytes.
            //The user sees StreamingBlockSize ADC-style(insofar as they see it at all), but AIOUSB_SetStreamingBlockSize effectively left it in integral half-packets.
            //So, if there's a stray half-packet, then give it another half-packet to make integral packets.
            BlockSize := StreamingBlockSize;
            if (BlockSize and $100) <> 0 then
              Inc(BlockSize, $100)
            ;
          end
          else begin
            BCStyle := bsADC;
            BlockSize := StreamingBlockSize;
          end;
          bAbort := False;
          Start;
        end;

        if oADCWorker <> nil then oADCWorker.Free;
      end
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_BulkPoll(DeviceIndex: LongWord; var BytesLeft: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bADCBulk or bADCDIOStream then begin
        if ADCWorker = nil then begin
          Result := ERROR_FILE_NOT_FOUND;
          Exit;
        end;

        if (WaitForSingleObject(ADCWorker.Handle, 0) = WAIT_OBJECT_0) and (ADCWorker.ReturnValue <> ERROR_SUCCESS) then begin
          Result := ADCWorker.ReturnValue;
          Exit;
        end;

        BytesLeft := ADCWorker.BytesLeft;
      end
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_BulkAbort(DeviceIndex: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bADCBulk or bADCDIOStream then begin
        if ADCWorker = nil then begin
          Result := ERROR_FILE_NOT_FOUND;
          Exit;
        end;

        if WaitForSingleObject(ADCWorker.Handle, 0) = WAIT_OBJECT_0 then
          Result := ADCWorker.ReturnValue
        else begin
          ADCWorker.bAbort := True;
          Result := ERROR_SUCCESS;
        end;
      end
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_BulkMode(DeviceIndex, BulkMode: LongWord): LongWord; cdecl;
begin
  Result := ERROR_NOT_SUPPORTED;
end;

procedure CalcHzDivisors(pHz: PDouble; pDivisorA, pDivisorB: PWord; RootClock: Double);
var
  L, DivisorA, DivisorB: LongWord;
  DivisorAB: Extended;
  Err, MinErr, Hz: Double;

begin
  Hz := pHz^;
  if Hz * 4 >= RootClock then begin
    DivisorA := 2;
    DivisorB := 2;
  end
  else begin
    DivisorAB := RootClock / Hz;

    L := Round(SqRt(DivisorAB));
    DivisorA := Round(DivisorAB / L);
    DivisorB := L;
    MinErr := Abs(Hz - (RootClock / (DivisorA * L)));
    for L := L downto 2 do begin
      DivisorA := Round(DivisorAB / L);
      if DivisorA > $FFFF then Break; //Limited to 16 bits, so this and all further L are invalid.
      Err := Abs(Hz - (RootClock / (DivisorA * L)));
      if Err = 0 then begin
        DivisorB := L;
        Break;
      end;
      if Err < MinErr then begin
        DivisorB := L;
        MinErr := Err;
      end;
    end;
    DivisorA := Round(DivisorAB / DivisorB);
  end;

  pDivisorA^ := DivisorA;
  pDivisorB^ := DivisorB;

  pHz^ := RootClock / (DivisorA * DivisorB);
end;

{ TADCContAcqWorker }

procedure TADCContAcqWorker.Execute;

  function DoBCControl(TCSize: LongWord; ControlData: LongWord): LongWord;
  begin
    Result := _GenericVendorWrite(DI, $BC, TCSize shr 16, TCSize, SizeOf(ControlData), @ControlData);
  end;

  procedure DoErrOut(Status: LongWord);
  begin
    IOStatus := Status;
    ReturnValue := Status;
    ReleaseSemaphore(MyBufThread.hKillSem, 1, nil);
    ReleaseSemaphore(MyBufThread.hDataBufSem, 1, nil);
  end;

var
  BytesLeft, DataSize,
  Status: LongWord;
  ThisBuf: PContBuf;

begin
  SetThreadPriority(Handle, THREAD_PRIORITY_TIME_CRITICAL);

  IOStatus := ERROR_SUCCESS;
  if BCStyle = bsDIO then
    _GenericVendorWrite(DI, $BC, $3, 0, 0, nil)
  else begin
    //_GenericVendorWrite(DI, AUR_SET_GPIF_MODE, 0, $1, 0, nil);
    if bCounterControl then
      _GenericVendorWrite(DI, $C5, DivisorA, DivisorB, 0, nil)
    else
      DoBCControl(0, $01000007)
    ;
  end;
  SetEvent(hStartEvent);
  while not Terminated do begin
    ThisBuf := MyBufThread.GetBlankBuf(0);

    ThisBuf.UsedSize := 0;
    Status := _GenericBulk(DI, TargetPipe, @ThisBuf.ADBuf[0], Length(ThisBuf.ADBuf), ThisBuf.UsedSize);

    if Status <> ERROR_SUCCESS then begin
      DoErrOut(Status);
      if BCStyle = bsDIO then
        _GenericVendorWrite(DI, $BC, $10, 0, 0, nil)
      else
        DoBCControl(0, $00020002)
      ;
      Exit;
    end;

    if ThisBuf.UsedSize <> 0 then
      MyBufThread.PutDataBuf(ThisBuf)
    else
      MyBufThread.PutBlankBuf(ThisBuf)
    ;
  end;

  if BCStyle = bsDIO then begin
    _GenericVendorWrite(DI, $BC, $10, 0, 0, nil);
    AIOUSB_ClearFIFO(DI, 0);
  end
  else begin
    DoBCControl(0, $00020002);

    repeat
      BytesLeft := 0;
      DataSize := SizeOf(BytesLeft);
      Status := _GenericVendorRead(DI, $BC, 0, 0, DataSize, @BytesLeft);
      if Status <> ERROR_SUCCESS then begin
        DoErrOut(Status);
        Exit;
      end;
      BytesLeft := BytesLeft and $0000FFFF;
      if BytesLeft = 0 then Break;

      ThisBuf := MyBufThread.GetBlankBuf(0);

      ThisBuf.UsedSize := 0;
      DataSize := Length(ThisBuf.ADBuf);
      if DataSize < BytesLeft then BytesLeft := DataSize;
      Status := _GenericBulk(DI, TargetPipe, @ThisBuf.ADBuf[0], BytesLeft, ThisBuf.UsedSize);

      if Status <> ERROR_SUCCESS then begin
        MyBufThread.PutBlankBuf(ThisBuf);
        DoErrOut(Status);
        Exit;
      end;

      if ThisBuf.UsedSize <> 0 then
        MyBufThread.PutDataBuf(ThisBuf)
      else
        MyBufThread.PutBlankBuf(ThisBuf)
      ;
    until True;//`@ False;
  end;
  ReturnValue := ERROR_SUCCESS;
end;

{ TADCContBufWorker }

procedure TADCContBufWorker.Execute;
var
  ThisBuf: PContBuf;

begin
  repeat
    if Terminated then begin
      ReturnValue := ERROR_OPERATION_ABORTED;
      Exit;
    end;

    ThisBuf := GetDataBufOrKilled;
    if ThisBuf = nil then begin
      try
        Callback(nil, 0, CallbackFlag_EndStream, CallbackContext);
      except
      end;
      ReturnValue := ERROR_OPERATION_ABORTED;
      Exit;
    end;

    if (ThisBuf.UsedSize <> 0) or (ThisBuf.Flags <> 0) then try
      Callback(@ThisBuf.ADBuf[0], ThisBuf.UsedSize, ThisBuf.Flags, CallbackContext);
    except
    end;

    PutBlankBuf(ThisBuf);
  until False;
  ReturnValue := ERROR_SUCCESS;
end;

function TADCContBufWorker.ExtraBuf: PContBuf;
var
  I: Integer;

begin
  WaitForSingleObject(hBufMutex, INFINITE);
    I := Length(BufBuf);
    SetLength(BufBuf, I + 1);
    New(BufBuf[I]);
    Result := BufBuf[I];
    SetLength(Result.ADBuf, BytesPerBuf);
    Result.BufState := bsAccessing;
  ReleaseMutex(hBufMutex);
end;

function TADCContBufWorker.GetBlankBuf(Flags: LongWord): PContBuf;
var
  I: Integer;

begin
  if WaitForSingleObject(hBlankBufSem, 0) = WAIT_TIMEOUT then begin
    Result := ExtraBuf;
    Result.Flags := CallbackFlag_Inserted or Flags;
    Exit;
  end;
  Result := nil;
  WaitForSingleObject(hBufMutex, INFINITE);
    for I := 0 to High(BufBuf) do
      if BufBuf[I].BufState = bsBlank then begin
        Result := BufBuf[I];
        Result.Flags := Flags;
        Break;
      end
    ;
  ReleaseMutex(hBufMutex);

  if Result = nil then begin
    Result := ExtraBuf; //We have a semaphore to prevent this, so not likely to matter.
    Result.Flags := CallbackFlag_Inserted or Flags;
  end;
end;

function TADCContBufWorker.GetDataBuf(Timeout: LongWord = INFINITE): PContBuf;
var
  I: Integer;

begin
  Result := nil;
  repeat
    if WaitForSingleObject(hDataBufSem, Timeout) <> WAIT_OBJECT_0 then Exit;

    Result := nil;
    WaitForSingleObject(hBufMutex, INFINITE);
      for I := 0 to High(BufBuf) do
        if (BufBuf[I].BufState = bsGotData) and (BufBuf[I].Index = NextIndexOut) then begin
          Result := BufBuf[I];
          Result.BufState := bsAccessing;
          Inc(NextIndexOut);
          Break;
        end
      ;
    ReleaseMutex(hBufMutex);

    if Result = nil then Exit;
  until Result <> nil; //We have a semaphore to prevent this, so just go around again if it happens.
end;

function TADCContBufWorker.GetDataBufOrKilled: PContBuf;
var
  I: Integer;

begin
  repeat
    WaitForSingleObject(hDataBufSem, INFINITE);
    Result := nil;
    WaitForSingleObject(hBufMutex, INFINITE);
      for I := 0 to High(BufBuf) do
        if (BufBuf[I].BufState = bsGotData) and (BufBuf[I].Index = NextIndexOut) then begin
          Result := BufBuf[I];
          Result.BufState := bsAccessing;
          Inc(NextIndexOut);
          Break;
        end
      ;
    ReleaseMutex(hBufMutex);

    if Result = nil then begin
      if WaitForSingleObject(hKillSem, 0) <> WAIT_TIMEOUT then Exit;
    end;
  until Result <> nil; //We have a semaphore to prevent this, so just go around again if it happens.
end;

procedure TADCContBufWorker.GetDebugStats(var Blanks, Accessings, GotDatas: LongWord);
var
  I: Integer;
  iBlanks, iAccessings, iGotDatas: LongWord;

begin
  iBlanks := 0;
  iAccessings := 0;
  iGotDatas := 0;
  WaitForSingleObject(hBufMutex, INFINITE);
    for I := 0 to High(BufBuf) do
      case BufBuf[I].BufState of
        bsBlank: Inc(iBlanks);
        bsAccessing: Inc(iAccessings);
        bsGotData: Inc(iGotDatas);
      end
    ;
  ReleaseMutex(hBufMutex);
  Blanks     := iBlanks;
  Accessings := iAccessings;
  GotDatas   := iGotDatas;
end;

procedure TADCContBufWorker.PutBlankBuf(pNewBuf: PContBuf);
begin
  WaitForSingleObject(hBufMutex, INFINITE);
    pNewBuf.BufState := bsBlank;
  ReleaseMutex(hBufMutex);
  ReleaseSemaphore(hBlankBufSem, 1, nil);
end;

procedure TADCContBufWorker.PutDataBuf(pNewBuf: PContBuf);
begin
  WaitForSingleObject(hBufMutex, INFINITE);
    pNewBuf.BufState := bsGotData;
    pNewBuf.Index := NextIndexIn;
    Inc(NextIndexIn);
  ReleaseMutex(hBufMutex);
  ReleaseSemaphore(hDataBufSem, 1, nil);
end;

{ Done }

function ADC_BulkContinuousCallbackStart_Inner(DeviceIndex: LongWord; BufSize: LongWord; BaseBufCount: LongWord; Context: LongWord; pCallback: Pointer; pHz: PDouble): LongWord; register;
var
  oADCWorker: TADCWorker;
  oADCContAcqWorker: TADCContAcqWorker;
  oADCContBufWorker: TADCContBufWorker;
  I: Integer;
  hWaits: array[0..1] of THandle;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bADCBulk or bADCDIOStream then begin
        if (BufSize and $1FF) <> 0 then begin
          Result := ERROR_INVALID_USER_BUFFER;
          Exit;
        end;

        if BufSize < StreamingBlockSizeFloor then begin
          Result := ERROR_INVALID_USER_BUFFER;
          Exit;
        end;

        {
        if pCallback = nil then begin
          Result := ERROR_INVALID_FUNCTION;
          Exit;
        end;
        }

        oADCWorker := ADCWorker;
        oADCContAcqWorker := ADCContAcqWorker;
        oADCContBufWorker := ADCContBufWorker;
        if ((oADCWorker <> nil) and (oADCWorker.BytesLeft <> 0))
        or (oADCContAcqWorker <> nil) or (oADCContBufWorker <> nil) then begin
          Result := ERROR_TOO_MANY_OPEN_FILES;
          Exit;
        end;

        if (pHz <> nil) and bADCBulk then begin
          CTR_8254Mode(DeviceIndex, 0, 1, 2);
          CTR_8254Mode(DeviceIndex, 0, 2, 3);
        end;

        ADCContAcqWorker := TADCContAcqWorker.Create(True);
        ADCContBufWorker := TADCContBufWorker.Create(True);
        with ADCContBufWorker do begin
          FreeOnTerminate := False;
          MyAcqThread := ADCContAcqWorker;
          BytesPerBuf := BufSize;
          Callback := pCallback;
          CallbackContext := Context;
          hBufMutex := CreateMutex(nil, False, nil);
          hKillSem := CreateSemaphore(nil, 0, $FFFFFF, nil);
          hBlankBufSem := CreateSemaphore(nil, BaseBufCount, $FFFFFF, nil);
          hDataBufSem := CreateSemaphore(nil, 0, $FFFFFF, nil);
          SetLength(ADCContBufWorker.BufBuf, BaseBufCount);
          for I := 0 to BaseBufCount-1 do begin
            New(ADCContBufWorker.BufBuf[I]);
            SetLength(ADCContBufWorker.BufBuf[I].ADBuf, BufSize);
            ADCContBufWorker.BufBuf[I].BufState := bsBlank;
          end;
          if pCallback = nil then Terminate;
          Start;
        end;
        with ADCContAcqWorker do begin
          FreeOnTerminate := False;
          MyBufThread := ADCContBufWorker;
          hStartEvent := CreateEvent(nil, True, False, nil);
          DI := DeviceIndex;
          TargetPipe := $86;
          //BytesPerBC := BufSize * BaseBufCount;
          if bADCDIOStream then begin
            BCStyle := bsDIO;
            bCounterControl := False;
            if pHz <> nil then pHz^ := RootClock;
          end
          else begin
            BCStyle := bsADC;
            if pHz = nil then
              bCounterControl := False
            else begin
              bCounterControl := True;//Hz > 1/2;
              if bCounterControl then CalcHzDivisors(pHz, @DivisorA, @DivisorB, RootClock);
            end;
          end;
          Start;
        end;
        hWaits[0] := ADCContAcqWorker.Handle;
        hWaits[1] := ADCContAcqWorker.hStartEvent;
        WaitForMultipleObjects(2, @hWaits[0], False, INFINITE);
        CloseHandle(ADCContAcqWorker.hStartEvent);

        if oADCWorker <> nil then oADCWorker.Free;
      end
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_BulkContinuousCallbackStart(DeviceIndex: LongWord; BufSize: LongWord; BaseBufCount: LongWord; Context: LongWord; pCallback: Pointer): LongWord; cdecl;
begin
  Result := ADC_BulkContinuousCallbackStart_Inner(DeviceIndex, BufSize, BaseBufCount, Context, pCallback, nil);
end;

function ADC_BulkContinuousCallbackStartClocked(DeviceIndex: LongWord; BufSize: LongWord; BaseBufCount: LongWord; Context: LongWord; pCallback: Pointer; var Hz: Double): LongWord; cdecl;
begin
  Result := ADC_BulkContinuousCallbackStart_Inner(DeviceIndex, BufSize, BaseBufCount, Context, pCallback, @Hz);
end;

procedure BGRingContCallback(pBuf: PWord; BufSize, Flags, Context: LongWord); cdecl;
var
  SamplesUntilWrap, L: LongWord;

begin
  BufSize := BufSize shr 1; //BufSize is henceforth in samples.
  if BufSize = 0 then Exit;
  if Context >= 32 then Exit;
  if Dev[Context].pRingAcqData = nil then Exit;

  with Dev[Context].pRingAcqData^ do begin
    L := Length(RingBuffer);
    SamplesUntilWrap := L - iNextWrite;

    //This is the write authority for iNextWrite.
    if BufSize < SamplesUntilWrap then begin //Transfer in the beginning or middle.
      Move(pBuf^, RingBuffer[iNextWrite], 2*BufSize);
      Inc(iNextWrite, BufSize);
    end
    else if BufSize = SamplesUntilWrap then begin //Transfer right at the end.
      Move(pBuf^, RingBuffer[iNextWrite], 2*BufSize);
      iNextWrite := 0;
    end
    else begin //Transfer crossing the end, must wrap to beginning as well.
      Move(pBuf^, RingBuffer[iNextWrite], 2*SamplesUntilWrap);
      Dec(BufSize, SamplesUntilWrap);
      Inc(pBuf, SamplesUntilWrap);
      //This assumes the remainder isn't bigger than the entire ring buffer, since ADC_BulkContinuousRingStart already made sure of that.
      Move(pBuf^, RingBuffer[0], 2*BufSize);
      iNextWrite := BufSize;
    end;

    ReleaseSemaphore(hSem, 1, nil);
  end;
end;

function ADC_BulkContinuousRingStart(DeviceIndex: LongWord; RingBufferSize: LongWord; PacketsPerBlock: LongWord): LongWord; cdecl;
var
  oADCWorker: TADCWorker;
  oADCContAcqWorker: TADCContAcqWorker;
  oADCContBufWorker: TADCContBufWorker;
  I: Integer;
  hWaits: array[0..1] of THandle;
  BufSize, BaseBufCount: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bADCBulk or bADCDIOStream then begin
        RingBufferSize := RingBufferSize and not $1FF;
        if RingBufferSize < 4*1024 then begin
          Result := ERROR_INVALID_USER_BUFFER;
          Exit;
        end;

        if PacketsPerBlock > (RingBufferSize shr 9) then begin
          Result := ERROR_INVALID_USER_BUFFER;
          Exit;
        end;
        if PacketsPerBlock <> 0 then
          BufSize := $200 * PacketsPerBlock
        else
          BufSize := Ceil(RingBufferSize / (8*512)) * 512
        ;
        BaseBufCount := 3;

        oADCWorker := ADCWorker;
        oADCContAcqWorker := ADCContAcqWorker;
        oADCContBufWorker := ADCContBufWorker;
        if ((oADCWorker <> nil) and (oADCWorker.BytesLeft <> 0))
        or (oADCContAcqWorker <> nil) or (oADCContBufWorker <> nil) then begin
          Result := ERROR_TOO_MANY_OPEN_FILES;
          Exit;
        end;

        if pRingAcqData = nil then begin
          New(pRingAcqData);
          pRingAcqData.hSem := CreateSemaphore(nil, 0, 1, nil);
        end;
        ADCContAcqWorker := TADCContAcqWorker.Create(True);
        ADCContBufWorker := TADCContBufWorker.Create(True);
        with pRingAcqData^ do begin
          SetLength(RingBuffer, RingBufferSize shr 1);
          iNextRead := 0;
          iNextWrite := 0;
        end;
        with ADCContBufWorker do begin
          FreeOnTerminate := False;
          MyAcqThread := ADCContAcqWorker;
          BytesPerBuf := BufSize;
          Callback := BGRingContCallback;
          CallbackContext := DeviceIndex;
          hBufMutex := CreateMutex(nil, False, nil);
          hKillSem := CreateSemaphore(nil, 0, $FFFFFF, nil);
          hBlankBufSem := CreateSemaphore(nil, BaseBufCount, $FFFFFF, nil);
          hDataBufSem := CreateSemaphore(nil, 0, $FFFFFF, nil);
          SetLength(ADCContBufWorker.BufBuf, BaseBufCount);
          for I := 0 to BaseBufCount-1 do begin
            New(ADCContBufWorker.BufBuf[I]);
            SetLength(ADCContBufWorker.BufBuf[I].ADBuf, BufSize);
            ADCContBufWorker.BufBuf[I].BufState := bsBlank;
          end;
          Start;
        end;
        with ADCContAcqWorker do begin
          FreeOnTerminate := False;
          MyBufThread := ADCContBufWorker;
          hStartEvent := CreateEvent(nil, True, False, nil);
          DI := DeviceIndex;
          TargetPipe := $86;
          if bADCDIOStream then begin
            BCStyle := bsDIO;
          end
          else begin
            BCStyle := bsADC;
          end;
          bCounterControl := False;
          Start;
        end;
        hWaits[0] := ADCContAcqWorker.Handle;
        hWaits[1] := ADCContAcqWorker.hStartEvent;
        WaitForMultipleObjects(2, @hWaits[0], False, INFINITE);
        CloseHandle(ADCContAcqWorker.hStartEvent);

        if oADCWorker <> nil then oADCWorker.Free;
      end
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_BulkContinuousEnd(DeviceIndex: LongWord; pIOStatus: PLongWord): LongWord; cdecl;
var
  oADCContAcqWorker: TADCContAcqWorker;
  oADCContBufWorker: TADCContBufWorker;
  I: Integer;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bADCBulk or bADCDIOStream then begin
        oADCContAcqWorker := ADCContAcqWorker;
        oADCContBufWorker := ADCContBufWorker;
        ADCContAcqWorker := nil;
        ADCContBufWorker := nil;
        if (oADCContAcqWorker = nil) or (oADCContBufWorker = nil) then begin
          Result := ERROR_HANDLE_EOF;
          Exit;
        end;

        if pIOStatus <> nil then pIOStatus^ := oADCContAcqWorker.IOStatus;

        oADCContAcqWorker.Terminate;
        ReleaseSemaphore(oADCContBufWorker.hKillSem, 1, nil);
        ReleaseSemaphore(oADCContBufWorker.hDataBufSem, 1, nil);

        AIOUSB_AbortPipe(DeviceIndex, $86);

        oADCContAcqWorker.WaitFor;
        oADCContBufWorker.WaitFor;
        CloseHandle(oADCContBufWorker.hBufMutex);
        CloseHandle(oADCContBufWorker.hKillSem);
        CloseHandle(oADCContBufWorker.hBlankBufSem);
        CloseHandle(oADCContBufWorker.hDataBufSem);
        for I := 0 to High(oADCContBufWorker.BufBuf) do begin
          Dispose(oADCContBufWorker.BufBuf[I]);
        end;
        SetLength(oADCContBufWorker.BufBuf, 0);

        oADCContAcqWorker.Free;
        oADCContBufWorker.Free;

        if pRingAcqData <> nil then begin
          CloseHandle(pRingAcqData.hSem);
          Dispose(pRingAcqData);
          pRingAcqData := nil;
        end;
      end
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_BulkContinuousDebug(DeviceIndex: LongWord; var Blanks, Accessings, GotDatas: LongWord): LongWord; cdecl;
var
  oADCContAcqWorker: TADCContAcqWorker;
  oADCContBufWorker: TADCContBufWorker;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      oADCContAcqWorker := ADCContAcqWorker;
      oADCContBufWorker := ADCContBufWorker;
      if (oADCContAcqWorker = nil) or (oADCContBufWorker = nil) then begin
        Result := ERROR_HANDLE_EOF;
        Exit;
      end;

      oADCContBufWorker.GetDebugStats(Blanks, Accessings, GotDatas);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_GetImmediate(DeviceIndex, Channel: LongWord; pBuf: PWord): LongWord; cdecl;
var
  L: LongWord;
  oADCWorker: TADCWorker;
  oADCContAcqWorker: TADCContAcqWorker;
  oADCContBufWorker: TADCContBufWorker;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bADCBulk then begin
        {
        if not bADCOpen then begin
          Result := ERROR_FILE_NOT_FOUND;
          Exit;
        end;
        }

        oADCWorker := ADCWorker;
        oADCContAcqWorker := ADCContAcqWorker;
        oADCContBufWorker := ADCContBufWorker;
        if ((oADCWorker <> nil) and (oADCWorker.BytesLeft <> 0))
        or (oADCContAcqWorker <> nil) or (oADCContBufWorker <> nil) then begin
          Result := ERROR_TOO_MANY_OPEN_FILES;
          Exit;
        end;

        try
          pBuf^ := $0000; //Probe buffer
        except
          Result := ERROR_NOACCESS;
          Exit;
        end;

        L := 0;
        Result := GenericVendorWrite(DeviceIndex, AUR_ADC_IMMEDIATE, 0, Channel, L, nil);
      end
      //else if bADCDIOStream then begin end
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

type
  TTimeoutTriggerThread = class(TStartableThread)
  public
    DI: Integer;
    TimeoutMS: LongInt;
    bTimeout: Boolean;
  protected
    procedure Execute; override;
  end;

procedure TTimeoutTriggerThread.Execute;
var
  StartTime, ThisTime, DeltaTime, TimeoutTime: Int64;
  L: LongWord;

begin
  bTimeout := False;
  QueryPerformanceFrequency(TimeoutTime);
  TimeoutTime := (TimeoutTime * TimeoutMS) div 1000;
  QueryPerformanceCounter(StartTime);
  repeat
    Sleep(1);
    if Terminated then Break;

    QueryPerformanceCounter(ThisTime);
    DeltaTime := ThisTime - StartTime;
    if DeltaTime > TimeoutTime then begin
      L := 0;
      GenericVendorWrite(DI, AUR_ADC_IMMEDIATE, 0, 0, L, nil);
      bTimeout := True;
      Break;
    end;
  until False;
end;

function _BlockingADCDIORead(DeviceIndex: LongWord; pData: PByte; DataBytes: LongWord): LongWord;
const
	MinBlock = 512;
	TargetPipe = $86;

var
	BytesToTransfer, BytesTransferred: LongWord;

begin
	Result := _GenericVendorWrite(DeviceIndex, $BC, $3, 0, 0, nil);
	if Result <> ERROR_SUCCESS then Exit;

	try
		repeat
			BytesToTransfer := Max(MinBlock, Min(DataBytes, Dev[DeviceIndex].StreamingBlockSize));
			BytesTransferred := 0;
			Result := _GenericBulk(DeviceIndex, TargetPipe, pData, BytesToTransfer, BytesTransferred);
			if Result <> ERROR_SUCCESS then Exit;

			if BytesTransferred > LongWord(DataBytes) then BytesTransferred := DataBytes;

			Inc(pData, BytesTransferred);
			Dec(DataBytes, BytesTransferred);
		until DataBytes = 0;
	finally
		_GenericVendorWrite(DeviceIndex, $BC, $0, 0, 0, nil);
	end;
end;

function ADC_GetScan_Inner(var DeviceIndex: LongWord; var Config: array of Byte; var ADBuf: TWordArray; var StartChannel, EndChannel: Byte; TimeoutMS: LongInt): LongWord;
const
  ADCDIOOversample = $80; //Samples per channel in a packet.

var
  pADBuf: PByte;
  L, BytesLeft, TargetPipe, BCData: LongWord;
  Channels: Byte;
  I: Integer;
  TimeoutTriggerThread: TTimeoutTriggerThread;
  InterBuf: array of packed record
    AD0, AD1: Word;
    DITS: LongWord;
  end;

begin
  Result := ValidateAndEnsureOpen(DeviceIndex);
  if Result <> ERROR_SUCCESS then Exit;

  if Dev[DeviceIndex].bADCBulk then begin
    L := SizeOf(Config);
    Result := ADC_GetConfig(DeviceIndex, @Config[0], L);
    if Result <> ERROR_SUCCESS then Exit;

    if TimeoutMS <> 0 then
      Config[$11] := $04 or Config[$11] //Turn scan on.
    else
      Config[$11] := $04 or Config[$11] and not $03 //Turn scan on, turn timer and external trigger off.
    ;
    StartChannel := Config[$12] and $F;
    EndChannel := Config[$12] shr 4;
    if L >= 21 then begin
      StartChannel := StartChannel or ((Config[20] and $F) shl 4);
      EndChannel := EndChannel or (Config[20] and $F0);
    end;
    Channels := EndChannel - StartChannel + 1;
    Config[$13] := Max(1, Config[$13]); //Oversample at least +1.
    if Channels * (1 + Config[$13]) > 1024 then Config[$13] := (1024 div Channels) - 1; //Don't take more than the board can buffer, since we aren't threading.
    SetLength(ADBuf, Channels * (1 + Config[$13]));
    Result := ADC_SetConfig(DeviceIndex, @Config[0], L);
    if Result <> ERROR_SUCCESS then Exit;

    TargetPipe := $86;
    BytesLeft := SizeOf(ADBuf[0]) * Length(ADBuf);
    pADBuf := @ADBuf[0];

    //GenericVendorWrite(DeviceIndex, AUR_SET_GPIF_MODE, 0, $0, 0, nil);
    BCData := $00000005;
    Result := GenericVendorWrite(DeviceIndex, $BC, 0, Length(ADBuf), SizeOf(BCData), @BCData);
    if Result <> ERROR_SUCCESS then Exit;
    if TimeoutMS <> 0 then begin
      //Spawn timeout-trigger thread.
      TimeoutTriggerThread := TTimeoutTriggerThread.Create(True);
      TimeoutTriggerThread.FreeOnTerminate := False;
      TimeoutTriggerThread.DI := DeviceIndex;
      TimeoutTriggerThread.TimeoutMS := TimeoutMS;
      TimeoutTriggerThread.Start;
    end
    else begin
      ADC_GetImmediate(DeviceIndex, 0, @ADBuf[0]);
      TimeoutTriggerThread := nil;
    end;
    repeat
      L := 0;
      Result := AWU_GenericBulkIn(DeviceIndex, TargetPipe, pADBuf, BytesLeft, L);
      if Result <> ERROR_SUCCESS then Break;
      Dec(BytesLeft, L);
      Inc(pADBuf, L);
    until BytesLeft <= 0;
    if TimeoutTriggerThread <> nil then begin
      //Tell timeout-trigger thread to not bother if it hasn't tripped yet.
      TimeoutTriggerThread.Terminate;
      //Report timeout if it did.
      if (Result = ERROR_SUCCESS) and TimeoutTriggerThread.bTimeout then Result := ERROR_TIMEOUT;
      //And clean up the thread.
      TimeoutTriggerThread.Free;
    end;
  end
  else if Dev[DeviceIndex].bADCDIOStream then begin
    //Set intermediate array to receive packet.
    SetLength(InterBuf, ADCDIOOversample);

    Result := _BlockingADCDIORead(DeviceIndex, @InterBuf[0], Length(InterBuf) * SizeOf(InterBuf[0]));
    if Result <> ERROR_SUCCESS then Exit;

    {
    if TimeoutMS = 0 then TimeoutMS := 1000;

    //Begin get-data.
    Result := ADC_BulkAcquire(DeviceIndex, Length(InterBuf) * SizeOf(InterBuf[0]), @InterBuf[0]);
    if Result <> ERROR_SUCCESS then Exit;

    //Complete get-data.
    if WaitForSingleObject(Dev[DeviceIndex].ADCWorker.Handle, TimeoutMS) <> WAIT_OBJECT_0 then begin
      Result := ERROR_TIMEOUT;
      Exit;
    end;
    Result := ADC_BulkPoll(DeviceIndex, BytesLeft);
    if Result <> ERROR_SUCCESS then Exit;
    if BytesLeft <> 0 then begin
      Result := ERROR_HANDLE_EOF;
      Exit;
    end;
    }

    StartChannel := 0;
    EndChannel := 1;
    ZeroMemory(@Config[0], Length(Config));
    L := Dev[DeviceIndex].ConfigBytes;
    ADC_GetConfig(DeviceIndex, @Config[0], L);
    Config[$13] := ADCDIOOversample-1;

    //Collect just the A/D data, in channel-major form.
    SetLength(ADBuf, 2*ADCDIOOversample);
    for I := 0 to ADCDIOOversample-1 do
      ADBuf[I] := InterBuf[I].AD0
    ;
    for I := 0 to ADCDIOOversample-1 do
      ADBuf[ADCDIOOversample + I] := InterBuf[I].AD1
    ;
  end
  else if Dev[DeviceIndex].ImmADCs <> 0 then begin
    SetLength(ADBuf, Dev[DeviceIndex].ImmADCs);
    L := Dev[DeviceIndex].ImmADCs * 2;
    Result := GenericVendorRead(DeviceIndex, AUR_ADC_IMMEDIATE, 0, 0, L, @ADBuf[0]);
    StartChannel := 0;
    EndChannel := Dev[DeviceIndex].ImmADCs - 1;
    for I := 0 to 15 do Config[I] := $02; //0-5V
    Config[$13] := 0;
  end
  else begin
    Result := ERROR_BAD_TOKEN_TYPE;
  end;
end;

function ADC_GetScan(DeviceIndex: LongWord; pBuf: PWord): LongWord; cdecl;
var
  Config: array[0..21] of Byte;
  ADBuf: TWordArray;
  I, Ch, J, Tot: Integer;
  StartChannel, EndChannel: Byte;

begin
  try
    Result := ADC_GetScan_Inner(DeviceIndex, Config, ADBuf, StartChannel, EndChannel, 0);
    if Result <> ERROR_SUCCESS then Exit;

    if Config[$13] <> 0 then begin
      I := 0;
      Inc(pBuf, StartChannel);
      for Ch := StartChannel to EndChannel do begin
        Tot := 0;
        for J := 1 to Config[$13] do
          Tot := Tot + ADBuf[I * (1 + Config[$13]) + J]
        ;
        pBuf^ := Round(Tot / Config[$13]);
        Inc(pBuf);
        Inc(I);
      end;
    end
    else begin
      I := 0;
      Inc(pBuf, StartChannel);
      for Ch := StartChannel to EndChannel do begin
        pBuf^ := ADBuf[I];
        Inc(pBuf);
        Inc(I);
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_GetScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; cdecl;
var
  Config: array[0..21] of Byte;
  ADBuf: TWordArray;
  I, Ch, J, Tot: Integer;
  V: Double;
  StartChannel, EndChannel, RangeCode, RangeShift: Byte;
  bApplyPostScale: Boolean;

begin
  try
    Result := ADC_GetScan_Inner(DeviceIndex, Config, ADBuf, StartChannel, EndChannel, 0);
    if Result <> ERROR_SUCCESS then Exit;

    RangeShift := Dev[DeviceIndex].RangeShift;
    bApplyPostScale := Dev[DeviceIndex].ImmADCPostScale <> 1;
    if Config[$13] <> 0 then begin
      I := 0;
      Inc(pBuf, StartChannel);
      for Ch := StartChannel to EndChannel do begin
        RangeCode := Config[Ch shr RangeShift];

        Tot := 0;
        for J := 1 to Config[$13] do
          Tot := Tot + ADBuf[I * (1 + Config[$13]) + J]
        ;

        V := Tot / Config[$13] * (1 / 65536);
        if (RangeCode and 1) <> 0 then V := V * 2 - 1;
        if (RangeCode and 2) = 0 then V := V * 2;
        if (RangeCode and 4) = 0 then V := V * 5;
        if bApplyPostScale then V := V * Dev[DeviceIndex].ImmADCPostScale;
        pBuf^ := V;

        Inc(pBuf);
        Inc(I);
      end;
    end
    else begin
      I := 0;
      Inc(pBuf, StartChannel);
      for Ch := StartChannel to EndChannel do begin
        V := ADBuf[I] * (5 / 65536);
        pBuf^ := V;
        Inc(pBuf);
        Inc(I);
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_GetTrigScan(DeviceIndex: LongWord; pBuf: PWord; TimeoutMS: LongInt): LongWord; cdecl;
var
  Config: array[0..21] of Byte;
  ADBuf: TWordArray;
  I, Ch, J, Tot: Integer;
  StartChannel, EndChannel: Byte;

begin
  try
    if TimeoutMS <= 0 then TimeoutMS := 1;
    Result := ADC_GetScan_Inner(DeviceIndex, Config, ADBuf, StartChannel, EndChannel, TimeoutMS);
    if Result <> ERROR_SUCCESS then Exit;

    if Config[$13] <> 0 then begin
      I := 0;
      Inc(pBuf, StartChannel);
      for Ch := StartChannel to EndChannel do begin
        Tot := 0;
        for J := 1 to Config[$13] do
          Tot := Tot + ADBuf[I * (1 + Config[$13]) + J]
        ;
        pBuf^ := Round(Tot / Config[$13]);
        Inc(pBuf);
        Inc(I);
      end;
    end
    else begin
      I := 0;
      Inc(pBuf, StartChannel);
      for Ch := StartChannel to EndChannel do begin
        pBuf^ := ADBuf[I];
        Inc(pBuf);
        Inc(I);
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_GetTrigScanV(DeviceIndex: LongWord; pBuf: PDouble; TimeoutMS: LongInt): LongWord; cdecl;
var
  Config: array[0..21] of Byte;
  ADBuf: TWordArray;
  I, Ch, J, Tot: Integer;
  V: Double;
  StartChannel, EndChannel, RangeCode, RangeShift: Byte;

begin
  try
    if TimeoutMS <= 0 then TimeoutMS := 1;
    Result := ADC_GetScan_Inner(DeviceIndex, Config, ADBuf, StartChannel, EndChannel, TimeoutMS);
    if (Result <> ERROR_SUCCESS) and (Result <> ERROR_TIMEOUT) then Exit;

    RangeShift := Dev[DeviceIndex].RangeShift;
    if Config[$13] <> 0 then begin
      I := 0;
      Inc(pBuf, StartChannel);
      for Ch := StartChannel to EndChannel do begin
        RangeCode := Config[Ch shr RangeShift];

        Tot := 0;
        for J := 1 to Config[$13] do
          Tot := Tot + ADBuf[I * (1 + Config[$13]) + J]
        ;

        V := Tot / Config[$13] * (1 / 65536);
        if (RangeCode and 1) <> 0 then V := V * 2 - 1;
        if (RangeCode and 2) = 0 then V := V * 2;
        if (RangeCode and 4) = 0 then V := V * 5;
        pBuf^ := V;

        Inc(pBuf);
        Inc(I);
      end;
    end
    else begin
      I := 0;
      Inc(pBuf, StartChannel);
      for Ch := StartChannel to EndChannel do begin
        V := ADBuf[I] * (5 / 65536);
        pBuf^ := V;
        Inc(pBuf);
        Inc(I);
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_GetChannelV(DeviceIndex, ChannelIndex: LongWord; pBuf: PDouble): LongWord; cdecl;
var
  ScanData: array of Double;
  I: Integer;
  Chans: LongWord;

begin
  try
    Result := Validate(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bADCBulk or bADCDIOStream then
        Chans := ADCMUXChannels
      else if ImmADCs <> 0 then
        Chans := ImmADCs
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ChannelIndex >= Chans then begin
        Result := ERROR_INVALID_INDEX;
        Exit;
      end;

      SetLength(ScanData, Chans);
      for I := 0 to Chans - 1 do ScanData[I] := NAN;

      Result := ADC_GetScanV(DeviceIndex, @ScanData[0]);
      if Result <> ERROR_SUCCESS then Exit;

      pBuf^ := ScanData[ChannelIndex];
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_GetCalRefV(DeviceIndex, CalRefIndex: LongWord; var pRef: Double): LongWord; cdecl;
var
  oConfig, nConfig: array of Byte;
  L: LongWord;
  bBip: Boolean;
  ADData: array of Double;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ConfigBytes < 20 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      L := ConfigBytes;
      SetLength(oConfig, L);
      SetLength(nConfig, L);
      FillChar(oConfig[0], L, $00);
      FillChar(nConfig[0], L, $00);
      Result := ADC_GetConfig(DeviceIndex, @oConfig[0], L);
      if Result <> ERROR_SUCCESS then Exit;

      try
        bBip := (oConfig[$00] and 1) <> 0; //Select bip or unip ref based on how they've set channel 0.
        nConfig[$00] := oConfig[$00]; //Use their selected range.
        case CalRefIndex of
          0: if bBip then //Lo ref.
            nConfig[$10] := $05
          else
            nConfig[$10] := $01
          ;
          1: if bBip then //Hi ref.
            nConfig[$10] := $07
          else
            nConfig[$10] := $03
          ;
          else begin
            Result := ERROR_INVALID_INDEX;
            Exit;
          end;
        end;
        nConfig[$13] := $FF; //Max oversample, make sure we get a good read.
        nConfig[$12] := $00; //Scan one channel.
        if ConfigBytes > $14 then nConfig[$14] := $00; //Scan one channel.
        ADC_SetConfig(DeviceIndex, @nConfig[0], L);

        SetLength(ADData, ADCMUXChannels);
        Result := ADC_GetScanV(DeviceIndex, @ADData[0]);
        if Result <> ERROR_SUCCESS then Exit;
      finally
        L := ConfigBytes;
        ADC_SetConfig(DeviceIndex, @oConfig[0], L);
        SetLength(oConfig, 0);
        SetLength(nConfig, 0);
      end;

      pRef := ADData[0];
      //Result := ERROR_SUCCESS;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_GetBuf(DeviceIndex: LongWord; out pData: Pointer; out BufSize: LongWord; pReserved: Pointer; Timeout: Double): LongWord; cdecl;
var
  oADCContAcqWorker: TADCContAcqWorker;
  oADCContBufWorker: TADCContBufWorker;
  pThisBuf: PContBuf;
  mTimeoutEnd: LongWord;

{$J+}
const
  pLastBuf: PContBuf = nil;
{$J-}

  function mTimeoutLeft: LongWord;
  begin
    if Timeout = Infinity then
      Result := INFINITE
    else begin
      Result := mTimeoutEnd - GetTickCount;
      if LongInt(Result) < 0 then Result := 0;
    end;
  end;

begin
  try
    try
      pData := nil;
      BufSize := 0;
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not (bADCBulk or bADCDIOStream) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      oADCContAcqWorker := ADCContAcqWorker;
      oADCContBufWorker := ADCContBufWorker;

      pThisBuf := pLastBuf;
      pLastBuf := nil;
      if pThisBuf <> nil then begin
        if oADCContBufWorker <> nil then
          oADCContBufWorker.PutBlankBuf(pThisBuf)
        else
          Dispose(pThisBuf)
        ;
      end;

      if (oADCContAcqWorker = nil) or (oADCContBufWorker = nil) then begin
        Result := ERROR_NOT_SUPPORTED;
        Exit;
      end;

      if Timeout <> Infinity then
        mTimeoutEnd := GetTickCount + Round(1000 * Timeout)
      ;

      repeat
        pThisBuf := oADCContBufWorker.GetDataBuf(mTimeoutLeft);
        if pThisBuf = nil then begin
          Result := ERROR_NO_DATA;
          Exit;
        end;
        if pThisBuf.UsedSize <> 0 then break;

        oADCContBufWorker.PutBlankBuf(pThisBuf);
      until False;

      pLastBuf := pThisBuf;
      pData := @pLastBuf.ADBuf[0];
      BufSize := pLastBuf.UsedSize;
      //pLastBuf.Flags
    end;

  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_ReadData(DeviceIndex: LongWord; pConfigBuf: Pointer; var ScansToRead: LongWord; pData: PDouble; Timeout: Double): LongWord; cdecl;
var
  oADCContAcqWorker: TADCContAcqWorker;
  oADCContBufWorker: TADCContBufWorker;
  oRingAcqData: TPRingAcqData;
  mTimeoutEnd: LongWord;
  StartCh, StopCh,
  Oversample, ScanChannels, ScanSamples, SamplesToRead, ScansInRing, ScansRead,
  Transfer: LongWord;
  ADBuf: array of Word;

  function ConfigByte(Offset: Integer): Byte;
  var
    pConfigByte: PByte;

  begin
    pConfigByte := pConfigBuf;
    Inc(pConfigByte, Offset);
    Result := pConfigByte^;
  end;

  function RingSamplesLeft(pRing: TPRingAcqData): LongWord;
  begin
    if pRing = nil then
      Result := 0
    else begin
      Result := pRing.iNextWrite - pRing.iNextRead;
      if LongInt(Result) < 0 then Inc(Result, Length(pRing.RingBuffer));
    end;
  end;

  procedure ReadRingSamples(ToIndex, Count: LongWord);
  var
    nNextRead, RingBufLen: LongWord;

  begin
    with Dev[DeviceIndex].pRingAcqData^ do begin
      //This is the write authority for iNextRead.
      RingBufLen := Length(RingBuffer);
      nNextRead := iNextRead + Count;
      if nNextRead < RingBufLen then begin
        Move(RingBuffer[iNextRead], ADBuf[ToIndex], 2*Count);
      end
      else if nNextRead = RingBufLen then begin
        nNextRead := 0;
        Move(RingBuffer[iNextRead], ADBuf[ToIndex], 2*Count);
      end
      else begin
        Dec(nNextRead, RingBufLen);
        Transfer := RingBufLen - iNextRead;
        Move(RingBuffer[iNextRead], ADBuf[ToIndex], 2*Transfer);
        Move(RingBuffer[0], ADBuf[ToIndex + Transfer], 2*nNextRead);
      end;
      iNextRead := nNextRead;
    end;
  end;

  function WaitForData: Boolean;
  var
    mTimeoutLeft: LongWord;

  begin
    if Timeout = Infinity then
      mTimeoutLeft := INFINITE
    else begin
      mTimeoutLeft := mTimeoutEnd - GetTickCount;
      if LongInt(mTimeoutLeft) < 0 then begin
        Result := False;
        Exit;
      end;
    end;
    Result := WaitForSingleObject(Dev[DeviceIndex].pRingAcqData.hSem, mTimeoutLeft) <> ERROR_TIMEOUT;
  end;

  procedure PrepareData;
  var
    ThisCh: LongWord;
    iSample, iOversample, iADBuf, Ct: Integer;
    OvScale: Double;
    Range: Byte;
    pIData: PDouble;
    DITSData: LongWord;

  begin
    pIData := pData;
    ThisCh := StartCh;
    iADBuf := 0;
    if Dev[DeviceIndex].bADCBulk then begin
      OvScale := 1/$10000 / Oversample;
      for iSample := 0 to ScansToRead*ScanChannels - 1 do begin
        Range := ConfigByte(ThisCh shr Dev[DeviceIndex].RangeShift);
        {
        V := 0;
        for iOversample := 0 to Oversample-1 do
          V := V + ADBuf[iADBuf + iOversample]
        ;
        Inc(iADBuf, Oversample);
        V := 1/65536 * V / Oversample;

        if (Range and 1) <> 0 then V := V * 2 - 1;
        if (Range and 2) = 0 then V := V * 2;
        if (Range and 4) = 0 then V := V * 5;
        }
        Ct := 0;
        for iOversample := 0 to Oversample-1 do
          Ct := Ct + ADBuf[iADBuf + iOversample]
        ;
        Inc(iADBuf, Oversample);

        if (Range and 1) <> 0 then Ct := Ct * 2 - ($10000 * LongInt(Oversample));
        if (Range and 2) = 0 then Ct := Ct * 2;
        if (Range and 4) = 0 then Ct := Ct * 5;
        pIData^ := OvScale * Ct;
        Inc(pIData);

        if ThisCh = StopCh then
          ThisCh := StartCh
        else
          ThisCh := (ThisCh + 1) mod Dev[DeviceIndex].ADCMUXChannels
        ;
      end;
    end
    else begin
      DITSData := 0; //For the compiler.
      for iSample := 0 to ScansToRead*ScanChannels - 1 do begin
        case ThisCh of
          0..1: begin
            Range := ConfigByte(ThisCh shr Dev[DeviceIndex].RangeShift);
            Ct := ADBuf[iADBuf];
            Inc(iADBuf);
            if (Range and 1) <> 0 then Ct := Ct * 2 - ($10000 * LongInt(Oversample));
            if (Range and 2) = 0 then Ct := Ct * 2;
            if (Range and 4) = 0 then Ct := Ct * 5;
            pIData^ := 1/$10000 * Ct;
            Inc(pIData);
          end;
          2: begin
            DITSData := ADBuf[iADBuf];
            Inc(iADBuf);
          end;
          3: begin
            DITSData := (DITSData shl 16) or ADBuf[iADBuf]; //It's middle-endian(2301) in the buffer, so flip it around.
            Inc(iADBuf);
            pIData^ := DITSData;
            Inc(pIData);
          end;
        end;

        ThisCh := (ThisCh + 1) mod 4;
      end;
    end;
  end;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bADCBulk or bADCDIOStream then begin
        //Currently only supports cont ring mode. In the future, should support bulk block mode, and hypothetically whatever the hell it would mean to support cont callback mode.
        oADCContAcqWorker := ADCContAcqWorker;
        oADCContBufWorker := ADCContBufWorker;
        oRingAcqData := pRingAcqData;
        if (oADCContAcqWorker = nil) or (oADCContBufWorker = nil) or (oRingAcqData = nil) then begin
          Result := ERROR_NOT_SUPPORTED;
          Exit;
        end;

        if ScansToRead = 0 then Exit; //Requested nop, fast return success.

        if bADCBulk then begin
          StartCh := (ConfigByte($12) and $F) or ((ConfigByte($14) shl 4) and $F0);
          StopCh := ((ConfigByte($12) shr 4) and $F) or (ConfigByte($14) and $F0);
          Oversample := 1 + ConfigByte($13);
        end
        else begin
          StartCh := 0;
          StopCh := 3;
          Oversample := 1;
        end;
        if StopCh < StartCh then
          ScanChannels := ADCMUXChannels + StartCh - StopCh + 1
        else
          ScanChannels := StopCh - StartCh + 1
        ;
        ScanSamples := ScanChannels * Oversample;
        SamplesToRead := ScanSamples * ScansToRead;
        SetLength(ADBuf, SamplesToRead);

        if Timeout = 0 then begin //They want whatever we already have.
          ScansRead := 0;
          ScansInRing := RingSamplesLeft(pRingAcqData) div ScanSamples;
          if ScansInRing > 0 then begin
            if ScansInRing > ScansToRead then
              ScansInRing := ScansToRead
            ;
            ReadRingSamples(0, ScanSamples * ScansInRing);
            ScansToRead := ScansInRing;
          end
          else begin
            ScansToRead := 0;
            Result := ERROR_TIMEOUT;
          end;
          if ScansRead > 0 then
            PrepareData
          else
            Result := ERROR_TIMEOUT
          ;
        end
        else if Timeout < 0 then begin //They want all or nothing.
          Timeout := -Timeout;
          if Timeout <> Infinity then
            mTimeoutEnd := GetTickCount + Round(1000 * Timeout)
          ;
          while RingSamplesLeft(pRingAcqData) < SamplesToRead do
            if not WaitForData then begin
              ScansToRead := 0;
              Result := ERROR_TIMEOUT;
              Exit;
            end
          ;

          ReadRingSamples(0, SamplesToRead);
          PrepareData;
        end
        else begin //They want everything we can give them.
          ScansRead := 0;
          if Timeout <> Infinity then
            mTimeoutEnd := GetTickCount + Round(1000 * Timeout)
          ;
          repeat
            ScansInRing := RingSamplesLeft(pRingAcqData) div ScanSamples;
            if ScansInRing > 0 then begin
              if ScansInRing >= ScansToRead - ScansRead then
                ScansInRing := ScansToRead - ScansRead
              ;
              ReadRingSamples(ScanSamples * ScansRead, ScanSamples * ScansInRing);
              Inc(ScansRead, ScansInRing);
              if ScansRead >= ScansToRead then
                Break
              ;
            end;

          until not WaitForData;
          ScansToRead := ScansRead;
          if ScansRead > 0 then
            PrepareData
          else
            Result := ERROR_TIMEOUT
          ;
        end;
      end
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_FullStartRing(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord; CalFileName: PAnsiChar; pCounterHz: PDouble; RingBufferSize: LongWord; PacketsPerBlock: LongWord): LongWord; cdecl;
var
  bCounterTriggered: Boolean;
  Content: AnsiString;
  Hz: Double;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if bADCBulk or bADCDIOStream then begin
        if (ConfigBytes = 0) then begin
          Result := ERROR_BAD_TOKEN_TYPE;
          Exit;
        end;

        if ConfigBufSize < ConfigBytes then begin
          Result := ERROR_INSUFFICIENT_BUFFER;
          ConfigBufSize := ConfigBytes;
          Exit;
        end;

        if pConfigBuf = nil then begin
          Result := ERROR_INVALID_PARAMETER;
          Exit;
        end;

        SetString(Content, PAnsiChar(pConfigBuf), ConfigBytes); //probe config buffer
        Content := '';

        if bADCBulk then begin
          bCounterTriggered := (PByteArray(pConfigBuf)[$11] and $01) <> 0;

          if bCounterTriggered then begin
            Hz := 0;
            Result := CTR_StartOutputFreq(DeviceIndex, 0, @Hz);
            if Result <> ERROR_SUCCESS then Exit;
          end;
        end
        else begin
          bCounterTriggered := False;
        end;

        Result := ADC_SetConfig(DeviceIndex, pConfigBuf, ConfigBufSize);
        if Result <> ERROR_SUCCESS then Exit;

        if bADCBulk and (CalFileName <> nil) then begin
          Result := ADC_SetCal(DeviceIndex, CalFileName);
          if (Result <> ERROR_SUCCESS) and (Result <> ERROR_NOT_SUPPORTED) then Exit;
        end;

        Result := ADC_BulkContinuousRingStart(DeviceIndex, RingBufferSize, PacketsPerBlock);
        if Result <> ERROR_SUCCESS then Exit;

        if bADCDIOStream then try
          if pCounterHz <> nil then
            pCounterHz^ := RootClock
          ;
        except
        end
        else if bCounterTriggered then
          CTR_StartOutputFreq(DeviceIndex, 0, pCounterHz)
        ;
      end
      else begin
        Result := ERROR_BAD_TOKEN_TYPE;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;



function ADC_InitFastITScanV(DeviceIndex: LongWord): LongWord; cdecl;
var
  I: Integer;
  L: LongWord;
  Dat: Byte;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ConfigBytes < 20 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      SetLength(FastITConfig, ConfigBytes);
      SetLength(FastITBakConfig, ConfigBytes);

      L := ConfigBytes;
      Result := ADC_GetConfig(DeviceIndex, @FastITBakConfig[0], L);
      if Result <> ERROR_SUCCESS then Exit;

      for I := 0 to 15 do FastITConfig[I] := FastITBakConfig[I]; //Use their range codes.
      //FastITConfig[$11] := $04 or (FastITBakConfig[$11] and $10); //Software-start scan, use their CTR0 EXT bit.
      FastITConfig[$11] := $05 or (FastITBakConfig[$11] and $10); //Timer scan, use their CTR0 EXT bit.
      FastITConfig[$13] := Max(3, FastITBakConfig[$13]); //Oversample at least +3.
      Dat := Min(64, ADCMUXChannels) - 1;
      FastITConfig[$12] := Dat shl 4;
      FastITConfig[$14] := Dat and $F0;
      Result := ADC_SetConfig(DeviceIndex, @FastITConfig[0], L);
      if Result <> ERROR_SUCCESS then begin
        ADC_SetConfig(DeviceIndex, @FastITBakConfig[0], L);
        Exit;
      end;
      Dat := $01;
      Result := GenericVendorWrite(DeviceIndex, $D4, $1E, 0, SizeOf(Dat), @Dat);
      if Result <> ERROR_SUCCESS then ADC_SetConfig(DeviceIndex, @FastITBakConfig[0], L);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_ResetFastITScanV(DeviceIndex: LongWord): LongWord; cdecl;
var
  L: LongWord;
  Dat: Byte;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ConfigBytes < 20 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      L := Length(FastITBakConfig);
      Result := ADC_SetConfig(DeviceIndex, @FastITBakConfig[0], L);
      if Result <> ERROR_SUCCESS then Exit;

      Dat := $00;
      Result := GenericVendorWrite(DeviceIndex, $D4, $1E, 0, SizeOf(Dat), @Dat);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_SetFastITScanVChannels(DeviceIndex, NewChannels: LongWord): LongWord; cdecl;
var
  L: LongWord;
  Dat: Byte;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ConfigBytes < 20 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if Length(FastITConfig) < 20 then begin
        Result := ERROR_NOT_READY;
        Exit;
      end;

      L := Length(FastITConfig);
      Dat := Min(NewChannels, ADCMUXChannels) - 1;
      FastITConfig[$12] := Dat shl 4;
      FastITConfig[$14] := Dat and $F0;
      Result := ADC_SetConfig(DeviceIndex, @FastITConfig[0], L);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_GetFastITScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; cdecl;
var
  ADBuf: TWordArray;
  I, Ch, J, Tot, Wt: Integer;
  V: Double;
  StartChannel, EndChannel, Channels, RangeCode: Byte;
  //Dummy: Word;
  BytesLeft: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ConfigBytes < 20 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      //Determine channels.
      StartChannel := FastITConfig[$12] and $F;
      EndChannel := FastITConfig[$12] shr 4;
      if ConfigBytes >= 21 then begin
        StartChannel := StartChannel or ((FastITConfig[20] and $F) shl 4);
        EndChannel := EndChannel or (FastITConfig[20] and $F0);
      end;
      Channels := EndChannel - StartChannel + 1;

      //Set array to receive scan(=channels * (1+oversample)).
      SetLength(ADBuf, Channels * (1 + FastITConfig[$13]));

      //Begin get-data.
      Result := ADC_BulkAcquire(DeviceIndex, Length(ADBuf) * SizeOf(ADBuf[0]), @ADBuf[0]);
      if Result <> ERROR_SUCCESS then Exit;
      CTR_8254Mode(DeviceIndex, 0, 2, 0);
      CTR_8254Mode(DeviceIndex, 0, 2, 1);
      //ADC_GetImmediate(DeviceIndex, 0, @Dummy);

      //Complete get-data.
      if WaitForSingleObject(ADCWorker.Handle, 1000) <> WAIT_OBJECT_0 then begin
        Result := ERROR_TIMEOUT;
        Exit;
      end;
      Result := ADC_BulkPoll(DeviceIndex, BytesLeft);
      if Result <> ERROR_SUCCESS then Exit;
      if BytesLeft <> 0 then begin
        Result := ERROR_HANDLE_EOF;
        Exit;
      end;

      //Condition data; cull 75%(round down) of samples per channel from first block of channels, cull first from others, and average.
      I := 0;
      Inc(pBuf, StartChannel);
      for Ch := StartChannel to EndChannel do begin
        RangeCode := FastITConfig[Ch shr RangeShift];

        Tot := 0;
        Wt := 0;
        if (Ch shr RangeShift) = 0 then J := 4 else J := 1; //Discard first 4 samples from first 8 channels, and first 1 sample from other channels.
        J := Min(J, FastITConfig[$13]); //Except always keep at least one sample.
        for J := J to FastITConfig[$13] do begin
          Tot := Tot + ADBuf[I * (1 + FastITConfig[$13]) + J];
          Inc(Wt);
        end;

        V := Tot / Wt * (1 / 65536);
        if (RangeCode and 1) <> 0 then V := V * 2 - 1;
        if (RangeCode and 2) = 0 then V := V * 2;
        if (RangeCode and 4) = 0 then V := V * 5;
        pBuf^ := V;

        Inc(pBuf);
        Inc(I);
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function ADC_GetITScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; cdecl;
begin
  try
    Result := ADC_InitFastITScanV(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;
    Result := ADC_GetFastITScanV(DeviceIndex, pBuf);
    if Result <> ERROR_SUCCESS then begin
      ADC_ResetFastITScanV(DeviceIndex);
      Exit;
    end;
    Result := ADC_ResetFastITScanV(DeviceIndex);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;


// J2H New Code added 20130401 for Jeff Smith: Convert "Fast IT" code to CSA generic

function ADC_CSA_InitFastScanV(DeviceIndex: LongWord): LongWord; cdecl;
var
  I: Integer;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ConfigBytes < 20 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      SetLength(CSA_FastConfig, ConfigBytes);
      SetLength(CSA_FastBakConfig, ConfigBytes);

      L := ConfigBytes;
      Result := ADC_GetConfig(DeviceIndex, @CSA_FastBakConfig[0], L);     // backup existing config
      if Result <> ERROR_SUCCESS then Exit;

      for I := 0 to 15 do CSA_FastConfig[I] := CSA_FastBakConfig[I]; //Use their range codes.
      CSA_FastConfig[$11] := $05 or (CSA_FastBakConfig[$11] and $10); //Timer scan, use their CTR0 EXT bit.
      CSA_FastConfig[$13] := Max(1, CSA_FastBakConfig[$13]); //Oversample at least +1.

      //Use their start & end channel.
      CSA_FastConfig[$12] := CSA_FastBakConfig[$12];
      if ConfigBytes > $14 then
        CSA_FastConfig[$14] := CSA_FastBakConfig[$14]
      ;

      Result := ADC_SetConfig(DeviceIndex, @CSA_FastConfig[0], L);
      if Result <> ERROR_SUCCESS then begin
        ADC_SetConfig(DeviceIndex, @CSA_FastBakConfig[0], L);
        Exit;
      end;

      if Result <> ERROR_SUCCESS then ADC_SetConfig(DeviceIndex, @CSA_FastBakConfig[0], L);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;


function ADC_CSA_ResetFastScanV(DeviceIndex: LongWord): LongWord; cdecl;
var
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ConfigBytes < 20 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      L := Length(CSA_FastBakConfig);
      Result := ADC_SetConfig(DeviceIndex, @CSA_FastBakConfig[0], L);
      if Result <> ERROR_SUCCESS then Exit;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;



function ADC_CSA_GetFastScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; cdecl;
var
  ADBuf: TWordArray;
  I, Ch, J, Tot, Wt: Integer;
  V: Double;
  StartChannel, EndChannel, Channels, RangeCode: Byte;
  //Dummy: Word;
  BytesLeft: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bADCBulk then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ConfigBytes < 20 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      //Determine channels.
      StartChannel := CSA_FastConfig[$12] and $F;
      EndChannel := CSA_FastConfig[$12] shr 4;
      if ConfigBytes >= 21 then begin
        StartChannel := StartChannel or ((CSA_FastConfig[20] and $F) shl 4);
        EndChannel := EndChannel or (CSA_FastConfig[20] and $F0);
      end;
      Channels := EndChannel - StartChannel + 1;

      //Set array to receive scan(=channels * (1+oversample)).
      SetLength(ADBuf, Channels * (1 + CSA_FastConfig[$13]));

      //Begin get-data.
      Result := ADC_BulkAcquire(DeviceIndex, Length(ADBuf) * SizeOf(ADBuf[0]), @ADBuf[0]);
      if Result <> ERROR_SUCCESS then Exit;
      //ADC_GetImmediate(DeviceIndex, 0, @Dummy);

      //Complete get-data.
      if WaitForSingleObject(ADCWorker.Handle, 1000) <> WAIT_OBJECT_0 then begin
        Result := ERROR_TIMEOUT;
        Exit;
      end;
      Result := ADC_BulkPoll(DeviceIndex, BytesLeft);
      if Result <> ERROR_SUCCESS then Exit;
      if BytesLeft <> 0 then begin
        Result := ERROR_HANDLE_EOF;
        Exit;
      end;

      //Condition data; cull first sample per channel, and average.
      I := 0;
      Inc(pBuf, StartChannel);
      for Ch := StartChannel to EndChannel do begin
        RangeCode := CSA_FastConfig[Ch shr RangeShift];

        Tot := 0;
        Wt := 0;
        J := Min(1, CSA_FastConfig[$13]); //Discard first sample, except always keep at least one sample.
        for J := J to CSA_FastConfig[$13] do begin
          Tot := Tot + ADBuf[I * (1 + CSA_FastConfig[$13]) + J];
          Inc(Wt);
        end;

        V := Tot / Wt * (1 / 65536);
        if (RangeCode and 1) <> 0 then V := V * 2 - 1;
        if (RangeCode and 2) = 0 then V := V * 2;
        if (RangeCode and 4) = 0 then V := V * 5;
        pBuf^ := V;

        Inc(pBuf);
        Inc(I);
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;




function AIOUSB_OfflineWrite1(DeviceIndex: LongWord; SampleIndex: LongWord; Buf: Word): LongWord; cdecl;
//var
//  Data: AnsiString;

begin
  Result := ERROR_NOT_SUPPORTED;
  {
  Result := ValidateAndEnsureOpen(DeviceIndex);
  if Result <> ERROR_SUCCESS then Exit;

  SetString(Data, PAnsiChar(@Buf), 2);

  Result := GenericVendorWrite(DeviceIndex, AUR_OFFLINE_READWRITE, SampleIndex, SampleIndex shr 16, Length(Data), PAnsiChar(Data));
  }
end;

function AIOUSB_OfflineRead1(DeviceIndex: LongWord; SampleIndex: LongWord; pBuf: PWord): LongWord; cdecl;
//var
//  Buf: Word;
//  L: LongWord;

begin
  Result := ERROR_NOT_SUPPORTED;
  {
  Result := ValidateAndEnsureOpen(DeviceIndex);
  if Result <> ERROR_SUCCESS then Exit;

  with Dev[DeviceIndex] do begin
    L := SizeOf(Buf);
    Result := GenericVendorRead(DeviceIndex, AUR_OFFLINE_READWRITE, SampleIndex, SampleIndex shr 16, L, @Buf);

    if Result = ERROR_SUCCESS then begin
      pBuf^ := Buf;
    end;
  end;
  }
end;





function DIO_Configure(DeviceIndex: LongWord; Tristate: ByteBool; pOutMask: Pointer; pData: Pointer): LongWord; cdecl;
var
  Content: AnsiString;
  Data, OutMask, COSMask: AnsiString;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if DIOBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if (pOutMask = nil) or (pData = nil) then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      SetString(Data, PAnsiChar(pData), DIOBytes);
      Move(Data[1], LastDIOData[0], DIOBytes);
      L := (DIOConfigBits + 7) div 8;
      SetString(OutMask, PAnsiChar(pOutMask), L);
      COSMask := StringOfChar(AnsiChar(#$00), L);

      Content := Data + OutMask + COSMask;
      Result := GenericVendorWrite(DeviceIndex, AUR_DIO_CONFIG, Ord(Tristate), 0, Length(Content), PAnsiChar(Content));
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_ConfigureEx(DeviceIndex: LongWord; pOutMask: Pointer; pData: Pointer; pTristateMask: Pointer): LongWord; cdecl;
var
  Content: AnsiString;
  Data, OutMask, TriMask: AnsiString;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if (DIOBytes = 0) or (Tristates = 0) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if (pOutMask = nil) or (pData = nil) or (pTristateMask = nil) then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      SetString(Data, PAnsiChar(pData), DIOBytes);
      Move(Data[1], LastDIOData[0], DIOBytes);
      L := (DIOConfigBits + 7) div 8;
      SetString(OutMask, PAnsiChar(pOutMask), L);
      L := (Tristates + 7) div 8;
      SetString(TriMask, PAnsiChar(pTristateMask), L);

      Content := Data + OutMask + TriMask;
      Result := GenericVendorWrite(DeviceIndex, AUR_DIO_CONFIG, 0, DIOBytes, Length(Content), PAnsiChar(Content));
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_ConfigurationQuery(DeviceIndex: LongWord; pOutMask: Pointer; pTristateMask: Pointer): LongWord; cdecl;
var
  Content: AnsiString;
  OutMask, TriMask: AnsiString;
  L, OutL, TriL: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if (Tristates = 0) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if (pOutMask = nil) or (pTristateMask = nil) then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      OutL := (DIOConfigBits + 7) div 8;
      TriL := (Tristates + 7) div 8;

      L := OutL + TriL;
      SetString(Content, nil, L);
      Result := GenericVendorRead(DeviceIndex, AUR_DIO_CONFIG_QUERY, 0, DIOBytes, L, PAnsiChar(Content));
      //OutMask + TriMask := Content;
      OutMask := Copy(Content, 1, OutL);
      TriMask := Copy(Content, 1 + OutL, TriL);
      Move(OutMask[1], pOutMask^, OutL);
      Move(TriMask[1], pTristateMask^, TriL);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_ConfigureMasked(DeviceIndex: LongWord; pOuts: Pointer; pOutsMask: Pointer; pData: Pointer; pDataMask: Pointer; pTristates: Pointer; pTristatesMask: Pointer): LongWord; cdecl;

  function StringOfByte(B: Byte; Count: Integer): AnsiString;
  begin
    SetString(Result, nil, Count);
    FillChar(Result[1], Count, B);
  end;

  procedure SetBuffersFromPointers(out DataBuf, MaskBuf: AnsiString; DefDataByte, DefMaskByte: Byte; Len: Integer; pThisData, pThisMask: PAnsiChar);
  begin
    if pThisMask = nil then begin
      if pThisData = nil then begin
        DataBuf := StringOfByte(DefDataByte, Len);
        MaskBuf := StringOfByte(DefMaskByte, Len);
      end
      else begin
        SetString(DataBuf, PAnsiChar(pThisData), Len);
        MaskBuf := StringOfByte($FF, Len);
      end;
    end
    else begin
      if pThisData = nil then begin
        DataBuf := StringOfByte(DefDataByte, Len);
        SetString(MaskBuf, PAnsiChar(pThisMask), Len);
      end
      else begin
        SetString(DataBuf, PAnsiChar(pThisData), Len);
        SetString(MaskBuf, PAnsiChar(pThisMask), Len);
      end;
    end;
  end;

var
  Data, DataMask, Outs, OutsMask, Tris, TrisMask,
  Content: AnsiString;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if (DIOBytes = 0) or (Tristates = 0) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      SetBuffersFromPointers(Data, DataMask, $FF, $00, DIOBytes, pData, pDataMask);
      SetBuffersFromPointers(Outs, OutsMask, $00, $00, (DIOConfigBits + 7) div 8, pOuts, pOutsMask);
      SetBuffersFromPointers(Tris, TrisMask, $00, $FF, (Tristates + 7) div 8, pTristates, pTristatesMask);

      Move(Data[1], LastDIOData[0], DIOBytes);

      Content := OutsMask + Outs + DataMask + Data + TrisMask + Tris;
      Result := GenericVendorWrite(DeviceIndex, AUR_DIO_CONFIG_MASKED, 0, 0, Length(Content), PAnsiChar(Content));
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_Write1(DeviceIndex, BitIndex: LongWord; Data: ByteBool): LongWord; cdecl;
var
  ByteIndex: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if DIOBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      ByteIndex := BitIndex div 8;

      if ByteIndex >= DIOBytes then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      if Data then
        LastDIOData[ByteIndex] := LastDIOData[ByteIndex] or (1 shl (BitIndex and 7))
      else
        LastDIOData[ByteIndex] := LastDIOData[ByteIndex] and not (1 shl (BitIndex and 7))
      ;

      if bFirmware20 and bDevHasPNPByte(PNPData.HasDIOWrite1) and (PNPData.HasDIOWrite1 <> 0) then
        Result := GenericVendorWrite(DeviceIndex, AUR_DIO_WRITE, Ord(Data), BitIndex, 0, nil)
      else
        Result := GenericVendorWrite(DeviceIndex, AUR_DIO_WRITE, 0, 0, DIOBytes, @LastDIOData[0])
      ;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_Write8(DeviceIndex, ByteIndex: LongWord; Data: Byte): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if DIOBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ByteIndex >= DIOBytes then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      LastDIOData[ByteIndex] := Data;

      Result := GenericVendorWrite(DeviceIndex, AUR_DIO_WRITE, 0, 0, DIOBytes, @LastDIOData[0]);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_WriteAll(DeviceIndex: LongWord; pData: Pointer): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if DIOBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Move(pData^, LastDIOData[0], DIOBytes);

      Result := GenericVendorWrite(DeviceIndex, AUR_DIO_WRITE, 0, 0, DIOBytes, @LastDIOData[0]);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_Read1(DeviceIndex, BitIndex: LongWord; Buffer: PByte): LongWord; cdecl;
var
  Content: AnsiString;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if DIOBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if BitIndex >= DIOBytes * 8 then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      L := DIOBytes;
      SetString(Content, nil, L);
      Result := GenericVendorRead(DeviceIndex, AUR_DIO_READ, 0, 0, L, PAnsiChar(Content));

      if Result = ERROR_SUCCESS then begin

        if (Byte(Content[(BitIndex div 8) + 1]) and (1 shl (BitIndex mod 8))) <> 0 then
          Buffer^ := 1
        else
          Buffer^ := 0
        ;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_Read8(DeviceIndex, ByteIndex: LongWord; Buffer: PByte): LongWord; cdecl;
var
  Content: AnsiString;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if DIOBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if ByteIndex >= DIOBytes then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      L := DIOBytes;
      SetString(Content, nil, L);
      Result := GenericVendorRead(DeviceIndex, AUR_DIO_READ, 0, 0, L, PAnsiChar(Content));

      if Result = ERROR_SUCCESS then begin
        PAnsiChar(Buffer)^ := Content[ByteIndex + 1];
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_ReadAll(DeviceIndex: LongWord; pData: Pointer): LongWord; cdecl;
var
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if DIOBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      L := DIOBytes;
      Result := GenericVendorRead(DeviceIndex, AUR_DIO_READ, 0, 0, L, pData);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_SetWatchdog16(DeviceIndex: LongWord; Delay, Data: Word): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if DIOBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      case PID of
        $8010, $8011, $8012, $8014, $8015, $8016: ; //USB-IIRO-16 family
        else begin
          Result := ERROR_BAD_TOKEN_TYPE;
          Exit;
        end;
      end;

      Result := GenericVendorWrite(DeviceIndex, AUR_DIO_WDG16_DEPREC, Delay, Data, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function SetWatchdog(DeviceIndex: LongWord; var Delay: Double; pData: Pointer): LongWord; cdecl;
var
  DV: Word;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if WDGBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      DV := Max(1, Round(Delay));
      Delay := DV;
      Result := GenericVendorWrite(DeviceIndex, AUR_WDG, 0, 0, WDGBytes, pData);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;



function DIO_StreamOpen(DeviceIndex: LongWord; bIsRead: LongBool): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bDIOStream then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if bDIOOpen then begin
        Result := ERROR_TOO_MANY_OPEN_FILES;
        Exit;
      end;

      //Result := DoSetIFace(Handle, $100);
      //if Result <> ERROR_SUCCESS then Exit;

      if bIsRead then begin
        bDIORead := True;

        Result := GenericVendorWrite(DeviceIndex, $BC, 0, 0, 0, nil);
      end
      else begin
        bDIORead := False;

        Result := GenericVendorWrite(DeviceIndex, $BB, 0, 0, 0, nil);
      end;
      if Result <> ERROR_SUCCESS then Exit;

      bDIOOpen := True;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function WordAsStr(W: Word): AnsiString;
begin
  SetString(Result, PAnsiChar(@W), 2);
end;

function DIO_StreamSetClocks(DeviceIndex: LongWord; var ReadClockHz, WriteClockHz: Double): LongWord; cdecl;
var
  {
  Content: AnsiString;
  pDB: PByte;
  pDW: PWord absolute pDB;
  }
  DCD: TDIO16ClockData;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bDIOStream then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      {
      if not bDIOOpen then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;
      }

      {
      SetString(Content, nil, 5);
      pDB := PByte(PAnsiChar(Content));
      pDB^ := $00;
      if WriteClockHz = 0 then Inc(pDB^, 1);
      if  ReadClockHz = 0 then Inc(pDB^, 2);
      Inc(pDB);
      pDW^ := OctDacFromFreq(WriteClockHz);
      Inc(pDW);
      pDW^ := OctDacFromFreq(ReadClockHz);

      Result := GenericVendorWrite(DeviceIndex, AUR_DIO_SETCLOCKS, 0, 0, Length(Content), PAnsiChar(Content));
      }
      DCD.Disables := 0;
      if WriteClockHz = 0 then Inc(DCD.Disables, 1);
      if  ReadClockHz = 0 then Inc(DCD.Disables, 2);
      DCD.WriteOctDac := OctDacFromFreq(WriteClockHz);
      DCD.ReadOctDac := OctDacFromFreq(ReadClockHz);
      Result := GenericVendorWrite(DeviceIndex, AUR_DIO_SETCLOCKS, 0, 0, SizeOf(DCD), @DCD);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_StreamClose(DeviceIndex: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bDIOStream then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bDIOOpen then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      bDIOOpen := False;
      Result := ERROR_SUCCESS;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_StreamFrame(DeviceIndex, FramePoints: LongWord; pFrameData: PWord; var BytesTransferred: LongWord): LongWord; cdecl;
var
  TargetPipe: LongWord;
  L: LongWord;

begin
  try
    BytesTransferred := 0;

    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bDIOStream then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bDIOOpen then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      if FramePoints <= 0 then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      if bDIORead then
        TargetPipe := $86
      else
        TargetPipe := $02
      ;

      while FramePoints > StreamingBlockSize do begin
        L := 0;
        Result := _GenericBulk(DeviceIndex, TargetPipe, pFrameData, StreamingBlockSize * 2, L);
        if L < StreamingBlockSize * 2 then Result := ERROR_HANDLE_EOF;
        BytesTransferred := BytesTransferred + L;
        if Result <> ERROR_SUCCESS then Break;
        Inc(pFrameData, StreamingBlockSize);
        Dec(FramePoints, StreamingBlockSize);
      end;
      if (Result = ERROR_SUCCESS) and (FramePoints <> 0) then begin
        L := 0;
        Result := _GenericBulk(DeviceIndex, TargetPipe, pFrameData, FramePoints * 2, L);
        if Result = ERROR_SUCCESS then BytesTransferred := BytesTransferred + L;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_16A_SetFunctionDirection(DeviceIndex, DIOStreaming, SPIBus, DIOA, DIOB, DIOCH: LongWord): LongWord; cdecl;
const
  FDD_Input                 = $00000001;
  FDD_Output                = $00000010;
  FDD_                      = $00000011;
  FDM_HandshakeAuto         = $00000100;
  FDM_HandshakeSlave        = $00001000;
  FDM_HandshakeForcedMaster = $00010000;
  FDM_                      = $00011100;

begin
  //`@
  Result := ERROR_NOT_SUPPORTED;
end;



function MapCounterBlock(DeviceIndex: LongWord; var CounterIndex, BlockIndex: LongWord): LongWord;
begin
  Result := ERROR_SUCCESS;

  if BlockIndex = 0 then begin
    //Contiguous counter addressing
    BlockIndex := CounterIndex div 3;
    CounterIndex := CounterIndex mod 3;

    if BlockIndex >= Dev[DeviceIndex].Counters then
      Result := ERROR_INVALID_ADDRESS
    ;
  end
  else begin
    if (BlockIndex >= Dev[DeviceIndex].Counters)
    or (CounterIndex >= 3) then
      Result := ERROR_INVALID_ADDRESS
    ;
  end;
end;

function CTR_8254Mode(DeviceIndex, BlockIndex, CounterIndex, Mode: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Result := MapCounterBlock(DeviceIndex, CounterIndex, BlockIndex);
      if Result <> ERROR_SUCCESS then Exit;

      if Mode >= 6 then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      Mode := (CounterIndex shl 6) or (Mode shl 1) or $30;

      Result := GenericVendorWrite(DeviceIndex, AUR_CTR_MODE, BlockIndex or (Mode shl 8), 0, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_8254Load(DeviceIndex, BlockIndex, CounterIndex: LongWord; LoadValue: Word): LongWord; cdecl;
var
  Mode: Byte;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Result := MapCounterBlock(DeviceIndex, CounterIndex, BlockIndex);
      if Result <> ERROR_SUCCESS then Exit;

      Mode := (CounterIndex shl 6) //or (Mode shl 1) or $30
      ;

      Result := GenericVendorWrite(DeviceIndex, AUR_CTR_LOAD, BlockIndex or (Mode shl 8), LoadValue, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_8254ModeLoad(DeviceIndex, BlockIndex, CounterIndex, Mode: LongWord; LoadValue: Word): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Result := MapCounterBlock(DeviceIndex, CounterIndex, BlockIndex);
      if Result <> ERROR_SUCCESS then Exit;

      if Mode >= 6 then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      Mode := (CounterIndex shl 6) or (Mode shl 1) or $30;

      Result := GenericVendorWrite(DeviceIndex, AUR_CTR_MODELOAD, BlockIndex or (Mode shl 8), LoadValue, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_8254ReadModeLoad(DeviceIndex, BlockIndex, CounterIndex, Mode: LongWord; LoadValue: Word; pReadValue: PWord): LongWord; cdecl;
var
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Result := MapCounterBlock(DeviceIndex, CounterIndex, BlockIndex);
      if Result <> ERROR_SUCCESS then Exit;

      if Mode >= 6 then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      Mode := (CounterIndex shl 6) or (Mode shl 1) or $30;

      L := 2;
      Result := GenericVendorRead(DeviceIndex, AUR_CTR_MODELOAD, BlockIndex or (Mode shl 8), LoadValue, L, pReadValue);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_8254Read(DeviceIndex, BlockIndex, CounterIndex: LongWord; pReadValue: PWord): LongWord; cdecl;
var
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Result := MapCounterBlock(DeviceIndex, CounterIndex, BlockIndex);
      if Result <> ERROR_SUCCESS then Exit;

      L := 2;
      Result := GenericVendorRead(DeviceIndex, AUR_CTR_READ, BlockIndex or (CounterIndex shl 8), 0, L, pReadValue);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_8254ReadStatus(DeviceIndex, BlockIndex, CounterIndex: LongWord; pReadValue: PWord; pStatus: PByte): LongWord; cdecl;
var
  Content: AnsiString;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Result := MapCounterBlock(DeviceIndex, CounterIndex, BlockIndex);
      if Result <> ERROR_SUCCESS then Exit;

      L := 3;
      SetString(Content, nil, L);
      Result := GenericVendorRead(DeviceIndex, AUR_CTR_READ, BlockIndex or (CounterIndex shl 8), 0, L, PAnsiChar(Content));
      pReadValue^ := PWord(@Content[1])^;
      pStatus^    := PByte(@Content[3])^;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_8254ReadAll(DeviceIndex: LongWord; pData: PWord): LongWord; cdecl;
var
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      L := Counters * 3 * 2;
      Result := GenericVendorRead(DeviceIndex, AUR_CTR_READALL, 0, 0, L, pData);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_8254ReadLatched(DeviceIndex: LongWord; pData: PWord): LongWord; cdecl;
var
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      L := Counters * 3 * 2 + 1;
      Result := GenericVendorRead(DeviceIndex, AUR_CTR_READLATCHED, 0, 0, L, pData);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_8254SelectGate(DeviceIndex, GateIndex: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bGateSelectable then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if GateIndex >= Counters * 3 then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      Result := GenericVendorWrite(DeviceIndex, AUR_CTR_SELGATE, GateIndex, 0, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_StartOutputFreq(DeviceIndex, BlockIndex: LongWord; pHz: PDouble): LongWord; cdecl;
var
  L, DivisorA, DivisorB: LongWord;
  DivisorAB: Extended;
  Err, MinErr, Hz: Double;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if BlockIndex >= Counters then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      if pHz = nil then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      Hz := pHz^;
      if Hz <= 0 then begin
        CTR_8254Mode(DeviceIndex, BlockIndex, 1, 2);
        Result := CTR_8254Mode(DeviceIndex, BlockIndex, 2, 3);
      end
      else begin
        try
          if Hz * 4 >= RootClock then begin
            DivisorA := 2;
            DivisorB := 2;
          end
          else begin
            DivisorAB := RootClock / Hz;

            L := Round(SqRt(DivisorAB));
            DivisorA := Round(DivisorAB / L);
            DivisorB := L;
            MinErr := Abs(Hz - (RootClock / (DivisorA * L)));
            for L := L downto 2 do begin
              DivisorA := Round(DivisorAB / L);
              if DivisorA > $FFFF then Break; //Limited to 16 bits, so this and all further L are invalid.
              Err := Abs(Hz - (RootClock / (DivisorA * L)));
              if Err = 0 then begin
                DivisorB := L;
                Break;
              end;
              if Err < MinErr then begin
                DivisorB := L;
                MinErr := Err;
              end;
            end;
            DivisorA := Round(DivisorAB / DivisorB);
          end;
        except
          Result := ERROR_INVALID_DATA;
          Exit;
        end;

        //LastPurpose := AUR_CTR_PUR_OFRQ;

        pHz^ := RootClock / (DivisorA * DivisorB);

        CTR_8254ModeLoad(DeviceIndex, BlockIndex, 1, 2, DivisorA);
        Result := CTR_8254ModeLoad(DeviceIndex, BlockIndex, 2, 3, DivisorB);
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_SetWaitGates(DeviceIndex: LongWord; A, B: Byte): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bGateSelectable then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if A >= Counters * 3 then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      if B >= Counters * 3 then begin
        Result := ERROR_INVALID_ADDRESS;
        Exit;
      end;

      //DoSetIFace(Handle, $100);

      Result := GenericVendorWrite(DeviceIndex, AUR_CTR_COS_BULK_GATE2, 0, A or (B shl 8), 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_EndWaitGates(DeviceIndex: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bGateSelectable then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Result := GenericVendorWrite(DeviceIndex, AUR_CTR_COS_BULK_ABORT, 0, 0, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_WaitForGate(DeviceIndex: LongWord; GateIndex: Byte; var Content: Word): LongWord; cdecl;
var
  TargetPipe: LongWord;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if not bGateSelectable then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      case GateIndex of
        0: TargetPipe := $82;
        1: TargetPipe := $86;
        else begin
          Result := ERROR_INVALID_ADDRESS;
          Exit;
        end;
      end;

      L := 0;
      Result := AWU_GenericBulkIn(DeviceIndex, TargetPipe, @Content, SizeOf(Content), L);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

procedure TCtrMonitorThread.Execute;
var
  ReadingsA, ReadingsB: array of Word;
  I, L: Integer;
  bA: Boolean;

begin
  L := Length(MeasuredPulseWidth);
  SetLength(ReadingsA, L);
  SetLength(ReadingsB, L);
  CTR_8254ReadAll(DI, @ReadingsB[0]);
  bA := True;
  repeat
    if bA then
      CTR_8254ReadAll(DI, @ReadingsA[0])
    else
      CTR_8254ReadAll(DI, @ReadingsB[0])
    ;
    bA := not bA;

    WaitForSingleObject(hListMutex, INFINITE);
    for I := 0 to L - 1 do
      if ReadingsA[I] = ReadingsB[I] then
        MeasuredPulseWidth[I] := ReadingsA[I]
    ;
    ReleaseMutex(hListMutex);

  until Terminated;
  CloseHandle(hListMutex);
end;

function CTR_StartMeasuringPulseWidth(DeviceIndex: LongWord): LongWord; cdecl;
var
  I: Integer;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if CtrMonitorThread <> nil then CTR_StopMeasuringPulseWidth(DeviceIndex);
      CtrMonitorThread := nil;
      try
        CtrMonitorThread := TCtrMonitorThread.Create(True);
        with CtrMonitorThread do begin
          DI := DeviceIndex;
          hListMutex := CreateMutex(nil, False, nil);
          SetLength(MeasuredPulseWidth, Counters * 3);
          for I := 0 to High(MeasuredPulseWidth) do MeasuredPulseWidth[I] := 0;
          Start;
        end;
        Result := ERROR_SUCCESS;
      except
        Result := ERROR_INTERNAL_ERROR;
        FreeAndNil(CtrMonitorThread);
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_StopMeasuringPulseWidth(DeviceIndex: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if CtrMonitorThread = nil then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      FreeAndNil(CtrMonitorThread);
      Result := ERROR_SUCCESS;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function CTR_GetPulseWidthMeasurement(DeviceIndex, BlockIndex, CounterIndex: LongWord; pReadValue: PWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if Counters = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Result := MapCounterBlock(DeviceIndex, CounterIndex, BlockIndex);
      if Result <> ERROR_SUCCESS then Exit;

      if CtrMonitorThread = nil then begin
        Result := ERROR_FILE_NOT_FOUND;
        Exit;
      end;

      try
        pReadValue^ := 0;
        try
          WaitForSingleObject(CtrMonitorThread.hListMutex, INFINITE);
          pReadValue^ := CtrMonitorThread.MeasuredPulseWidth[BlockIndex * 3 + CounterIndex];
          CtrMonitorThread.MeasuredPulseWidth[BlockIndex * 3 + CounterIndex] := 0;
          ReleaseMutex(CtrMonitorThread.hListMutex);
          if pReadValue^ = 0 then
            Result := ERROR_NO_DATA_DETECTED
          else
            Result := ERROR_SUCCESS
          ;
        except
          Result := ERROR_INTERNAL_ERROR;
        end;
      except
        Result := ERROR_NOACCESS;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;



function DIO_SPI_Write(DeviceIndex: LongWord; Address, Reg, Value: Byte): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bDIOSPI then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Result := GenericVendorWrite(DeviceIndex, AUR_DIO_SPI_WRITE, Value, Reg or (Address shl 8), 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_SPI_Read(DeviceIndex: LongWord; Address, Reg: Byte; pValue: PByte): LongWord; cdecl;
var
  ReadValue: Byte;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bDIOSPI then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      L := SizeOf(ReadValue);
      Result := GenericVendorRead(DeviceIndex, AUR_DIO_SPI_READ, 0, Reg or (Address shl 8), L, @ReadValue);

      if Result = ERROR_SUCCESS then pValue^ := ReadValue;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;



function AIOUSB_ClearFIFO(DeviceIndex: LongWord; TimeMethod: LongWord): LongWord; cdecl;
var
  Req: Byte;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bClearFIFO then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      case TimeMethod of
        0: Req := AUR_GEN_CLEAR_FIFO;       // 0x35
        1: Req := AUR_GEN_CLEAR_FIFO_NEXT;  // 0x34
        5: Req := AUR_GEN_ABORT_AND_CLEAR;  // 0x38
        86: Req := AUR_GEN_CLEAR_FIFO_WAIT; // 0x36
        else begin
          Result := ERROR_INVALID_PARAMETER;
          Exit;
        end;
      end;
      Result := GenericVendorWrite(DeviceIndex, Req, 0, 0, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_GetStreamStatus(DeviceIndex: LongWord; var Status: LongWord): LongWord; cdecl;
var
  L: LongWord;
  ReadValue: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bClearFIFO then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      L := SizeOf(ReadValue);
      Result := GenericVendorRead(DeviceIndex, AUR_GEN_STREAM_STATUS, 0, 0, L, @ReadValue);

      if Result = ERROR_SUCCESS then Status := ReadValue;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_SetStreamingBlockSize(DeviceIndex, BlockSize: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not (bDIOStream or bADCBulk) then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if (BlockSize = 0) or (BlockSize > 31*1024*1024) then begin
        Result := ERROR_INVALID_PARAMETER;
        Exit;
      end;

      if BlockSize < StreamingBlockSizeFloor then BlockSize := StreamingBlockSizeFloor;

      if bADCBulk then begin
        if (BlockSize and $1FF) <> 0 then
          BlockSize := (BlockSize and $FFFFFE00) + $200
        else
          BlockSize := (BlockSize and $FFFFFE00)
        ;
      end;

      if bDIOStream then begin
        if (BlockSize and $FF) <> 0 then
          BlockSize := (BlockSize and $FFFFFF00) + $100
        else
          BlockSize := (BlockSize and $FFFFFF00)
        ;
      end;

      StreamingBlockSize := BlockSize;

      Result := ERROR_SUCCESS;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_ResetChip(DeviceIndex: LongWord): LongWord; cdecl;
var
  CPUCSByte: Byte;

begin
  try
    //Put CPU into reset
    CPUCSByte := $01;
    Result := GenericVendorWrite(DeviceIndex, $A0, $E600, 0, 1, @CPUCSByte);
    if Result <> ERROR_SUCCESS then Exit;

    //take CPU out of reset
    CPUCSByte := $00;
    Result := GenericVendorWrite(DeviceIndex, $A0, $E600, 0, 1, @CPUCSByte);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_AbortPipe(DeviceIndex: LongWord; PipeID: Byte): LongWord; cdecl;
var
  BytesReturned: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    BytesReturned := 0;
    if DeviceIoControl(GetThreadHandleForDevice(DeviceIndex), IOCTL_ADAPT_ABORT_PIPE, @PipeID, SizeOf(PipeID), nil, 0, BytesReturned, nil) then
      Result := ERROR_SUCCESS
    else
      Result := GetMappedFailure(DeviceIndex)
    ;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;





function DIO_CSA_DoSync(DeviceIndex: LongWord; var BaseRateHz, DurAms, DurBms, DurCms: Double): LongWord; cdecl;
const
  RootSyncClock = 3000;

var
  Divisor, DurATicks, DurBTicks, DurCTicks: Integer;
  Value, Index: Word;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if not bSetCustomClocks then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if BaseRateHz < (RootSyncClock/255.5) then
        Divisor := 0
      else if BaseRateHz >= RootSyncClock then
        Divisor := 1
      else
        Divisor := Min($FF, Round(RootSyncClock / BaseRateHz))
      ;

      if Divisor = 0 then begin
        BaseRateHz := 0;
        DurATicks := 0; DurAms := 0;
        DurBTicks := 0; DurBms := 0;
        DurCTicks := 0; DurCms := 0;
      end
      else begin
        BaseRateHz := RootSyncClock / Divisor;
        DurATicks := Min($FF, Round(3 * DurAms)); DurAms := 1/3 * DurATicks;
        DurBTicks := Min($FF, Round(3 * DurBms)); DurBms := 1/3 * DurBTicks;
        DurCTicks := Min($FF, Round(3 * DurCms)); DurCms := 1/3 * DurCTicks;
      end;
      Value := Divisor or (DurATicks shl 8);
      Index := DurBTicks or (DurCTicks shl 8);

      Result := GenericVendorWrite(DeviceIndex, AUR_SET_CUSTOM_CLOCKS, Value, Index, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_CSA_DebounceSet(DeviceIndex, DebounceCounts: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if (DIOBytes = 0) or not bDIODebounce then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      Result := GenericVendorWrite(DeviceIndex, AUR_DIO_ADVANCED, DebounceCounts, $100, 0, nil);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_CSA_DebounceReadAll(DeviceIndex: LongWord; pData: Pointer): LongWord; cdecl;
var
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if (DIOBytes = 0) or not bDIODebounce then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      L := DIOBytes * 2;
      Result := GenericVendorRead(DeviceIndex, AUR_DIO_ADVANCED, 0, $101, L, pData);
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DAC_CSA_SetRangeLimits(DeviceIndex: LongWord; pData: Pointer): LongWord; cdecl;
var
  InterBuf: AnsiString;

begin
  try
    SetString(InterBuf, PAnsiChar(pData), 32);
  except
    Result := ERROR_NOACCESS;
    Exit;
  end;
  InterBuf := #1 + InterBuf;
  Result := GenericVendorWrite(DeviceIndex, $A2, $1D00, 0, Length(InterBuf), PAnsiChar(InterBuf));
  InterBuf := '';
end;

function DAC_CSA_ClearRangeLimits(DeviceIndex: LongWord): LongWord; cdecl;
var
  InterBuf: AnsiString;

begin
  InterBuf := #0;
  Result := GenericVendorWrite(DeviceIndex, $A2, $1D00, 0, Length(InterBuf), PAnsiChar(InterBuf));
  InterBuf := '';
end;

function DIO_CSA_ReadAllString(DeviceIndex: LongWord; pData: Pointer; pDataBytes: PLongWord): LongWord; cdecl;
var
  L, LPer, BytesRead: LongWord;

begin
  try
    Result := Validate(DeviceIndex);
    if Result <> ERROR_SUCCESS then begin
      pDataBytes^ := 0;
      Exit;
    end;

    Result := EnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then begin
      pDataBytes^ := 0;
      Exit;
    end;

    with Dev[DeviceIndex] do begin
      if DIOBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        pDataBytes^ := 0;
        Exit;
      end;

      LPer := DIOBytes;
      BytesRead := 0;
      L := pDataBytes^;
      Result := ERROR_SUCCESS;
      while L < LPer do begin
        Result := GenericVendorRead(DeviceIndex, AUR_DIO_READ, 0, 0, LPer, pData);
        if (Result <> ERROR_SUCCESS) or (LPer < DIOBytes) then Break;
        Inc(BytesRead, LPer);
        Dec(L, LPer);
        Inc(PByte(pData), LPer);
      end;
      pDataBytes^ := BytesRead;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
    pDataBytes^ := 0;
  end;
end;

function ADC_CSA_GetScanOversamples(DeviceIndex: LongWord; pBuf: PWord): LongWord; cdecl;
var
	Config: array[0..21] of Byte;
	ADBuf: TWordArray;
	L: Integer;
	StartChannel, EndChannel: Byte;

begin
	try
		Result := ADC_GetScan_Inner(DeviceIndex, Config, ADBuf, StartChannel, EndChannel, 0);
		if Result <> ERROR_SUCCESS then Exit;

		L := (EndChannel - StartChannel + 1) * (1 + Config[$13]);
		Move(ADBuf[0], pBuf^, L * SizeOf(pBuf^));
	except
		Result := ERROR_INTERNAL_ERROR;
	end;
end;

function DACDIO_WriteAll(DeviceIndex: LongWord; pDACCounts: PWord; pDIOData: PByte): LongWord; cdecl;
var
  I: Integer;
  Content: AnsiString;

begin
  try

    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      if DIOBytes = 0 then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      if (ImmDACs = 0) or bDACDIOStream then begin
        Result := ERROR_BAD_TOKEN_TYPE;
        Exit;
      end;

      SetLength(Content, 2 + DIOBytes + 2*ImmDACs);
      I := 1;

      Content[I] := AnsiChar(DIOBytes); //Length byte.
      Inc(I);

      Move(pDIOData^, Content[I], DIOBytes); //DIO.
      Inc(I, DIOBytes);

      Content[I] := AnsiChar(2*ImmDACs); //Length byte.
      Inc(I);

      Move(pDACCounts^, Content[I], 2*ImmDACs); //DACs.
      //Inc(BufI, 2*ImmDACs);

      Result := _GenericVendorWrite(DeviceIndex, AUR_DACDIO_WRITEALL, 0, 0, Length(Content), PAnsiChar(Content));
    end;

  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;





//FWE 2.0 PNP in general.
function AIOUSB_QuerySimplePNPData(DeviceIndex: LongWord; pPNPData: Pointer; pPNPDataBytes: PLongWord): LongWord; cdecl;
var
  pDevPNPData: PByte;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    with Dev[DeviceIndex] do begin
      Result := CheckFirmware20(DeviceIndex);
      if Result <> ERROR_SUCCESS then Exit;

      if PNPData.PNPSize = 0 then begin
        pPNPDataBytes^ := 0;
        Exit;
      end;

      L := Min(pPNPDataBytes^, PNPData.PNPSize-1);
      pPNPDataBytes^ := PNPData.PNPSize-1;

      //Loaded data starting /after/ the size.
      pDevPNPData := @PNPData.PNPSize;
      Inc(pDevPNPData, SizeOf(PNPData.PNPSize));

      try
        Move(pDevPNPData^, pPNPData^, L);
      except
        Result := ERROR_NOACCESS;
        //Exit;
      end;
    end;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;


//Load-time defaults.
function AIOUSB_SaveStateAsDefaults(DeviceIndex: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $ACCE, $0010, 0, nil);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_RestoreFactoryDefaults(DeviceIndex: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $ACCE, $0011, 0, nil);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_SetDefaultsTable(DeviceIndex: LongWord; pDefTable: Pointer; pDefTableBytes: PLongWord): LongWord; cdecl;
var
  DefBuf: array of Byte;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    L := pDefTableBytes^;
    if L > 1024 then begin
      Result := ERROR_BAD_LENGTH;
      Exit;
    end;

    SetLength(DefBuf, L);
    try
      Move(pDefTable^, DefBuf[0], L);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $ACCE, $0022, L, @DefBuf[0]);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function AIOUSB_GetDefaultsTable(DeviceIndex: LongWord; pDefTable: Pointer; pDefTableBytes: PLongWord): LongWord; cdecl;
var
  DefBuf: array of Byte;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    L := pDefTableBytes^;
    if L > 1024 then begin
      Result := ERROR_BAD_LENGTH;
      Exit;
    end;

    SetLength(DefBuf, L);
    try
      Move(pDefTable^, DefBuf[0], L);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    Result := GenericVendorRead(DeviceIndex, AUR_GEN_REGISTER, $0000, $0020, L, @DefBuf[0]);
    if L > LongWord(Length(DefBuf)) then L := Length(DefBuf);
    Move(DefBuf[0], pDefTable^, L);
    pDefTableBytes^ := L;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;


//Global tick.
{
  function AIOUSB_SetGlobalTickRate(DeviceIndex: LongWord; pHz: PDouble): LongWord; cdecl;
  var
    Hz, fDivisor: Double;
    Divisor: Word;

  begin
    try
      Result := ValidateAndEnsureOpen(DeviceIndex);
      if Result <> ERROR_SUCCESS then Exit;

      Result := CheckFirmware20(DeviceIndex);
      if Result <> ERROR_SUCCESS then Exit;

      Hz := pHz^;
      if Hz = 0 then
        Divisor := $FFFF //Will load 0 into the counter.
      else begin
        fDivisor := 12000000 / Hz; //12MHz is the CPU clock.
        if fDivisor <= 0 then
          Divisor := 0
        else if fDivisor >= $FFFF then
          Divisor := $FFFF
        else
          Divisor := Round(fDivisor)
        ;
      end;

      Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $FFFF - Divisor, $8001, 0, nil);
    except
      Result := ERROR_INTERNAL_ERROR;
    end;
  end;
}

function AIOUSB_SetGlobalTickRate(DeviceIndex: LongWord; pHz: PDouble): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := WriteGlobalTick(DeviceIndex, pHz);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;


//Watchdog.
function WDG_SetConfig(DeviceIndex: LongWord; pTimeoutSeconds: PDouble; pWDGTable: Pointer; pWDGTableBytes: PLongWord): LongWord; cdecl;
var
  WDGBuf: array of Byte;
  fTimeout: Double;
  Timeout: Word;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    fTimeout := pTimeoutSeconds^;
    if fTimeout <= 0 then
      Timeout := 0
    else if fTimeout >= $FFFF then
      Timeout := $FFFF
    else
      Timeout := Round(fTimeout)
    ;

    L := pWDGTableBytes^;
    if L > 1024 then begin
      Result := ERROR_BAD_LENGTH;
      Exit;
    end;

    SetLength(WDGBuf, 2 + L);
    PWord(@WDGBuf[0])^ := Timeout;
    try
      Move(pWDGTable^, WDGBuf[2], L);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $0000, $0041, 2 + L, @WDGBuf[0]);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function WDG_GetStatus(DeviceIndex: LongWord; pStatus: Pointer; pStatusBytes: PLongWord): LongWord; cdecl;
var
  WDGBuf: array of Byte;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    L := pStatusBytes^;
    if L > 1024 then begin
      Result := ERROR_BAD_LENGTH;
      Exit;
    end;

    SetLength(WDGBuf, L);
    try
      Move(pStatus^, WDGBuf[0], L);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    Result := GenericVendorRead(DeviceIndex, AUR_WDG_STATUS, $0000, $0041, L, @WDGBuf[0]);
    if L > LongWord(Length(WDGBuf)) then L := Length(WDGBuf);
    Move(WDGBuf[0], pStatus^, L);
    pStatusBytes^ := L;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function WDG_Pet(DeviceIndex: LongWord; PetFlag: LongWord): LongWord; cdecl;
var
  TimeoutLeft: Word;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    case PetFlag of
      0: begin
        //Read a little status and throw it away, because we can't read zero bytes.
        L := SizeOf(TimeoutLeft);
        Result := GenericVendorRead(DeviceIndex, AUR_WDG_STATUS, $0000, $0041, L, @TimeoutLeft);
      end;
      else begin
        Result := ERROR_INVALID_FLAG_NUMBER;
      end;
    end;

  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;


//DIO automapping.
function DIO_Automap_ClearTable(DeviceIndex: LongWord): LongWord; cdecl;
begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $0000, $0082, 0, nil);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_Automap_SetTable(DeviceIndex: LongWord; pMapTable: Pointer; pMapTableBytes: PLongWord): LongWord; cdecl;
const
  MapCount = 32;

var
  AutomapBuf: array of Byte;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    L := pMapTableBytes^;
    if L > 2*MapCount then begin
      Result := ERROR_BAD_LENGTH;
      Exit;
    end;

    if (L and 1) <> 0 then begin
      L := L and not 1;
      pMapTableBytes^ := L;
    end;

    SetLength(AutomapBuf, 2*MapCount + 1);
    FillChar(AutomapBuf[0], 2*MapCount, 0);
    try
      Move(pMapTable^, AutomapBuf[0], L);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;
    AutomapBuf[2*MapCount] := L div 2;

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $0000, $0081, L, @AutomapBuf[0]);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_Automap_AddEntry(DeviceIndex: LongWord; pMapEntry: PWord): LongWord; cdecl;
var
  MapEntry: Word;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    try
      MapEntry := pMapEntry^;
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $0000, $0084, SizeOf(MapEntry), @MapEntry);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_Automap_SetTickDivisor(DeviceIndex: LongWord; pDivisor: PByte): LongWord; cdecl;
{
var
  Divisor: Byte;
}

begin
  Result := ERROR_NOT_SUPPORTED;
  {
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    try
      Divisor := pDivisor^;
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $0000, $0083, SizeOf(Divisor), @Divisor);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
  }
end;


//DIO PWM.
function DIO_PWM_Start(DeviceIndex: LongWord; pPWMTable: Pointer; pPWMTableBytes: PLongWord): LongWord; cdecl;
const
  PWMCount = 8;

var
  PWMBuf: array of Byte;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    L := pPWMTableBytes^;
    if L > 2*PWMCount then begin
      Result := ERROR_BAD_LENGTH;
      Exit;
    end;

    if (L and 1) <> 0 then begin
      L := L and not 1;
      pPWMTableBytes^ := L;
    end;

    SetLength(PWMBuf, 2*PWMCount + 2);
    FillChar(PWMBuf[1], 2*PWMCount, 0);
    try
      Move(pPWMTable^, PWMBuf[1], L);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;
    PWMBuf[2*PWMCount + 1] := L div 2;
    PWMBuf[0] := 100;

    {
      try
        PWMBuf[0] := pDivisor^;
      except
        Result := ERROR_NOACCESS;
        Exit;
      end;
    }

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $0000, $0071, Length(PWMBuf), @PWMBuf[0]);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

//DIO latching.
function DIO_Latch_SetDivisor(DeviceIndex: LongWord; pDivisor: PByte): LongWord; cdecl;
var
  Divisor: Byte;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    try
      Divisor := pDivisor^;
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $0000, $0063, SizeOf(Divisor), @Divisor);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_Latch_Reset(DeviceIndex: LongWord): LongWord; cdecl;
var
  L: LongWord;
  LatchBuf: array of Byte;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    SetLength(LatchBuf, Dev[DeviceIndex].DIOBytes * 3);

    L := Length(LatchBuf);
    Result := GenericVendorRead(DeviceIndex, AUR_DIO_LATCH_READ, $0000, $0000, L, @LatchBuf[0]);
    if Result <> ERROR_SUCCESS then Exit;
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_Latch_Read(DeviceIndex: LongWord; pLowLatches, pHighLatches, pNoLatches: PByte; pLatchesBytes: PLongWord): LongWord; cdecl;
var
  L, oL: LongWord;
  LatchBuf: array of Byte;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    oL := Min(pLatchesBytes^, Dev[DeviceIndex].DIOBytes);
    SetLength(LatchBuf, Dev[DeviceIndex].DIOBytes * 3);
    try
      Move(pLowLatches^, LatchBuf[0], oL);
      Move(pHighLatches^, LatchBuf[0], oL);
      Move(pNoLatches^, LatchBuf[0], oL);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    L := Length(LatchBuf);
    Result := GenericVendorRead(DeviceIndex, AUR_DIO_LATCH_READ, $0000, $0000, L, @LatchBuf[0]);
    if Result <> ERROR_SUCCESS then Exit;
    if Integer(L) < Length(LatchBuf) then begin
      Result := ERROR_INVALID_DATA;
      Exit;
    end;

    L := Dev[DeviceIndex].DIOBytes;
    try
      Move(LatchBuf[  L], pLowLatches^, oL);
      Move(LatchBuf[2*L], pHighLatches^, oL);
      Move(LatchBuf[0  ], pNoLatches^, oL);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;
    pLatchesBytes^ := L;

  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;


//DIO debounce.
function DIO_Deb_SetConfig(DeviceIndex: LongWord; pDebTable: Pointer; pDebTableBytes: PLongWord): LongWord; cdecl;
var
  DebBuf: array of Byte;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    L := pDebTableBytes^;
    if L > 1024 then begin
      Result := ERROR_BAD_LENGTH;
      Exit;
    end;

    SetLength(DebBuf, L);
    try
      Move(pDebTable^, DebBuf[0], L);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    Result := GenericVendorWrite(DeviceIndex, AUR_GEN_REGISTER, $0000, $0051, L, @DebBuf[0]);
  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

function DIO_Deb_ReadAll(DeviceIndex: LongWord; pDebData: PByte): LongWord; cdecl;
var
  DebBuf: array of Byte;
  L: LongWord;

begin
  try
    Result := ValidateAndEnsureOpen(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    Result := CheckFirmware20(DeviceIndex);
    if Result <> ERROR_SUCCESS then Exit;

    L := Dev[DeviceIndex].DIOBytes;
    SetLength(DebBuf, L);
    try
      Move(pDebData^, DebBuf[0], L);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

    Result := GenericVendorRead(DeviceIndex, AUR_DIO_DEB_READ, $0000, $0000, L, @DebBuf[0]);
    if Result <> ERROR_SUCCESS then Exit;

    try
      Move(DebBuf[0], pDebData^, L);
    except
      Result := ERROR_NOACCESS;
      Exit;
    end;

  except
    Result := ERROR_INTERNAL_ERROR;
  end;
end;

begin
  IsMultiThread := True;
end.
