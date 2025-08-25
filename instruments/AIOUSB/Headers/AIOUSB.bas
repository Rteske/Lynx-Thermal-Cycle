Attribute VB_Name = "AIOUSB"
Public Const diNone = -1
Public Const diFirst = -2
Public Const diOnly = -3



Public Declare Function GetDevices Lib "AIOUSB" Alias "VBGetDevices" () As Long
Public Declare Function QueryDeviceInfo Lib "AIOUSB" Alias "VBQueryDeviceInfo" (ByVal DeviceIndex As Long, ByRef PID As Long, ByRef NameSize As Long, ByVal Name As String, ByRef DIOBytes As Long, ByRef Counters As Long) As Long
Public Declare Function AIOUSB_CloseDevice Lib "AIOUSB" Alias "VBAIOUSB_CloseDevice" (ByVal DeviceIndex As Long) As Long
Public Declare Function ClearDevices Lib "AIOUSB" Alias "VBClearDevices" () As Long
Public Declare Function GetDeviceUniqueStr Lib "AIOUSB" Alias "VBGetDeviceUniqueStr" (ByVal DeviceIndex As Long, ByRef pIIDSize As Long, ByVal pIID As String) As Long
Public Declare Function GetDeviceSerialNumber Lib "AIOUSB" Alias "VBGetDeviceSerialNumber" (ByVal DeviceIndex As Long, ByRef pSerialNumber As Currency) As Long
Public Declare Function ResolveDeviceIndex Lib "AIOUSB" Alias "VBResolveDeviceIndex" (ByVal DeviceIndex As Long) As Long
Public Declare Function GetDeviceByEEPROMByte Lib "AIOUSB" Alias "VBGetDeviceByEEPROMByte" (ByVal Data As Byte) As Long
Public Declare Function GetDeviceByEEPROMData Lib "AIOUSB" Alias "VBGetDeviceByEEPROMData" (ByVal StartAddress As Long, ByVal DataSize As Long, ByRef pData As Byte) As Long
Public Declare Function GetDeviceBySerialNumber Lib "AIOUSB" Alias "VBGetDeviceBySerialNumber" (ByRef pSerialNumber As Currency) As Long

Public Declare Function AIOUSB_ClearFIFO Lib "AIOUSB" Alias "VBAIOUSB_ClearFIFO" (ByVal DeviceIndex As Long, ByVal TimeMethod As Long) As Long
Public Declare Function AIOUSB_SetStreamingBlockSize Lib "AIOUSB" Alias "VBAIOUSB_SetStreamingBlockSize" (ByVal DeviceIndex As Long, ByVal BlockSize As Long) As Long
Public Declare Function AIOUSB_ResetChip Lib "AIOUSB" Alias "VBAIOUSB_ResetChip" (ByVal DeviceIndex As Long) As Long
Public Declare Function AIOUSB_ReloadDeviceLinks Lib "AIOUSB" Alias "VBAIOUSB_ReloadDeviceLinks" () As Long
Public Declare Function AIOUSB_UploadD15LoFirmwaresByPID Lib "AIOUSB" Alias "VBAIOUSB_UploadD15LoFirmwaresByPID" (ByVal pFirmScript As String) As Long
Public Declare Function AIOUSB_SetGlobalTickRate Lib "AIOUSB" Alias "VBAIOUSB_SetGlobalTickRate" (ByVal DeviceIndex As Long, ByRef pHz As Double) As Long

Public Declare Function AIOUSB_QuerySimplePNPData Lib "AIOUSB" Alias "VBAIOUSB_QuerySimplePNPData" (ByVal DeviceIndex As Long, ByRef pPNPData As Any, ByRef pPNPDataBytes As Long) As Long

