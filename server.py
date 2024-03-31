"""
Author: Tihamer Aldana

This script is a chat server that uses sockets and threading to handle
multiple client connections concurrently. It provides functions for
creating and binding a server socket, broadcasting messages to all clients,
removing a client from the chat room, receiving incoming client connections,
handling messages received from a client, and writing a message and sending it
to all connected clients.

Example usage:

server_socket = create_socket()
bind_socket(server_socket, 'localhost', 5000)
server_socket.listen(5)
print('Server is running...')
receive_connections(server_socket)
"""

import socket
import threading
import time
import utils as u

from _socket import error

clients = []
user_names = []


def create_socket():
    """
    Create a socket.

    :return: The created socket.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return server_socket


def bind_socket(server_socket, _host, _port):
    """
    Binds the server socket to a specific host and port.

    :param server_socket: The server socket object.
    :param _host: The host address to bind to.
    :param _port: The port number to bind to.
    :return: None
    """
    while True:
        try:
            server_socket.bind((_host, _port))
            break
        except error as e:
            print(str(e))


def broadcast(message, _client):
    """
    :param message: The message to be broadcast to all clients.
    :param _client: The client object that should not receive the message.
    :return: None

    Broadcasts the given message to all clients except for the specified client object (_client). The message is sent
    using UTF-8 encoding.
    """
    for client in clients:
        if client != _client:
            client.send(message.encode('utf-8'))


def handle_messages(client):
    """
    Handles the messages received from a client.

    :param client: a socket representing the client connection
    :return: None
    """
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.__contains__('exit chat'):
                client.send('You have left the chat room!'.encode('utf-8'))
                remove_client(client, False)
                client.close()
                break
            else:
                broadcast(message, client)
        except (ConnectionResetError, ConnectionAbortedError) as e:
            print('Error occurred: ', e)
            # only remove client from list if it's still in the list.
            if client in clients:
                remove_client(client, True)
                client.close()
                time.sleep(5)
            break


def remove_client(client, is_left_error):
    """
    Remove a client from the chat.

    :param client: The client to be removed.
    :param is_left_error: Indicates whether the removal is due to an error or not.
    :return: None
    """
    index = clients.index(client)
    clients.remove(client)
    username = user_names[index]
    print(f'{username} left the chat')
    if not is_left_error:
        broadcast(f'{username} left the chat', client)
    user_names.remove(username)


def receive_connections(server):
    """
    :param server: The server socket object used to accept incoming connections.
    :return: None

    This method is responsible for receiving and handling incoming connections in a chat server. It continuously listens
    for new client connections and performs the necessary steps to add
    * the client to the chat room.

    The `server` parameter is the socket object used for accepting incoming connections.

    The method first accepts a new client connection and adds it to the `clients` list. It then sends a predefined
    message to the client to request their username, receives the username
    * from the client, and adds it to the `user_names` list.

    Next, it prints a message indicating that a new user has joined the chat along with their address.

    A separate thread is then started to handle incoming messages from the client, using the `handle_messages` function.
    Another thread is also started to handle writing messages to all
    * clients in the chat room, using the `write_message` function.

    If the number of clients in the chat room exceeds the allowed limit (3 in this case), the client is informed that
    the chat room is full and the connection is closed. Otherwise, a broadcast
    * message is sent to all clients indicating that the user has joined the chat.

    Finally, a series of initial welcome messages are sent to the client.

    To exit the chat, the user should type "exit chat".
    ```
    """
    while True:
        client, address = server.accept()
        clients.append(client)

        client.send('@username'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        user_names.append(username)

        print(f'{username} joined the chat with {str(address)}')

        thread = threading.Thread(target=handle_messages, args=(client,))
        thread.start()

        msg = threading.Thread(target=write_message, args=(clients,))
        msg.start()

        if len(clients) > 3:
            client.send('Chat room is full. Cannot accept more connections.'.encode('utf-8'))
            client.send(''.encode('utf-8'))
            client.close()
        else:
            broadcast(f'{username} joined the chat', client)

            client.send('You have joined the chat room!'.encode('utf-8'))
            client.send('Start chatting...'.encode('utf-8'))

            client.send('To exit, type "exit chat"'.encode('utf-8'))
            client.send('------------------------'.encode('utf-8'))
            client.send(''.encode('utf-8'))


def write_message(_clients):
    """
    Write a message and send it to all connected clients.

    :param _clients: A list of connected clients.
    :return: None

    Raises:
        UnicodeDecodeError: If invalid characters are entered.
    """
    while True:
        try:
            message = f'Server: {input()}'
            for client in _clients:
                client.send(message.encode('utf-8'))
        except UnicodeDecodeError:
            print("Invalid characters entered.")


if __name__ == '__main__':
    host = u.HOST
    port = u.PORT
    s = create_socket()
    bind_socket(s, host, port)
    s.listen(5)
    print('Server is running at %s:%s' % (host, port))
    print("You are the server, can't receive messages but you can send.")
    print("Waiting for clients...")
    receive_connections(s)
