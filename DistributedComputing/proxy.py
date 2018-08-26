#!/usr/bin/env python

#------------------------------------
#Jose Rubianes (jer2201)
#CSEE4119: Computer Networks
#Project 1: Video CDN
#
#Contains all the functions and classes needed to
#implement the HTTP ABR video proxy server for Project 1
#
#Requires the following command line arguments when run:
#	<logFilePath> <alpha> <proxyListenPort> <proxyFakeIP> <webServerIP>
#------------------------------------


import sys
import socket
import thread
import threading
import time
import re


#Setting printDebug to True prints out debugging statements into the terminal
global printDebug
printDebug = False

global rateSelectors
rateSelectors = {}

global accessLock
accessLock = threading.Lock()

global bindingPort
bindingPort = 5000


class bitrateSelector:
	'''
	Object class that keeps track of the average throughput
	for a single client.
	Average throughput is exponentially weighted.
	Persistent across reconnects within the epoch.
	'''

	#Class constructor
	def __init__ (self, alpha):
		self.alpha = alpha
		self.bitrates = [10]
		self.tcurrent = 1875.0  #Bytes per second
		self.printDebug = printDebug
		self.rate = 10

	#updates selector variables
	def update(self, bitrateList):
		self.bitrates = bitrateList
		self.tcurrent = 1875.0  #Bytes per second
		self.rate = bitrateList[0]
		if (self.printDebug):
			print("--bitrateSelector updated")
			print("--alpha = " + str(self.alpha))

	#calculates new tcurrent, returns selected rate
	def getRate(self, tnew):
		self.tcurrent = (self.alpha*tnew) + ((1-self.alpha)*self.tcurrent)
		self.tcBits = (self.tcurrent * 8.0) / (1000 * 1.5)
		for i in range(0,len(self.bitrates),1):
			if (self.tcBits >= self.bitrates[i]):
				self.rate = self.bitrates[i]
			elif (i==0):
				self.rate = self.bitrates[i]			
			else:
				break
		if (self.printDebug):
			print("--Tcurrent: " + str(self.tcurrent) + " Bps")
			print("--Selected bitrate: " + str(self.rate) + " kbps")
		
		return self.rate
	
	#resets current rate upon reconnect
	def reset(self):
		self.rate = self.bitrates[0]
		self.tcurrent = (self.rate / 8) * 1000
		self.tcBits = (self.tcurrent * 8.0) / (1000 * 1.5)
		

def f4mIntercept(requestList, outbound, webServerIP, serverListenPort, rateSelector):
	'''
	Intercepts the f4m manifest file; fowards nolist to client

	requestList: cliet GET request in list form

	outbound: the server socket
	
	webServerIP: IP address of the webserver

	serverListenPort: the TCP port the webserver listens on for incoming client connections. 
	
	rateSelector: the bitrateSelector object to modify
	'''

	serverRequestList = [requestList[0],"Host: " + webServerIP +":"+ str(serverListenPort)]
	for i in range(2,len(requestList),1):
		serverRequestList.append(requestList[i])

	serverRequest = '\n'.join(map(str,serverRequestList))

	if (printDebug):
		print("------------------------------------------------")
		print("|PROXY| Server Request")
		print("------------------------------------------------")
		print(serverRequest)

	#Sends f4m GET request
	if (printDebug):
		print("--|PROXY| requesting f4m...")
		fowardTime = time.time()

	outbound.sendall(serverRequest)
	
	if (printDebug):
		print("--Request sent(" + str(time.time()-fowardTime)+" s)")

	#Obtains server response
	time.sleep(0.5)
	while True:
		try:
			serverResponse = outbound.recv(16384)
			break
		except Exception as e:
			if (not (serverResponse)):
				break

	#If server closed socket, closes both connections
	if (not (serverResponse)):
		raise ValueError("Server closed connection while awaiting f4m file")

	#If there is a response from the server
	if (len(serverResponse) > 0):
		responseStartTime = time.time()
		if (printDebug):
			print("------------------------------------------------")
			print("Server Response")
			print("------------------------------------------------")
			print(serverResponse[:500] + "\n--**END**--")
	
	responseList = serverResponse.split("\n")
	for i in range(0,len(responseList),1):
		if (responseList[i][0:12] == "Content-Type"):
			#obtains f4m as list of lines
			f4mList = responseList[(i+2):]
			break
	
	if (printDebug):
		print("------------------------------------------------")
		print("f4m Manifest Captured")
		print("------------------------------------------------")

	#Obtains list of availible bitrates
	bitrateList = []
	for i in range(0, len(f4mList),1):
		line = f4mList[i]
		line = line.replace(" ","")
		line = line.replace("	","")
		if (line[0:7] == "bitrate"):
			rate = int(line.split("=")[1].replace('"',''))
			bitrateList.append(rate)
	bitrateList.sort()
	if (printDebug):
		print ("--Bitrate options obtained: " + str(bitrateList))
	
	#Creates new GET request to return nolist version of manifest
	getLineList = requestList[0].split(".")
	getLineList[0] = getLineList[0] + "_nolist"
	getLine = '.'.join(map(str,getLineList))

	#Updates bitrateSelector
	rateSelector.update(bitrateList)

	return getLine
		