Public Declare Function CustomEEPROMRead Lib "AIOUSB" Alias "VBCustomEEPROMRead" (ByVal DeviceIndex As Long, ByVal StartAddress As Long, ByRef DataSize As Long, ByRef Data As Any) As Long
Public Declare Function CustomEEPROMWrite Lib "AIOUSB" Alias "VBCustomEEPROMWrite" (ByVal DeviceIndex As Long, ByVal StartAddress As Long, ByVal DataSize As Long, ByRef Data As Any) As Long
Public Declare Function AIOUSB_FlashRead Lib "AIOUSB" Alias "VBAIOUSB_FlashRead" (ByVal DeviceIndex As Long, ByVal StartAddress As Long, ByRef DataSize As Long, ByRef Data As Any) As Long
Public Declare Function AIOUSB_FlashWrite Lib "AIOUSB" Alias "VBAIOUSB_FlashWrite" (ByVal DeviceIndex As Long, ByVal StartAddress As Long, ByVal DataSize As Long, ByRef Data As Any) As Long
Public Declare Function AIOUSB_FlashEraseSector Lib "AIOUSB" Alias "VBAIOUSB_FlashEraseSector" (ByVal DeviceIndex As Long, ByVal Sector As Long) As Long

Public Declare Function GenericVendorRead Lib "AIOUSB" Alias "VBGenericVendorRead" (ByVal DeviceIndex As Long, ByVal Request As Byte, ByVal Value As Integer, ByVal Index As Integer, ByRef pDataSize As Long, ByRef pData As Any) As Long
Public Declare Function GenericVendorWrite Lib "AIOUSB" Alias "VBGenericVendorWrite" (ByVal DeviceIndex As Long, ByVal Request As Byte, ByVal Value As Integer, ByVal Index As Integer, ByVal DataSize As Long, ByRef pData As Any) As Long
Public Declare Function AWU_GenericBulkIn Lib "AIOUSB" Alias "VBAWU_GenericBulkIn" (ByVal DeviceIndex As Long, ByVal PipeID As Long, ByRef pData As Any, ByVal DataSize As Long, ByVal BytesRead As Long) As Long
Public Declare Function AWU_GenericBulkOut Lib "AIOUSB" Alias "VBAWU_GenericBulkOut" (ByVal DeviceIndex As Long, ByVal PipeID As Long, ByRef pData As Any, ByVal DataSize As Long, ByVal BytesWritten As Long) As Long



Public Declare Function ADC_GetScan Lib "AIOUSB" Alias "VBADC_GetScan" (ByVal DeviceIndex As Long, ByRef pBuf As Integer) As Long
Public Declare Function ADC_GetScanV Lib "AIOUSB" Alias "VBADC_GetScanV" (ByVal DeviceIndex As Long, ByRef pBuf As Double) As Long
Public Declare Function ADC_GetChannelV Lib "AIOUSB" Alias "VBADC_GetChannelV" (ByVal DeviceIndex As Long, ByVal ChannelIndex As Long, ByRef pBuf As Double) As Long
Public Declare Function ADC_GetCalRefV Lib "AIOUSB" Alias "VBADC_GetCalRefV" (ByVal DeviceIndex As Long, ByVal CalRefIndex As Long, ByRef pRef As Double) As Long

Public Declare Function ADC_GetTrigScan Lib "AIOUSB" Alias "VBADC_GetTrigScan" (ByVal DeviceIndex As Long, ByRef pBuf As Integer, ByVal TimeoutMS As Long) As Long
Public Declare Function ADC_GetTrigScanV Lib "AIOUSB" Alias "VBADC_GetTrigScanV" (ByVal DeviceIndex As Long, ByRef pBuf As Double, ByVal TimeoutMS As Long) As Long

