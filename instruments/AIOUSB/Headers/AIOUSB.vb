'This module demonstrates the declarations required for using the AIOUSB driver with Visual Studio 2005.
'This won't work with previous versions of Visual Basic

Imports System
Imports System.Runtime.InteropServices 'For the structLayout thing

Module AIOUSB




    Public Const diOnly As UInteger = &HFFFFFFFD&
    Public Const diFirst As UInteger = &HFFFFFFFE&
    Public Const diNone As UInteger = &HFFFFFFFF&

    'This structure is for DACOutputFrame

    <StructLayout(LayoutKind.Sequential, pack:=1)> _
    Public Structure DACDataPoint
        Public X As UShort
        Public Y As UShort
        Public R As UShort
        Public G As UShort
        Public B As UShort
    End Structure

    'This structure is for DACMultiDirect

    <StructLayout(LayoutKind.Sequential, Pack:=1)> _
    Public Structure DACChange
        Public Channel As UShort
        Public Counts As UShort
    End Structure



	Public Declare Function GetDevices Lib "AIOUSB" Alias "VBGetDevices" () As UInteger
	Public Declare Function QueryDeviceInfo Lib "AIOUSB" Alias "VBQueryDeviceInfo" (ByVal DeviceIndex As UInteger, ByRef pPID As UInteger, ByRef pNameSize As UInteger, ByVal pName As String, ByRef pDIOBytes As UInteger, ByRef pCounters As UInteger) As UInteger
	Public Declare Function AIOUSB_CloseDevice Lib "AIOUSB" Alias "VBAIOUSB_CloseDevice" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function ClearDevices Lib "AIOUSB" Alias "VBClearDevices" () As UInteger
	Public Declare Function GetDeviceUniqueStr Lib "AIOUSB" Alias "VBGetDeviceUniqueStr" (ByVal DeviceIndex As UInteger, ByRef pUIDSize As UInteger, ByVal pUID As String) As UInteger
	Public Declare Function GetDeviceSerialNumber Lib "AIOUSB" Alias "VBGetDeviceSerialNumber" (ByVal DeviceIndex As UInteger, ByRef pSerialNumber As ULong) As UInteger
	Public Declare Function ResolveDeviceIndex Lib "AIOUSB" Alias "VBResolveDeviceIndex" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function GetDeviceByEEPROMByte Lib "AIOUSB" Alias "VBGetDeviceByEEPROMByte" (ByVal Data As Byte) As UInteger
	Public Declare Function GetDeviceByEEPROMData Lib "AIOUSB" Alias "VBGetDeviceByEEPROMData" (ByVal StartAddress As UInteger, ByVal DataSize As UInteger, ByRef pData As Byte) As UInteger
	Public Declare Function GetDeviceBySerialNumber Lib "AIOUSB" Alias "VBGetDeviceBySerialNumber" (ByRef pSerialNumber As ULong) As UInteger

	Public Declare Function AIOUSB_ClearFIFO Lib "AIOUSB" Alias "VBAIOUSB_ClearFIFO" (ByVal DeviceIndex As UInteger, ByVal TimeMethod As UInteger) As UInteger
	Public Declare Function AIOUSB_SetStreamingBlockSize Lib "AIOUSB" Alias "VBAIOUSB_SetStreamingBlockSize" (ByVal DeviceIndex As UInteger, ByVal BlockSize As UInteger) As UInteger
	Public Declare Function AIOUSB_ResetChip Lib "AIOUSB" Alias "VBAIOUSB_ResetChip" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function AIOUSB_ReloadDeviceLinks Lib "AIOUSB" Alias "VBAIOUSB_ReloadDeviceLinks" () As UInteger
	Public Declare Function AIOUSB_UploadD15LoFirmwaresByPID Lib "AIOUSB" Alias "VBAIOUSB_UploadD15LoFirmwaresByPID" (ByVal pFirmScript As String) As UInteger
	Public Declare Function AIOUSB_SetGlobalTickRate Lib "AIOUSB" Alias "VBAIOUSB_SetGlobalTickRate" (ByVal DeviceIndex As UInteger, ByRef pHz As Double) As UInteger

	Public Declare Function AIOUSB_QuerySimplePNPData Lib "AIOUSB" Alias "VBAIOUSB_QuerySimplePNPData" (ByVal DeviceIndex As UInteger, ByRef pPNPData As Byte, ByRef pPNPDataBytes As UInteger) As UInteger

	Public Declare Function CustomEEPROMRead Lib "AIOUSB" Alias "VBCustomEEPROMRead" (ByVal DeviceIndex As UInteger, ByVal StartAddress As UInteger, ByRef DataSize As UInteger, ByRef pData As Byte) As UInteger
	Public Declare Function CustomEEPROMWrite Lib "AIOUSB" Alias "VBCustomEEPROMWrite" (ByVal DeviceIndex As UInteger, ByVal StartAddress As UInteger, ByVal DataSize As UInteger, ByRef pData As Byte) As UInteger
	Public Declare Function AIOUSB_FlashRead Lib "AIOUSB" Alias "VBAIOUSB_FlashRead" (ByVal DeviceIndex As UInteger, ByVal StartAddress As UInteger, ByRef DataSize As UInteger, ByRef Data As Byte) As UInteger
	Public Declare Function AIOUSB_FlashWrite Lib "AIOUSB" Alias "VBAIOUSB_FlashWrite" (ByVal DeviceIndex As UInteger, ByVal StartAddress As UInteger, ByVal DataSize As UInteger, ByRef Data As Byte) As UInteger
	Public Declare Function AIOUSB_FlashEraseSector Lib "AIOUSB" Alias "VBAIOUSB_FlashEraseSector" (ByVal DeviceIndex As UInteger, ByVal Sector As UInteger) As UInteger

	Public Declare Function GenericVendorRead Lib "AIOUSB" Alias "VBGenericVendorRead" (ByVal DeviceIndex As UInteger, ByVal Request As Byte, ByVal Value As UShort, ByVal Index As UShort, ByRef pDataSize As UInteger, ByRef pData As Byte) As UInteger
	Public Declare Function GenericVendorWrite Lib "AIOUSB" Alias "VBGenericVendorWrite" (ByVal DeviceIndex As UInteger, ByVal Request As Byte, ByVal Value As UShort, ByVal Index As UShort, ByVal DataSize As UInteger, ByRef pData As Byte) As UInteger
	Public Declare Function AWU_GenericBulkIn Lib "AIOUSB" Alias "VBAWU_GenericBulkIn" (ByVal DeviceIndex As UInteger, ByVal PipeID As UInteger, ByRef pData As Byte, ByVal DataSize As UInteger, ByVal BytesRead As UInteger) As UInteger
	Public Declare Function AWU_GenericBulkOut Lib "AIOUSB" Alias "VBAWU_GenericBulkOut" (ByVal DeviceIndex As UInteger, ByVal PipeID As UInteger, ByRef pData As Byte, ByVal DataSize As UInteger, ByVal BytesWritten As UInteger) As UInteger



	Public Declare Function ADC_GetImmediate Lib "AIOUSB" Alias "VBADC_GetImmediate" (ByVal DeviceIndex As UInteger, ByVal Channel As UInteger, ByRef pBuf As UShort) As UInteger
	Public Declare Function ADC_GetScan Lib "AIOUSB" Alias "VBADC_GetScan" (ByVal DeviceIndex As UInteger, ByRef pBuf As UShort) As UInteger
	Public Declare Function ADC_GetScanV Lib "AIOUSB" Alias "VBADC_GetScanV" (ByVal DeviceIndex As UInteger, ByRef pBuf As Double) As UInteger
	Public Declare Function ADC_GetChannelV Lib "AIOUSB" Alias "VBADC_GetChannelV" (ByVal DeviceIndex As UInteger, ByVal ChannelIndex As UInteger, ByRef pBuf As Double) As UInteger
	Public Declare Function ADC_GetCalRefV Lib "AIOUSB" Alias "VBADC_GetCalRefV" (ByVal DeviceIndex As UInteger, ByVal CalRefIndex As UInteger, ByRef pRef As Double) As UInteger

	Public Declare Function ADC_GetTrigScan Lib "AIOUSB" Alias "VBADC_GetTrigScan" (ByVal DeviceIndex As UInteger, ByRef pBuf As UShort, ByVal TimeoutMS As Integer) As UInteger
	Public Declare Function ADC_GetTrigScanV Lib "AIOUSB" Alias "VBADC_GetTrigScanV" (ByVal DeviceIndex As UInteger, ByRef pBuf As Double, ByVal TimeoutMS As Integer) As UInteger

	Public Declare Function ADC_GetConfig Lib "AIOUSB" Alias "VBADC_GetConfig" (ByVal DeviceIndex As UInteger, ByRef pConfigBuf As Byte, ByRef ConfigBufSize As UInteger) As UInteger
	Public Declare Function ADC_SetConfig Lib "AIOUSB" Alias "VBADC_SetConfig" (ByVal DeviceIndex As UInteger, ByRef pConfigBuf As Byte, ByRef ConfigBufSize As UInteger) As UInteger
	Public Declare Function ADC_ADMode Lib "AIOUSB" Alias "VBADC_ADMode" (ByVal DeviceIndex As UInteger, ByVal TriggerMode As Byte, ByVal CalMode As Byte) As UInteger
	Public Declare Function ADC_Range1 Lib "AIOUSB" Alias "VBADC_Range1" (ByVal DeviceIndex As UInteger, ByVal ADChannel As UInteger, ByVal GainCode As Byte, ByVal bDifferential As UInteger) As UInteger
	Public Declare Function ADC_RangeAll Lib "AIOUSB" Alias "VBADC_RangeAll" (ByVal DeviceIndex As UInteger, ByRef pGainCodes As Byte, ByVal bDifferential As UInteger) As UInteger
	Public Declare Function ADC_SetScanLimits Lib "AIOUSB" Alias "VBADC_SetScanLimits" (ByVal DeviceIndex As UInteger, ByVal StartChannel As UInteger, ByVal EndChannel As UInteger) As UInteger
	Public Declare Function ADC_SetOversample Lib "AIOUSB" Alias "VBADC_SetOversample" (ByVal DeviceIndex As UInteger, ByVal Oversample As Byte) As UInteger
	Public Declare Function ADC_QueryCal Lib "AIOUSB" Alias "VBADC_QueryCal" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function ADC_SetCal Lib "AIOUSB" Alias "VBADC_SetCal" (ByVal DeviceIndex As UInteger, ByVal CalFileName As String) As UInteger
	Public Declare Function ADC_SetCalAndSave Lib "AIOUSB" Alias "VBADC_SetCalAndSave" (ByVal DeviceIndex As UInteger, ByVal CalFileName As String, ByVal SaveCalFileName As String) As UInteger
	Public Declare Function ADC_Initialize Lib "AIOUSB" Alias "VBADC_Initialize" (ByVal DeviceIndex As UInteger, ByRef pConfigBuf As Byte, ByRef ConfigBufSize As UInteger, ByVal CalFileName As String) As UInteger

	Public Declare Function ADC_BulkAcquire Lib "AIOUSB" Alias "VBADC_BulkAcquire" (ByVal DeviceIndex As UInteger, ByVal BufSize As UInteger, ByRef pBuf As Byte) As UInteger
	Public Declare Function ADC_BulkPoll Lib "AIOUSB" Alias "VBADC_BulkPoll" (ByVal DeviceIndex As UInteger, ByRef BytesLeft As UInteger) As UInteger
	Public Declare Function ADC_BulkAbort Lib "AIOUSB" Alias "VBADC_BulkAbort" (ByVal DeviceIndex As UInteger) As UInteger

	Public Declare Function ADC_BulkContinuousRingStart Lib "AIOUSB" Alias "VBADC_BulkContinuousRingStart" (ByVal DeviceIndex As UInteger, ByVal RingBufferSize As UInteger, ByVal PacketsPerBlock As UInteger) As UInteger
	Public Declare Function ADC_BulkContinuousEnd Lib "AIOUSB" Alias "VBADC_BulkContinuousEnd" (ByVal DeviceIndex As UInteger, ByRef pIOStatus As UInteger) As UInteger

	Public Declare Function ADC_FullStartRing Lib "AIOUSB" Alias "VBADC_FullStartRing" (ByVal DeviceIndex As UInteger, ByRef pConfigBuf As Byte, ByRef ConfigBufSize As UInteger, ByVal CalFileName As String, ByRef pCounterHz As Double, ByVal RingBufferSize As UInteger, ByVal PacketsPerBlock As UInteger) As UInteger
	Public Declare Function ADC_ReadData Lib "AIOUSB" Alias "VBADC_ReadData" (ByVal DeviceIndex As UInteger, ByRef pConfigBuf As Byte, ByRef ScansToRead As UInteger, ByRef pData As Double, ByVal Timeout As Double) As UInteger

	Public Declare Function ADC_InitFastITScanV Lib "AIOUSB" Alias "VBADC_InitFastITScanV" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function ADC_ResetFastITScanV Lib "AIOUSB" Alias "VBADC_ResetFastITScanV" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function ADC_SetFastITScanVChannels Lib "AIOUSB" Alias "VBADC_SetFastITScanVChannels" (ByVal DeviceIndex As UInteger, NewChannels As UInteger) As UInteger
	Public Declare Function ADC_GetFastITScanV Lib "AIOUSB" Alias "VBADC_GetFastITScanV" (ByVal DeviceIndex As UInteger, ByRef pBuf As Double) As UInteger
	Public Declare Function ADC_GetITScanV Lib "AIOUSB" Alias "VBADC_GetITScanV" (ByVal DeviceIndex As UInteger, ByRef pBuf As Double) As UInteger

	Public Declare Function ADC_InitFastScanV Lib "AIOUSB" Alias "VBADC_InitFastScanV" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function ADC_ResetFastScanV Lib "AIOUSB" Alias "VBADC_ResetFastScanV" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function ADC_GetFastScanV Lib "AIOUSB" Alias "VBADC_GetFastScanV" (ByVal DeviceIndex As UInteger, ByRef pBuf As Double) As UInteger



	Public Declare Function CTR_8254Load Lib "AIOUSB" Alias "VBCTR_8254Load" (ByVal DeviceIndex As UInteger, _
		ByVal BlockIndex As UInteger, ByVal CounterIndex As UInteger, ByVal LoadValue As UShort) As UInteger
	Public Declare Function CTR_8254Mode Lib "AIOUSB" Alias "VBCTR_8254Mode" (ByVal DeviceIndex As UInteger, _
		ByVal BlockIndex As UInteger, ByVal CounterIndex As UInteger, ByVal Mode As UInteger) As UInteger
	Public Declare Function CTR_8254ModeLoad Lib "AIOUSB" Alias "VBCTR_8254ModeLoad" (ByVal DeviceIndex As UInteger, _
		ByVal BlockIndex As UInteger, ByVal CounterIndex As UInteger, ByVal Mode As UInteger, ByVal LoadValue As UShort) As UInteger
	Public Declare Function CTR_8254Read Lib "AIOUSB" Alias "VBCTR_8254Read" (ByVal DeviceIndex As UInteger, _
		ByVal BlockIndex As UInteger, ByVal CounterIndex As UInteger, ByRef pReadValue As UShort) As UInteger
	Public Declare Function CTR_8254ReadStatus Lib "AIOUSB" Alias "VBCTR_8254ReadStatus" (ByVal DeviceIndex As UInteger, _
		ByVal BlockIndex As UInteger, ByVal CounterIndex As UInteger, ByRef pReadValue As UShort, ByRef pStatus As Byte) As UInteger
	Public Declare Function CTR_8254ReadModeLoad Lib "AIOUSB" Alias "VBCTR_8254ReadModeLoad" (ByVal DeviceIndex As UInteger, _
		ByVal BlockIndex As UInteger, ByVal CounterIndex As UInteger, ByVal Mode As UInteger, ByVal LoadValue As UShort, ByRef pReadValue As UShort) As UInteger

	Public Declare Function CTR_StartOutputFreq Lib "AIOUSB" Alias "VBCTR_StartOutputFreq" (ByVal DeviceIndex As UInteger, _
		ByVal CounterIndex As UInteger, ByRef pHz As Double) As UInteger

	Public Declare Function CTR_8254ReadAll Lib "AIOUSB" Alias "VBCTR_8254ReadAll" (ByVal DeviceIndex As UInteger, _
		ByRef pData As UShort) As UInteger

	Public Declare Function CTR_8254SelectGate Lib "AIOUSB" Alias "VBCTR_8254SelectGate" (ByVal DeviceIndex As UInteger, _
		ByVal GateIndex As UInteger) As UInteger
	Public Declare Function CTR_8254ReadLatched Lib "AIOUSB" Alias "VBCTR_8254ReadLatched" (ByVal DeviceIndex As UInteger, _
		ByRef pData As UShort) As UInteger
	Public Declare Function CTR_SetWaitGates Lib "AIOUSB" Alias "VBCTR_SetWaitGates" (ByVal DeviceIndex As UInteger, _
		ByVal A As Byte, ByVal B As Byte) As UInteger
	Public Declare Function CTR_EndWaitGates Lib "AIOUSB" Alias "VBCTR_EndWaitGates" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function CTR_WaitForGate Lib "AIOUSB" Alias "VBCTR_WaitForGate" (ByVal DeviceIndex As UInteger, _
		ByVal GateIndex As Byte, ByRef pContent As UShort) As UInteger

	Public Declare Function CTR_StartMeasuringPulseWidth Lib "AIOUSB" Alias "VBCTR_StartMeasuringPulseWidth" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function CTR_StopMeasuringPulseWidth Lib "AIOUSB" Alias "VBCTR_StopMeasuringPulseWidth" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function CTR_GetPulseWidthMeasurement Lib "AIOUSB" Alias "VBCTR_GetPulseWidthMeasurement" (ByVal DeviceIndex As UInteger, _
		ByVal BlockIndex As UInteger, ByVal CounterIndex As UInteger, ByRef pReadValue As UShort) As UInteger



	Public Declare Function DIO_Configure Lib "AIOUSB" Alias "VBDIO_Configure" (ByVal DeviceIndex As UInteger, _
		ByVal bTristate As Byte, ByRef pOutMask As Byte, ByRef pData As Byte) As UInteger
	Public Declare Function DIO_ConfigureEx Lib "AIOUSB" Alias "VBDIO_ConfigureEx" (ByVal DeviceIndex As UInteger, _
		ByRef pOutMask As Byte, ByRef pData As Byte, ByRef pTristateMask As Byte) As UInteger
	Public Declare Function DIO_ConfigureMasked Lib "AIOUSB" Alias "VBDIO_ConfigureMasked" (ByVal DeviceIndex As UInteger, ByRef pOuts As Byte, ByRef pOutsMask As Byte, ByRef pData As Byte, ByRef pDataMask As Byte, ByRef pTristates As Byte, ByRef pTristatesMask As Byte) As UInteger
	Public Declare Function DIO_ConfigurationQuery Lib "AIOUSB" Alias "VBDIO_ConfigurationQuery" (ByVal DeviceIndex As UInteger, _
		ByRef pOutMask As Byte, ByRef pTristateMask As Byte) As UInteger

	Public Declare Function DIO_Read1 Lib "AIOUSB" Alias "VBDIO_Read1" (ByVal DeviceIndex As UInteger, ByVal BitIndex As UInteger, ByRef bData As Byte) As UInteger
	Public Declare Function DIO_Read8 Lib "AIOUSB" Alias "VBDIO_Read8" (ByVal DeviceIndex As UInteger, _
		ByVal ByteIndex As UInteger, ByRef Data As Byte) As UInteger
	Public Declare Function DIO_ReadAll Lib "AIOUSB" Alias "VBDIO_ReadAll" (ByVal DeviceIndex As UInteger, _
		ByRef Data As Byte) As UInteger

	Public Declare Function DIO_Write1 Lib "AIOUSB" Alias "VBDIO_Write1" (ByVal DeviceIndex As UInteger, _
		ByVal BitIndex As UInteger, ByVal bData As Byte) As UInteger
	Public Declare Function DIO_Write8 Lib "AIOUSB" Alias "VBDIO_Write8" (ByVal DeviceIndex As UInteger, _
		ByVal ByteIndex As UInteger, ByVal Data As Byte) As UInteger
	Public Declare Function DIO_WriteAll Lib "AIOUSB" Alias "VBDIO_WriteAll" (ByVal DeviceIndex As UInteger, _
		ByRef Data As Byte) As UInteger



	Public Declare Function DIO_StreamOpen Lib "AIOUSB" Alias "VBDIO_StreamOpen" (ByVal DeviceIndex As UInteger, _
		ByVal bIsRead As UInteger) As UInteger
	Public Declare Function DIO_StreamClose Lib "AIOUSB" Alias "VBDIO_StreamClose" (ByVal DeviceIndex As UInteger) As UInteger
	Public Declare Function DIO_StreamFrame Lib "AIOUSB" Alias "VBDIO_StreamFrame" (ByVal DeviceIndex As UInteger, _
		ByVal FramePoints As UInteger, ByRef pFrameData As UShort, ByRef BytesTransferred As UInteger) As UInteger
	Public Declare Function DIO_StreamSetClocks Lib "AIOUSB" Alias "VBDIO_StreamSetClocks" (ByVal DeviceIndex As UInteger, _
		ByRef ReadClockHz As Double, ByRef WriteClockHz As Double) As UInteger

	Public Declare Function DIO_SPI_Read Lib "AIOUSB" Alias "VBDIO_SPI_Read" (ByVal DeviceIndex As UInteger, _
		ByVal Address As Byte, ByVal Reg As Byte, ByRef pValue As Byte) As UInteger
	Public Declare Function DIO_SPI_Write Lib "AIOUSB" Alias "VBDIO_SPI_Write" (ByVal DeviceIndex As UInteger, _
		ByVal Address As Byte, ByVal Reg As Byte, ByVal Value As Byte) As UInteger

	Public Declare Function DIO_CSA_DoSync Lib "AIOUSB" Alias "VBDIO_CSA_DoSync" (ByVal DeviceIndex As UInteger, _
		ByRef BaseRateHz As Double, ByRef DurAms As Double, ByRef DurBms As Double, ByRef DurCms As Double) As UInteger
	Public Declare Function DIO_CSA_DebounceSet Lib "AIOUSB" Alias "VBDIO_CSA_DebounceSet" (ByVal DeviceIndex As UInteger, _
		ByVal DebounceCounts As UInteger) As UInteger
	Public Declare Function DIO_CSA_DebounceReadAll Lib "AIOUSB" Alias "VBDIO_CSA_DebounceReadAll" (ByVal DeviceIndex As UInteger, _
		ByRef pData As Byte) As UInteger

	Public Declare Function DAC_CSA_SetRangeLimits Lib "AIOUSB" Alias "DAC_CSA_SetRangeLimits" (ByVal DeviceIndex As UInteger, ByRef pData As Byte) As UInteger
	Public Declare Function DAC_CSA_ClearRangeLimits Lib "AIOUSB" Alias "DAC_CSA_ClearRangeLimits" (ByVal DeviceIndex As UInteger) As UInteger

	Public Declare Function DACDIO_WriteAll Lib "AIOUSB" Alias "DACDIO_WriteAll" (ByVal DeviceIndex As UInteger, ByRef pDACCounts As UShort, ByRef pDIOData As Byte) As UInteger



	Public Declare Function DACDirect Lib "AIOUSB" Alias "VBDACDirect" (ByVal DeviceIndex As UInteger, _
		ByVal Channel As UInteger, ByVal Counts As UShort) As UInteger
	Public Declare Function DACMultiDirect Lib "AIOUSB" Alias "VBDACMultiDirect" (ByVal DeviceIndex As UInteger, _
		ByRef pDACData As DACChange, ByVal DACDataCount As UInteger) As UInteger
	Public Declare Function DACSetBoardRange Lib "AIOUSB" Alias "VBDACSetBoardRange" (ByVal DeviceIndex As UInteger, ByVal RangeCode As UInteger) As UInteger
	Public Declare Function DACSetChannelCal Lib "AIOUSB" Alias "VBDACSetChannelCal" (ByVal DeviceIndex As UInteger, ByVal Channel As UInteger, ByVal CalFileName As String) As UInteger

	Public Declare Function DACOutputOpen Lib "AIOUSB" Alias "VBDACOutputOpen" (ByVal DeviceIndex As UInteger, _
		ByRef ClockHz As Double) As UInteger
	Public Declare Function DACOutputClose Lib "AIOUSB" Alias "VBDACOutputClose" (ByVal DeviceIndex As UInteger, _
		ByVal bWait As UInteger) As UInteger
	Public Declare Function DACOutputCloseNoEnd Lib "AIOUSB" Alias "VBDACOutputCloseNoEnd" (ByVal DeviceIndex As UInteger, ByVal bWait As UInteger) As UInteger
	Public Declare Function DACOutputFrame Lib "AIOUSB" Alias "VBDACOutputFrame" (ByVal DeviceIndex As UInteger, _
		ByVal FramePoints As UInteger, ByRef FrameData As DACDataPoint) As UInteger
	Public Declare Function DACOutputFrameRaw Lib "AIOUSB" Alias "VBDACOutputFrameRaw" (ByVal DeviceIndex As UInteger, ByVal FramePoints As UInteger, ByRef FrameData As UShort) As UInteger
	Public Declare Function DACOutputSetCount Lib "AIOUSB" Alias "VBDACOutputSetCount" (ByVal DeviceIndex As UInteger, _
		ByVal NewCount As UInteger) As UInteger
	Public Declare Function DACOutputSetInterlock Lib "AIOUSB" Alias "VBDACOutputSetInterlock" (ByVal DeviceIndex As UInteger, ByVal bInterlock As UInteger) As UInteger
	Public Declare Function DACOutputSetClock Lib "AIOUSB" Alias "VBDACOutputSetClock" (ByVal DeviceIndex As UInteger, ByRef ClockHZ As Double) As UInteger
	Public Declare Function DACOutputStart Lib "AIOUSB" Alias "VBDACOutputStart" (ByVal DeviceIndex As UInteger) As UInteger

	Public Declare Function DACOutputProcess Lib "AIOUSB" Alias "VBDACOutputProcess" (ByVal DeviceIndex As UInteger, ByRef ClockHz As Double, ByVal NumSamples As UInteger, ByRef SampleData As UShort) As UInteger

	'Note that all error codes returned are Windows error codes; they can be found in winerror.h in the Windows SDK, or on the Web.

End Module
