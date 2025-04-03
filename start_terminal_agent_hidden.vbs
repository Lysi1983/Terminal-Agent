Set WshShell = CreateObject("WScript.Shell")
strPath = WshShell.CurrentDirectory & "\start_terminal_agent_helper.bat"
WshShell.Run Chr(34) & strPath & Chr(34), 0, False
Set WshShell = Nothing