Public Declare Function ADC_GetConfig Lib "AIOUSB" Alias "VBADC_GetConfig" (ByVal DeviceIndex As Long, ByRef pConfigBuf As Any, ByRef ConfigBufSize As Long) As Long
Public Declare Function ADC_SetConfig Lib "AIOUSB" Alias "VBADC_SetConfig" (ByVal DeviceIndex As Long, ByRef pConfigBuf As Any, ByRef ConfigBufSize As Long) As Long
Public Declare Function ADC_ADMode Lib "AIOUSB" Alias "VBADC_ADMode" (ByVal DeviceIndex As Long, ByVal TriggerMode As Byte, ByVal CalMode As Byte) As Long
Public Declare Function ADC_Range1 Lib "AIOUSB" Alias "VBADC_Range1" (ByVal DeviceIndex As Long, ByVal ADChannel As Long, ByVal GainCode As Byte, ByVal bDifferential As Long) As Long
Public Declare Function ADC_RangeAll Lib "AIOUSB" Alias "VBADC_RangeAll" (ByVal DeviceIndex As Long, ByRef GainCodes As Byte, ByVal bDifferential As Long) As Long
Public Declare Function ADC_SetScanLimits Lib "AIOUSB" Alias "VBADC_SetScanLimits" (ByVal DeviceIndex As Long, ByVal StartChannel As Long, ByVal EndChannel As Long) As Long
Public Declare Function ADC_SetOversample Lib "AIOUSB" Alias "VBADC_SetOversample" (ByVal DeviceIndex As Long, ByVal Oversample As Byte) As Long
Public Declare Function ADC_QueryCal Lib "AIOUSB" Alias "VBADC_QueryCal" (ByVal DeviceIndex As Long) As Long
Public Declare Function ADC_SetCal Lib "AIOUSB" Alias "VBADC_SetCal" (ByVal DeviceIndex As Long, ByVal CalFileName As String) As Long
Public Declare Function ADC_SetCalAndSave Lib "AIOUSB" Alias "VBADC_SetCalAndSave" (ByVal DeviceIndex As Long, ByVal CalFileName As String, ByVal SaveCalFileName As String) As Long
Public Declare Function ADC_Initialize Lib "AIOUSB" Alias "VBADC_Initialize" (ByVal DeviceIndex As Long, ByRef pConfigBuf As Byte, ByRef pConfigBufSize As Long, ByVal CalFileName As String) As Long
Public Declare Function ADC_GetImmediate Lib "AIOUSB" Alias "VBADC_GetImmediate" (ByVal DeviceIndex As Long, ByVal Channel As Long, ByRef pBuf As Integer) As Long

Public Declare Function ADC_BulkAcquire Lib "AIOUSB" Alias "VBADC_BulkAcquire" (ByVal DeviceIndex As Long, ByVal BufSize As Long, ByRef Buf As Any) As Long
Public Declare Function ADC_BulkPoll Lib "AIOUSB" Alias "VBADC_BulkPoll" (ByVal DeviceIndex As Long, ByRef BytesLeft As Long) As Long
Public Declare Function ADC_BulkAbort Lib "AIOUSB" Alias "VBADC_BulkAbort" (ByVal DeviceIndex As Long) As Long

Public Declare Function ADC_BulkContinuousRingStart Lib "AIOUSB" Alias "VBADC_BulkContinuousRingStart" (ByVal DeviceIndex As Long, ByVal RingBufferSize As Long, ByVal PacketsPerBlock As Long) As Long
Public Declare Function ADC_BulkContinuousEnd Lib "AIOUSB" Alias "VBADC_BulkContinuousEnd" (ByVal DeviceIndex As Long, ByRef pIOStatus As Long) As Long

Public Declare Function ADC_FullStartRing Lib "AIOUSB" Alias "VBADC_FullStartRing" (ByVal DeviceIndex As Long, ByRef pConfigBuf As Any, ByRef ConfigBufSize As Long, ByVal CalFileName As String, ByRef pCounterHz As Double, ByVal RingBufferSize As Long, ByVal PacketsPerBlock As Long) As Long
Public Declare Function ADC_ReadData Lib "AIOUSB" Alias "VBADC_ReadData" (ByVal DeviceIndex As Long, ByRef pConfigBuf As Any, ByRef ScansToRead As Long, ByRef pData As Double, ByVal Timeout As Double) As Long

