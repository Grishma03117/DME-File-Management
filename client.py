import xmlrpc.client
import threading
import time
import random

class RicartAgrawalaClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.server = xmlrpc.client.ServerProxy('http://localhost:8000')

    def request_critical_section(self):
        print(f"Client {self.client_id} is requesting critical section...")
        timestamp = time.time()
        response = self.server.request_critical_section(self.client_id, timestamp)
        if response:
            print(f"Client {self.client_id} has entered critical section.")
            time.sleep(random.uniform(1, 3))  # Simulate work in the critical section
            print(f"Client {self.client_id} has left critical section.")
            self.server.release_critical_section(self.client_id, timestamp)
        else:
            print(f"Client {self.client_id} is waiting in the queue.")

if __name__ == "__main__":
    num_clients = 3
    clients = []

    for i in range(num_clients):
        client = RicartAgrawalaClient(i)
        clients.append(client)
        threading.Thread(target=client.request_critical_section).start()
