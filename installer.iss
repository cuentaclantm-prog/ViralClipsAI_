#define MyAppName "ViralClipsAI"
#define MyAppVersion "1.0.0"
[Setup]
AppId=ViralClipsAI-1.0.0-Windows-x64
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\ViralClipsAI
DefaultGroupName=ViralClipsAI
OutputDir=dist
OutputBaseFilename=ViralClipsAI_Setup_Windows10_64bit
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\ViralClipsAI.exe
[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos adicionales:"
[Files]
Source: "dist\ViralClipsAI\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
[Icons]
Name: "{group}\ViralClipsAI"; Filename: "{app}\ViralClipsAI.exe"
Name: "{autodesktop}\ViralClipsAI"; Filename: "{app}\ViralClipsAI.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\ViralClipsAI.exe"; Description: "Abrir ViralClipsAI"; Flags: postinstall nowait skipifsilent
