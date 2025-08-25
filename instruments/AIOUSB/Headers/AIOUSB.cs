using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;

namespace AIOUSBNet
{
	public class AIOUSB // Prototype AIOUSB.dll data and functions in managed C# for .Net -- Watch for char arrays, UNICODE v ANSI, and strings
	{
		#region Constants for simplifying use of Device Index
		public const UInt32 diNone = 0xFFFFFFFF; // "-1"
		public const UInt32 diFirst = 0xFFFFFFFE; // "-2" First board (lowest DeviceIndex)
		public const UInt32 diOnly = 0xFFFFFFFD; // "-3" One and only board
		#endregion
		#region Constants for Win32 Error codes
		public const UInt32 ERROR_SUCCESS = 0;
		#endregion
		#region Constants, Misc
		public const UInt32 MAXNAMESIZE = 32;
		#endregion
		# region Constants related to AIOUSB_ClearFIFO() and similar
		public const UInt32 TIME_METHOD_NOW = 0;
		public const UInt32 TIME_METHOD_WAIT_INPUT_ENABLE = 86;
		public const UInt32 TIME_METHOD_NOW_AND_ABORT = 5;
		public const UInt32 TIME_METHOD_WHEN_INPUT_ENABLE = 1;
		#endregion
		#region General Board Discovery & Utility Functions

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 GetDevices();

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 QueryDeviceInfo(UInt32 DeviceIndex, ref UInt32 pPID, ref UInt32 pNameSize, IntPtr Name, ref UInt32 DIOBytes, ref UInt32 Counters);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 QueryDeviceInfo(UInt32 DeviceIndex, ref UInt32 pPID, ref UInt32 pNameSize, StringBuilder DEVName, ref UInt32 DIOBytes, ref UInt32 Counters);

