Track customers directly in the Django Web Framework using Woopra's Django SDK

The SDK can be used both for front-end and back-end tracking. In either cases, the first step is to setup the tracker SDK in your <code>views.py</code> file. For example, if you want to set up tracking with Woopra on your homepage, the file <code>views.py</code> should look like:
``` python
#import the SDK
import woopra_tracker

def homepage(request):
   woopra = woopraTracker.WoopraTracker(request)
   woopra.config({'domain' : 'mybusiness.com'})

   # Your code here...
   
   # When you're done setting up your WoopraTracker object, send a hook containing the value of
   # woopra.woopraCode() among all the other hooks you are passing to the template.
   response = render(request, 'homepage.html', {'woopra_code': woopra.woopraCode(), 'foo' : 'bar', })
   #Set the cookie after the response was rendered, and before sending any headers
   woopra.setWoopraCookie(response)
   return response
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
If you wish to track page views, just call track():
``` python
woopra.track()
# Or, for back-end tracking:
woopra.track(true)
```
You can also track custom events through the front-end or the back-end. With all the previous steps done at once, your <code>views.py</code> file should look like:
``` python
import woopraTracker

def homepage(request):
   woopra = woopraTracker.WoopraTracker(request)
   woopra.config(config_dict).identify(user_dict).track()
   # Track a custom event through the front end...
   woopra.track("play", {'artist' : 'Dave Brubeck', 'song' : 'Take Five', 'genre' : 'Jazz'})
   # ... and through the back end by passing the optional param True
   woopra.track('signup', {'company' : 'My Business', 'username' : 'johndoe', 'plan' : 'Gold'}, True)

   # Your code here...
   
   response = render(request, 'homepage.html', {'woopra_code': woopra.woopraCode(), 'foo' : 'bar', })
   woopra.setWoopraCookie(response)
   return response
```
and add the hook in your template's header (here <code>homepage.html</code>)
``` html
<!DOCTYPE html>
<html>
   <head>
      <!-- Your header here... -->
      {{ woopra_code }}
   </head>
   <body>
      <!-- Your body here... -->

   </body>
</html>
```
If you identify the user after the last tracking event, don't forget to push() the update to Woopra:
``` python
woopra.identify(user).push()
# or, to push through back-end:
woopra.identify(user).push(True)
```
