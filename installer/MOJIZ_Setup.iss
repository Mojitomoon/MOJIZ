; MOJIZ V1 — Inno Setup Script

#define MyAppName      "MOJIZ"
#define MyAppVersion   "1.0"
#define MyAppExeName   "MOJIZ.exe"

[Setup]
AppId={{A7C4E3F2-9B01-4D56-8E23-1F0A2B3C4D5E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=MOJIZ
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\Output
OutputBaseFilename=MOJIZ_Setup
SetupIconFile=..\MOJIZ.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
MinVersion=6.1sp1
CloseApplications=yes

[Languages]
Name: "english";  MessagesFile: "compiler:Default.isl"
Name: "russian";  MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autostart";   Description: "Запускать MOJIZ при старте Windows"; GroupDescription: "Дополнительно"; Flags: unchecked

[Files]
Source: "..\dist\MOJIZ.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}";       Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "MojizApp"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить MOJIZ"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "reg.exe"; Parameters: "delete ""HKCU\Software\Microsoft\Windows\CurrentVersion\Run"" /v MojizApp /f"; Flags: runhidden; RunOnceId: "RemoveAutostart"

[UninstallDelete]
Type: files; Name: "{app}\mojiz_settings.json"
