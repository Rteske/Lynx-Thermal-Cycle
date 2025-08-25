unit ContBufThreads;

interface

uses
  Windows, Classes;

type
{$IFDEF VER130} //Delphi 5
  TStartableThread = class(TThread)
    procedure Start; virtual;
  end;
{$ELSE}
  TStartableThread = TThread;
{$ENDIF}

const
  //Flags for streaming callback(s).
  CallbackFlag_BeginBC = $1;
  CallbackFlag_EndStream = $2;
  CallbackFlag_Inserted = $4;

type
  TContBuf = record
    ADBuf: array of Byte;
    BufState: (bsBlank, bsAccessing, bsGotData);
    Index: Integer;
    UsedSize, Flags: LongWord;
  end;
  PContBuf = ^TContBuf;

  TContBufThread = class(TStartableThread)
  public
    BytesPerBuf: LongWord;
    hBufMutex, hBlankBufSem, hDataBufSem, hKillEvent: THandle;
    BufBuf: array of PContBuf;
    NextIndexIn, NextIndexOut: Integer;

    procedure GetBufDebugStats(var Blanks, Accessings, GotDatas: LongWord);
  protected
    function GetBlankBuf(Flags: LongWord): PContBuf;
    procedure PutDataBuf(pNewBuf: PContBuf);
    function GetDataBufOrKilled: PContBuf;
    procedure PutBlankBuf(pNewBuf: PContBuf);
    function ExtraBuf(BaseFlags: LongWord): PContBuf;
  end;



implementation

{$IFDEF VER130} //Delphi 5
  procedure TStartableThread.Start;
  begin
    Resume;
  end;
{$ENDIF}

{ TContBufThread }

function TContBufThread.ExtraBuf(BaseFlags: LongWord): PContBuf;
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
    Result.Flags := CallbackFlag_Inserted or BaseFlags;
  ReleaseMutex(hBufMutex);
end;

function TContBufThread.GetBlankBuf(Flags: LongWord): PContBuf;
var
  I: Integer;

begin
  Result := nil;
  if WaitForSingleObject(hBlankBufSem, 0) = WAIT_TIMEOUT then begin
    //Result := ExtraBuf(Flags);
    Exit;
  end;
  WaitForSingleObject(hBufMutex, INFINITE);
    for I := 0 to High(BufBuf) do
      if BufBuf[I].BufState = bsBlank then begin
        Result := BufBuf[I];
        Result.Flags := Flags;
        Break;
      end
    ;
  ReleaseMutex(hBufMutex);

  {
  if Result = nil then begin
    Result := ExtraBuf(Flags); //We have a semaphore to prevent this, so not likely to matter.
  end;
  }
end;

function TContBufThread.GetDataBufOrKilled: PContBuf;
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
      if WaitForSingleObject(hKillEvent, 0) <> WAIT_TIMEOUT then Exit;
    end;
  until Result <> nil; //We have a semaphore to prevent this, so just go around again if it happens.
end;

procedure TContBufThread.GetBufDebugStats(var Blanks, Accessings, GotDatas: LongWord);
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

procedure TContBufThread.PutBlankBuf(pNewBuf: PContBuf);
begin
  WaitForSingleObject(hBufMutex, INFINITE);
    pNewBuf.BufState := bsBlank;
  ReleaseMutex(hBufMutex);
  ReleaseSemaphore(hBlankBufSem, 1, nil);
end;

procedure TContBufThread.PutDataBuf(pNewBuf: PContBuf);
begin
  WaitForSingleObject(hBufMutex, INFINITE);
    pNewBuf.BufState := bsGotData;
    pNewBuf.Index := NextIndexIn;
    Inc(NextIndexIn);
  ReleaseMutex(hBufMutex);
  ReleaseSemaphore(hDataBufSem, 1, nil);
end;

end.
