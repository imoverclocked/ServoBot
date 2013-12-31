#!/usr/bin/python

import argparse
import socket,os

cli_args = argparse.ArgumentParser( description="Connect to a socket to send a pwm command" )
cli_args.add_argument('socket', metavar='socket', help='unix socket path')
cli_args = cli_args.parse_args()

client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client_sock.connect( cli_args.socket )
client_sock.send("freq 1000\n")
print client_sock.recv(1024)
client_sock.send("chan 0 0 2048\n")
print client_sock.recv(1024)
client_sock.send("chan 1 0 2\n")
print client_sock.recv(1024)
client_sock.send("chan")
client_sock.send(" 2")
client_sock.send(" 0")
client_sock.send(" 1")
client_sock.send("\n")
print client_sock.recv(1024)
client_sock.close()

