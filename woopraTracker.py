#-*- coding: utf-8 -*-

import string
import random
import json
import urllib
import httplib
from django.http import HttpRequest
from django.http import HttpResponse

class WoopraTracker:
	"""
	Woopra Python SDK.
	This class represents the Python equivalent of the JavaScript Woopra Object.
	"""

	DEFAULT_CONFIG = {
		"domain" : "", 
		"cookie_name" : "wooTracker",
		"cookie_domain" : "",
		"cookie_path" : "/",
		"ping" : True,
		"ping_interval" : 12000,
		"idle_timeout" : 300000,
		"download_tracking" : True,
		"outgoing_tracking" : True,
		"download_pause" : 200,
		"outgoing_pause" : 400,
		"ignore_query_url" : True,
		"hide_campaign" : False,
		"ip_address" : "",
		"cookie_value" : ""
	}


	def __init__(self, request):

		self.request = request

		self.current_config = WoopraTracker.DEFAULT_CONFIG
		self.custom_config = {}

		self.user = {}
		self.events = []
		
		self.current_config["domain"] = self.request.META['HTTP_HOST']
		self.current_config["cookie_domain"] = self.request.META['HTTP_HOST']
		self.current_config["ip_address"] = self.get_client_ip()

		self.user_up_to_date = True
		self.has_pushed = False

		self.current_config["cookie_value"] = request.COOKIES.get(self.current_config["cookie_name"], self.random_cookie())


	def woopra_http_request(self, is_tracking, event = None):
		"""
		Sends an Http Request to Woopra for back-end identification and/or tracking.
		This method takes 2 parameters:
		- isTracking : is this request supposed to track an event or just identify the user?
		- event (optional - only matters if isTracking = True) : the event to pass. Default is pageview.
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

		if(is_tracking == False):
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

	def woopra_code(self):
		"""
		This method returns the woopra code string to be passed to the Template, and outputed in its header.
		"""
		code = '\n   <!-- Woopra code starts here -->\n   <script>\n      (function(){\n      var t,i,e,n=window,o=document,a=arguments,s="script",r=["config","track","identify","visit","push","call"],c=function(){var t,i=this;for(i._e=[],t=0;r.length>t;t++)(function(t){i[t]=function(){return i._e.push([t].concat(Array.prototype.slice.call(arguments,0))),i}})(r[t])};for(n._w=n._w||{},t=0;a.length>t;t++)n._w[a[t]]=n[a[t]]=n[a[t]]||new c;i=o.createElement(s),i.async=1,i.src="//static.woopra.com/js/w.js",e=o.getElementsByTagName(s)[0],e.parentNode.insertBefore(i,e)\n      })("woopra");\n'
		if (len(self.custom_config) != 0):
			code += "      woopra.config(" + json.dumps(self.custom_config) + ");\n"
		if (self.user_up_to_date == False):
			code += "      woopra.identify(" + json.dumps(self.user) + ");\n"
		if (len(self.events) != 0):
			for event in self.events:
				code += "      woopra.track('" + event[0] + "', " + json.dumps(event[1]) + ");\n"
		if (self.has_pushed == True):
			code += "      woopra.push();\n"
		code += "   </script>\n   <!-- Woopra code ends here -->\n"
		return code


	def config(self, data):
		"""
		Configure WoopraTracker Object.
		This method takes one parameter:
		data : a dictionary where :
			key = the configuration option
			value = the configuration value
		Example:
		config({'domain' : 'mywebsite.com', 'ping' : True})
		"""
		for k, v in data.iteritems():
			if k in WoopraTracker.DEFAULT_CONFIG:
				self.current_config[k] = v
				if (k != "ip_address" and k != "cookie_value"):
					self.custom_config[k] = v
				if (k == "cookie_name"):
					self.current_config["cookie_value"] = request.COOKIES.get(self.current_config["cookie_name"], self.current_config["cookie_value"])
		return self




	def identify(self, user):
		"""
		Identifies the user currently being tracked.
		This method takes two parameters:
		user : a dictionary where :
			key = the configuration option
			value = the configuration value
		Example:
		config({'domain' : 'mywebsite.com', 'ping' : True})
		"""
		self.user = user
		self.user_up_to_date = False
		return self

	def track(self, event_name = None, event_data = None, back_end_tracking = False):
		"""
		Identifies the user currently being tracked.
		This method takes two optional parameters:
		user : a dictionary where :
			key = the configuration option
			value = the configuration value
		Example:
		config({'domain' : 'mywebsite.com', 'ping' : True})
		"""
		if back_end_tracking:
			self.woopra_http_request(True, [event_name, event_data])
		else:
			self.events += [[event_name, event_data]]
		return self


	def push(self, back_end_tracking = False):
		"""
		Pushes the indentification information on the user to Woopra in case no tracking event occurs.
		Parameters:
			back_end_tracking (optional) - boolean : Should the information be pushed through the back-end? Defaults to False.
		Result:
			None
		"""
		if (self.user_up_to_date == False):
			if back_end_tracking:
				self.woopra_http_request(False)
			else:
				self.has_pushed = True

	def set_woopra_cookie(self, response):
		response.set_cookie(self.current_config["cookie_name"], self.current_config["cookie_value"], 60*60*24*365*2)

	def random_cookie(self):
		return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(12))

	def get_client_ip(self):
		x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = self.request.META.get('REMOTE_ADDR')
		return ip
