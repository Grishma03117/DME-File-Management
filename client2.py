import xmlrpc.client
import time
import socket

# Server configuration
SERVER_HOST = "localhost"
SERVER_PORT = 8000

# Global variables
request_timestamp = 0
replied_processes = set()
access_granted = False

# Get the client address as a string
client_address = socket.gethostbyname(socket.gethostname())

# XML-RPC client
try:
    client = xmlrpc.client.ServerProxy(f"http://{SERVER_HOST}:{SERVER_PORT}", allow_none=True)
    print("Connected to server successfully")
except Exception as e:
    print(f"Error connecting to server: {e}")
    exit(1)

def send_request():
    global request_timestamp, replied_processes, access_granted
    
    print("Sending request...")

    request_timestamp = time.time()
    
    try:
        reply = client.request_critical_section(client_address, request_timestamp)
        print("Request sent successfully.")
    except Exception as e:
        print(f"Error sending request: {e}")
        return
    
    replied_processes.clear()
    replied_processes.add(reply)
    time.sleep(0.1)

def handle_reply(reply_message):
    global replied_processes, access_granted

    try:
        reply_parts = reply_message.split(' ')
        print('parts of reply ',reply_parts)
        reply_timestamp = int(float(reply_parts[0]))
        in_critical_section = reply_parts[1] == "True"

        if not in_critical_section and request_timestamp < reply_timestamp:
            access_granted = True
        elif request_timestamp > reply_timestamp:
            replied_processes.add(reply_message[:reply_message.index(" ")])
        
        if len(replied_processes) == 3 and access_granted:
            print("Access granted, writing to the file...")
            time.sleep(5)  # Simulate file writing
            client.release_critical_section(client_address)
            print("File writing completed, releasing critical section.")
            access_granted = False
    except Exception as e:
        print(f"Error in handle_reply: {e}")

# Client loop
while True:
    try:
        send_request()
        print('replied processes in main: ', replied_processes)
        
        # Check if "ENTER" is in replied_processes
        if "ENTER" in replied_processes:
            access_granted = True
            print("Access granted")
            
            replied_processes.remove("ENTER")  # Remove "ENTER" from replied_processes
        else:
            # Process other replies
            while replied_processes:
                reply = replied_processes.pop()
                handle_reply(reply)

        # Check if all replies have been received except "ENTER"
        if len(replied_processes) == 2 and access_granted:
            print("Writing to file...")
            time.sleep(5)  # Simulate file writing
            client.release_critical_section(client_address)
            print("File writing completed, releasing critical section.")
            access_granted = False
            
    except Exception as e:
        print(f"Error: {e}")
        break
