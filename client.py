"""
Chat Room Client script

This is a simple script that can be used as a chat room client.
Users input their usernames and send messages to a server.

Author:
Tihamer Aldana

"""

import socket
import threading
import utils as u


username = input('Welcome to the chat room! Please enter your username: ')


def create_socket():
    """
    Creates a new socket object using the AF_INET address family and SOCK_STREAM socket type.

    :return: a socket object
    """
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def receive_message():
    """
    Receive messages from the server.

    :return: None
    """
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == '@username':
                client.send(username.encode('utf-8'))
            else:
                print(message)
        except:
            print("The chat room is closed.")
            client.close()
            break


def write_message():
    """
    Sends user input as a message to the server.

    :return: None
    """
    while True:
        try:
            message = f'{username}: {input()}'
            client.send(message.encode('utf-8'))
        except UnicodeDecodeError:
            print("Invalid input.")


if __name__ == '__main__':
    host = u.HOST
    port = u.PORT
    client = create_socket()
    client.connect((host, port))

    thread = threading.Thread(target=receive_message)
    thread.start()

    msg = threading.Thread(target=write_message)
    msg.start()