		public static UInt32 QueryDeviceInformation(UInt32 DeviceIndex, out UInt32 pPID, out string Name, out UInt32 DIOBytes, out UInt32 Counters)
		{
			UInt32 Status;
			DIOBytes = 0; Counters = 0;
			StringBuilder strNameIn = new StringBuilder((Int32)(AIOUSB.MAXNAMESIZE) + 1);
			UInt32 NameSize = AIOUSB.MAXNAMESIZE;
			pPID = 0;

			Status = AIOUSB.QueryDeviceInfo(DeviceIndex, ref pPID, ref NameSize, strNameIn, ref DIOBytes, ref Counters);
			if (Status == AIOUSB.ERROR_SUCCESS)
			{
				strNameIn.Length = strNameIn.Capacity;
				Name = strNameIn.ToString(0, (Int32)(NameSize));
			}
			else
			{
				Name = "";
			}
			return Status;
		}

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 AIOUSB_ReloadDeviceLinks();

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ResolveDeviceIndex(UInt32 DeviceIndex);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 AIOUSB_CloseDevice(UInt32 DeviceIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ClearDevices();

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 AIOUSB_SetGlobalTickRate(UInt32 DeviceIndex, ref double pHz);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CustomEEPROMRead(UInt32 DeviceIndex, UInt32 StartAddress, ref UInt32 DataSize, out Byte[] Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CustomEEPROMWrite(UInt32 DeviceIndex, UInt32 StartAddress, UInt32 DataSize, [In] Byte[] Data);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 GetDeviceByEEPROMByte(Byte Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 GetDeviceByEEPROMData(UInt32 StartAddress, UInt32 DataSize, [In] Byte[] pData);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 GetDeviceSerialNumber(UInt32 DeviceIndex, ref UInt64 pSerialNumber);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 AIOUSB_ClearFIFO(UInt32 DeviceIndex, UInt32 TimeMethod);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 AIOUSB_QuerySimplePNPData(UInt32 DeviceIndex, ref Byte[] pPNPData, ref UInt32 pPNPDataBytes);
		#endregion
		#region DIO (Digital I/O, Including FET, Relay, and Isolated Inputs) Specific Functions

		// DIO_Configure is overloaded for your convenience
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_Configure(UInt32 DeviceIndex, Byte Tristate, ref UInt32 OutMask, ref UInt32 Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_Configure(UInt32 DeviceIndex, Byte Tristate, ref UInt16 OutMask, [In] Byte[] Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_Configure(UInt32 DeviceIndex, Byte Tristate, [In] Byte[] OutMask, [In] Byte[] Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_Configure(UInt32 DeviceIndex, Byte Tristate, ref Byte OutMask, ref byte[] Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_Configure(uint deviceIndex, Byte bTristateAll, ref uint outMask, ref byte[] Data);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_Configure(uint deviceIndex, Byte bTristateAll, IntPtr outMask, IntPtr Data);

		public static UInt32 DIO_Configure(UInt32 DeviceIndex, UInt32 bTristateAll, Byte[] Outs, Byte[] Data)
		{
			IntPtr OutsPtr = Marshal.AllocHGlobal(Outs.Length);
			IntPtr DataPtr = Marshal.AllocHGlobal(Data.Length);
			UInt32 Status;

            try {
				Marshal.Copy(Outs, 0, OutsPtr, Outs.Length);
				Marshal.Copy(Data, 0, DataPtr, Data.Length);
				Status = DIO_Configure(DeviceIndex, Convert.ToByte(bTristateAll), OutsPtr, DataPtr);
			}
			finally
			{
				Marshal.FreeHGlobal(DataPtr);
				Marshal.FreeHGlobal(OutsPtr);
			}

			return Status;
		}

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_ConfigureEx(UInt32 DeviceIndex, [In] Byte[] pOutMask, [In] Byte[] pData, [In] Byte[] pTristateMask);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_StreamOpen(UInt32 DeviceIndex, UInt32 bIsRead);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_StreamClose(UInt32 DeviceIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_StreamFrame(UInt32 DeviceIndex, UInt32 FramePoints, ref UInt16[] FrameData, out UInt32 BytesTransferred);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_StreamSetClocks(UInt32 DeviceIndex, ref double ReadClockHz, ref double WriteClockHz);



		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_ConfigureMasked(UInt32 DeviceIndex, [In] Byte[] pOuts, [In] Byte[] pOutsMask, [In] Byte[] pData, [In] Byte[] pDataMask, [In] Byte[] pTristates, [In] Byte[] pTristatesMask);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_ConfigurationQuery(UInt32 DeviceIndex, out Byte[] pOutMask, out Byte[] pTristateMask);



		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]

		// DIO_WriteAll is overloaded for your convenience
		public static extern UInt32 DIO_WriteAll(UInt32 DeviceIndex, ref UInt32 Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_WriteAll(UInt32 DeviceIndex, [In] Byte[] Data);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_Write8(UInt32 DeviceIndex, UInt32 ByteIndex, Byte Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_Write1(UInt32 DeviceIndex, UInt32 BitIndex, Byte Data);

		// DIO_ReadAll is overloaded for your convenience


		// [DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)] public static extern UInt32 DIO_ReadAll(UInt32 DeviceIndex, ref UInt32 Data);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		private static extern UInt32 DIO_ReadAll(UInt32 DeviceIndex, IntPtr Data);

		public static UInt32 DIO_ReadAll(UInt32 DeviceIndex, int DataLength, Byte[] Data)
		{
			Data = new Byte[DataLength];
			IntPtr outPtr = Marshal.AllocHGlobal(DataLength);
			UInt32 Status;
			try
			{
				Status = DIO_ReadAll(DeviceIndex, outPtr);
				Marshal.Copy(outPtr, Data, 0, DataLength);
			}
			finally
			{
				Marshal.FreeHGlobal(outPtr);
			}
			return Status;
		}
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_ReadAll(UInt32 DeviceIndex, ref UInt32 Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_ReadAll(UInt32 DeviceIndex,  Byte[] Data);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_Read8(UInt32 DeviceIndex, UInt32 ByteIndex, ref Byte Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_Read1(UInt32 DeviceIndex, UInt32 BitIndex, out Byte Data);
		#endregion
		#region USB-DIO-16H Family-specific (streaming, fast) functions

		#endregion
		#region ADC (Analog Input (Analog-to-Digital)) Specific Functions
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_GetScanV(UInt32 DeviceIndex, Double[] pBuf);
		#region USB-AIx and DPK-AIx Family-Specific Functions
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_SetConfig(UInt32 DeviceIndex, [In] Byte[] pConfigBuf, ref UInt32 ConfigBufSize);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_GetConfig(UInt32 DeviceIndex, out Byte[] pConfigBuf, ref UInt32 ConfigBufSize);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_Initialize(UInt32 DeviceIndex, [In] Byte pConfigBuf, ref UInt32 pConfigBufSize, [In] Char[] CalFileName); // wrapper for SetConfig AND SetCal, nothing more.
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_QueryCal(UInt32 DeviceIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_SetCalAndSave(UInt32 DeviceIndex, [In] Char[] CalFileName, [In] Char[] SaveCalFileName);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_SetCal(UInt32 DeviceIndex, [In] Char[] CalFileName);
		public static UInt32 ADC_SetCal(UInt32 DeviceIndex, String CalFileName)
		{
			UInt32 NameSize = Convert.ToUInt32(CalFileName.Length + 1); // This is the only func in dll that takes a null terminator, so add 1 character for it
			Char[] charName = new Char[NameSize];
			CalFileName.CopyTo(0, charName, 0, CalFileName.Length);
			return ADC_SetCal(DeviceIndex, charName);
		}
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_BulkAcquire(UInt32 DeviceIndex, UInt32 BufSize, out UInt16[] Buf);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_BulkPoll(UInt32 DeviceIndex, out UInt32 BytesLeft);

		// Continuous mode for USB-AIx and DPK-AIx:

		// Callback function delegate for use as function pointer parameter passed to AIOUSB.DLL:
		// Declare delegate -- defines required signature:
		// Original from Pascal: procedure ADCallback(pBuf: PWord; BufSize, Flags, Context: LongWord); cdecl;
		// Must be Cdecl not default stdcall to match dll:
		// We need to use Intptr for the buffer:
		// Application probably needs to use GCHandle.Alloc(foo), where "foo" is the callback function name, to prevent garbage collection of the callback function
		[UnmanagedFunctionPointer(CallingConvention.Cdecl)]
		public delegate void ADCallback(IntPtr pBuf, UInt32 BufSize, UInt32 Flags, UInt32 Context);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_BulkContinuousCallbackStart(UInt32 DeviceIndex, UInt32 BufSize, UInt32 BaseBufCount, UInt32 Context, ADCallback pCallback);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_FullStartRing(UInt32 DeviceIndex, out byte[] pConfigBuf, ref UInt32 ConfigBufSize, [ Out] Char[] CalFileName, ref double pCounterHz, UInt32 RingBufferSize, UInt32 PacketsPerBlock);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_ReadData(UInt32 DeviceIndex, out byte[] pConfigBuf, ref UInt32 ScansToRead, ref double[] pData, ref double Timeout);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_ReadData(UInt32 DeviceIndex, out byte[] pConfigBuf, ref UInt32 ScansToRead, ref double[][] pDataScans, ref double Timeout);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_BulkContinuousEnd(UInt32 DeviceIndex, UInt32 pIOStatus);
		#endregion
		#endregion
		#region DAC (Analog Output (Digital-to-Analog)) Specific Functions

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACDirect(UInt32 DeviceIndex, UInt16 Channel, UInt16 Counts);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACMultiDirect(UInt32 DeviceIndex, [In] UInt16[] pDACData, UInt32 DACDataCount);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACSetBoardRange(UInt32 DeviceIndex, UInt32 RangeCode);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACSetChannelCal(UInt32 DeviceIndex, UInt32 Channel, [In] Char[] CalFileName);
		public static UInt32 DACSetChannelCal(UInt32 DeviceIndex, UInt32 Channel, String CalFileName)
		{
			UInt32 NameSize = Convert.ToUInt32(CalFileName.Length);
			Char[] charName = new Char[NameSize];
			CalFileName.CopyTo(0, charName, 0, CalFileName.Length);
			return DACSetChannelCal(DeviceIndex, Channel, charName);
		}

		#region DAC Functions for USB-DA12-8A only
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACOutputProcess(UInt32 DeviceIndex, ref Double ClockHz, UInt32 NumSamples, [In] UInt16[] SampleData);

		// More DAC Functions for USB-DA12-8A only (advanced, rare)
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACOutputOpen(UInt32 DeviceIndex, ref Double ClockHZ);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACOutputCloseNoEnd(UInt32 DeviceIndex, UInt32 bWait);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACOutputFrameRaw(UInt32 DeviceIndex, UInt32 FramePoints, [In] UInt16[] FrameData);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACOutputSetCount(UInt32 DeviceIndex, UInt32 NewCount);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACOutputSetInterlock(UInt32 DeviceIndex, UInt32 bInterlock);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACOutputStart(UInt32 DeviceIndex);
		#endregion
		#endregion
		#region CTR (Counter/Timer (8254)) Specific Functions
		// more 8254 functions (rare, advanced)
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_8254Load(UInt32 DeviceIndex, UInt32 BlockIndex, UInt32 CounterIndex, UInt16 LoadValue);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_8254Mode(UInt32 DeviceIndex, UInt32 BlockIndex, UInt32 CounterIndex, UInt32 Mode);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_8254ModeLoad(UInt32 DeviceIndex, UInt32 BlockIndex, UInt32 CounterIndex, UInt32 Mode, UInt16 LoadValue);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_8254Read(UInt32 DeviceIndex, UInt32 BlockIndex, UInt32 CounterIndex, ref UInt16 ReadValue);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_8254ReadStatus(UInt32 DeviceIndex, UInt32 BlockIndex, UInt32 CounterIndex, ref UInt16 ReadValue, ref Byte Status);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_8254ReadModeLoad(UInt32 DeviceIndex, UInt32 BlockIndex, UInt32 CounterIndex, UInt32 Mode, UInt16 LoadValue, ref UInt16 ReadValue);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_StartOutputFreq(UInt32 DeviceIndex, UInt32 BlockIndex, ref Double Hz);
		#region USB-CTR-15 Specific Functions
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_8254ReadAll(UInt32 DeviceIndex, out UInt16[] pData);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_8254SelectGate(UInt32 DeviceIndex, UInt32 GateIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_8254ReadLatched(UInt32 DeviceIndex, out UInt16[] pData);

		// Legacy functions that were for a custom Application
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_SetWaitGates(UInt32 DeviceIndex, Byte A, Byte B);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_EndWaitGates(UInt32 DeviceIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_WaitForGate(UInt32 DeviceIndex, Byte GateIndex, ref UInt16 pContent);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_StartMeasuringPulseWidth(UInt32 DeviceIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_StopMeasuringPulseWidth(UInt32 DeviceIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 CTR_GetPulseWidthMeasurement(UInt32 DeviceIndex, UInt32 BlockIndex, UInt32 CounterIndex, out UInt16 pReadValue);
		#endregion
		#endregion
		#region These functions are reserved for factory use only, or are deprecated
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 GenericVendorRead(UInt32 DeviceIndex, Byte Request, UInt16 Value, UInt16 Index, ref UInt32 pDataSize, byte[] pData);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 GenericVendorWrite(UInt32 DeviceIndex, Byte Request, UInt16 Value, UInt16 Index, UInt32 DataSize, ref byte[] pData);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_SPI_Read(UInt32 DeviceIndex, UInt32 Address, byte Reg, out byte[] pValue);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DIO_SPI_Write(UInt32 DeviceIndex, UInt32 Address, byte Reg, byte Value);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_Initialize(UInt32 DeviceIndex, [In, Out] byte[] pConfigBuf, ref UInt32 ConfigBufSize, [In, Out] Char[] CalFileName); // Unicode
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_GetImmediate(UInt32 DeviceIndex, UInt32 Channel, out UInt16 pBuf);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACOutputClose(UInt32 DeviceIndex, UInt32 bWait);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 AIOUSB_FlashRead(UInt32 DeviceIndex, UInt32 StartAddress, [In, Out] UInt32 DataSize, ref byte[] Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 AIOUSB_FlashWrite(UInt32 DeviceIndex, UInt32 StartAddress, UInt32 DataSize, out byte[] Data);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 AIOUSB_FlashEraseSector(UInt32 DeviceIndex, UInt32 Sector);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DACOutputFrame(UInt32 DeviceIndex, UInt32 FramePoints, [In, Out] UInt16 pFrameData);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DAC_CSA_SetRangeLimits(UInt32 DeviceIndex, [In, Out] Byte[] pData);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 DAC_CSA_ClearRangeLimits(UInt32 DeviceIndex);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_InitFastITScanV(UInt32 DeviceIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_ResetFastITScanV(UInt32 DeviceIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_SetFastITScanVChannels(UInt32 DeviceIndex, UInt32 NewChannels);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_GetFastITScanV(UInt32 DeviceIndex, [In, Out] double pBuf);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_GetITScanV(UInt32 DeviceIndex, [In, Out] double pBuf);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_CSA_InitFastScanV(UInt32 DeviceIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_CSA_ResetFastScanV(UInt32 DeviceIndex);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_CSA_GetFastScanV(UInt32 DeviceIndex, [In, Out] double[] pBuf);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_RangeAll(UInt32 DeviceIndex, ref byte GainCodes, UInt32 bDifferential);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_Range1(UInt32 DeviceIndex, UInt32 ADChannel, byte GainCode, UInt32 bDifferential);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_ADMode(UInt32 DeviceIndex, byte TriggerMode, byte CalMode);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_SetScanLimits(UInt32 DeviceIndex, UInt32 StartChannel, UInt32 EndChannel);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_SetOversample(UInt32 DeviceIndex, byte Oversample);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_GetCalRefV(UInt32 DeviceIndex, UInt32 CalRefIndex, out double pRef);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_BulkContinuousCallbackStartClocked(UInt32 DeviceIndex, UInt32 BufSize, UInt32 BaseBufCount, UInt32 Context, ADCallback pCallback, ref double Hz);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 GetDeviceBySerialNumber(UInt64 SerialNumber);



		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 AIOUSB_GetStreamStatus(UInt32 DeviceIndex, out UInt32 Status);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 AIOUSB_SetStreamingBlockSize(UInt32 DeviceIndex, UInt32 BlockSize);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 GetDeviceUniqueStr(UInt32 DeviceIndex, ref UInt32 pIIDSize, [In, Out] Char pIID);

		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_GetChannelV(UInt32 DeviceIndex, UInt32 ChannelIndex, out double pBuf); // If you're taking more than one channel of data, ADC_GetScanV() is faster!
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_GetScan(UInt32 DeviceIndex, [In, Out] UInt16[] pBuf);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_BulkMode(UInt32 DeviceIndex, UInt32 BulkMode);
		[DllImport("AIOUSB.DLL", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
		public static extern UInt32 ADC_BulkContinuousRingStart(UInt32 DeviceIndex, UInt32 RingBufferSize, UInt32 PacketsPerBlock);

		//__declspec(dllimport) unsigned long DIO_CSA_DoSync(unsigned long DeviceIndex, double * BaseRateHz, double * DurAms, double * DurBms, double * DurCms);
		//__declspec(dllimport) unsigned long DIO_CSA_DebounceSet(unsigned long DeviceIndex, unsigned long DebounceCounts);
		//__declspec(dllimport) unsigned long DIO_CSA_DebounceReadAll(unsigned long DeviceIndex, void *pData);
		//__declspec(dllimport) unsigned long DACDIO_WriteAll(unsigned long DeviceIndex, unsigned short *pDACCounts, unsigned char *pDIOData);
		#endregion
	}
}
