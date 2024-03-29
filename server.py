import sys
import math
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import xml.etree.ElementTree as ET
import phylib
import Physics
import os

# Constants
VEL_EPSILON = 0.0001
DRAG = 0.01

# Create an instance of the Game class with constructor arguments
game_instance = Physics.Game(gameID=None, gameName="Example", player1Name="Player1", player2Name="Player2")

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = self.path.split('?')[0]
        if parsed_path == '/':
            self.send_response(302)
            self.send_header('Location', '/shoot.html')
            self.end_headers()
        elif parsed_path == '/shoot.html':
            self.serve_file('shoot.html', 'text/html')
        elif parsed_path.startswith('/table-'):
            self.serve_svg(parsed_path)
        else:
            self.handle_not_found(parsed_path)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        if self.path == '/shoot':
            self.process_shoot_post(post_data)
        else:
            self.handle_not_found(self.path)

    def serve_file(self, file_path, content_type):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        with open(file_path, 'rb') as file:
            self.wfile.write(file.read())

    def serve_svg(self, parsed_path):
        table_number = parsed_path.split('-')[1]
        table_path = f"table-{table_number}.svg"
        if os.path.exists(table_path):
            self.serve_file(table_path, 'image/svg+xml')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes(f"404 Not Found: {parsed_path} does not exist", 'utf-8'))

    def handle_not_found(self, parsed_path):
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(bytes(f"404 Not Found: {parsed_path}", 'utf-8'))

    def process_shoot_post(self, post_data):
        post_data = json.loads(post_data.decode('utf-8'))  # Parse JSON data
        velocityX = float(post_data.get('velocityX', 0))
        velocityY = float(post_data.get('velocityY', 0))
        svg_data = post_data.get('svg', '')

        # Calculate speed
        speed = math.sqrt(velocityX ** 2 + velocityY ** 2)

        # Compute acceleration with drag
        if speed > VEL_EPSILON:
            acceleration_x = -velocityX / speed * DRAG
            acceleration_y = -velocityY / speed * DRAG
        else:
            acceleration_x = 0.0
            acceleration_y = 0.0

        # Parse SVG data
        tablee = self.parse_svg(svg_data)
        print("hello")
        print(tablee)
        # Perform shoot action in the game instance
        game_instance.shoot(gameName='Example' ,playerName='Player1', table=tablee, xvel=velocityX, yvel=velocityY)

        # Send response back to the client
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Shoot data received successfully')

    def parse_svg(self, svg_data):
        root = ET.fromstring(svg_data)

        table = Physics.Table()

        for elem in root.iter():
            # if elem.tag == '{http://www.w3.org/2000/svg}rect':
            #     x = float(elem.attrib.get('x', 0))
            #     y = float(elem.attrib.get('y', 0))
            #     width = float(elem.attrib.get('width', 0))
            #     height = float(elem.attrib.get('height', 0))
            #     if width > height:  # Assuming horizontal cushions
            #         table +=Physics.HCushion(y)
            #     if height > width:
            #         table += Physics.VCushion(x)
            if elem.tag == '{http://www.w3.org/2000/svg}circle':
                cx = float(elem.attrib.get('cx', 0))
                cy = float(elem.attrib.get('cy', 0))
                r = float(elem.attrib.get('r', 0))
                fill = elem.attrib.get('fill', '')
                # if r > 30:
                #     table += Physics.Hole(Physics.Coordinate(cx, cy))
                if r < 30:
                    if fill == 'white':
                            ball_number = 0
                            table += Physics.StillBall(0, Physics.Coordinate(cx, cy)) 
                    elif fill in Physics.BALL_COLOURS:
                        ball_number = Physics.BALL_COLOURS.index(fill)
                        table += Physics.StillBall(ball_number, Physics.Coordinate(cx, cy)) 
                        

        return table

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port number")
        sys.exit(1)

    httpd = HTTPServer(('localhost', port), MyHandler)
    print("Server listening on port:", port)
    httpd.serve_forever()
