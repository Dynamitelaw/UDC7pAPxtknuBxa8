Set oShell = CreateObject ("WScript.Shell") 
Dim strArgs
strArgs = "python DistributedNetworking\BotConnection.py"
oShell.Run strArgs, 0, false
