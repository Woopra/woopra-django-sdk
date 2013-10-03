#-*- coding: utf-8 -*-

import string
import random
import json
import urllib

from django.http import HttpRequest
from django.http import HttpResponse
import httplib

from django.contrib.sites.models import Site


class WoopraTracker:
	"""
	Woopra Python SDK.
	This class represents the PHP equivalent of the JavaScript Woopra Object.
	"""

	DEFAULT_CONFIG = {
		"domain" : "", 
		"cookieName" : "wooTracker",
		"cookieDomain" : "",
		"cookiePath" : "/",
		"ping" : True,
		"pingInterval" : 12000,
		"idleTimeout" : 300000,
		"downloadTracking" : True,
		"outgoingTracking" : True,
		"downloadPause" : 200,
		"outgoingPause" : 400,
		"ignoreQueryUrl" : True,
		"hideCampaign" : False,
		"ipAddress" : "",
		"cookieValue" : ""
	}


	def __init__(self, request):

		self.request = request

		self.trackerReady = False

		self.currentConfig = WoopraTracker.DEFAULT_CONFIG
		self.customConfig = {}

		self.user = {}
		self.events = []
		
		self.currentConfig["domain"] = self.request.META['HTTP_HOST']
		self.currentConfig["cookieDomain"] = self.request.META['HTTP_HOST']
		self.currentConfig["ipAddress"] = self.getClientIp(request)

		self.userUpToDate = True
		self.hasPushed = False

		self.currentConfig["cookieValue"] = request.COOKIES.get(self.currentConfig["cookieName"], self.randomCookie())


	def woopraHttpRequest(self, isTracking, event = None):
		"""
		Sends an Http Request to Woopra for back-end identification and/or tracking.
		This method takes 2 parameters:
		- isTracking : is this request supposed to track an event or just identify the user?
		- event (optional - only matters if isTracking = True) : the event to pass. Default is pageview.
		"""
		baseUrl = "www.woopra.com"
		getParams = {}

		# Configuration
		getParams["host"] = self.currentConfig["domain"]
		getParams["cookie"] = self.currentConfig["cookieValue"]
		getParams["ip"] = self.currentConfig["ipAddress"]
		getParams["timeout"] = self.currentConfig["idleTimeout"]

		# Identification
		for k, v in self.user.iteritems():
			getParams["cv_" + k] = v

		if(isTracking == False):
			url = "/track/identify/?" + urllib.urlencode(getParams)
		else:
			if(event == None):
				getParams["ce_name"] = "pv"
				getParams["ce_url"] = request.get_full_path()
			else:
				getParams["ce_name"] = event[0]
				for k,v in event[1].iteritems():
					getParams["ce_" + k] = v
			url = "/track/ce/?" + urllib.urlencode(getParams)

		userAgent = {'User-agent': self.request.META['HTTP_USER_AGENT']}
		conn = httplib.HTTPConnection(baseUrl)
		conn.request("GET", url, headers=userAgent)

	def woopraCode(self):
		"""
		This method returns the woopra code string to be passed to the Template, and outputed in its header.
		"""
		code = '\n   <!-- Woopra code starts here -->\n   <script>\n      (function(){\n      var t,i,e,n=window,o=document,a=arguments,s="script",r=["config","track","identify","visit","push","call"],c=function(){var t,i=this;for(i._e=[],t=0;r.length>t;t++)(function(t){i[t]=function(){return i._e.push([t].concat(Array.prototype.slice.call(arguments,0))),i}})(r[t])};for(n._w=n._w||{},t=0;a.length>t;t++)n._w[a[t]]=n[a[t]]=n[a[t]]||new c;i=o.createElement(s),i.async=1,i.src="//static.woopra.com/js/w.js",e=o.getElementsByTagName(s)[0],e.parentNode.insertBefore(i,e)\n      })("woopra");\n'
		if (len(self.customConfig) != 0):
			code += "      woopra.config(" + json.dumps(self.customConfig) + ");\n"
		if (self.userUpToDate == False):
			code += "      woopra.identify(" + json.dumps(self.user) + ");\n"
		if (len(self.events) != 0):
			for event in self.events:
				code += "      woopra.track('" + event[0] + "', " + json.dumps(event[1]) + ");\n"
		if (self.hasPushed == True):
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
			if k in self.DEFAULT_CONFIG:
				self.currentConfig[k] = v
				if (k != "ipAddress" and k != "cookieValue"):
					self.customConfig[k] = v
				if (k == "cookieName"):
					self.currentConfig["cookieValue"] = request.COOKIES.get(self.currentConfig["cookieName"], self.currentConfig["cookieValue"])




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
		self.userUpToDate = False

	def track(self, eventName = None, eventData = None, backEndTracking = False):
		"""
		Identifies the user currently being tracked.
		This method takes two optional parameters:
		user : a dictionary where :
			key = the configuration option
			value = the configuration value
		Example:
		config({'domain' : 'mywebsite.com', 'ping' : True})
		"""
		if backEndTracking:
			self.woopraHttpRequest(True, [eventName, eventData])
		else:
			self.events += [[eventName, eventData]]


	def push(self, backEndTracking = False):
		"""
		Pushes the indentification information on the user to Woopra in case no tracking event occurs.
		Parameters:
			backEndTracking (optional) - boolean : Should the information be pushed through the back-end? Defaults to False.
		Result:
			None
		"""
		if (self.userUpToDate == False):
			if backEndTracking:
				self.woopraHttpRequest(False)
			else:
				self.hasPushed = True

	def setWoopraCookie(self, response):
		response.set_cookie(self.currentConfig["cookieName"], self.currentConfig["cookieValue"], 60*60*24*365*2)

	def randomCookie(self):
		return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(12))

	def getClientIp(self, request):
		x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		return ip
