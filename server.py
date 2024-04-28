from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import threading
import time

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
with SimpleXMLRPCServer(('localhost', 8000),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    # Global variables
    critical_section_held = False
    request_queue = []

    def request_critical_section(client_id, timestamp):
        global critical_section_held, request_queue

        print(f"Received request from Client {client_id} with timestamp {timestamp}")

        # Check if the critical section is held or if there are requests with higher priority
        if critical_section_held or (request_queue and (timestamp, client_id) > request_queue[0]):
            print(f"Client {client_id} added to request queue.")
            request_queue.append((timestamp, client_id))
            return False
        else:
            print(f"Client {client_id} granted access to critical section.")
            critical_section_held = True
            return True

    def release_critical_section(client_id, timestamp):
        global critical_section_held, request_queue

        print(f"Received release from Client {client_id}")

        # Release the critical section and grant access to the next client in the queue
        critical_section_held = False
        if request_queue:
            next_client_id = request_queue.pop(0)[1]
            print(f"Granting access to next client in queue: Client {next_client_id}")
            return True
        else:
            print("No clients in the queue.")
            return False

    server.register_function(request_critical_section, 'request_critical_section')
    server.register_function(release_critical_section, 'release_critical_section')

    print("Server is listening on port 8000...")
    # Run the server's main loop
    server.serve_forever()
