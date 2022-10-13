# Creating TCP servers in Python is just as easy as creating a client. You might 
# want to use your own TCP server when writing command shells or crafting a 
# proxy (both of which we’ll do later). Let’s start by creating a standard multi-
# threaded TCP server. Crank out the following code:

import socket
import threading

IP = "0.0.0.0"
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP,PORT)) #1 #binds the IP and PORT the sever should listen on
    server.listen(5) #2 #tells the server to start listening(with a max. backlog of connections set to 5.)
    print(f'[*] Listening on {IP}:{PORT}')

    while True: 
        client, address = server.accept() #3 #puts the server into its Main loop, where it waits for incoming connection.
        # When a client connects, we receive the client socket in the client variable and the remote connection details in the address variable.
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client,))# we then create a new thread object that points to our handle_client function, and we pass it the client socket object as an argument.
        client_handler.start() #4 #we then start the threadto handle the client connection, at which point the main server loop is ready to handle another incoming connection.

def handle_client(client_socket): #5 #The handle_client function performs the recv() and then sends a simple message back to the client.
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')

if __name__ == '__main__':
    main()

# if you use the TCP client that we built earlier, you can send some test packets to the server. you should see output like the following:
#[*] Listening on 0.0.0.0:9998
#[*] Accepted connection from: 127.0.0.1:62512
#[*] Received: ABCDEF

# That’s it! While pretty simple, this is a very useful piece of code. We’ll
# extend it in the next couple of sections, when we build a netcat replacement
# and a TCP proxy.