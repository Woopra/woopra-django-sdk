# coding: utf-8
import string
import random

from django.http import HttpRequest
from django.http import HttpResponse

from django.contrib.sites.models import Site


class WoopraTracker:
	"""
	Woopra Python SDK.
	This class represents the PHP equivalent of the JavaScript Woopra Object.
	"""

	DEFAULT_CONFIG = {
		"domain" : "", 
		"cookie_name" : "wooTracker",
		"cookie_domain" : "",
		"cookie_path" : "/",
		"ping" : true,
		"ping_interval" : 12000,
		"idle_timeout" : 300000,
		"download_tracking" : true,
		"outgoing_tracking" : true,
		"download_pause" : 200,
		"outgoing_pause" : 400,
		"ignore_query_url" : true,
		"hide_campaign" : false,
		"ip_address" : "",
		"cookie_value" : ""
	}


	def __init__(self, request, response):

		self.request = request
		self.response = response

		self.trackerReady = False

		self.currentConfig = WoopraTracker.DEFAULT_CONFIG
		
		self.currentConfig["domain"] = Site.objects.get_current().domain
		self.currentConfig["cookie_domain"] = Site.objects.get_current().domain
		self.currentConfig["ip_address"] = getClientIp(request)

		self.userUpToDate = True

		self.currentConfig["cookie_value"] = request.COOKIES.get(self.currentConfig["cookie_name"], self.randomCookie())


	def setWoopraCookie(self):
		

	def randomCookie(self):
		return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(12))

	def getClientIp(self, request):
		x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		return ip
