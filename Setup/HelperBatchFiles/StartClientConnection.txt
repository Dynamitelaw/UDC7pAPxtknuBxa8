Set oShell = CreateObject ("WScript.Shell") 
Dim strArgs
strArgs = "python DistributedComputing\BotConnection.py"
oShell.Run strArgs, 0, false