Public Declare Function ADC_InitFastITScanV Lib "AIOUSB" Alias "VBADC_InitFastITScanV" (ByVal DeviceIndex As Long) As Long
Public Declare Function ADC_ResetFastITScanV Lib "AIOUSB" Alias "VBADC_ResetFastITScanV" (ByVal DeviceIndex As Long) As Long
Public Declare Function ADC_SetFastITScanVChannels Lib "AIOUSB" Alias "VBADC_SetFastITScanVChannels" (ByVal DeviceIndex As Long, NewChannels As Long) As Long
Public Declare Function ADC_GetFastITScanV Lib "AIOUSB" Alias "VBADC_GetFastITScanV" (ByVal DeviceIndex As Long, ByRef pBuf As Double) As Long
Public Declare Function ADC_GetITScanV Lib "AIOUSB" Alias "VBADC_GetITScanV" (ByVal DeviceIndex As Long, ByRef pBuf As Double) As Long

Public Declare Function ADC_InitFastScanV Lib "AIOUSB" Alias "VBADC_InitFastScanV" (ByVal DeviceIndex As Long) As Long
Public Declare Function ADC_ResetFastScanV Lib "AIOUSB" Alias "VBADC_ResetFastScanV" (ByVal DeviceIndex As Long) As Long
Public Declare Function ADC_GetFastScanV Lib "AIOUSB" Alias "VBADC_GetFastScanV" (ByVal DeviceIndex As Long, ByRef pBuf As Double) As Long


Public Declare Function CTR_8254Load Lib "AIOUSB" Alias "VBCTR_8254Load" (ByVal DeviceIndex As Long, ByVal BlockIndex As Long, ByVal CounterIndex As Long, ByVal LoadValue As Integer) As Long
Public Declare Function CTR_8254Mode Lib "AIOUSB" Alias "VBCTR_8254Mode" (ByVal DeviceIndex As Long, ByVal BlockIndex As Long, ByVal CounterIndex As Long, ByVal Mode As Long) As Long
Public Declare Function CTR_8254ModeLoad Lib "AIOUSB" Alias "VBCTR_8254ModeLoad" (ByVal DeviceIndex As Long, ByVal BlockIndex As Long, ByVal CounterIndex As Long, ByVal Mode As Long, ByVal LoadValue As Integer) As Long
Public Declare Function CTR_8254Read Lib "AIOUSB" Alias "VBCTR_8254Read" (ByVal DeviceIndex As Long, ByVal BlockIndex As Long, ByVal CounterIndex As Long, ByRef ReadValue As Integer) As Long
Public Declare Function CTR_8254ReadStatus Lib "AIOUSB" Alias "VBCTR_8254ReadStatus" (ByVal DeviceIndex As Long, ByVal BlockIndex As Long, ByVal CounterIndex As Long, ByRef ReadValue As Integer, ByRef Status As Byte) As Long
Public Declare Function CTR_8254ReadModeLoad Lib "AIOUSB" Alias "VBCTR_8254ReadModeLoad" (ByVal DeviceIndex As Long, ByVal BlockIndex As Long, ByVal CounterIndex As Long, ByVal Mode As Long, ByVal LoadValue As Integer, ByRef ReadValue As Integer) As Long

Public Declare Function CTR_StartOutputFreq Lib "AIOUSB" Alias "VBCTR_StartOutputFreq" (ByVal DeviceIndex As Long, ByVal BlockIndex As Long, ByRef Hz As Double) As Long

Public Declare Function CTR_8254ReadAll Lib "AIOUSB" Alias "VBCTR_8254ReadAll" (ByVal DeviceIndex As Long, ByRef pData As Any) As Long

Public Declare Function CTR_8254SelectGate Lib "AIOUSB" Alias "VBCTR_8254SelectGate" (ByVal DeviceIndex As Long, ByVal GateIndex As Long) As Long
Public Declare Function CTR_8254ReadLatched Lib "AIOUSB" Alias "VBCTR_8254ReadLatched" (ByVal DeviceIndex As Long, ByRef pData As Any) As Long
Public Declare Function CTR_SetWaitGates Lib "AIOUSB" Alias "VBCTR_SetWaitGates" (ByVal DeviceIndex As Long, ByVal A As Byte, ByVal B As Byte) As Long
Public Declare Function CTR_EndWaitGates Lib "AIOUSB" Alias "VBCTR_EndWaitGates" (ByVal DeviceIndex As Long) As Long
Public Declare Function CTR_WaitForGate Lib "AIOUSB" Alias "VBCTR_WaitForGate" (ByVal DeviceIndex As Long, ByVal GateIndex As Byte, ByRef pContent As Integer) As Long

