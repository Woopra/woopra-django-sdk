Track customers directly in the Django Web Framework using Woopra's Django SDK

The purpose of this SDK is to allow our customers who have servers running the Django Framework to track their users by writing only Python code. Tracking directly in Python will allow you to decide whether you want to track your users:
- through the front-end: after configuring the tracker, identifying the user, and tracking page views and events in Python, the SDK will generate the corresponding JavaScript code, and by passing this code to your view using a hook (examples will be shown below), you will be able to print that code in your view's header.
- through the back-end: after configuring the tracker & identifying the user, add the optional parameter true to the methods <code>track</code> or <code>push</code>, and the Python tracker will handle sending the data to Woopra by making HTTP Requests. By doing that, the client is never involved in the tracking process.

The first step is to setup the tracker SDK in your <code>views.py</code> file. For example, if you want to set up tracking with Woopra on your homepage, the file <code>views.py</code> should look like:
``` python
#import the SDK
import woopra_tracker

def homepage(request):
   woopra = woopra_tracker.WoopraTracker(request)
   woopra.config({'domain' : 'mybusiness.com'})

   # Your code here...

```
You can also customize all the properties of the woopra during that step by adding them to the config_dict. For example, to also update your idle timeout (default: 30 seconds):
``` python
# instead of:
woopra.config({'domain' : 'mybusiness.com'})
# directly write:
woopra.config({'domain' : 'mybusiness.com', 'idle_timeout' : 15000})
```
To add custom visitor properties, you should use the identify(user_dict) function:
``` python
woopra.identify({'email' : 'johndoe@mybusiness.com', 'name' : 'John Doe', 'company' : 'My Business'})
```
If you wish to identify a user without any tracking event, don't forget to push() the update to Woopra:
``` python
woopra.identify(user).push()
# or, to push through back-end:
woopra.identify(user).push(True)
```
If you wish to track page views, just call track():
``` python
woopra.track()
# Or, for back-end tracking:
woopra.track(True)
```
You can also track custom events through the front-end or the back-end. With all the previous steps done at once, your <code>views.py</code> file should look like:
``` python
import woopraTracker

def homepage(request):
   woopra = woopra_tracker.WoopraTracker(request)
   woopra.config(config_dict).identify(user_dict).track()
   # Track a custom event through the front end...
   woopra.track("play", {'artist' : 'Dave Brubeck', 'song' : 'Take Five', 'genre' : 'Jazz'})
   # ... and through the back end by passing the optional param True
   woopra.track('signup', {'company' : 'My Business', 'username' : 'johndoe', 'plan' : 'Gold'}, True)

   # Your code here...
   
   # When you're done setting up your WoopraTracker object, send a hook containing the value of
   # woopra.js_code() among all the other hooks you are passing to the template.
   response = render(request, 'homepage.html', {'woopra_code': woopra.js_code(), 'foo' : 'bar', })
   return response
```
and add the hook in your template's header (here <code>homepage.html</code>)
``` html
<!DOCTYPE html>
<html>
   <head>
      <!-- Your header here... -->
      <!-- Make sure to deactivate html auto-escaping -->
      {% autoescape off %}{{ woopra_code }}{% endautoescape %}
   </head>
   <body>
      <!-- Your body here... -->

   </body>
</html>
```
Finally, if you wish to track your users only through the back-end, you should set the cookie on your user's browser. However, if you are planning to also use front-end tracking, don't even bother with that step, the JavaScript tracker will handle it for you.
``` python
...
response = render(request, 'homepage.html', {'woopra_code': woopra.js_code(), 'foo' : 'bar', })
#Set the cookie after the response was rendered, and before sending any headers:
woopra.set_woopra_cookie(response)
return response
```