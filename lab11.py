import http.server as srv
import json
from gpiozero import AngularServo
import requests
from time import sleep

# Setup the servo
s = AngularServo(17, min_angle=-90, max_angle= 90)

# Serve the html page
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Servo Control</title>
<script>
function setup() {
    let slider = document.getElementById('slider')
    let feedback = document.getElementById('feedback')
    slider.oninput = async function () {
        feedback.textContent = 'Updating...'
        const angle = slider.value
        const timeoutId = setTimeout(function() {
            feedback.textContent = 'Failed!'
        }, 3000)
        const response = await fetch(`${window.location.href}endpoints/server/servo/${angle}`)
        const json_obj = await response.json()
        if (json_obj.response) {
            clearTimeout(timeoutId)
            feedback.textContent = 'Done!'
        }
    }
    slider.value = 0
}
</script>
</head>
<body onload="setup()">
<span>Select an angle:</span><br/>
<input type="range" min="0" max="1000" class="slider" id="slider" value="0"/> 
<br/>
<span id="feedback"></span>
</body>
</html>
"""

# Takes in the HTTP Request
class ExampleHandler(srv.BaseHTTPRequestHandler):
    """Runs everytime a get comes in"""
    def do_GET(self):
        if self.path.startswith('/endpoints/server/servo/'):	# Check If Path is Correct
            print(self.path)
            last_slash = self.path.rfind("/")	# Find the Last / in the path
            value = int(self.path[last_slash+1:])	# The value is after the last slash
            self.servo(value)	# Pass The Value To The Servo Function
            
        # Display The Index Page
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            self.send_error(404, 'Page not found')

    """Move The Servo With The Passed Value"""
    def servo(self, value):
        global s
        angle = value
    
        minimum, maximum = 0, 1000
        diff = maximum - minimum
        duty_cycle = ((angle - 500) / 500) * 90	# Ensure Value Is Between -90 and 90
        print(duty_cycle)
        
        # Change Angle Of Servo
        s.angle = duty_cycle
        value_sent = {"response": True}	# Send Back True
        
        # Send A Response Back To The Page
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        self.wfile.write(json.dumps(value_sent).encode())



location = ('', 8000) # use port 8080
server = srv.HTTPServer(location, ExampleHandler)
print(f'Serving on port {location[1]}')
server.serve_forever()
