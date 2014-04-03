from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from django.core import serializers
import subprocess, socket, os, time
from django.utils import simplejson

from controller.basic.models import *

# dictionary of sockets by address
sockets = {}

def get_pwm_sock(request, addr):
	try:
		s = sockets[addr]
		s.sendall("")
	except:
		s = init_pwm_sock(request, addr)
	return s

def init_pwm_sock(request, addr):
	# How do we talk to a PWM server
	pwm_server_sock = "/tmp/pwm_%d.sock" % addr
	pwm_server_args = ['/home/apwm/controller/pwm_server/pwm_server.py', pwm_server_sock, "%d" % addr]

	# Assume we can connect if the server happens to be running... otherwise start it
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		s.connect( pwm_server_sock )
	except:
		pid = subprocess.Popen(pwm_server_args, close_fds=True).pid
		# Wait for server to open its socket
		time.sleep(1)
		s.connect( pwm_server_sock )

		# Init controller based on stored values
		controller = PWMController.objects.get(i2c_address=addr)
		if controller:
			s.send("freq %d\n" % controller.frequency)
			s.recv(1024)

			# Init ports on controller based on stored values
			l = list(PWMPort.objects.filter( controller=controller ))
			for port in l:
				s.send("chan %d %d %d\n" % (port.port, port.low, port.high))
				s.recv(1024)

	# Store the socket for later use? (NB: may need to use django cache framework)
	sockets[addr] = s
	return s

def myTemplate(name, request, extra_vars={}):
	t = loader.get_template(name)
	c = RequestContext(request, extra_vars)
	return t.render(c)

def home(request):
	return HttpResponse(myTemplate('basic_home.html',request))

def add_port_dialog(request):
	return HttpResponse(myTemplate('add_port.html',request))

def get_port(request, port_id):
	l = list( PWMPort.objects.filter( pk=int(port_id) ) )
	return HttpResponse( serializers.serialize('json', l) )

def set_port(request, port_id, high, low):
	''' returns new port status '''
	p = PWMPort.objects.get( pk=int(port_id) )
	p.high = int(high)
	p.low = int(low)
	s = get_pwm_sock(request, p.controller.i2c_address)
	s.sendall("chan %d %d %d\n" % (p.port, p.low, p.high))
	## Avoid saving to sqlite constantly...
	# p.save()
	# l = list( PWMPort.objects.filter( pk=p.id ) )
	return HttpResponse( serializers.serialize('json',[p]) )

def get_port_list(request, controller_id):
	l = list(
		PWMPort.objects.filter(
			controller=PWMController.objects.get(pk=int(controller_id))
		))
	return HttpResponse( serializers.serialize('json', l) )

def get_controller_list(request):
	l = list( PWMController.objects.all() )
	return HttpResponse( serializers.serialize('json', l) )

def add_controller(request, description, i2c_bus, i2c_address, frequency):
	''' returns new controller list '''
	i2c_bus = int(i2c_bus)
	i2c_address = int(i2c_address)
	controller = PWMController( description=description, i2c_bus=i2c_bus, i2c_address=i2c_address, frequency=frequency )
	s = get_pwm_sock(request, p.controller.i2c_address)
	controller.save()
	l = list(PWMController.objects.all())
	return HttpResponse(serializers.serialize('json', l))

def add_port(request, controller_id, port, high, low):
	''' returns all ports for a specified controller '''
	controller = PWMController.objects.get( pk=int(controller_id) )
	port = PWMPort( controller=controller, port=int(port), high=int(high), low=int(low) )
	port.save()
	l = list(PWMPort.objects.filter( controller=controller ))
	return HttpResponse(serializers.serialize('json', l))

def remove_controller(request, controller_id):
	controller = PWMController.objects.get( pk=int(controller_id) )
	controller.delete()
	return HttpResponse( '' )

def remove_port(request, port_id):
	port = PWMPort.objects.get( pk=int(port_id) )
	port.delete()
	return HttpResponse( '' )

