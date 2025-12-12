import http.server as srv
import json
from gpiozero import AngularServo

from time import sleep

# s = AngularServo(17, min_angle=-90, max_angle= 90)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Servo control app</title>
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

class ExampleHandler(srv.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/endpoints/server/servo/'):
            print("hello")
            last_slash = self.path.rfind("/")
            self.value = self.path[last_slash+1:]
            result = int(self.value)
            print(result)
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            self.send_error(404, 'Page not found')


def servo():
    s.angle = 0.0



location = ('', 8000) # use port 8080
server = srv.HTTPServer(location, ExampleHandler)
print(f'Serving on port {location[1]}')
server.serve_forever()