Public Declare Function CTR_StartMeasuringPulseWidth Lib "AIOUSB" Alias "VBCTR_StartMeasuringPulseWidth" (ByVal DeviceIndex As Long) As Long
Public Declare Function CTR_StopMeasuringPulseWidth Lib "AIOUSB" Alias "VBCTR_StopMeasuringPulseWidth" (ByVal DeviceIndex As Long) As Long
Public Declare Function CTR_GetPulseWidthMeasurement Lib "AIOUSB" Alias "VBCTR_GetPulseWidthMeasurement" (ByVal DeviceIndex As Long, ByVal BlockIndex As Long, ByVal CounterIndex As Long, ByRef pReadValue As Integer) As Long



Public Declare Function DIO_Configure Lib "AIOUSB" Alias "VBDIO_Configure" (ByVal DeviceIndex As Long, ByVal Tristate As Boolean, ByRef OutMask As Any, ByRef Data As Any) As Long
Public Declare Function DIO_ConfigureEx Lib "AIOUSB" Alias "VBDIO_ConfigureEx" (ByVal DeviceIndex As Long, ByRef pOutMask As Any, ByRef pData As Any, ByRef pTristateMask As Any) As Long
Public Declare Function DIO_ConfigureMasked Lib "AIOUSB" Alias "VBDIO_ConfigureMasked" (ByVal DeviceIndex As Long, ByRef pOuts As Any, ByRef pOutsMask As Any, ByRef pData As Any, ByRef pDataMask As Any, ByRef pTristates As Any, ByRef pTristatesMask As Any) As Long
Public Declare Function DIO_ConfigurationQuery Lib "AIOUSB" Alias "VBDIO_ConfigurationQuery" (ByVal DeviceIndex As Long, ByRef pOutMask As Any, ByRef pTristateMask As Any) As Long

Public Declare Function DIO_Read1 Lib "AIOUSB" Alias "VBDIO_Read1" (ByVal DeviceIndex As Long, ByVal BitIndex As Long, ByRef Data As Byte) As Long
Public Declare Function DIO_Read8 Lib "AIOUSB" Alias "VBDIO_Read8" (ByVal DeviceIndex As Long, ByVal ByteIndex As Long, ByRef Data As Byte) As Long
Public Declare Function DIO_ReadAll Lib "AIOUSB" Alias "VBDIO_ReadAll" (ByVal DeviceIndex As Long, ByRef Data As Any) As Long

Public Declare Function DIO_Write1 Lib "AIOUSB" Alias "VBDIO_Write1" (ByVal DeviceIndex As Long, ByVal BitIndex As Long, ByVal Data As Boolean) As Long
Public Declare Function DIO_Write8 Lib "AIOUSB" Alias "VBDIO_Write8" (ByVal DeviceIndex As Long, ByVal ByteIndex As Long, ByVal Data As Byte) As Long
Public Declare Function DIO_WriteAll Lib "AIOUSB" Alias "VBDIO_WriteAll" (ByVal DeviceIndex As Long, ByRef Data As Any) As Long

Public Declare Function DIO_StreamOpen Lib "AIOUSB" Alias "VBDIO_StreamOpen" (ByVal DeviceIndex As Long, ByVal bIsRead As Long) As Long
Public Declare Function DIO_StreamClose Lib "AIOUSB" Alias "VBDIO_StreamClose" (ByVal DeviceIndex As Long) As Long
Public Declare Function DIO_StreamFrame Lib "AIOUSB" Alias "VBDIO_StreamFrame" (ByVal DeviceIndex As Long, ByVal FramePoints As Long, ByRef FrameData As Any, ByRef ByteTransferred As Long) As Long
Public Declare Function DIO_StreamSetClocks Lib "AIOUSB" Alias "VBDIO_StreamSetClocks" (ByVal DeviceIndex As Long, ByRef ReadClockHz As Double, ByRef WriteClockHz As Double) As Long

