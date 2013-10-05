#-*- coding: utf-8 -*-

import string
import random
import json
import urllib
import httplib

class WoopraTracker:
	"""
	Woopra Python SDK.
	This class represents the Python equivalent of the JavaScript Woopra Object.
	"""

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
		"cookie_value" : ""
	}


	def __init__(self):
		"""
		The constructor.
		Parameter:
			None
		Result:
			WoopraTracker
		"""

		self.current_config = WoopraTracker.DEFAULT_CONFIG
		self.custom_config = {}

		self.user = {}
		self.events = []

		self.user_up_to_date = True
		self.has_pushed = False


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
			else:
				get_params["ce_name"] = event[0]
				for k,v in event[1].iteritems():
					get_params["ce_" + k] = v
			url = "/track/ce/?" + urllib.urlencode(get_params)

		try:
			conn = httplib.HTTPConnection(base_url)
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
		if (len(self.custom_config) != 0):
			code += "      woopra.config(" + json.dumps(self.custom_config) + ");\n"
		if not self.user_up_to_date:
			code += "      woopra.identify(" + json.dumps(self.user) + ");\n"
		if (len(self.events) != 0):
			for event in self.events:
				code += "      woopra.track('" + event[0] + "', " + json.dumps(event[1]) + ");\n"
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
				if (k != "ip_address" and k != "cookie_value"):
					self.custom_config[k] = v
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

