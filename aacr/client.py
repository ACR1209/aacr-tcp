import socket
import json
from aacr.methods import VALID_METHODS

class Client:
    """
    This class is an utility class that allows to connect using AACR 
    (Adapted Application Communication and Routing) is used to send a message
    using sockets.

    The way to make a request is passing an object using the following structure:
    {"method": "GET", "uri": "/", "params": {"id": 1}}
    
    Raises:
        ConnectionError: If the value returned by the server is wrong assumes its compromised.
        ValueError: If the passed message is not a valid JSON
    """
    def __init__(self, host = '127.0.0.1', port = 5000 ) -> None:
        """
        Initializes the parameters to be used for the connection

        Args:
            host (str, optional): The address of the server. Defaults to '127.0.0.1'.
            port (int, optional): The port to connect to the server. Defaults to 5000.
        """
        self.host = host
        self.port = port

    def send_message(self, message: dict)->dict:
        """
        Sends a valid JSON object containing a valid AACR message.

        Args:
            message (dict): The message to be sent as JSON

        Raises:
            ValueError: If the message is not a valid AACR message
            ConnectionError: If the value returned from the server is not valid

        Returns:
            dict: The response from the server
        """
        if "method" not in message or message["method"] not in VALID_METHODS:
            raise ValueError(f"A valid method ({VALID_METHODS}) must be passed.")

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))  # Connect to the server
        client_socket.send(json.dumps(message).encode())  # Send the message to the server
        buffer = b''
        while True:
            response = client_socket.recv(1024)  # Receive the response from the server
            if not response:
                break
            buffer += response
        res: dict
        try: 
            res = json.loads(buffer.decode())
        except:
            raise ConnectionError(f"Invalid JSON recived from server at {self.host} on port {self.port}") 

        client_socket.close()
        return res
     
    def start_cli(self):
        """
        Starts a simple command line interface to interact with a AACR based server

        Raises:
            ValueError: if the message to be sent is not a valid JSON
        """
        while True:
            try: 
                message = input("Enter a message (or 'q' to exit): ")
                if message.lower() == 'q':
                    break
                res: dict
                try: 
                    res = json.loads(message)
                except:
                    raise ValueError(f"Invalid JSON passed as message") 

                print(self.send_message(res))
            except KeyboardInterrupt: 
                break
            except Exception as e:
                print(f"[ERROR] f{e}")



