from django.template import RequestContext, Context, loader
from django.http import HttpResponse
# from django.core import serializers

def myTemplate(name, request, extra_vars={}):
	t = loader.get_template(name)
	c = RequestContext(request, extra_vars)
	return t.render(c)

def home(request):
	return HttpResponse(myTemplate('home.html',request))