Public Declare Function DIO_SPI_Read Lib "AIOUSB" Alias "VBDIO_SPI_Read" (ByVal DeviceIndex As Long, ByVal Address, ByVal Reg As Byte, ByRef pValue As Byte) As Long
Public Declare Function DIO_SPI_Write Lib "AIOUSB" Alias "VBDIO_SPI_Write" (ByVal DeviceIndex As Long, ByVal Address, ByVal Reg As Byte, ByVal Value As Byte) As Long

Public Declare Function DIO_Automap_ClearTable Lib "AIOUSB" Alias "VBDIO_Automap_ClearTable" (ByVal DeviceIndex As Long) As Long
Public Declare Function DIO_Automap_SetTable Lib "AIOUSB" Alias "VBDIO_Automap_SetTable" (ByVal DeviceIndex As Long, ByRef pMapTable As Byte, ByRef pMapTableBytes As Long) As Long
Public Declare Function DIO_Automap_AddEntry Lib "AIOUSB" Alias "VBDIO_Automap_AddEntry" (ByVal DeviceIndex As Long, ByRef pMapEntry As Integer) As Long
Public Declare Function DIO_Automap_SetTickDivisor Lib "AIOUSB" Alias "VBDIO_Automap_SetTickDivisor" (ByVal DeviceIndex As Long, ByRef pDivisor As Byte) As Long

Public Declare Function DIO_PWM_Start Lib "AIOUSB" Alias "VBDIO_PWM_Start" (ByVal DeviceIndex As Long, ByRef pPWMTable As Byte, ByRef pPWMTableBytes As Long) As Long

Public Declare Function DIO_Latch_SetDivisor Lib "AIOUSB" Alias "VBDIO_Latch_SetDivisor" (ByVal DeviceIndex As Long, ByRef pDivisor As Byte) As Long
Public Declare Function DIO_Latch_Reset Lib "AIOUSB" Alias "VBDIO_Latch_Reset" (ByVal DeviceIndex As Long) As Long
Public Declare Function DIO_Latch_Read Lib "AIOUSB" Alias "VBDIO_Latch_Read" (ByVal DeviceIndex As Long, ByRef pLowLatches As Byte, ByRef pHighLatches As Byte, ByRef pNoLatches As Byte, ByRef pLatchesBytes As Long) As Long

Public Declare Function DIO_Deb_SetConfig Lib "AIOUSB" Alias "VBDIO_Deb_SetConfig" (ByVal DeviceIndex As Long, ByRef pDebTable As Byte, ByRef pDebTableBytes As Long) As Long
Public Declare Function DIO_Deb_ReadAll Lib "AIOUSB" Alias "VBDIO_Deb_ReadAll" (ByVal DeviceIndex As Long, ByRef pDebData As Byte) As Long

Public Declare Function DIO_CSA_DoSync Lib "AIOUSB" Alias "VBDIO_CSA_DoSync" (ByVal DeviceIndex As Long, ByRef BaseRateHz As Double, ByRef DurAms As Double, ByRef DurBms As Double, ByRef DurCms As Double) As Long
Public Declare Function DIO_CSA_DebounceSet Lib "AIOUSB" Alias "VBDIO_CSA_DebounceSet" (ByVal DeviceIndex As Long, ByVal DebounceCounts As Long) As Long
Public Declare Function DIO_CSA_DebounceReadAll Lib "AIOUSB" Alias "VBDIO_CSA_DebounceReadAll" (ByVal DeviceIndex As Long, ByRef pData As Any) As Long

Public Declare Function DAC_CSA_SetRangeLimits Lib "AIOUSB" Alias "DAC_CSA_SetRangeLimits" (ByVal DeviceIndex As Long, ByRef pData As Byte) As Long
Public Declare Function DAC_CSA_ClearRangeLimits Lib "AIOUSB" Alias "DAC_CSA_ClearRangeLimits" (ByVal DeviceIndex As Long) As Long

