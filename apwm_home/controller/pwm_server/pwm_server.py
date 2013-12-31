#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
import argparse
import socket,os
from multiprocessing import Process

cli_args = argparse.ArgumentParser( description="Listen on a socket for pwm commands" )
cli_args.add_argument('socket', metavar='socket', help='unix socket path')
cli_args.add_argument('address', metavar='i2c_address', help='i2c address')
cli_args = cli_args.parse_args()

serv_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
  os.remove( cli_args.socket )
except OSError:
  pass

class PWMSocketServer:

  def __init__(self, *args, **kwargs):
    self.pwm = PWM(*args, **kwargs)
    self.accept_commands = {
      'chan': self.cmd_chan,
      'freq': self.cmd_freq,
      'sleep': self.cmd_sleep,
    }

  def debug(self, str):
    print "DEBUG: ", str

  def interpret(self,conn,data):
    for n in data.splitlines(True):
      if '\n' in n:
        b = n.index(' ')
        try:
          cmd = self.accept_commands[ n[:b] ]
          cmd(n[b:])
          conn.send(n)
          self.debug(n)
        except KeyError:
          conn.send('invalid command: ' + n[0:b])
      else:
        self.debug("incomplete line: " + n)
        return n
    return ''

  def cmd_chan(self, args):
    args = args.split()
    self.pwm.setPWM(
      int(args[0]),
      int(args[1]),
      int(args[2]),
      )

  def cmd_freq(self, args):
    args = args.split()
    self.pwm.setPWMFreq(int(args[0]))

  def cmd_sleep(self, args):
    args = args.split()
    time.sleep(int(args[0]))

  def sock(self, sock):
    serv_sock.bind( cli_args.socket )
    serv_sock.listen(1)
    data = ''
    def iter_conn(s):
      while 1:
        yield serv_sock.accept()

    for (conn,address) in iter_conn(serv_sock):
      data = ''
      while 1:
        data += conn.recv(1024)
        if not data:
          break
        if '\n' in data:
          data = self.interpret(conn,data)
      conn.close()

# PWM board access
pwm = PWMSocketServer(0x40, debug=False)
pwm.sock( cli_args.socket )

