import socket

target_host = "127.0.0.1" #localhost ip
target_port = 9997

#create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#SOCK_DGRAM: is used instead of a SOCK_STREAM

#send some data
client.sendto(b"AAABBBCCC",(target_host,target_port))
#client.sendto: instead of client.send; and then pass in the data and the server you want to send data to
#UDP is a connectionless protocol, there is no call to connect() beforehand

#receive some data
data, addr = client.recvfrom(4096)
#last step is to call recvfrom() to receive UDP data back.


print(data.decode())
#returnes both the data and the details of the remote host and port
client.close()