Public Declare Function DACDIO_WriteAll Lib "AIOUSB" Alias "DACDIO_WriteAll" (ByVal DeviceIndex As Long, ByRef pDACCounts As Integer, ByRef pDIOData As Byte) As Long



Public Declare Function DACDirect Lib "AIOUSB" Alias "VBDACDirect" (ByVal DeviceIndex As Long, ByVal Channel As Long, ByVal Counts As Integer) As Long
Public Declare Function DACMultiDirect Lib "AIOUSB" Alias "VBDACMultiDirect" (ByVal DeviceIndex As Long, ByRef pDACData As Any, ByVal DACDataCount As Long) As Long
Public Declare Function DACSetBoardRange Lib "AIOUSB" Alias "VBDACSetBoardRange" (ByVal DeviceIndex As Long, ByVal RangeCode As Long) As Long
Public Declare Function DACSetChannelCal Lib "AIOUSB" Alias "VBDACSetChannelCal" (ByVal DeviceIndex As Long, ByVal Channel As Long, ByVal CalFileName As String) As Long

Public Declare Function DACOutputProcess Lib "AIOUSB" Alias "VBDACOutputProcess" (ByVal DeviceIndex As Long, ByRef ClockHz As Double, ByVal NumSamples As Long, ByRef SampleData As Integer) As Long

Public Declare Function DACOutputOpen Lib "AIOUSB" Alias "VBDACOutputOpen" (ByVal DeviceIndex As Long, ByRef ClockHZ As Double) As Long
Public Declare Function DACOutputClose Lib "AIOUSB" Alias "VBDACOutputClose" (ByVal DeviceIndex As Long, ByVal bWait As Long) As Long
Public Declare Function DACOutputCloseNoEnd Lib "AIOUSB" Alias "VBDACOutputCloseNoEnd" (ByVal DeviceIndex As Long, ByVal bWait As Long) As Long
Public Declare Function DACOutputFrame Lib "AIOUSB" Alias "VBDACOutputFrame" (ByVal DeviceIndex As Long, ByVal FramePoints As Long, ByRef FrameData As Integer) As Long
Public Declare Function DACOutputFrameRaw Lib "AIOUSB" Alias "VBDACOutputFrameRaw" (ByVal DeviceIndex As Long, ByVal FramePoints As Long, ByRef FrameData As Integer) As Long
Public Declare Function DACOutputSetCount Lib "AIOUSB" Alias "VBDACOutputSetCount" (ByVal DeviceIndex As Long, ByVal NewCount As Long) As Long
Public Declare Function DACOutputSetInterlock Lib "AIOUSB" Alias "VBDACOutputSetInterlock" (ByVal DeviceIndex As Long, ByVal bInterlock As Long) As Long
Public Declare Function DACOutputSetClock Lib "AIOUSB" Alias "VBDACOutputSetClock" (ByVal DeviceIndex As Long, ByRef ClockHZ As Double) As Long
Public Declare Function DACOutputStart Lib "AIOUSB" Alias "VBDACOutputStart" (ByVal DeviceIndex As Long) As Long

'Note that all error codes returned are Windows error codes; they can be found in winerror.h in the Windows SDK, or on the Web.



Public Function ShiftRight(ByVal InitNum As Long, ByVal BitsRight As Long) As Long

    'Performs a bitwise right-shift. This is equivalent to C++'s >> operator.

    ShiftRight = InitNum \ (2 ^ BitsRight)

End Function

Public Function ShiftLeft(ByVal InitNum As Long, ByVal BitsLeft As Long) As Long

    'Performs a bitwise left-shift. This is equivalent to C++'s << operator.

    'C++:
    ' 1024 << 8 //Shift left 8 bits

    'VB:
    ' ShiftLeft(1024, 8) 'Shift left 8 bits

    ShiftLeft = CLng(InitNum * (2 ^ BitsLeft))

End Function
