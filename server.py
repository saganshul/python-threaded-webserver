#!/usr/bin/env python
import os, datetime
from socket import *

BYTES_TO_RECEIVE = 1024
SCRIPT_LOCATION = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SERVER_PORT = 8000

# Form the HTTP header response to be sent to the client
def formHeaderResponse():
    response = ("HTTP/1.1 200 TRUE\r\n\r\n")
    return response

# Form the HTTP response of the requested to be sent to the client
def webPageResponse(wpSize, wpName):
    responseHeader = ("HTTP/1.1 200 OK\r\n"
                "Date: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST")) + "\r\n"
                "Server: PySinghal/0.1\r\n"
                "Content-Length: " + str(wpSize) + "\r\n"
                "Content-Type: text/html\r\n"
                "Connection: Closed\r\n\r\n")
    return responseHeader

# Form the HTTP 404 response to be sent to the client
def serve404Response(filename, isGetRequest):
    html = ("<h1><center>Error 404: File not found!</h1><br>"
            "<center>You have requested for a non existing file: <b>" + filename[1:] + "</b><br><br>"
            "Please try another file</center>")

    response = ("HTTP/1.1 404 Not Found\r\n"
                "Date: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST")) + "\r\n"
                "Server: PySinghal/0.1\r\n"
                "Content-Length: " + str(len(html)) + "\r\n"
                "Content-Type: text/html\r\n"
                "Connection: Closed\r\n\r\n")
    if isGetRequest:
        return (response + html)
    else:
        return response

# Form the HTTP homepage response to be sent to the client
def HomePageResponse():
    html = ("<center><b><h1>Welcome!</h1></b><br>"
            "This web server is created by <b>Anshul Singhal</b><br><br>"
            "This is basic implementation of web server using python. Hope you will like it :)</center>")
    response = ("HTTP/1.1 200 OK\r\n"
                "Date: " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST")) + "\r\n"
                "Server: PySinghal/0.1\r\n"
                "Content-Length: " + str(html) + "\r\n"
                "Content-Type: text/html\r\n"
                "Connection: Closed\r\n\r\n")

    return (response + html)

def main():
    # Create a TCP Socket and bind it to port (Because this is web server not client)
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(('', SERVER_PORT))
    serverSocket.listen(10)

    print("Server is Up and Running")

    # Infinite loop to check the request from client
    try:
        while True:
            connectionSocket, addr = serverSocket.accept()
            request = connectionSocket.recv(BYTES_TO_RECEIVE)
            if not request:
                continue    # Basically to optimize the server

            # Get the request type and file
            try:
                requestType = request.split()[0]
                requestedFile = request.split()[1]
                # Only handle GET and HEAD request types
                if requestType != 'GET' and requestType != 'HEAD':
                    raise Exception;
                print("\nIncoming request:\n\n" + request)
            except:
                print("Malformed HTTP request; ignoring..") #Security so that none can hack the server only valid HTTP request will be served.
                continue

            # Server Home page on root request. This page is hard coded in code.
            if requestedFile == "/":
                connectionSocket.send(HomePageResponse())
                continue

            print("Requested file: " + requestedFile[1:])

            try:
                webPage = open(os.path.join(SCRIPT_LOCATION, requestedFile[1:]), 'r+')
                print(" FOUND AT " + SCRIPT_LOCATION)
                if requestType == 'GET':
                    webPageSize = os.path.getsize(os.path.join(SCRIPT_LOCATION, requestedFile[1:]))
                    connectionSocket.send(webPageResponse(webPageSize, requestedFile[1:]))
                    for block in iter(lambda: webPage.read(BYTES_TO_RECEIVE), ""):
                        connectionSocket.send(block)

                    print("Finished sending " + str(webPageSize) + "/" + str(webPageSize) + " bytes to client")
                else:
                    connectionSocket.send(formHeaderResponse())
                webPage.close()
            except IOError:
                # Send 404 response on not found of requested file.
                print("NOT FOUND at " + SCRIPT_LOCATION)
                connectionSocket.send(serve404Response(requestedFile, requestType == 'GET'))
            finally:
                connectionSocket.close()
    except KeyboardInterrupt:
        print("\n^C Some interrupt Detected: Terminating gracefully")
    finally:
        print("Server socket closed")
        serverSocket.close()

if __name__ == "__main__":
    main()
