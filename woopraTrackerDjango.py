#-*- coding: utf-8 -*-

import string
import random
import json
import urllib
import httplib
from django.http import HttpRequest
from django.http import HttpResponse
import woopraTracker

class WoopraTrackerDjango(woopraTracker.WoopraTracker):
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

		woopraTracker.WoopraTracker.__init__(self)

		self.request = request
		self.current_config["domain"] = self.request.META['HTTP_HOST']
		self.current_config["cookie_domain"] = self.request.META['HTTP_HOST']
		self.current_config["ip_address"] = self.get_client_ip()
		self.current_config["cookie_value"] = request.COOKIES.get(self.current_config["cookie_name"], self.random_cookie())


	def woopra_http_request(self, is_tracking, event = None):
		"""
		Sends an Http Request to Woopra for back-end identification and/or tracking.
		Parameters:
			isTracking - boolean : is this request supposed to track an event or just identify the user?
			event (optional) - dict : only matters if isTracking == True. The event to pass. Default is None.
		Result:
			None
		"""
		base_url = "www.woopra.com"
		get_params = {}

		# Configuration
		get_params["host"] = self.current_config["domain"]
		get_params["cookie"] = self.current_config["cookie_value"]
		get_params["ip"] = self.current_config["ip_address"]
		get_params["timeout"] = self.current_config["idle_timeout"]

		# Identification
		for k, v in self.user.iteritems():
			get_params["cv_" + k] = v

		if not is_tracking:
			url = "/track/identify/?" + urllib.urlencode(get_params)
		else:
			if(event == None):
				get_params["ce_name"] = "pv"
				get_params["ce_url"] = request.get_full_path()
			else:
				get_params["ce_name"] = event[0]
				for k,v in event[1].iteritems():
					get_params["ce_" + k] = v
			url = "/track/ce/?" + urllib.urlencode(get_params)

		user_agent = {'User-agent': self.request.META['HTTP_USER_AGENT']}
		try:
			conn = httplib.HTTPConnection(base_url)
			conn.request("GET", url, headers=user_agent)
		except HTTPException:
			print "exception occured"


	def config(self, data):
		"""
		Configure WoopraTracker Object.
		Parameter:
			data - dict :
				key - str : the configuration option
				value - str, int, bool : the configuration value
		Result:
			WoopraTracker
		Example:
			config({'domain' : 'mywebsite.com', 'ping' : True})
		"""
		for k, v in data.iteritems():
			if k in WoopraTrackerDjango.DEFAULT_CONFIG:
				self.current_config[k] = v
				if (k != "ip_address" and k != "cookie_value"):
					self.custom_config[k] = v
				if (k == "cookie_name"):
					self.current_config["cookie_value"] = request.COOKIES.get(self.current_config["cookie_name"], self.current_config["cookie_value"])
		return self


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
