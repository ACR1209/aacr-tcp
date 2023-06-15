import socket
import threading
import json
from aacr.methods import get, post, get_functions, post_functions, delete_functions, update_functions, VALID_METHODS
import signal
import os

PORT = 5000
HOST = '127.0.0.1'
MESSAGE_LIMIT = 30_000_000 # 10 MB 

# METHODS GO BEFORE SERVER START

@get("/")
def hello():
    return {"mesagge": "hello"}

@get("/p", {"id": str})
def hello_with_params(id: str):
    return {"message": "hello " + id}

@post("/p", {"id": str})
def hello_with_params(id: str):
    return {"message": "hello " + id}



class Server:
    """
    Hanldes a server using the protocol AACR (Adapted Application Communication and Routing) 
    """
    def __init__(self, host: str = HOST, port: int = PORT, buffer_size: int = MESSAGE_LIMIT)->None:
        """
        Create the server using the given host and port

        Args:
            host (str, optional): The host address, probably localhost. Defaults to HOST.
            port (int, optional): The port to make communications. Defaults to PORT.
            buffer_size (int, optional): The port to make communications. Defaults to PORT.
        """
        self.host = host
        self.port = port
        self.buffer_size = buffer_size

        # Creates a socket to allow connections
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.print_colored_text("[INFO] Server started on {}:{}".format(self.host, self.port), "blue")

    def start_server(self)->None:
        """
        Listens for connections and if one is adquired accepts it and handles it
        """
        while True:
            # Accept any connection incomming
            client_socket, client_address = self.server_socket.accept()
            self.print_colored_text("[INFO] Connected to {}:{}".format(client_address[0], client_address[1]), "blue")
            # Create a new thread to handle the client request
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def start(self)->None:
        """
            Intended way to start the server.
        """
        signal.signal(signal.SIGINT, self.exit_handler)
        # Create a thread for the server to run onto
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()
        while True:
            try:
           
                pass
            except KeyboardInterrupt:
                break

        self.print_colored_text("[INFO] Stopping the server...", "blue")
        server_thread.join()
        self.print_colored_text("[INFO] Server stopped.", "blue")

    def handle_client(self, client_socket: socket.socket)->None:
        """
        Handles a client request

        Args:
            client_socket (socket.socket): client socket where connection is made
        """
        while True:
            # Gets client's request
            data = self.get_data(client_socket)
            try:
                # Parses the data into JSON
                data_json = json.loads(data.decode())

                # If no data passed or an invalid method passed, return an error
                if not data_json or "method" not in data_json or data_json["method"] not in VALID_METHODS:
                    self.send_response(client_socket, {"errorCode": "400", "error": "Method not found"})
                    break

                # Get the method and the endpoint to be hit, default to /
                requested_method = data_json["method"]
                requested_uri = data_json.get("uri", "/")

                # Python switch xd
                method_functions = {
                    "GET": get_functions,
                    "POST": post_functions,
                    "UPDATE": update_functions,
                    "DELETE": delete_functions
                }

                # Execute the request in the correct method
                if requested_method in method_functions:
                    self.execute_request(client_socket, method_functions[requested_method], data_json, requested_uri)

                break
            except TypeError as e:
                # This means the method called had errors in the parameters passed
                self.send_response(client_socket, {"errorCode": "400", "error": str(e)})
                break
            except Exception as e:
                # Error parsing JSON or any other
                self.send_response(client_socket, {"errorCode": "500", "error": str(e)})
                break

        client_socket.close()
        self.print_colored_text("[INFO] Disconnected from client, request succeded", "blue")

    def get_data(self, client_socket: socket.socket)->bytes:
        """
        Gets the data recived from a socket.

        Args:
            client_socket (socket.socket): socket connection to the client

        Returns:
            (bytes): the recovered data from the connection 
        """
        client_socket.settimeout(3)

        try:
            # Retrive request send by the client
            data = client_socket.recv(self.buffer_size)  # Adjust the buffer size as needed
        except socket.timeout:
            data = b''

        return data

    def exit_handler(self, signal, frame)->None:
        """
        Gracefully closes the program
        """
        self.print_colored_text("[INFO] Closing server...", "red")
        os._exit(0)

    def send_response(self, client_socket: socket.socket, response: dict)->None:
        """
        Sends a JSON response to the client.

        Args:
            client_socket (socket.socket): a socket where the client is connected
            response (dict): a response object. 
        """
        response_json = json.dumps(response)
        client_socket.send(response_json.encode())

    def execute_request(self, client_socket: socket.socket, method_functions: dict, data: dict, requested_uri: str)->None:
        """
        Executes the request asked by the client, using the know methods functions.

        Args:
            client_socket (socket.socket): socket to client connection.
            method_functions (dict): the valid functions declared.
            data (dict): the "body" of the request.
            requested_uri (str): the endpoint being hit.
        """

        # If the endpoint does not exist return an error
        if requested_uri not in method_functions:
            self.print_colored_text(f"{data['method']} {requested_uri}  404 Element not found", "red")
            self.send_response(client_socket, {"errorCode": "404", "error": "Element not found"})
            return

        # Execute the function with or without params acording to the case
        if "params" not in data:
            self.send_response(client_socket, method_functions[requested_uri]())
        else:
            self.send_response(client_socket, method_functions[requested_uri](**data["params"]))
        self.print_colored_text(f"{data['method']} {requested_uri}  Success", "green")
    
    def print_colored_text(self, text, color):
        colors = {
            'black': '30',
            'red': '31',
            'green': '32',
            'yellow': '33',
            'blue': '34',
            'magenta': '35',
            'cyan': '36',
            'white': '37'
        }
        
        color_code = colors.get(color.lower())
        if color_code is None:
            raise ValueError(f"Invalid color: {color}")
        
        print(f"\033[{color_code}m{text}\033[0m")
