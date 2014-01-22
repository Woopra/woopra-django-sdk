# -*- coding: utf-8 -*-

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
	It is specific for use with the Django Web Framework
	"""

	SDK_ID = "django"
	# Default Configuration Dictionary
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
		"cookie_value" : "",
		"user_agent" : "",
		"current_url" : ""
	}
	
	def __init__(self, request):
		"""
		The constructor.
		Parameter:
			request - HttpRequest : The request sent by the user we want to track.
		Result:
			WoopraTracker
		"""

		self.current_config = WoopraTracker.DEFAULT_CONFIG
		self.custom_config = {"app" : WoopraTracker.SDK_ID}

		self.user = {}
		self.events = []

		self.user_up_to_date = True
		self.has_pushed = False

		self.request = request
		self.current_config["domain"] = self.request.META['HTTP_HOST']
		self.current_config["cookie_domain"] = self.request.META['HTTP_HOST']
		self.current_config["ip_address"] = self.get_client_ip()
		self.current_config["cookie_value"] = self.request.COOKIES.get(self.current_config["cookie_name"], self.random_cookie())
		self.current_config["user_agent"] = self.request.META['HTTP_USER_AGENT']
		self.current_config["current_url"] = request.get_full_path()

	def woopra_http_request(self, is_tracking, event = None):
		"""
		Sends an Http Request to Woopra for back-end identification and/or tracking.
		Parameters:
			isTracking - boolean : is this request supposed to track an event or just identify the user?
			event (optional) - dict : only matters if isTracking == True. The event to pass. Default is None.
		Result:
			None
		"""
		if self.current_config["domain"] == "":
			return
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
			url = "/track/identify/?" + urllib.urlencode(get_params) + "&ce_app=" + WoopraTracker.SDK_ID
		else:
			if event[0] == None:
				get_params["ce_name"] = "pv"
				if not self.current_config["current_url"] == "":
					get_params["ce_url"] = self.current_config["current_url"]
			else:
				get_params["ce_name"] = event[0]
				for k,v in event[1].iteritems():
					get_params["ce_" + k] = v
			url = "/track/ce/?" + urllib.urlencode(get_params) + "&ce_app=" + WoopraTracker.SDK_ID

		user_agent = self.request.META['HTTP_USER_AGENT']
		try:
			conn = httplib.HTTPConnection(base_url)
			if not user_agent == "":
				conn.request("GET", url, headers={'User-agent': user_agent})
			else:
				conn.request("GET", url)
		except HTTPException:
			print "exception occured"

	def js_code(self):
		"""
		This method returns the woopra code string to be passed to the Template, and outputed in its header.
		Parameters:
			None
		Result:
			code - str : The front-end tracking code.
		"""
		code = '\n   <!-- Woopra code starts here -->\n   <script>\n      (function(){\n      var t,i,e,n=window,o=document,a=arguments,s="script",r=["config","track","identify","visit","push","call"],c=function(){var t,i=this;for(i._e=[],t=0;r.length>t;t++)(function(t){i[t]=function(){return i._e.push([t].concat(Array.prototype.slice.call(arguments,0))),i}})(r[t])};for(n._w=n._w||{},t=0;a.length>t;t++)n._w[a[t]]=n[a[t]]=n[a[t]]||new c;i=o.createElement(s),i.async=1,i.src="//static.woopra.com/js/w.js",e=o.getElementsByTagName(s)[0],e.parentNode.insertBefore(i,e)\n      })("woopra");\n'
		if len(self.custom_config) != 0:
			code += "      woopra.config(" + json.dumps(self.custom_config) + ");\n"
			self.custom_config = {}
		if not self.user_up_to_date:
			code += "      woopra.identify(" + json.dumps(self.user) + ");\n"
			self.user_up_to_date = True
		if len(self.events) != 0:
			for event in self.events:
				if event[0] == None:
					code += "      woopra.track();\n"
				else:
					code += "      woopra.track('" + event[0] + "', " + json.dumps(event[1]) + ");\n"
			self.events = []
		if self.has_pushed:
			code += "      woopra.push();\n"
		code += "   </script>\n   <!-- Woopra code ends here -->\n"
		return code

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
			if k in WoopraTracker.DEFAULT_CONFIG:
				self.current_config[k] = v
				if k != "ip_address" and k != "cookie_value":
					self.custom_config[k] = v
					if k == "cookie_name":
						self.actualize_cookie
		return self

	def identify(self, user):
		"""
		Identifies the user currently being tracked.
		Parameters:
			user - dict :
				key - str : the user property name
				value -str, int, bool = the user property value
		Example:
			identify({'email' : 'johndoe@mybusiness.com', 'name' : 'John Doe', 'company' : 'My Business'})
		"""
		self.user = user
		self.user_up_to_date = False
		return self

	def track(self, event_name = None, event_data = None, back_end_tracking = False):
		"""
		Tracks pageviews and custom events
		Parameters:
			event_name (optional) - str : The name of the event. If none is specified, will track pageview
			event_data (optional) - dict : Properties the custom event
				key - str : the event property name
				value - str, int, bool : the event property value
			back_end_tracking (optional) - bool : Should this event be tracked through the back-end?
		Examples:
			# Track a pageview through the front-end:
			track()
			# Track a pageview through the back-end:
			track(True)
			# Track a custom event through the front-end:
			woopra.track("play", {'artist' : 'Dave Brubeck', 'song' : 'Take Five', 'genre' : 'Jazz'})
			# Track a custom event through the back-end:
			woopra.track('signup', {'company' : 'My Business', 'username' : 'johndoe', 'plan' : 'Gold'}, True)
		"""
		if back_end_tracking:
			self.woopra_http_request(True, [event_name, event_data])
		else:
			self.events += [[event_name, event_data]]
		return self

	def push(self, back_end_tracking = False):
		"""
		Pushes the indentification information on the user to Woopra in case no tracking event occurs.
		Parameter:
			back_end_tracking (optional) - boolean : Should the information be pushed through the back-end? Defaults to False.
		Result:
			None
		"""
		if not self.user_up_to_date:
			if back_end_tracking:
				self.woopra_http_request(False)
			else:
				self.has_pushed = True

	def random_cookie(self):
		"""
		Generates a random 12 characters (Capital Letters and Numbers)
		Parameter:
			None
		Result:
			None
		"""
		return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(12))

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