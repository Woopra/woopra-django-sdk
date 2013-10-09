# -*- coding: utf-8 -*-

import string
import random
import json
import urllib
import httplib
from django.http import HttpRequest
from django.http import HttpResponse
import woopra_tracker

class WoopraTrackerDjango(woopra_tracker.WoopraTracker):
	"""
	Woopra Python SDK.
	This class represents the Python equivalent of the JavaScript Woopra Object.
	It is specific for use with the Django Web Framework
	"""
	
	def __init__(self, request):
		"""
		The constructor.
		Parameter:
			request - HttpRequest : The request sent by the user we want to track.
		Result:
			WoopraTracker
		"""

		woopra_tracker.WoopraTracker.__init__(self)

		self.request = request
		self.current_config["domain"] = self.request.META['HTTP_HOST']
		self.current_config["cookie_domain"] = self.request.META['HTTP_HOST']
		self.current_config["ip_address"] = self.get_client_ip()
		self.current_config["cookie_value"] = self.request.COOKIES.get(self.current_config["cookie_name"], self.random_cookie())
		self.current_config["user_agent"] = self.request.META['HTTP_USER_AGENT']
		self.current_config["current_url"] = request.get_full_path()

	def set_woopra_cookie(self, response):
		"""
		Sets the woopra cookie.
		Parameter:
			response - HttpResponse : The response in which the cookie should be set.
		Result:
			None
		"""
		response.set_cookie(self.current_config["cookie_name"], self.current_config["cookie_value"], 60*60*24*365*2)

	def get_client_ip(self):
		"""
		Get the IP address of the client:
		Parameter:
			None
		Result:
			ip - str : the IP address of the client
		"""
		x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = self.request.META.get('REMOTE_ADDR')
		return ip

	def actualize_cookie(self):
		"""
		If the cookie name changes, call this method to see if a cookie matches the new name, and update cookie_value.
		Parameter:
			None
		Result:
			None
		"""
		self.current_config["cookie_value"] = self.request.COOKIES.get(self.current_config["cookie_name"], self.current_config["cookie_value"])