def clientThread(connection, bufferSize, address, fakeIP, webServerIP, alpha, logPath, serverListenPort = 8080):
	'''
	defines the main loop for a single client thread

	connection: the incoming client socket

	bufferSize: the size of the socket buffers

	address: the IP address and port of the client
	
	fakeIP: the fake IP address that the proxy binds to when connecting to the 
	webserver
	
	webServerIP: IP address of the webserver

	alpha: Constant that controls the responsiveness of the throughput estimate.
	Must be between 0 and 1

	logPath: The filepath to the log file that will be saved from this session.
	Overwrites previous log files with the same name.

	serverListenPort: the TCP port the webserver listens on for incoming client connections. 
	Defaults to 8080
	'''
	
	noInitialError = True

	#Retrieves client's persistent bitrateSelector object, or creates a new one for this client
	global rateSelectors
	try:
		rateSelector = rateSelectors[(address[0] + fakeIP)]
		rateSelector.reset()
		if (printDebug):
			print("--Selector found. Restoring selector object")
	except Exception as e:
		if (printDebug):
			print("--No selector found, creating new one")
		rateSelector = bitrateSelector(alpha)
		rateSelectors[(address[0] + fakeIP)] = rateSelector

	#Open connection to speciifed webserver
	if (printDebug):
		print("--Connecting to web server: " + webServerIP +":"+ str(serverListenPort) +"...")

	outbound = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	global bindingPort
	while True:
		try:
			outbound.bind((fakeIP,bindingPort))
			break
		except Exception as e:
			bindingPort += 1
	
	if (printDebug):
		print("--Binding port: " + str(bindingPort))
	
	try:
		outbound.connect((webServerIP,serverListenPort))
	except Exception as e:
		if (printDebug):
			print("--Could not connect to server")
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(exc_type, e, exc_tb.tb_lineno)
		noInitialError = False

	if (printDebug):
		print("--Connected to server: " + webServerIP +":"+ str(serverListenPort))

	#Initial timout value
	timeout = 30
	#Initial Content Length
	contentLength = 0
	#Initial response time
	responseStartTime = time.time()
	#Instantiate serverResponse variable to allow reconnections
	serverResponse = ""
	#Initial bitrate
	rate = 10

	#While client and server connections are open
	try:
		while noInitialError:
			connection.settimeout(timeout)

			#If connection timeout
			if ((time.time() - responseStartTime) > timeout):
				if (printDebug):
					print("--Server connection timeout")
				break

			#Splits request into a list for parsing and modification
			try:
				request = connection.recv(bufferSize)
			except Exception as e:
				print (e)
			requestList = request.split("\n")
			
			#If there is a request from client
			if (len(request) > 0):
				requestStartTime = time.time()
				if (printDebug):
					print("------------------------------------------------")
					print("Client Request: " + address[0] + ":" + str(address[1]))
					print("------------------------------------------------")
					print(request)

				#Modifies HTTP GET request for webserver 
				isf4m = ((requestList[0].split(" ")[1][-4:]) == ".f4m")
				try:
					isVid = ((requestList[0].split(" ")[1].split("-")[1][0:4]) == "Frag")
				except:
					isVid = False
				
				if (isf4m): #intercepts manifest file
					if (printDebug):
						print("--intercepting f4m file")
					getLine = f4mIntercept(requestList, outbound, webServerIP, serverListenPort, rateSelector)
					serverRequestList = [getLine,"Host: " + webServerIP +":"+ str(serverListenPort)]
				elif (isVid):	#intercepts and modifies video GET requests
					if (printDebug):
						print("--modifying video GET request")
					getLineList = requestList[0].split(" ")
					segmentList = getLineList[1].split("/")
					segmentNameList = segmentList[-1].split("Seg")
					segmentNameList[0] = str(rate)
					segmentList[-1] = 'Seg'.join(map(str,segmentNameList))
					getLineList[1] = '/'.join(map(str,segmentList))
					getLine = ' '.join(map(str,getLineList))
					serverRequestList = [getLine,"Host: " + webServerIP +":"+ str(serverListenPort)]
				else:
					serverRequestList = [requestList[0],"Host: " + webServerIP +":"+ str(serverListenPort)]
				for i in range(2,len(requestList),1):
					serverRequestList.append(requestList[i])

				serverRequest = '\n'.join(map(str,serverRequestList))

				if (printDebug):
					print("------------------------------------------------")
					print("Server Request")
					print("------------------------------------------------")
					print(serverRequest)

				#Fowards modified GET request
				if (printDebug):
					print("--Fowarding request...")
					fowardTime = time.time()

				outbound.sendall(serverRequest)
				
				if (printDebug):
					print("--Request sent(" + str(time.time()-fowardTime)+" s)")

			#Fowards server response
			responseStartTime = time.time()
			while True:
				try:
					serverResponse = outbound.recv(bufferSize)
					break
				except Exception as e:
					if (time.time() - responseStartTime > timeout):
						if (printDebug):
							print("--Server connection timeout")
						break

			#If server closed socket, closes both connections
			if (not (serverResponse)):
				if (printDebug):
					print("--Server Closed Connection")
				break

			#If there is a response from the server
			if (len(serverResponse) > 0):
				if (printDebug):
					print("------------------------------------------------")
					print("Server Response")
					print("------------------------------------------------")
					print(serverResponse[:600] + "\n--**END**--")
					print("--Fowarding response...")

				serverResponseList = serverResponse.split("\n")
				lengthToSend = 2
				
				#Parse HTTP fields
				for i in range(0,len(serverResponseList),1):
					responseLine = serverResponseList[i]
					lengthToSend += (len(responseLine)+ 1)
					if (responseLine[0:14] == "Content-Length"):
						contentLength = int(responseLine.replace(" ","").split(":")[1])
						lengthToSend += contentLength
					elif (responseLine[0:10] == "Keep-Alive"):
						timeout = int(responseLine.replace("=",",").split(",")[1])
					elif (responseLine[0:12] == "Content-Type"):
						break	
				packetCount = 0
				totalLengthSent = 0

				#Fowards Server Response
				while True:
					try:
						connection.sendall(serverResponse)
						totalLengthSent += len(serverResponse)
						packetCount += 1 
						if (totalLengthSent == lengthToSend):
							break
						serverResponse = outbound.recv(bufferSize)
						if (not (serverResponse)):
							if (printDebug):
								raise ValueError("Server Closed Connection!")

					except Exception as e:
						if (printDebug):
							exc_type, exc_obj, exc_tb = sys.exc_info()
							print(exc_type, e, exc_tb.tb_lineno)
						raise ValueError(str(e))
				
				chunkTime = time.time() - requestStartTime			
				if (printDebug):
					print("--Response sent (px"+ str(packetCount) + ") "+str(time.time()-responseStartTime)+" s")
					print("--Chunk time: " + str(chunkTime) + "s")
					print("--Parsed Content Length: " + str(contentLength))
					print("--Total bytes to send: " + str(lengthToSend))
					print("--Total bytes sent: " + str(totalLengthSent))
					print("--Parsed timout: " + str(timeout))
				
				
			else:
				if (printDebug):
					sys.stdout.write('\r')
					sys.stdout.write("--Waiting for server response...")
					sys.stdout.flush()
				break
			
			oldRate = rate
			rate = rateSelector.getRate((contentLength / chunkTime))
			
			#Creates line to add to log file
			logList = [time.time(), chunkTime, ((contentLength * 8)/(1000.0*chunkTime)), ((rateSelector.tcBits)*1.5), rate, webServerIP, serverRequestList[0].split(" ")[1]]
			logLine = ' '.join(map(str,logList))
			if (printDebug):
				print("--Tcurrent: " + str((rateSelector.tcBits)*1.5) + " kbps")
				print("--Log Entry: " + str(logList))

			with accessLock:	#prevents file-access collisions among threads
				log = open(logPath, 'a+')
				log.write(logLine + "\n")
				log.close()
			

	except Exception as e:
		if (printDebug):
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(exc_type, e, exc_tb.tb_lineno)
	
	bindingPort += 1	
	
	#Closes both connections
	if (printDebug):
		print("X	--Closing connection with client: " + address[0] + ":" + str(address[1]))
	connection.close()	

	if (printDebug):
		print("X	--Closing connection with server: " + webServerIP + ":" + str(serverListenPort))
	outbound.close()


