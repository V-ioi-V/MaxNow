Option Explicit

Dim shell
Dim scriptDir
Dim command
Dim exitCode

Set shell = CreateObject("WScript.Shell")
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & scriptDir & "\report_codex_usage.ps1"""

exitCode = shell.Run(command, 0, True)
WScript.Quit exitCode
