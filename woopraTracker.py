
from django.contrib.sites.models import Site

# coding: utf-8

"""
A Python SDK class for Woopra.
"""

# This class

class WoopraTracker:
	"A python c"
	def __init__(self, request):

		self.request = request
		

		#Get domain name
		current_site = Site.objects.get_current()
		current_site.domain



	def get_client_ip(self, request):
	    x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
	    if x_forwarded_for:
	        ip = x_forwarded_for.split(',')[0]
	    else:
	        ip = request.META.get('REMOTE_ADDR')
	    return ip