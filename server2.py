import socketserver
import threading
from xmlrpc.server import SimpleXMLRPCServer
from collections import deque

# Global variables
request_queue = deque()
clients = {}
critical_section_held = False
current_timestamp = 0

# XML-RPC server
class Server(SimpleXMLRPCServer):
    def __init__(self, addr):
        self.allow_reuse_address = True
        super().__init__(addr, bind_and_activate=False)
        self.server_bind()
        self.server_activate()

    def broadcast(self, message, sender_addr):
        for client_addr, client_id in clients.items():
            if client_addr != sender_addr:
                self.send_reply(client_addr, message)

    def send_reply(self, client_addr, message):
        clients[client_addr].send_reply(message)

    def request_critical_section(self, client_addr, timestamp):
        global critical_section_held, current_timestamp

        print(f"Received request from {client_addr} with timestamp {timestamp}")
        reply_message = f"{current_timestamp} {critical_section_held}"
        self.broadcast(reply_message, client_addr)

        if not critical_section_held:
            print("Critical section is not held")
            if not request_queue:
                print("Request queue is empty")
            else:
                print(f"Oldest request timestamp in queue: {request_queue[0][0]}")

            if not request_queue or timestamp < request_queue[0][0]:
                print(f"Granting access to {client_addr} with timestamp {timestamp}")
                critical_section_held = True
                current_timestamp = timestamp
                self.send_reply(client_addr, "ENTER")
            else:
                print(f"Adding {client_addr} with timestamp {timestamp} to request queue")
                request_queue.append((timestamp, client_addr))
        else:
            print(f"Critical section is held by {current_timestamp}")

        print(f"Current request queue: {request_queue}")

        return reply_message

    def release_critical_section(self, client_addr):
        global critical_section_held

        print(f"Received release from {client_addr}")
        critical_section_held = False
        if request_queue:
            timestamp, next_client = request_queue.popleft()
            current_timestamp = timestamp
            self.send_reply(next_client, "ENTER")
            critical_section_held = True

        return "OK"

if __name__ == "__main__":
    # Server setup
    server_addr = ("localhost", 8000)
    server = Server(server_addr)
    print(f"Server listening on {server_addr[0]}:{server_addr[1]}")
    server.register_instance(server)
    server.register_function(server.request_critical_section, "request_critical_section")
    server.register_function(server.release_critical_section, "release_critical_section")

    try:
        # Serve forever in the main function
        print("Press Ctrl+C to stop the server")
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down the server...")
        server.server_close()
        print("Server stopped")