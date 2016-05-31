#!/usr/bin/env python
import os, sys
from socket import *

BYTES_TO_RECEIVE = 1024
TIME_OUT_LIMIT = 3
SCRIPT_LOCATION = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
CONTENT_LENGTH_HEADER = "Content-Length: "
CRLF = '\r\n'

# Form the HTTP request to be sent to the server
def formRequestHeader(req_webpage_name):
    httprequestheader = ("GET /" + req_webpage_name + " HTTP/1.1\r\n\r\n")
    return httprequestheader

# Parse content length from headers
def getContentLength(headers):
    leftIndex = headers.find(CONTENT_LENGTH_HEADER)
    if leftIndex == -1:
        return -1
    else:
        leftIndex += len(CONTENT_LENGTH_HEADER)
    rightIndex = headers.find(CRLF, leftIndex)
    return int(headers[leftIndex:rightIndex])

# Listen for and only return HTTP headers from server
def getHeaders(clientSocket):
    rcvBuffer = ""
    httpHeaders = ""
    while True:
        response = clientSocket.recv(BYTES_TO_RECEIVE)
        if not response:
            continue
        rcvBuffer += response;
        lastCRLFindex = rcvBuffer.rfind(CRLF)
        if lastCRLFindex != -1:
            # We assume valid HTTP responses (2 new line character as header termination)
            for line in rcvBuffer[:lastCRLFindex + 2].splitlines(True):
                httpHeaders += line
                if line == CRLF and httpHeaders[-2:] == CRLF:
                    return httpHeaders, rcvBuffer[2 + lastCRLFindex:]
            rcvBuffer = rcvBuffer[2 + lastCRLFindex:]

# Listen for and only return content from server
def getContent(rcvBuffer, cl, clientSocket):
    contentBuffer = rcvBuffer
    if len(contentBuffer) >= cl:
        return contentBuffer
    while True:
        content = clientSocket.recv(BYTES_TO_RECEIVE)
        if not content:
            continue
        contentBuffer += content
        if len(contentBuffer) >= cl:
            return contentBuffer

def getArguments():
    try:
        # Handle arguments from Commandline
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])
        file_name = sys.argv[3]
        return server_host, server_port, file_name
    except:
        print("""
                Wrong arguments. You have to give gour arguments i.e server_host, server_port, filename:
                For Example: python client.py localhost 8000 abcd.html
              """
        )
        sys.exit();

def main():
    server_host, server_port, file_name = getArguments()
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.settimeout(TIME_OUT_LIMIT)
        clientSocket.connect((server_host, server_port))
    except:
        print("Connection refused. Is the server up? Please Check")
        sys.exit();

    print ("Connected to " + server_host + ":" + str(server_port) + "\n")
    clientSocket.send(formRequestHeader(file_name))
    print("Request sent. Waiting for singhal's server response...\n")
    try:
        rcvBuffer = ""
        headers = ""
        headers, rcvBuffer = getHeaders(clientSocket)
        responseCode = headers.split()[1]
        if responseCode == '200':
            try:
                print("Response code 200 received: \n" + headers)
                content = getContent(rcvBuffer, getContentLength(headers), clientSocket)
                print content
            except timeout:
                # Timing out shouldn't happen, but if it does, continue anyways
                print "Sorry But Time out. Please Try again later."
        elif responseCode == '404':
            print("Response code 404 received: \n" + headers + getContent(rcvBuffer, getContentLength(headers), clientSocket) + "\n")
    except timeout:
        print("\nTimed out. Exiting")
    except (ValueError, IndexError):
        print("\nReceived malformed headers. Exiting")
    except KeyboardInterrupt:
        print("\n^C Detected. Terminating gracefully")
    finally:
        print("Client socket closed")
        clientSocket.close()

if __name__ == "__main__":
    main()