def proxyStart(logPath, alpha, listenPort, fakeIP, webServerIP):
	'''
	starts the proxy server's main loop

	logPath: The filepath to the log file that will be saved from this session.
	Overwrites previous log files with the same name.

	alpha: Constant that controls the responsiveness of the throughput estimate.
	Must be between 0 and 1

	listenPort: the TCP port the proxy listens on for incoming client connections

	fakeIP: the fake IP address that the proxy binds to when connecting to the 
	webserver
	
	webServerIP: IP address of the webserver
	'''

	incomingHost = ''
	listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	if (printDebug):
		print("\n\n\n\n*************************************************")
		print("*************************************************\n\n\n\n")
		print("Binding incoming port to " + str(listenPort) + "...")
	
	#Tries to bind the incoming port
	try:
		listen.bind((incomingHost,listenPort))
	except Exception as e:
		print("Error: " + str(e))
		print("Closing ProxyServer")
		listen.close()
		return
	
	if (printDebug):
		print("Listening on port " + str(listenPort) + "\n")
	else:
		print("Proxy server initiated")

	listen.listen(5)
	
	#Listens for incoming connection requests
	while True:
		conn, addr = listen.accept()

		if (printDebug):
			print("--Connected to client: " + addr[0] + ":" + str(addr[1]))

		#Opens new thread for each client
		bufferSize = 4096
		thread.start_new_thread(clientThread,(conn, bufferSize, addr, fakeIP, webServerIP, alpha, logPath))	


def main():
	try:
		#Parse Command Line Arguments
		arguments = sys.argv
		logPath = arguments[1]
		alpha = float(arguments[2])
		listenPort = int(arguments[3])
		fakeIP = arguments[4]
		webServerIP = arguments[5]

	except Exception as e:
		print("Error: Not enough or invalid input arguments")
		print(e)

	#Clears old log file if path is the same
	logFile = open(logPath, "w")
	logFile.close()

	#Initiates Proxy Server
	print("Initiating proxy server...")
	proxyStart(logPath, alpha, listenPort, fakeIP, webServerIP)


#------------------------------------------------------------------------

main()

