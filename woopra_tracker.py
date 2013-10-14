# -*- coding: utf-8 -*-

import urllib
import httplib
import hashlib

class WoopraTracker:
	"""
	Woopra Python SDK.
	This class represents the Python equivalent of the JavaScript Woopra Object.
	"""

	default_timeout = 300000
	EMAIL = "email"
	UNIQUE_ID = "unique_id"

	def __init__(self, domain):
		"""
		The constructor.
		Parameter:
			domain - str : the domain name of your website as submitted on woopra.com
		Result:
			WoopraTracker
		"""
		self.domain = domain
		self.idle_timeout = WoopraTracker.default_timeout
		self.user_properties = {}
		self.cookie_value = None
		self.user_agent = None
		self.ip_addresss = None

	def identify(self, identifier, value, user_properties = {}, ip_address = None, user_agent = None):
		"""
		Identifies a user.
		Parameters:
			identifier:
				WoopraTracker.EMAIL to identify the user with his email (will generate unique ID automatically with a hash of the email)
				WoopraTracker.UNIQUE_ID to identify the user with a unique ID directly
			value - str : the value of the identifier (email or unique ID)
			properties (optional) - dict : the user's additional properties (name, company, ...)
				key - str : the user property name
				value -str, int, bool = the user property value
			ip_address (optional) - str : the IP address of the user.
			user_agent (optional) - str : the value of the user_agent header
		"""
		if identifier == WoopraTracker.EMAIL:
			self.user_agent = user_agent
			self.ip_address = ip_address
			self.user_properties = user_properties
			self.user_properties["email"] = value
			m = hashlib.md5()
			m.update(value)
			long_cookie = m.hexdigest().upper()
			self.cookie_value = (long_cookie[:12]) if len(long_cookie) > 12 else long_cookie
		elif identifier == WoopraTracker.UNIQUE_ID:
			self.user_agent = user_agent
			self.ip_address = ip_address
			self.user_properties = user_properties
			self.cookie_value = value
		else:
			print "Wrong identifier. Accepted values are WoopraTracker.EMAIL or WoopraTracker.UNIQUE_ID"

	def track(self, event_name, event_data = {}):
		"""
		Tracks pageviews and custom events
		Parameters:
			event_name (optional) - str : The name of the event. If none is specified, will track pageview
			event_data (optional) - dict : Properties the custom event
				key - str : the event property name
				value - str, int, bool : the event property value
		Examples:
			# This code tracks a custom event through the back-end:
			woopra.track('signup', {'company' : 'My Business', 'username' : 'johndoe', 'plan' : 'Gold'})
		"""
		self.woopra_http_request(True, event_name, event_data)

	def push(self):
		"""
		Pushes the indentification information on the user to Woopra in case no tracking event occurs.
		Parameter:
			back_end_tracking (optional) - boolean : Should the information be pushed through the back-end? Defaults to False.
		Result:
			None
		"""
		self.woopra_http_request(False)

	def woopra_http_request(self, is_tracking, event_name = None, event_data = {}):
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
		get_params["host"] = self.domain
		get_params["cookie"] = self.cookie_value
		if self.ip_address != None:
			get_params["ip"] = self.ip_address
		if self.idle_timeout != None:
			get_params["timeout"] = self.idle_timeout

		# Identification
		for k, v in self.user_properties.iteritems():
			get_params["cv_" + k] = v

		if not is_tracking:
			url = "/track/identify/?" + urllib.urlencode(get_params)
		else:
			get_params["ce_name"] = event_name
			for k,v in event_data.iteritems():
				get_params["ce_" + k] = v
			url = "/track/ce/?" + urllib.urlencode(get_params)
		try:
			conn = httplib.HTTPConnection(base_url)
			if self.user_agent != None:
				conn.request("GET", url, headers={'User-agent': self.user_agent})
			else:
				conn.request("GET", url)
		except HTTPException:
			print "exception occured"
