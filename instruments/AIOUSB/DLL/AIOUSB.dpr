library AIOUSB;

{$R *.res}

uses
  Windows,
{$IFDEF VER130}  // Delphi 5
  SysUtils, Classes,
{$ELSE}         // anything other than Delphi 5, presumably XE2+
  System.SysUtils,
  System.Classes,
{$ENDIF}

  SetupDi in 'SetupDi.pas',
  WinUSB in 'WinUSB.pas',
  ContBufThreads in 'ContBufThreads.pas',
  TheseUtils in 'TheseUtils.pas',
  CoreExports in 'CoreExports.pas';

function VBGetDevices: LongWord; stdcall;
begin
  Result := GetDevices;
end;

function VBQueryDeviceInfo(DeviceIndex: LongWord; pPID: PLongWord; pNameSize: PLongWord; pName: PAnsiChar; pDIOBytes, pCounters: PLongWord): LongWord; stdcall;
begin
  Result := QueryDeviceInfo(DeviceIndex, pPID, pNameSize, pName, pDIOBytes, pCounters);
end;

function VBClearDevices: LongWord; stdcall;
begin
  Result := ClearDevices;
end;

function VBAIOUSB_CloseDevice(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := AIOUSB_CloseDevice(DeviceIndex);
end;

function VBAIOUSB_ReloadDeviceLinks: LongWord; stdcall;
begin
  Result := AIOUSB_ReloadDeviceLinks;
end;

function VBResolveDeviceIndex(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := ResolveDeviceIndex(DeviceIndex);
end;

function VBGetDeviceBySerialNumber(const pSerialNumber: Int64): LongWord; stdcall;
begin
  Result := GetDeviceBySerialNumber(pSerialNumber);
end;

function VBGetDeviceByEEPROMByte(Data: Byte): LongWord; stdcall;
begin
  Result := GetDeviceByEEPROMByte(Data);
end;

function VBGetDeviceByEEPROMData(StartAddress, DataSize: LongWord; pData: PByte): LongWord; stdcall;
begin
  Result := GetDeviceByEEPROMData(StartAddress, DataSize, pData);
end;

function VBDACDirect(DeviceIndex: LongWord; Channel: Word; Value: Word): LongWord; stdcall;
begin
  Result := DACDirect(DeviceIndex, Channel, Value);
end;

function VBDACMultiDirect(DeviceIndex: LongWord; pDACData: PDACEntry; DACDataCount: LongWord): LongWord; stdcall;
begin
  Result := DACMultiDirect(DeviceIndex, pDACData, DACDataCount);
end;

function VBDACSetBoardRange(DeviceIndex: LongWord; RangeCode: LongWord): LongWord; stdcall;
begin
  Result := DACSetBoardRange(DeviceIndex, RangeCode);
end;

function VBDACSetChannelCal(DeviceIndex: LongWord; Channel: LongWord; CalFileName: PAnsiChar): LongWord; stdcall;
begin
  Result := DACSetChannelCal(DeviceIndex, Channel, CalFileName);
end;

function VBDACOutputOpen(DeviceIndex: LongWord; var ClockHz: Double): LongWord; stdcall;
begin
  Result := DACOutputOpen(DeviceIndex, ClockHz);
end;

function VBDACOutputAbort(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := DACOutputAbort(DeviceIndex);
end;

function VBDACOutputClose(DeviceIndex: LongWord; bWait: LongBool): LongWord; stdcall;
begin
  Result := DACOutputClose(DeviceIndex, bWait);
end;

function VBDACOutputCloseNoEnd(DeviceIndex: LongWord; bWait: LongBool): LongWord; stdcall;
begin
  Result := DACOutputCloseNoEnd(DeviceIndex, bWait);
end;

function VBDACOutputSetCount(DeviceIndex, NewCount: LongWord): LongWord; stdcall;
begin
  Result := DACOutputSetCount(DeviceIndex, NewCount);
end;

function VBDACOutputFrame(DeviceIndex, FramePoints: LongWord; FrameData: PWord): LongWord; stdcall;
begin
  Result := DACOutputFrame(DeviceIndex, FramePoints, FrameData);
end;

function VBDACOutputFrameRaw(DeviceIndex, FramePoints: LongWord; FrameData: PWord): LongWord; stdcall;
begin
  Result := DACOutputFrameRaw(DeviceIndex, FramePoints, FrameData);
end;

function VBDACOutputStatus(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := DACOutputStatus(DeviceIndex);
end;

function VBDACOutputStart(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := DACOutputStart(DeviceIndex);
end;

function VBDACOutputSetInterlock(DeviceIndex: LongWord; bInterlock: LongBool): LongWord; stdcall;
begin
  Result := DACOutputSetInterlock(DeviceIndex, bInterlock);
end;

function VBDACOutputSetClock(DeviceIndex: LongWord; var ClockHz: Double): LongWord; stdcall;
begin
  Result := DACOutputSetClock(DeviceIndex, ClockHz);
end;

function VBDACOutputProcess(DeviceIndex: LongWord; var ClockHz: Double; Samples: LongWord; pSampleData: PWord): LongWord; stdcall;
begin
  Result := DACOutputProcess(DeviceIndex, ClockHz, Samples, pSampleData);
end;

function VBDACOutputLoadProcess(DeviceIndex: LongWord; var ClockHz: Double; Samples: LongWord; pSampleData: PWord): LongWord; stdcall;
begin
  Result := DACOutputLoadProcess(DeviceIndex, ClockHz, Samples, pSampleData);
end;

function VBWDG_SetConfig(DeviceIndex: LongWord; pTimeoutSeconds: PDouble; pWDGTable: Pointer; pWDGTableBytes: PLongWord): LongWord; stdcall;
begin
  Result := WDG_SetConfig(DeviceIndex, pTimeoutSeconds, pWDGTable, pWDGTableBytes);
end;

function VBWDG_GetStatus(DeviceIndex: LongWord; pStatus: Pointer; pStatusBytes: PLongWord): LongWord; stdcall;
begin
  Result := WDG_GetStatus(DeviceIndex, pStatus, pStatusBytes);
end;

function VBWDG_Pet(DeviceIndex: LongWord; PetFlag: LongWord): LongWord; stdcall;
begin
  Result := WDG_Pet(DeviceIndex, PetFlag);
end;

function VBADC_GetConfig(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord): LongWord; stdcall;
begin
  Result := ADC_GetConfig(DeviceIndex, pConfigBuf, ConfigBufSize);
end;

function VBADC_SetConfig(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord): LongWord; stdcall;
begin
  Result := ADC_SetConfig(DeviceIndex, pConfigBuf, ConfigBufSize);
end;

function VBADC_RangeAll(DeviceIndex: LongWord; pGainCodes: PByte; bSingleEnded: LongBool): LongWord; stdcall;
begin
  Result := ADC_RangeAll(DeviceIndex, pGainCodes, bSingleEnded);
end;

function VBADC_Range1(DeviceIndex, ADChannel: LongWord; GainCode: Byte; bSingleEnded: LongBool): LongWord; stdcall;
begin
  Result := ADC_Range1(DeviceIndex, ADChannel, GainCode, bSingleEnded);
end;

function VBADC_ADMode(DeviceIndex: LongWord; TriggerMode, CalMode: Byte): LongWord; stdcall;
begin
  Result := ADC_ADMode(DeviceIndex, TriggerMode, CalMode);
end;

function VBADC_SetScanLimits(DeviceIndex, StartChannel, EndChannel: LongWord): LongWord; stdcall;
begin
  Result := ADC_SetScanLimits(DeviceIndex, StartChannel, EndChannel);
end;

function VBADC_SetOversample(DeviceIndex: LongWord; Oversample: Byte): LongWord; stdcall;
begin
  Result := ADC_SetOversample(DeviceIndex, Oversample);
end;

function VBADC_QueryCal(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := ADC_QueryCal(DeviceIndex);
end;

function VBADC_SetCal(DeviceIndex: LongWord; CalFileName: PAnsiChar): LongWord; stdcall;
begin
  Result := ADC_SetCal(DeviceIndex, CalFileName);
end;

function VBADC_SetCalAndSave(DeviceIndex: LongWord; CalFileName, SaveCalFileName: PAnsiChar): LongWord; stdcall;
begin
  Result := ADC_SetCalAndSave(DeviceIndex, CalFileName, SaveCalFileName);
end;

function VBADC_Initialize(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord; CalFileName: PAnsiChar): LongWord; stdcall;
begin
  Result := ADC_Initialize(DeviceIndex, pConfigBuf, ConfigBufSize, CalFileName);
end;

function VBADC_Start(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := ADC_Start(DeviceIndex);
end;

function VBADC_Stop(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := ADC_Stop(DeviceIndex);
end;

function VBADC_BulkAcquire(DeviceIndex: LongWord; BufSize: LongWord; Buf: Pointer): LongWord; stdcall;
begin
  Result := ADC_BulkAcquire(DeviceIndex, BufSize, Buf);
end;

function VBADC_BulkPoll(DeviceIndex: LongWord; var BytesLeft: LongWord): LongWord; stdcall;
begin
  Result := ADC_BulkPoll(DeviceIndex, BytesLeft);
end;

function VBADC_GetImmediate(DeviceIndex, Channel: LongWord; pBuf: PWord): LongWord; stdcall;
begin
  Result := ADC_GetImmediate(DeviceIndex, Channel, pBuf);
end;

function VBADC_GetScan(DeviceIndex: LongWord; pBuf: PWord): LongWord; stdcall;
begin
  Result := ADC_GetScan(DeviceIndex, pBuf);
end;

function VBADC_GetScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; stdcall;
begin
  Result := ADC_GetScanV(DeviceIndex, pBuf);
end;

function VBADC_GetTrigScan(DeviceIndex: LongWord; pBuf: PWord; TimeoutMS: LongInt): LongWord; stdcall;
begin
  Result := ADC_GetTrigScan(DeviceIndex, pBuf, TimeoutMS);
end;

function VBADC_GetTrigScanV(DeviceIndex: LongWord; pBuf: PDouble; TimeoutMS: LongInt): LongWord; stdcall;
begin
  Result := ADC_GetTrigScanV(DeviceIndex, pBuf, TimeoutMS);
end;

function VBADC_GetChannelV(DeviceIndex, ChannelIndex: LongWord; pBuf: PDouble): LongWord; stdcall;
begin
  Result := ADC_GetChannelV(DeviceIndex, ChannelIndex, pBuf);
end;

function VBADC_GetCalRefV(DeviceIndex, CalRefIndex: LongWord; var pRef: Double): LongWord; stdcall;
begin
  Result := ADC_GetCalRefV(DeviceIndex, CalRefIndex, pRef);
end;

function VBAIOUSB_OfflineWrite1(DeviceIndex: LongWord; SampleIndex: LongWord; Buf: Word): LongWord; stdcall;
begin
  Result := AIOUSB_OfflineWrite1(DeviceIndex, SampleIndex, Buf);
end;

function VBAIOUSB_OfflineRead1(DeviceIndex: LongWord; SampleIndex: LongWord; pBuf: PWord): LongWord; stdcall;
begin
  Result := AIOUSB_OfflineRead1(DeviceIndex, SampleIndex, pBuf);
end;

function VBDIO_Configure(DeviceIndex: LongWord; Tristate: ByteBool; pOutMask: Pointer; pData: Pointer): LongWord; stdcall;
begin
  Result := DIO_Configure(DeviceIndex, Tristate, pOutMask, pData);
end;

function VBDIO_ConfigureEx(DeviceIndex: LongWord; pOutMask: Pointer; pData: Pointer; pTristateMask: Pointer): LongWord; stdcall;
begin
  Result := DIO_ConfigureEx(DeviceIndex, pOutMask, pData, pTristateMask);
end;

function VBDIO_ConfigurationQuery(DeviceIndex: LongWord; pOutMask: Pointer; pTristateMask: Pointer): LongWord; stdcall;
begin
  Result := DIO_ConfigurationQuery(DeviceIndex, pOutMask, pTristateMask);
end;

function VBDIO_ConfigureMasked(DeviceIndex: LongWord; pOuts: Pointer; pOutsMask: Pointer; pData: Pointer; pDataMask: Pointer; pTristates: Pointer; pTristatesMask: Pointer): LongWord; stdcall;
begin
  Result := DIO_ConfigureMasked(DeviceIndex, pOuts, pOutsMask, pData, pDataMask, pTristates, pTristatesMask);
end;

function VBDIO_Write1(DeviceIndex, BitIndex: LongWord; Data: ByteBool): LongWord; stdcall;
begin
  Result := DIO_Write1(DeviceIndex, BitIndex, Data);
end;

function VBDIO_Write8(DeviceIndex, ByteIndex: LongWord; Data: Byte): LongWord; stdcall;
begin
  Result := DIO_Write8(DeviceIndex, ByteIndex, Data);
end;

function VBDIO_WriteAll(DeviceIndex: LongWord; pData: Pointer): LongWord; stdcall;
begin
  Result := DIO_WriteAll(DeviceIndex, pData);
end;

function VBDIO_Read1(DeviceIndex, BitIndex: LongWord; Buffer: PByte): LongWord; stdcall;
begin
  Result := DIO_Read1(DeviceIndex, BitIndex, Buffer);
end;

function VBDIO_Read8(DeviceIndex, ByteIndex: LongWord; Buffer: PByte): LongWord; stdcall;
begin
  Result := DIO_Read8(DeviceIndex, ByteIndex, Buffer);
end;

function VBDIO_ReadAll(DeviceIndex: LongWord; pData: Pointer): LongWord; stdcall;
begin
  Result := DIO_ReadAll(DeviceIndex, pData);
end;

function VBDIO_StreamOpen(DeviceIndex: LongWord; bIsRead: LongBool): LongWord; stdcall;
begin
  Result := DIO_StreamOpen(DeviceIndex, bIsRead);
end;

function VBDIO_StreamClose(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := DIO_StreamClose(DeviceIndex);
end;

function VBDIO_StreamFrame(DeviceIndex, FramePoints: LongWord; pFrameData: PWord; var BytesTransferred: LongWord): LongWord; stdcall;
begin
  Result := DIO_StreamFrame(DeviceIndex, FramePoints, pFrameData, BytesTransferred);
end;

function VBDIO_StreamSetClocks(DeviceIndex: LongWord; var ReadClockHz, WriteClockHz: Double): LongWord; stdcall;
begin
  Result := DIO_StreamSetClocks(DeviceIndex, ReadClockHz, WriteClockHz);
end;

function VBCTR_8254Mode(DeviceIndex, BlockIndex, CounterIndex, Mode: LongWord): LongWord; stdcall;
begin
  Result := CTR_8254Mode(DeviceIndex, BlockIndex, CounterIndex, Mode);
end;

function VBCTR_8254Load(DeviceIndex, BlockIndex, CounterIndex: LongWord; LoadValue: Word): LongWord; stdcall;
begin
  Result := CTR_8254Load(DeviceIndex, BlockIndex, CounterIndex, LoadValue);
end;

function VBCTR_8254ModeLoad(DeviceIndex, BlockIndex, CounterIndex, Mode: LongWord; LoadValue: Word): LongWord; stdcall;
begin
  Result := CTR_8254ModeLoad(DeviceIndex, BlockIndex, CounterIndex, Mode, LoadValue);
end;

function VBCTR_8254ReadModeLoad(DeviceIndex, BlockIndex, CounterIndex, Mode: LongWord; LoadValue: Word; pReadValue: PWord): LongWord; stdcall;
begin
  Result := CTR_8254ReadModeLoad(DeviceIndex, BlockIndex, CounterIndex, Mode, LoadValue, pReadValue);
end;

function VBCTR_8254Read(DeviceIndex, BlockIndex, CounterIndex: LongWord; pReadValue: PWord): LongWord; stdcall;
begin
  Result := CTR_8254Read(DeviceIndex, BlockIndex, CounterIndex, pReadValue);
end;

function VBCTR_8254ReadStatus(DeviceIndex, BlockIndex, CounterIndex: LongWord; pReadValue: PWord; pStatus: PByte): LongWord; stdcall;
begin
  Result := CTR_8254ReadStatus(DeviceIndex, BlockIndex, CounterIndex, pReadValue, pStatus);
end;

function VBCTR_8254ReadAll(DeviceIndex: LongWord; pData: PWord): LongWord; stdcall;
begin
  Result := CTR_8254ReadAll(DeviceIndex, pData);
end;

function VBCTR_8254ReadLatched(DeviceIndex: LongWord; pData: PWord): LongWord; stdcall;
begin
  Result := CTR_8254ReadLatched(DeviceIndex, pData);
end;

function VBCTR_8254SelectGate(DeviceIndex, GateIndex: LongWord): LongWord; stdcall;
begin
  Result := CTR_8254SelectGate(DeviceIndex, GateIndex);
end;

function VBCTR_StartOutputFreq(DeviceIndex, BlockIndex: LongWord; pHz: PDouble): LongWord; stdcall;
begin
  Result := CTR_StartOutputFreq(DeviceIndex, BlockIndex, pHz);
end;

function VBCTR_SetWaitGates(DeviceIndex: LongWord; A, B: Byte): LongWord; stdcall;
begin
  Result := CTR_SetWaitGates(DeviceIndex, A, B);
end;

function VBCTR_EndWaitGates(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := CTR_EndWaitGates(DeviceIndex);
end;

function VBCTR_WaitForGate(DeviceIndex: LongWord; GateIndex: Byte; var Content: Word): LongWord; stdcall;
begin
  Result := CTR_WaitForGate(DeviceIndex, GateIndex, Content);
end;

function VBCTR_StartMeasuringPulseWidth(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := CTR_StartMeasuringPulseWidth(DeviceIndex);
end;

function VBCTR_StopMeasuringPulseWidth(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := CTR_StopMeasuringPulseWidth(DeviceIndex);
end;

function VBCTR_GetPulseWidthMeasurement(DeviceIndex, BlockIndex, CounterIndex: LongWord; pReadValue: PWord): LongWord; stdcall;
begin
  Result := CTR_GetPulseWidthMeasurement(DeviceIndex, BlockIndex, CounterIndex, pReadValue);
end;

function VBDIO_SPI_Write(DeviceIndex: LongWord; Address, Reg, Value: Byte): LongWord; stdcall;
begin
  Result := DIO_SPI_Write(DeviceIndex, Address, Reg, Value);
end;

function VBDIO_SPI_Read(DeviceIndex: LongWord; Address, Reg: Byte; pValue: PByte): LongWord; stdcall;
begin
  Result := DIO_SPI_Read(DeviceIndex, Address, Reg, pValue);
end;

function VBCustomEEPROMRead(DeviceIndex: LongWord; StartAddress: LongWord; var DataSize: LongWord; Data: Pointer): LongWord; stdcall;
begin
  Result := CustomEEPROMRead(DeviceIndex, StartAddress, DataSize, Data);
end;

function VBCustomEEPROMWrite(DeviceIndex: LongWord; StartAddress: LongWord; DataSize: LongWord; Data: Pointer): LongWord; stdcall;
begin
  Result := CustomEEPROMWrite(DeviceIndex, StartAddress, DataSize, Data);
end;

function VBAIOUSB_FlashRead(DeviceIndex: LongWord; StartAddress: LongWord; var DataSize: LongWord; Data: Pointer): LongWord; stdcall;
begin
 Result := AIOUSB_FlashRead(DeviceIndex, StartAddress, DataSize, Data);
end;

function VBAIOUSB_FlashWrite(DeviceIndex: LongWord; StartAddress: LongWord; DataSize: LongWord; Data: Pointer): LongWord; stdcall;
begin
  Result := AIOUSB_FlashWrite(DeviceIndex, StartAddress, DataSize, Data);
end;

function VBAIOUSB_FlashEraseSector(DeviceIndex: LongWord; Sector: Integer): LongWord; stdcall;
begin
  Result := AIOUSB_FlashEraseSector(DeviceIndex, Sector);
end;

function VBGenericVendorRead(DeviceIndex: LongWord; Request: Byte; Value, Index: Word; var DataSize: LongWord; Data: Pointer): LongWord; stdcall;
begin
  Result := GenericVendorRead(DeviceIndex, Request, Value, Index, DataSize, Data);
end;

function VBGenericVendorWrite(DeviceIndex: LongWord; Request: Byte; Value, Index: Word; DataSize: LongWord; Data: Pointer): LongWord; stdcall;
begin
  Result := GenericVendorWrite(DeviceIndex, Request, Value, Index, DataSize, Data);
end;

function VBAIOUSB_ClearFIFO(DeviceIndex: LongWord; TimeMethod: LongWord): LongWord; stdcall;
begin
  Result := AIOUSB_ClearFIFO(DeviceIndex, TimeMethod);
end;

function VBAIOUSB_GetStreamStatus(DeviceIndex: LongWord; var Status: LongWord): LongWord; stdcall;
begin
  Result := AIOUSB_GetStreamStatus(DeviceIndex, Status);
end;

function VBAIOUSB_SetStreamingBlockSize(DeviceIndex, BlockSize: LongWord): LongWord; stdcall;
begin
  Result := AIOUSB_SetStreamingBlockSize(DeviceIndex, BlockSize);
end;

function VBAIOUSB_ResetChip(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := AIOUSB_ResetChip(DeviceIndex);
end;

function VBAIOUSB_AbortPipe(DeviceIndex: LongWord; PipeID: Byte): LongWord; stdcall;
begin
  Result := AIOUSB_AbortPipe(DeviceIndex, PipeID);
end;

function VBAIOUSB_UploadD15LoFirmwaresByPID(pFirmScript: PAnsiChar): LongWord; stdcall;
begin
  Result := AIOUSB_UploadD15LoFirmwaresByPID(pFirmScript);
end;

function VBGetDeviceUniqueStr(DeviceIndex: LongWord; pIIDSize: PLongWord; pIID: PAnsiChar): LongWord; stdcall;
begin
  Result := GetDeviceUniqueStr(DeviceIndex, pIIDSize, pIID);
end;

function VBGetDeviceSerialNumber(DeviceIndex: LongWord; var pSerialNumber: Int64): LongWord; stdcall;
begin
  Result := GetDeviceSerialNumber(DeviceIndex, pSerialNumber);
end;

function SelectDeviceViaUI(NumPIDs: LongWord; pPIDs: PLongWord; CaptionStr, FindMultiPromptStr, Find1PromptStr, NoFindPromptStr: PAnsiChar; var SelectedDeviceIndex: LongWord): LongWord; cdecl;
begin
  Result := ERROR_NOT_SUPPORTED;
end;

function VBSelectDeviceViaUI(NumPIDs: LongWord; pPIDs: PLongWord; CaptionStr, FindMultiPromptStr, Find1PromptStr, NoFindPromptStr: PAnsiChar; var SelectedDeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := SelectDeviceViaUI(NumPIDs, pPIDs, CaptionStr, FindMultiPromptStr, Find1PromptStr, NoFindPromptStr, SelectedDeviceIndex);
end;


function VBADC_InitFastITScanV(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := ADC_InitFastITScanV(DeviceIndex);
end;

function VBADC_ResetFastITScanV(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := ADC_ResetFastITScanV(DeviceIndex);
end;

function VBADC_SetFastITScanVChannels(DeviceIndex, NewChannels: LongWord): LongWord; stdcall;
begin
  Result := ADC_SetFastITScanVChannels(DeviceIndex, NewChannels);
end;

function VBADC_GetFastITScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; stdcall;
begin
  Result := ADC_GetFastITScanV(DeviceIndex, pBuf);
end;

function VBADC_GetITScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; stdcall;
begin
  Result := ADC_GetITScanV(DeviceIndex, pBuf);
end;


function VBADC_CSA_InitFastScanV(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := ADC_CSA_InitFastScanV(DeviceIndex);
end;

function VBADC_CSA_ResetFastScanV(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := ADC_CSA_ResetFastScanV(DeviceIndex);
end;

function VBADC_CSA_GetFastScanV(DeviceIndex: LongWord; pBuf: PDouble): LongWord; stdcall;
begin
  Result := ADC_CSA_GetFastScanV(DeviceIndex, pBuf);
end;


function VBDIO_CSA_DoSync(DeviceIndex: LongWord; var BaseRateHz, DurAms, DurBms, DurCms: Double): LongWord; stdcall;
begin
  Result := DIO_CSA_DoSync(DeviceIndex, BaseRateHz, DurAms, DurBms, DurCms);
end;

function VBDIO_CSA_DebounceSet(DeviceIndex, DebounceCounts: LongWord): LongWord; stdcall;
begin
  Result := DIO_CSA_DebounceSet(DeviceIndex, DebounceCounts);
end;

function VBDIO_CSA_DebounceReadAll(DeviceIndex: LongWord; pData: Pointer): LongWord; stdcall;
begin
  Result := DIO_CSA_DebounceReadAll(DeviceIndex, pData);
end;

function VBDAC_CSA_SetRangeLimits(DeviceIndex: LongWord; pData: Pointer): LongWord; stdcall;
begin
  Result := DAC_CSA_SetRangeLimits(DeviceIndex, pData);
end;

function VBDAC_CSA_ClearRangeLimits(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := DAC_CSA_ClearRangeLimits(DeviceIndex);
end;

function VBDIO_CSA_ReadAllString(DeviceIndex: LongWord; pData: Pointer; pDataBytes: PLongWord): LongWord; stdcall;
begin
  Result := DIO_CSA_ReadAllString(DeviceIndex, pData, pDataBytes);
end;

function VBADC_CSA_GetScanOversamples(DeviceIndex: LongWord; pBuf: PWord): LongWord; stdcall;
begin
  Result := ADC_CSA_GetScanOversamples(DeviceIndex, pBuf);
end;

function VBDACDIO_WriteAll(DeviceIndex: LongWord; pDACCounts: PWord; pDIOData: PByte): LongWord; stdcall;
begin
  Result := DACDIO_WriteAll(DeviceIndex, pDACCounts, pDIOData);
end;

function VBAIOUSB_QuerySimplePNPData(DeviceIndex: LongWord; pPNPData: Pointer; pPNPDataBytes: PLongWord): LongWord; stdcall;
begin
  Result := AIOUSB_QuerySimplePNPData(DeviceIndex, pPNPData, pPNPDataBytes);
end;

function VBAIOUSB_SaveStateAsDefaults(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := AIOUSB_SaveStateAsDefaults(DeviceIndex);
end;

function VBAIOUSB_RestoreFactoryDefaults(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := AIOUSB_RestoreFactoryDefaults(DeviceIndex);
end;

function VBAIOUSB_SetDefaultsTable(DeviceIndex: LongWord; pDefTable: Pointer; pDefTableBytes: PLongWord): LongWord; stdcall;
begin
  Result := AIOUSB_SetDefaultsTable(DeviceIndex, pDefTable, pDefTableBytes);
end;

function VBAIOUSB_GetDefaultsTable(DeviceIndex: LongWord; pDefTable: Pointer; pDefTableBytes: PLongWord): LongWord; stdcall;
begin
  Result := AIOUSB_GetDefaultsTable(DeviceIndex, pDefTable, pDefTableBytes);
end;

function VBAIOUSB_SetGlobalTickRate(DeviceIndex: LongWord; pHz: PDouble): LongWord; stdcall;
begin
  Result := AIOUSB_SetGlobalTickRate(DeviceIndex, pHz);
end;

function VBDIO_Automap_ClearTable(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := DIO_Automap_ClearTable(DeviceIndex);
end;

function VBDIO_Automap_SetTable(DeviceIndex: LongWord; pMapTable: Pointer; pMapTableBytes: PLongWord): LongWord; stdcall;
begin
  Result := DIO_Automap_SetTable(DeviceIndex, pMapTable, pMapTableBytes);
end;

function VBDIO_Automap_AddEntry(DeviceIndex: LongWord; pMapEntry: PWord): LongWord; stdcall;
begin
  Result := DIO_Automap_AddEntry(DeviceIndex, pMapEntry);
end;

function VBDIO_Automap_SetTickDivisor(DeviceIndex: LongWord; pDivisor: PByte): LongWord; stdcall;
begin
  Result := DIO_Automap_SetTickDivisor(DeviceIndex, pDivisor);
end;

function VBDIO_PWM_Start(DeviceIndex: LongWord; pPWMTable: Pointer; pPWMTableBytes: PLongWord): LongWord; stdcall;
begin
  Result := DIO_PWM_Start(DeviceIndex, pPWMTable, pPWMTableBytes);
end;

function VBDIO_Latch_SetDivisor(DeviceIndex: LongWord; pDivisor: PByte): LongWord; stdcall;
begin
  Result := DIO_Latch_SetDivisor(DeviceIndex, pDivisor);
end;

function VBDIO_Latch_Reset(DeviceIndex: LongWord): LongWord; stdcall;
begin
  Result := DIO_Latch_Reset(DeviceIndex);
end;

function VBDIO_Latch_Read(DeviceIndex: LongWord; pLowLatches, pHighLatches, pNoLatches: PByte; pLatchesBytes: PLongWord): LongWord; stdcall;
begin
  Result := DIO_Latch_Read(DeviceIndex, pLowLatches, pHighLatches, pNoLatches, pLatchesBytes);
end;

function VBDIO_Deb_SetConfig(DeviceIndex: LongWord; pDebTable: Pointer; pDebTableBytes: PLongWord): LongWord; stdcall;
begin
  Result := DIO_Deb_SetConfig(DeviceIndex, pDebTable, pDebTableBytes);
end;

function VBDIO_Deb_ReadAll(DeviceIndex: LongWord; pDebData: PByte): LongWord; stdcall;
begin
  Result := DIO_Deb_ReadAll(DeviceIndex, pDebData);
end;

function VBADC_BulkMode(DeviceIndex, BulkMode: LongWord): LongWord; stdcall;
begin
  Result := ADC_BulkMode(DeviceIndex, BulkMode);
end;

function VBADC_BulkContinuousCallbackStart(DeviceIndex: LongWord; BufSize: LongWord; BaseBufCount: LongWord; Context: LongWord; pCallback: Pointer): LongWord; stdcall;
begin
  Result := ADC_BulkContinuousCallbackStart(DeviceIndex, BufSize, BaseBufCount, Context, pCallback);
end;

function VBADC_BulkContinuousCallbackStartClocked(DeviceIndex: LongWord; BufSize: LongWord; BaseBufCount: LongWord; Context: LongWord; pCallback: Pointer; var Hz: Double): LongWord; stdcall;
begin
  Result := ADC_BulkContinuousCallbackStartClocked(DeviceIndex, BufSize, BaseBufCount, Context, pCallback, Hz);
end;

function VBADC_BulkContinuousRingStart(DeviceIndex: LongWord; RingBufferSize: LongWord; PacketsPerBlock: LongWord): LongWord; stdcall;
begin
  Result := ADC_BulkContinuousRingStart(DeviceIndex, RingBufferSize, PacketsPerBlock);
end;

function VBADC_BulkContinuousEnd(DeviceIndex: LongWord; pIOStatus: PLongWord): LongWord; stdcall;
begin
  Result := ADC_BulkContinuousEnd(DeviceIndex, pIOStatus);
end;

function VBADC_GetBuf(DeviceIndex: LongWord; out pData: Pointer; out BufSize: LongWord; pReserved: Pointer; Timeout: Double): LongWord; stdcall;
begin
  Result := ADC_GetBuf(DeviceIndex, pData, BufSize, pReserved, Timeout);
end;

function VBADC_ReadData(DeviceIndex: LongWord; Config: PByte; var ScansToRead: LongWord; pData: PDouble; Timeout: Double): LongWord; stdcall;
begin
  Result := ADC_ReadData(DeviceIndex, Config, ScansToRead, pData, Timeout);
end;

function VBADC_FullStartRing(DeviceIndex: LongWord; pConfigBuf: Pointer; var ConfigBufSize: LongWord; CalFileName: PAnsiChar; pCounterHz: PDouble; RingBufferSize: LongWord; PacketsPerBlock: LongWord): LongWord; stdcall;
begin
  Result := ADC_FullStartRing(DeviceIndex, pConfigBuf, ConfigBufSize, CalFileName, pCounterHz, RingBufferSize, PacketsPerBlock);
end;





exports
  {
  , DoIOBench           , DoIOBench            name '_DoIOBench'           //, VBDoIOBench
  {}

    DEB_BufTest,
    GetDeviceHandle,
    GetPipes,
    DEB_SetInterface, DEB_BulkIn, DEB_BulkOut,
    AWU_GenericBulkIn, AWU_GenericBulkOut,
    ADC_BulkAbort,
    ADC_BulkContinuousDebug

  , ADC_GetBuf                                      , ADC_GetBuf                             name '_ADC_GetBuf'                               , VBADC_GetBuf

  , ADC_CSA_GetScanOversamples , ADC_CSA_GetScanOversamples name '_ADC_CSA_GetScanOversamples' , VBADC_CSA_GetScanOversamples



  , DACOutputLoadProcess                            , DACOutputLoadProcess                   name '_DACOutputLoadProcess'                     , VBDACOutputLoadProcess

  , AIOUSB_AbortPipe                                , AIOUSB_AbortPipe                       name '_AIOUSB_AbortPipe'                         , VBAIOUSB_AbortPipe

  , AIOUSB_QuerySimplePNPData                       , AIOUSB_QuerySimplePNPData              name '_AIOUSB_GetPNPData'                        , VBAIOUSB_QuerySimplePNPData

  , ADC_CSA_InitFastScanV  name 'ADC_InitFastScanV' , ADC_CSA_InitFastScanV                  name '_ADC_InitFastScanV'                        , VBADC_CSA_InitFastScanV  name 'VBADC_InitFastScanV'
  , ADC_CSA_ResetFastScanV name 'ADC_ResetFastScanV', ADC_CSA_ResetFastScanV                 name '_ADC_ResetFastScanV'                       , VBADC_CSA_ResetFastScanV name 'VBADC_ResetFastScanV'
  , ADC_CSA_GetFastScanV   name 'ADC_GetFastScanV'  , ADC_CSA_GetFastScanV                   name '_ADC_GetFastScanV'                         , VBADC_CSA_GetFastScanV   name 'VBADC_GetFastScanV'

  , WDG_Pet                                         , WDG_Pet                                name '_WDG_Pet'                                  , VBWDG_Pet
  , WDG_GetStatus                                   , WDG_GetStatus                          name '_WDG_GetStatus'                            , VBWDG_GetStatus
  , WDG_SetConfig                                   , WDG_SetConfig                          name '_WDG_SetConfig'                            , VBWDG_SetConfig

  , AIOUSB_ReloadDeviceLinks                        , AIOUSB_ReloadDeviceLinks               name '_AIOUSB_ReloadDeviceLinks'                 , VBAIOUSB_ReloadDeviceLinks

  , AIOUSB_UploadD15LoFirmwaresByPID                , AIOUSB_UploadD15LoFirmwaresByPID       name '_AIOUSB_UploadD15LoFirmwaresByPID'         , VBAIOUSB_UploadD15LoFirmwaresByPID

  , ADC_ReadData                                    , ADC_ReadData                           name '_ADC_ReadData'                             , VBADC_ReadData
  , ADC_FullStartRing                               , ADC_FullStartRing                      name '_ADC_FullStartRing'                        , VBADC_FullStartRing
  , ADC_BulkContinuousRingStart                     , ADC_BulkContinuousRingStart            name '_ADC_BulkContinuousRingStart'              , VBADC_BulkContinuousRingStart

  , DIO_ConfigureMasked                             , DIO_ConfigureMasked                    name '_DIO_ConfigureMasked'                      , VBDIO_ConfigureMasked
  , DACOutputSetClock                               , DACOutputSetClock                      name '_DACOutputSetClock'                        , VBDACOutputSetClock

  , DACDIO_WriteAll                                 , DACDIO_WriteAll                        name '_DACDIO_WriteAll'                          , VBDACDIO_WriteAll

  , ADC_BulkContinuousCallbackStartClocked          , ADC_BulkContinuousCallbackStartClocked name '_ADC_BulkContinuousCallbackStartClocked'   , VBADC_BulkContinuousCallbackStartClocked

  , ADC_SetCalAndSave                               , ADC_SetCalAndSave                      name '_ADC_SetCalAndSave'                        , VBADC_SetCalAndSave

  , ADC_CSA_InitFastScanV                           , ADC_CSA_InitFastScanV                  name '_ADC_CSA_InitFastScanV'                    , VBADC_CSA_InitFastScanV
  , ADC_CSA_ResetFastScanV                          , ADC_CSA_ResetFastScanV                 name '_ADC_CSA_ResetFastScanV'                   , VBADC_CSA_ResetFastScanV
  , ADC_CSA_GetFastScanV                            , ADC_CSA_GetFastScanV                   name '_ADC_CSA_GetFastScanV'                     , VBADC_CSA_GetFastScanV

  , ADC_BulkMode                                    , ADC_BulkMode                           name '_ADC_BulkMode'                             , VBADC_BulkMode
  , ADC_GetTrigScanV                                , ADC_GetTrigScanV                       name '_ADC_GetTrigScanV'                         , VBADC_GetTrigScanV
  , ADC_GetTrigScan                                 , ADC_GetTrigScan                        name '_ADC_GetTrigScan'                          , VBADC_GetTrigScan

  , DIO_CSA_ReadAllString                           , DIO_CSA_ReadAllString                  name '_DIO_CSA_ReadAllString'                    , VBDIO_CSA_ReadAllString
  , AIOUSB_ResetChip                                , AIOUSB_ResetChip                       name '_AIOUSB_ResetChip'                         , VBAIOUSB_ResetChip
  , ADC_BulkContinuousEnd                           , ADC_BulkContinuousEnd                  name '_ADC_BulkContinuousEnd'                    , VBADC_BulkContinuousEnd
  , ADC_BulkContinuousCallbackStart                 , ADC_BulkContinuousCallbackStart        name '_ADC_BulkContinuousCallbackStart'          , VBADC_BulkContinuousCallbackStart

  , DIO_Deb_ReadAll                                 , DIO_Deb_ReadAll                        name '_DIO_Deb_ReadAll'                          , VBDIO_Deb_ReadAll
  , DIO_Deb_SetConfig                               , DIO_Deb_SetConfig                      name '_DIO_Deb_SetConfig'                        , VBDIO_Deb_SetConfig

  , DIO_Latch_Read                                  , DIO_Latch_Read                         name '_DIO_Latch_Read'                           , VBDIO_Latch_Read
  , DIO_Latch_Reset                                 , DIO_Latch_Reset                        name '_DIO_Latch_Reset'                          , VBDIO_Latch_Reset
  , DIO_Latch_SetDivisor                            , DIO_Latch_SetDivisor                   name '_DIO_Latch_SetDivisor'                     , VBDIO_Latch_SetDivisor

  , DIO_PWM_Start                                   , DIO_PWM_Start                          name '_DIO_PWM_Start'                            , VBDIO_PWM_Start

  , DIO_Automap_SetTickDivisor                      , DIO_Automap_SetTickDivisor             name '_DIO_Automap_SetTickDivisor'               , VBDIO_Automap_SetTickDivisor
  , DIO_Automap_AddEntry                            , DIO_Automap_AddEntry                   name '_DIO_Automap_AddEntry'                     , VBDIO_Automap_AddEntry
  , DIO_Automap_SetTable                            , DIO_Automap_SetTable                   name '_DIO_Automap_SetTable'                     , VBDIO_Automap_SetTable
  , DIO_Automap_ClearTable                          , DIO_Automap_ClearTable                 name '_DIO_Automap_ClearTable'                   , VBDIO_Automap_ClearTable

  , AIOUSB_SetGlobalTickRate                        , AIOUSB_SetGlobalTickRate               name '_AIOUSB_SetGlobalTickRate'                 , VBAIOUSB_SetGlobalTickRate

  , AIOUSB_GetDefaultsTable                         , AIOUSB_GetDefaultsTable                name '_AIOUSB_GetDefaultsTable'                  , VBAIOUSB_GetDefaultsTable
  , AIOUSB_SetDefaultsTable                         , AIOUSB_SetDefaultsTable                name '_AIOUSB_SetDefaultsTable'                  , VBAIOUSB_SetDefaultsTable
  , AIOUSB_RestoreFactoryDefaults                   , AIOUSB_RestoreFactoryDefaults          name '_AIOUSB_RestoreFactoryDefaults'            , VBAIOUSB_RestoreFactoryDefaults
  , AIOUSB_SaveStateAsDefaults                      , AIOUSB_SaveStateAsDefaults             name '_AIOUSB_SaveStateAsDefaults'               , VBAIOUSB_SaveStateAsDefaults

  , DAC_CSA_ClearRangeLimits                        , DAC_CSA_ClearRangeLimits               name '_DAC_CSA_ClearRangeLimits'                 , VBDAC_CSA_ClearRangeLimits
  , DAC_CSA_SetRangeLimits                          , DAC_CSA_SetRangeLimits                 name '_DAC_CSA_SetRangeLimits'                   , VBDAC_CSA_SetRangeLimits
  , DIO_CSA_DebounceSet                             , DIO_CSA_DebounceSet                    name '_DIO_CSA_DebounceSet'                      , VBDIO_CSA_DebounceSet
  , DIO_CSA_DebounceReadAll                         , DIO_CSA_DebounceReadAll                name '_DIO_CSA_DebounceReadAll'                  , VBDIO_CSA_DebounceReadAll

  , ADC_SetFastITScanVChannels                      , ADC_SetFastITScanVChannels             name '_ADC_SetFastITScanVChannels'               , VBADC_SetFastITScanVChannels

  , GetDeviceByEEPROMByte                           , GetDeviceByEEPROMByte                  name '_GetDeviceByEEPROMByte'                    , VBGetDeviceByEEPROMByte
  , GetDeviceByEEPROMData                           , GetDeviceByEEPROMData                  name '_GetDeviceByEEPROMData'                    , VBGetDeviceByEEPROMData

  , DIO_CSA_DoSync                                  , DIO_CSA_DoSync                         name '_DIO_CSA_DoSync'                           , VBDIO_CSA_DoSync
  , ADC_ResetFastITScanV                            , ADC_ResetFastITScanV                   name '_ADC_ResetFastITScanV'                     , VBADC_ResetFastITScanV
  , ADC_InitFastITScanV                             , ADC_InitFastITScanV                    name '_ADC_InitFastITScanV'                      , VBADC_InitFastITScanV
  , ADC_GetFastITScanV                              , ADC_GetFastITScanV                     name '_ADC_GetFastITScanV'                       , VBADC_GetFastITScanV
  , ADC_GetITScanV                                  , ADC_GetITScanV                         name '_ADC_GetITScanV'                           , VBADC_GetITScanV

  , ADC_GetCalRefV                                  , ADC_GetCalRefV                         name '_ADC_GetCalRefV'                           , VBADC_GetCalRefV

  , AIOUSB_CloseDevice                              , AIOUSB_CloseDevice                     name '_AIOUSB_CloseDevice'                       , VBAIOUSB_CloseDevice

  , GetDeviceBySerialNumber                         , GetDeviceBySerialNumber                name '_GetDeviceBySerialNumber'                  , VBGetDeviceBySerialNumber

  , AIOUSB_FlashEraseSector                         , AIOUSB_FlashEraseSector                name '_AIOUSB_FlashEraseSector'                  , VBAIOUSB_FlashEraseSector
  , AIOUSB_FlashWrite                               , AIOUSB_FlashWrite                      name '_AIOUSB_FlashWrite'                        , VBAIOUSB_FlashWrite
  , AIOUSB_FlashRead                                , AIOUSB_FlashRead                       name '_AIOUSB_FlashRead'                         , VBAIOUSB_FlashRead
  , DACSetChannelCal                                , DACSetChannelCal                       name '_DACSetChannelCal'                         , VBDACSetChannelCal
  , DACSetBoardRange                                , DACSetBoardRange                       name '_DACSetBoardRange'                         , VBDACSetBoardRange

  , DACOutputProcess                                , DACOutputProcess                       name '_DACOutputProcess'                         , VBDACOutputProcess
  , DACOutputOpen name 'DACOutputOpenNoClear'       , DACOutputOpen                          name '_DACOutputOpenNoClear'                     , VBDACOutputOpen name 'VBDACOutputOpenNoClear'

  , ResolveDeviceIndex                              , ResolveDeviceIndex                     name '_ResolveDeviceIndex'                       , VBResolveDeviceIndex
  , DIO_Read1                                       , DIO_Read1                              name '_DIO_Read1'                                , VBDIO_Read1

  , SelectDeviceViaUI                               , SelectDeviceViaUI                      name '_SelectDeviceViaUI'                        , VBSelectDeviceViaUI

  , AIOUSB_GetStreamStatus                          , AIOUSB_GetStreamStatus                 name '_AIOUSB_GetStreamStatus'                   , VBAIOUSB_GetStreamStatus

  , ADC_GetChannelV                                 , ADC_GetChannelV                        name '_ADC_GetChannelV'                          , VBADC_GetChannelV

  , DACOutputSetInterlock                           , DACOutputSetInterlock                  name '_DACOutputSetInterlock'                    , VBDACOutputSetInterlock
  , DACOutputStart                                  , DACOutputStart                         name '_DACOutputStart'                           , VBDACOutputStart
  , DACOutputCloseNoEnd                             , DACOutputCloseNoEnd                    name '_DACOutputCloseNoEnd'                      , VBDACOutputCloseNoEnd
  , DACOutputFrameRaw                               , DACOutputFrameRaw                      name '_DACOutputFrameRaw'                        , VBDACOutputFrameRaw

  , ADC_SetScanLimits                               , ADC_SetScanLimits                      name '_ADC_SetScanLimits'                        , VBADC_SetScanLimits
  , ADC_SetOversample                               , ADC_SetOversample                      name '_ADC_SetOversample'                        , VBADC_SetOversample
  , ADC_GetScan                                     , ADC_GetScan                            name '_ADC_GetScan'                              , VBADC_GetScan
  , ADC_GetScanV                                    , ADC_GetScanV                           name '_ADC_GetScanV'                             , VBADC_GetScanV

  , AIOUSB_SetStreamingBlockSize                    , AIOUSB_SetStreamingBlockSize           name '_AIOUSB_SetStreamingBlockSize'             , VBAIOUSB_SetStreamingBlockSize

  , GetDeviceSerialNumber                           , GetDeviceSerialNumber                  name '_GetDeviceSerialNumber'                    , VBGetDeviceSerialNumber
  , GetDeviceUniqueStr                              , GetDeviceUniqueStr                     name '_GetDeviceUniqueStr'                       , VBGetDeviceUniqueStr

  , CTR_StartMeasuringPulseWidth                    , CTR_StartMeasuringPulseWidth           name '_CTR_StartMeasuringPulseWidth'             , VBCTR_StartMeasuringPulseWidth
  , CTR_StopMeasuringPulseWidth                     , CTR_StopMeasuringPulseWidth            name '_CTR_StopMeasuringPulseWidth'              , VBCTR_StopMeasuringPulseWidth
  , CTR_GetPulseWidthMeasurement                    , CTR_GetPulseWidthMeasurement           name '_CTR_GetPulseWidthMeasurement'             , VBCTR_GetPulseWidthMeasurement

  , ClearDevices                                    , ClearDevices                           name '_ClearDevices'                             , VBClearDevices

  , CTR_8254Load                                    , CTR_8254Load                           name '_CTR_8254Load'                             , VBCTR_8254Load

  , DIO_ConfigurationQuery                          , DIO_ConfigurationQuery                 name '_DIO_ConfigurationQuery'                   , VBDIO_ConfigurationQuery
  , DIO_ConfigureEx                                 , DIO_ConfigureEx                        name '_DIO_ConfigureEx'                          , VBDIO_ConfigureEx

  , AIOUSB_OfflineWrite1                            , AIOUSB_OfflineWrite1                   name '_AIOUSB_OfflineWrite1'                     , VBAIOUSB_OfflineWrite1
  , AIOUSB_OfflineRead1                             , AIOUSB_OfflineRead1                    name '_AIOUSB_OfflineRead1'                      , VBAIOUSB_OfflineRead1
  , ADC_QueryCal                                    , ADC_QueryCal                           name '_ADC_QueryCal'                             , VBADC_QueryCal

  , AIOUSB_ClearFIFO                                , AIOUSB_ClearFIFO                       name '_AIOUSB_ClearFIFO'                         , VBAIOUSB_ClearFIFO

  , ADC_GetConfig                                   , ADC_GetConfig                          name '_ADC_GetConfig'                            , VBADC_GetConfig
  , ADC_SetConfig                                   , ADC_SetConfig                          name '_ADC_SetConfig'                            , VBADC_SetConfig
  , ADC_RangeAll                                    , ADC_RangeAll                           name '_ADC_RangeAll'                             , VBADC_RangeAll
  , ADC_Range1                                      , ADC_Range1                             name '_ADC_Range1'                               , VBADC_Range1
  , ADC_ADMode                                      , ADC_ADMode                             name '_ADC_ADMode'                               , VBADC_ADMode
  , ADC_SetCal                                      , ADC_SetCal                             name '_ADC_SetCal'                               , VBADC_SetCal
  , ADC_Initialize                                  , ADC_Initialize                         name '_ADC_Initialize'                           , VBADC_Initialize
  , ADC_Start                                       , ADC_Start                              name '_ADC_Start'                                , VBADC_Start
  , ADC_Stop                                        , ADC_Stop                               name '_ADC_Stop'                                 , VBADC_Stop
  , ADC_BulkAcquire                                 , ADC_BulkAcquire                        name '_ADC_BulkAcquire'                          , VBADC_BulkAcquire
  , ADC_BulkPoll                                    , ADC_BulkPoll                           name '_ADC_BulkPoll'                             , VBADC_BulkPoll
  , ADC_GetImmediate                                , ADC_GetImmediate                       name '_ADC_GetImmediate'                         , VBADC_GetImmediate

  , DIO_SPI_Read                                    , DIO_SPI_Read                           name '_DIO_SPI_Read'                             , VBDIO_SPI_Read
  , DIO_SPI_Write                                   , DIO_SPI_Write                          name '_DIO_SPI_Write'                            , VBDIO_SPI_Write

  , CTR_8254ReadStatus                              , CTR_8254ReadStatus                     name '_CTR_8254ReadStatus'                       , VBCTR_8254ReadStatus

  , GenericVendorRead                               , GenericVendorRead                      name '_GenericVendorRead'                        , VBGenericVendorRead
  , GenericVendorWrite                              , GenericVendorWrite                     name '_GenericVendorWrite'                       , VBGenericVendorWrite

  , DIO_StreamOpen                                  , DIO_StreamOpen                         name '_DIO_StreamOpen'                           , VBDIO_StreamOpen
  , DIO_StreamClose                                 , DIO_StreamClose                        name '_DIO_StreamClose'                          , VBDIO_StreamClose
  , DIO_StreamFrame                                 , DIO_StreamFrame                        name '_DIO_StreamFrame'                          , VBDIO_StreamFrame
  , DIO_StreamSetClocks                             , DIO_StreamSetClocks                    name '_DIO_StreamSetClocks'                      , VBDIO_StreamSetClocks

  , CTR_SetWaitGates                                , CTR_SetWaitGates                       name '_CTR_SetWaitGates'                         , VBCTR_SetWaitGates
  , CTR_EndWaitGates                                , CTR_EndWaitGates                       name '_CTR_EndWaitGates'                         , VBCTR_EndWaitGates
  , CTR_WaitForGate                                 , CTR_WaitForGate                        name '_CTR_WaitForGate'                          , VBCTR_WaitForGate
  , CTR_8254ReadAll                                 , CTR_8254ReadAll                        name '_CTR_8254ReadAll'                          , VBCTR_8254ReadAll
  , CTR_8254ReadLatched                             , CTR_8254ReadLatched                    name '_CTR_8254ReadLatched'                      , VBCTR_8254ReadLatched
  , CTR_8254SelectGate                              , CTR_8254SelectGate                     name '_CTR_8254SelectGate'                       , VBCTR_8254SelectGate

  , DACMultiDirect                                  , DACMultiDirect                         name '_DACMultiDirect'                           , VBDACMultiDirect

  , DACDirect                                       , DACDirect                              name '_DACDirect'                                , VBDACDirect

  , CustomEEPROMRead                                , CustomEEPROMRead                       name '_CustomEEPROMRead'                         , VBCustomEEPROMRead
  , CustomEEPROMWrite                               , CustomEEPROMWrite                      name '_CustomEEPROMWrite'                        , VBCustomEEPROMWrite

  , AIOUSB_UploadFirmware                           , AIOUSB_UploadFirmware                  name '_AIOUSB_UploadFirmware'

  , DACOutputOpen                                   , DACOutputOpen                          name '_DACOutputOpen'                            , VBDACOutputOpen
  , DACOutputClose                                  , DACOutputClose                         name '_DACOutputClose'                           , VBDACOutputClose
  , DACOutputSetCount                               , DACOutputSetCount                      name '_DACOutputSetCount'                        , VBDACOutputSetCount
  , DACOutputFrame                                  , DACOutputFrame                         name '_DACOutputFrame'                           , VBDACOutputFrame
  , DACOutputAbort                                  , DACOutputAbort                         name '_DACOutputAbort'                           , VBDACOutputAbort
  , DACOutputStatus                                 , DACOutputStatus                        name '_DACOutputStatus'                          , VBDACOutputStatus

  , CTR_StartOutputFreq                             , CTR_StartOutputFreq                    name '_CTR_StartOutputFreq'                      , VBCTR_StartOutputFreq

  , CTR_8254Read                                    , CTR_8254Read                           name '_CTR_8254Read'                             , VBCTR_8254Read
  , CTR_8254ReadModeLoad                            , CTR_8254ReadModeLoad                   name '_CTR_8254ReadModeLoad'                     , VBCTR_8254ReadModeLoad
  , CTR_8254ModeLoad                                , CTR_8254ModeLoad                       name '_CTR_8254ModeLoad'                         , VBCTR_8254ModeLoad
  , CTR_8254Mode                                    , CTR_8254Mode                           name '_CTR_8254Mode'                             , VBCTR_8254Mode

  , DIO_ReadAll                                     , DIO_ReadAll                            name '_DIO_ReadAll'                              , VBDIO_ReadAll
  , DIO_Read8                                       , DIO_Read8                              name '_DIO_Read8'                                , VBDIO_Read8
  , DIO_WriteAll                                    , DIO_WriteAll                           name '_DIO_WriteAll'                             , VBDIO_WriteAll
  , DIO_Write8                                      , DIO_Write8                             name '_DIO_Write8'                               , VBDIO_Write8
  , DIO_Write1                                      , DIO_Write1                             name '_DIO_Write1'                               , VBDIO_Write1
  , DIO_Configure                                   , DIO_Configure                          name '_DIO_Configure'                            , VBDIO_Configure

  , QueryDeviceInfo                                 , QueryDeviceInfo                        name '_QueryDeviceInfo'                          , VBQueryDeviceInfo
  , GetDevices                                      , GetDevices                             name '_GetDevices'                               , VBGetDevices
  ;



begin
  LoadDriverLinks;
end.
