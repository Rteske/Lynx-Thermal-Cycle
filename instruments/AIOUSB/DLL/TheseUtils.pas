unit TheseUtils;

interface

const
  NAN = 0/0;
  Infinity = 1/0;

function MotorolaWord(W: Word): Word;
function IsNAN(V: Double): Boolean;
function InStrC(C: AnsiChar; S: AnsiString; StartIndex: Integer = 1): LongWord;
function SplitStr(S: AnsiString; SplitChar: AnsiChar; var Before, After: AnsiString): Integer;
function IsHex(S: AnsiString): Boolean;
function HexToNybble(Hex: AnsiChar): Byte;
function HexToStr(Hex: AnsiString): AnsiString;
function HexToInt(Hex: AnsiString): Integer;
function DumpFileToString(Path: AnsiString): AnsiString;



implementation

uses
  Windows,SysUtils, Classes;

function MotorolaWord(W: Word): Word;
//asm
//  xchg AL, AH
begin
  Result := (W shr 8) or (W shl 8);
end;

function IsNAN(V: Double): Boolean;
var
  NANBits: Int64;
  VBits: Int64 absolute V;

begin
  PDouble(@NANBits)^ := NAN;
  Result := VBits = NANBits;
end;

function InStrC(C: AnsiChar; S: AnsiString; StartIndex: Integer = 1): LongWord;
var
  I: Integer;

begin
  for I := StartIndex to Length(S) do
    if S[I] = C then begin
      Result := I;
      Exit;
    end
  ;

  Result := 0;
end;

function SplitStr(S: AnsiString; SplitChar: AnsiChar; var Before, After: AnsiString): Integer;
begin
  Result := InStrC(SplitChar, S);
  if Result = 0 then begin
    Before := S;
    After  := '';
  end
  else begin
    Before := Copy(S, 1, Result - 1);
    After  := Copy(S, Result + 1, MAXINT);
  end;
end;

function IsHex(S: AnsiString): Boolean;
var
  I: Integer;

begin
  Result := False;
  for I := 1 to Length(S) do
    if not (S[I] in ['0'..'9', 'A'..'F', 'a'..'f']) then
      Exit
  ;
  Result := True;
end;

function HexToNybble(Hex: AnsiChar): Byte;
begin
  case Hex of
  '0'..'9': Result := Byte(Hex) - Byte('0');
  'A'..'F': Result := Byte(Hex) - Byte('A') + 10;
  'a'..'f': Result := Byte(Hex) - Byte('a') + 10;
  else      raise Exception.CreateFmt('Invalid hex character "%s"', [ Hex ]);
  end;
end;

function HexToStr(Hex: AnsiString): AnsiString;
var
  I: Integer;

begin
  SetString(Result, nil, (Length(Hex) + 1) div 2);
  for I := Length(Result) downto 1 do
    Result[I] := AnsiChar(HexToNybble(Hex[I * 2]) + HexToNybble(Hex[I * 2 - 1]) shl 4)
  ;
end;

function HexToInt(Hex: AnsiString): Integer;
var
  I: Integer;

begin
  Result := 0;
  for I := 1 to Length(Hex) do
    Result := (Result shl 4) or HexToNybble(Hex[I])
  ;
end;

function DumpFileToString(Path: AnsiString): AnsiString;
var
  Fil: TFileStream;
  L: Integer;

begin
  Fil := TFileStream.Create(String(Path), fmOpenRead or fmShareDenyNone);
  try
    L := Fil.Size;
    SetString(Result, nil, L);
    Fil.Read(Result[1], L);
  finally
    Fil.Free;
  end;
end;

end.
