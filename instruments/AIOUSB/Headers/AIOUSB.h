// AIOUSB.h : Header file for AIOUSB.dll
//
//For Borland C++ Builder, use CBAIOUSB.lib
//For Microsoft Visual C++, use VCAIOUSB.lib

#ifdef __cplusplus
extern "C" {
#endif



#define diNone 0xFFFFFFFF
#define diFirst 0xFFFFFFFE
#define diOnly 0xFFFFFFFD

#define TIME_METHOD_NOW 0
#define TIME_METHOD_WAIT_INPUT_ENABLE 86
#define TIME_METHOD_NOW_AND_ABORT 5
#define TIME_METHOD_WHEN_INPUT_ENABLE 1



__declspec(dllimport) unsigned long GetDevices(void);
__declspec(dllimport) unsigned long QueryDeviceInfo(unsigned long DeviceIndex, unsigned long *pPID, unsigned long *pNameSize, char *pName, unsigned long *pDIOBytes, unsigned long *pCounters);
__declspec(dllimport) unsigned long AIOUSB_CloseDevice(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long ClearDevices(void);
__declspec(dllimport) unsigned long GetDeviceUniqueStr(unsigned long DeviceIndex, unsigned long *pUIDSize, char *pUID);
__declspec(dllimport) unsigned long GetDeviceSerialNumber(unsigned long DeviceIndex, unsigned __int64 *pSerialNumber);
__declspec(dllimport) unsigned long ResolveDeviceIndex(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long GetDeviceByEEPROMByte(unsigned char Data);
__declspec(dllimport) unsigned long GetDeviceByEEPROMData(unsigned long StartAddress, unsigned long DataSize, unsigned char *pData);
__declspec(dllimport) unsigned long GetDeviceBySerialNumber(unsigned __int64 *pSerialNumber);

__declspec(dllimport) unsigned long AIOUSB_ClearFIFO(unsigned long DeviceIndex, unsigned long TimeMethod);
__declspec(dllimport) unsigned long AIOUSB_GetStreamStatus(unsigned long DeviceIndex, unsigned long *Status);
__declspec(dllimport) unsigned long AIOUSB_SetStreamingBlockSize(unsigned long DeviceIndex, unsigned long BlockSize);
__declspec(dllimport) unsigned long AIOUSB_ResetChip(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long AIOUSB_ReloadDeviceLinks();
__declspec(dllimport) unsigned long AIOUSB_UploadD15LoFirmwaresByPID(char *pFirmScript);
__declspec(dllimport) unsigned long AIOUSB_SetGlobalTickRate(unsigned long DeviceIndex, double *pHz);

__declspec(dllimport) unsigned long AIOUSB_QuerySimplePNPData(unsigned long DeviceIndex, void *pPNPData, unsigned long *pPNPDataBytes);

__declspec(dllimport) unsigned long CustomEEPROMRead(unsigned long DeviceIndex, unsigned long StartAddress, unsigned long *DataSize, void *pData);
__declspec(dllimport) unsigned long CustomEEPROMWrite(unsigned long DeviceIndex, unsigned long StartAddress, unsigned long DataSize, void *pData);
__declspec(dllimport) unsigned long AIOUSB_FlashRead(unsigned long DeviceIndex, unsigned long StartAddress, unsigned long *DataSize, void *Data);
__declspec(dllimport) unsigned long AIOUSB_FlashWrite(unsigned long DeviceIndex, unsigned long StartAddress, unsigned long DataSize, void *Data);
__declspec(dllimport) unsigned long AIOUSB_FlashEraseSector(unsigned long DeviceIndex, signed long Sector);

__declspec(dllimport) unsigned long GenericVendorRead(unsigned long DeviceIndex, unsigned char Request, unsigned short Value, unsigned short Index, unsigned long *pDataSize, void *pData);
__declspec(dllimport) unsigned long GenericVendorWrite(unsigned long DeviceIndex, unsigned char Request, unsigned short Value, unsigned short Index, unsigned long DataSize, void *pData);
__declspec(dllimport) unsigned long AWU_GenericBulkIn(unsigned long DeviceIndex, unsigned long PipeID, void *pData, unsigned long DataSize, unsigned long *pBytesRead);
__declspec(dllimport) unsigned long AWU_GenericBulkOut(unsigned long DeviceIndex, unsigned long PipeID, void *pData, unsigned long DataSize, unsigned long *pBytesWritten);



__declspec(dllimport) unsigned long ADC_GetScan(unsigned long DeviceIndex, unsigned short *pBuf);
__declspec(dllimport) unsigned long ADC_GetScanV(unsigned long DeviceIndex, double *pBuf);
__declspec(dllimport) unsigned long ADC_GetChannelV(unsigned long DeviceIndex, unsigned long ChannelIndex, double *pBuf);
__declspec(dllimport) unsigned long ADC_GetCalRefV(unsigned long DeviceIndex, unsigned long CalRefIndex, double *pRef);

__declspec(dllimport) unsigned long ADC_GetTrigScan(unsigned long DeviceIndex, unsigned short *pBuf, long TimeoutMS);
__declspec(dllimport) unsigned long ADC_GetTrigScanV(unsigned long DeviceIndex, double *pBuf, long TimeoutMS);

__declspec(dllimport) unsigned long ADC_GetConfig(unsigned long DeviceIndex, void *pConfigBuf, unsigned long *ConfigBufSize);
__declspec(dllimport) unsigned long ADC_SetConfig(unsigned long DeviceIndex, void *pConfigBuf, unsigned long *ConfigBufSize);
__declspec(dllimport) unsigned long ADC_ADMode(unsigned long DeviceIndex, unsigned char TriggerMode, unsigned char CalMode);
__declspec(dllimport) unsigned long ADC_Range1(unsigned long DeviceIndex, unsigned long ADChannel, unsigned char GainCode, unsigned long bDifferential);
__declspec(dllimport) unsigned long ADC_RangeAll(unsigned long DeviceIndex, unsigned char *pGainCodes, unsigned long bDifferential);
__declspec(dllimport) unsigned long ADC_SetScanLimits(unsigned long DeviceIndex, unsigned long StartChannel, unsigned long EndChannel);
__declspec(dllimport) unsigned long ADC_SetOversample(unsigned long DeviceIndex, unsigned char Oversample);
__declspec(dllimport) unsigned long ADC_QueryCal(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long ADC_SetCal(unsigned long DeviceIndex, char *CalFileName);
__declspec(dllimport) unsigned long ADC_SetCalAndSave(unsigned long DeviceIndex, char *CalFileName, char *SaveCalFileName);
__declspec(dllimport) unsigned long ADC_Initialize(unsigned long DeviceIndex, void *pConfigBuf, unsigned long *ConfigBufSize, char *CalFileName);
__declspec(dllimport) unsigned long ADC_GetImmediate(unsigned long DeviceIndex, unsigned long Channel, unsigned short *pBuf);

__declspec(dllimport) unsigned long ADC_BulkAcquire(unsigned long DeviceIndex, unsigned long BufSize, void *pBuf);
__declspec(dllimport) unsigned long ADC_BulkPoll(unsigned long DeviceIndex, unsigned long *BytesLeft);
__declspec(dllimport) unsigned long ADC_BulkAbort(unsigned long DeviceIndex);

__declspec(dllimport) unsigned long ADC_BulkMode(unsigned long DeviceIndex, unsigned long BulkMode);
__declspec(dllimport) unsigned long ADC_BulkContinuousCallbackStart(unsigned long DeviceIndex, unsigned long BufSize, unsigned long BaseBufCount, unsigned long Context, void *pCallback);
__declspec(dllimport) unsigned long ADC_BulkContinuousCallbackStartClocked(unsigned long DeviceIndex, unsigned long BufSize, unsigned long BaseBufCount, unsigned long Context, void *pCallback, double *Hz);
__declspec(dllimport) unsigned long ADC_BulkContinuousRingStart(unsigned long DeviceIndex, unsigned long RingBufferSize, unsigned long PacketsPerBlock);
__declspec(dllimport) unsigned long ADC_BulkContinuousEnd(unsigned long DeviceIndex, unsigned long *pIOStatus);

__declspec(dllimport) unsigned long ADC_FullStartRing(unsigned long DeviceIndex, void *pConfigBuf, unsigned long *ConfigBufSize, char *CalFileName, double *pCounterHz, unsigned long RingBufferSize, unsigned long PacketsPerBlock);
__declspec(dllimport) unsigned long ADC_ReadData(unsigned long DeviceIndex, void *pConfigBuf, unsigned long *ScansToRead, double *pData, double Timeout);

__declspec(dllimport) unsigned long ADC_InitFastITScanV(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long ADC_ResetFastITScanV(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long ADC_SetFastITScanVChannels(unsigned long DeviceIndex, unsigned long NewChannels);
__declspec(dllimport) unsigned long ADC_GetFastITScanV(unsigned long DeviceIndex, double *pBuf);
__declspec(dllimport) unsigned long ADC_GetITScanV(unsigned long DeviceIndex, double *pBuf);

__declspec(dllimport) unsigned long ADC_InitFastScanV(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long ADC_ResetFastScanV(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long ADC_GetFastScanV(unsigned long DeviceIndex, double *pBuf);



__declspec(dllimport) unsigned long CTR_8254Load(unsigned long DeviceIndex, unsigned long BlockIndex, unsigned long CounterIndex, unsigned short LoadValue);
__declspec(dllimport) unsigned long CTR_8254Mode(unsigned long DeviceIndex, unsigned long BlockIndex, unsigned long CounterIndex, unsigned long Mode);
__declspec(dllimport) unsigned long CTR_8254ModeLoad(unsigned long DeviceIndex, unsigned long BlockIndex, unsigned long CounterIndex, unsigned long Mode, unsigned short LoadValue);
__declspec(dllimport) unsigned long CTR_8254Read(unsigned long DeviceIndex, unsigned long BlockIndex, unsigned long CounterIndex, unsigned short *pReadValue);
__declspec(dllimport) unsigned long CTR_8254ReadStatus(unsigned long DeviceIndex, unsigned long BlockIndex, unsigned long CounterIndex, unsigned short *pReadValue, unsigned char *pStatus);
__declspec(dllimport) unsigned long CTR_8254ReadModeLoad(unsigned long DeviceIndex, unsigned long BlockIndex, unsigned long CounterIndex, unsigned long Mode, unsigned short LoadValue, unsigned short *pReadValue);

__declspec(dllimport) unsigned long CTR_StartOutputFreq(unsigned long DeviceIndex, unsigned long CounterIndex, double *pHz);

__declspec(dllimport) unsigned long CTR_8254ReadAll(unsigned long DeviceIndex, unsigned short *pData);

__declspec(dllimport) unsigned long CTR_8254SelectGate(unsigned long DeviceIndex, unsigned long GateIndex);
__declspec(dllimport) unsigned long CTR_8254ReadLatched(unsigned long DeviceIndex, unsigned short *pData);
__declspec(dllimport) unsigned long CTR_SetWaitGates(unsigned long DeviceIndex, unsigned char A, unsigned char B);
__declspec(dllimport) unsigned long CTR_EndWaitGates(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long CTR_WaitForGate(unsigned long DeviceIndex, unsigned char GateIndex, unsigned short *pContent);

__declspec(dllimport) unsigned long CTR_StartMeasuringPulseWidth(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long CTR_StopMeasuringPulseWidth(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long CTR_GetPulseWidthMeasurement(unsigned long DeviceIndex, unsigned long BlockIndex, unsigned long CounterIndex, unsigned short *pReadValue);



__declspec(dllimport) unsigned long DIO_Configure(unsigned long DeviceIndex, unsigned char bTristate, void *pOutMask, void *pData);
__declspec(dllimport) unsigned long DIO_ConfigureEx(unsigned long DeviceIndex, void *pOutMask, void *pData, void *pTristateMask);
__declspec(dllimport) unsigned long DIO_ConfigureMasked(unsigned long DeviceIndex, void *pOuts, void *pOutsMask, void *pData, void *pDataMask, void *pTristates, void *pTristatesMask);
__declspec(dllimport) unsigned long DIO_ConfigurationQuery(unsigned long DeviceIndex, void *pOutMask, void *pTristateMask);

__declspec(dllimport) unsigned long DIO_Read1(unsigned long DeviceIndex, unsigned long BitIndex, unsigned char *Buffer);
__declspec(dllimport) unsigned long DIO_Read8(unsigned long DeviceIndex, unsigned long ByteIndex, unsigned char *pBuffer);
__declspec(dllimport) unsigned long DIO_ReadAll(unsigned long DeviceIndex, void *Buffer);

__declspec(dllimport) unsigned long DIO_Write1(unsigned long DeviceIndex, unsigned long BitIndex, unsigned char bData);
__declspec(dllimport) unsigned long DIO_Write8(unsigned long DeviceIndex, unsigned long ByteIndex, unsigned char Data);
__declspec(dllimport) unsigned long DIO_WriteAll(unsigned long DeviceIndex, void *pData);



__declspec(dllimport) unsigned long DIO_StreamOpen(unsigned long DeviceIndex, unsigned long bIsRead);
__declspec(dllimport) unsigned long DIO_StreamClose(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long DIO_StreamFrame(unsigned long DeviceIndex, unsigned long FramePoints, unsigned short *pFrameData, unsigned long *BytesTransferred);
__declspec(dllimport) unsigned long DIO_StreamSetClocks(unsigned long DeviceIndex, double *ReadClockHz, double *WriteClockHz);

__declspec(dllimport) unsigned long DIO_SPI_Read(unsigned long DeviceIndex, unsigned char Address, unsigned char Reg, unsigned char * pValue);
__declspec(dllimport) unsigned long DIO_SPI_Write(unsigned long DeviceIndex, unsigned char Address, unsigned char Reg, unsigned char Value);

__declspec(dllimport) unsigned long DIO_Automap_ClearTable(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long DIO_Automap_SetTable(unsigned long DeviceIndex, void *pMapTable, unsigned long *pMapTableBytes);
__declspec(dllimport) unsigned long DIO_Automap_AddEntry(unsigned long DeviceIndex, unsigned short *pMapEntry);
__declspec(dllimport) unsigned long DIO_Automap_SetTickDivisor(unsigned long DeviceIndex, unsigned char *pDivisor);

__declspec(dllimport) unsigned long DIO_PWM_Start(unsigned long DeviceIndex, void *pPWMTable, unsigned long *pPWMTableBytes);

__declspec(dllimport) unsigned long DIO_Latch_SetDivisor(unsigned long DeviceIndex, unsigned char *pDivisor);
__declspec(dllimport) unsigned long DIO_Latch_Reset(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long DIO_Latch_Read(unsigned long DeviceIndex, unsigned char *pLowLatches, unsigned char *pHighLatches, unsigned char *pNoLatches, unsigned long *pLatchesBytes);

__declspec(dllimport) unsigned long DIO_Deb_SetConfig(unsigned long DeviceIndex, void *pDebTable, unsigned long *pDebTableBytes);
__declspec(dllimport) unsigned long DIO_Deb_ReadAll(unsigned long DeviceIndex, unsigned char *pDebData);

__declspec(dllimport) unsigned long DIO_CSA_DoSync(unsigned long DeviceIndex, double * BaseRateHz, double * DurAms, double * DurBms, double * DurCms);
__declspec(dllimport) unsigned long DIO_CSA_DebounceSet(unsigned long DeviceIndex, unsigned long DebounceCounts);
__declspec(dllimport) unsigned long DIO_CSA_DebounceReadAll(unsigned long DeviceIndex, void *pData);

__declspec(dllimport) unsigned long DAC_CSA_SetRangeLimits(unsigned long DeviceIndex, unsigned char *pData);
__declspec(dllimport) unsigned long DAC_CSA_ClearRangeLimits(unsigned long DeviceIndex);

__declspec(dllimport) unsigned long DACDIO_WriteAll(unsigned long DeviceIndex, unsigned short *pDACCounts, unsigned char *pDIOData);



__declspec(dllimport) unsigned long DACDirect(unsigned long DeviceIndex, unsigned short Channel, unsigned short Counts);
__declspec(dllimport) unsigned long DACMultiDirect(unsigned long DeviceIndex, void *pDACData, unsigned long DACDataCount);
__declspec(dllimport) unsigned long DACSetBoardRange(unsigned long DeviceIndex, unsigned long RangeCode);
__declspec(dllimport) unsigned long DACSetChannelCal(unsigned long DeviceIndex, unsigned long Channel, char *CalFileName);

__declspec(dllimport) unsigned long DACOutputProcess(unsigned long DeviceIndex, double *ClockHz, unsigned long NumSamples, unsigned short *SampleData);

__declspec(dllimport) unsigned long DACOutputOpen(unsigned long DeviceIndex, double *ClockHz);
__declspec(dllimport) unsigned long DACOutputClose(unsigned long DeviceIndex, unsigned long bWait);
__declspec(dllimport) unsigned long DACOutputCloseNoEnd(unsigned long DeviceIndex, unsigned long bWait);
__declspec(dllimport) unsigned long DACOutputFrame(unsigned long DeviceIndex, unsigned long FramePoints, unsigned short *FrameData);
__declspec(dllimport) unsigned long DACOutputFrameRaw(unsigned long DeviceIndex, unsigned long FramePoints, unsigned short *FrameData);
__declspec(dllimport) unsigned long DACOutputSetCount(unsigned long DeviceIndex, unsigned long NewCount);
__declspec(dllimport) unsigned long DACOutputStart(unsigned long DeviceIndex);
__declspec(dllimport) unsigned long DACOutputSetInterlock(unsigned long DeviceIndex, unsigned long bInterlock);
__declspec(dllimport) unsigned long DACOutputSetClock(unsigned long DeviceIndex, double *ClockHz);



//Note that all error codes returned are Windows error codes; they can be found in winerror.h in the Windows SDK, or on the Web.

#ifdef __cplusplus
}
#endif
