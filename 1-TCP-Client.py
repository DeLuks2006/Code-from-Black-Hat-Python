#TCP Client

# Countless times during penetration tests, we (the authors) have needed to 
# whip up a TCP client to test for services, send garbage data, fuzz, or per-
# form any number of other tasks. If you are working within the confines of 
# large enterprise environments, you won’t have the luxury of using network
# -ing tools or compilers, and sometimes you’ll even be missing the absolute 
# basics, like the ability to copy/paste or connect to the internet. This is 
# where being able to quickly create a TCP client comes in extremely handy. 
# But enough jabbering—let’s get coding. Here is a simple TCP client:

import socket

target_host = "0.0.0.0"
target_port = 9998

#create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
#AF_INET & SOCK_STREAM: creates a socket object
#AF_INET: idicates that we will use a standard IPv4 address or hostname
#SOCK_STREAM: indicates that this will be a TCP-Client 


#connect to client
client.connect((target_host,target_port))

#send some data (as bytes)
client.send(b"GET / HTTP/1.1\r\nHost: google.com \r\n\r\n")

#receive some data
response = client.recv(4096)

print(response.decode())
client.close() #closes the socket

# Caution: connection will not always succeed! 
# And the Server won't always expect you to send data first (some Servers expect to send Data to you first and await your response!)!
# Server may not always return Data to us in a timely fashion!

