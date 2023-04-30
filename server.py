import http.server
import socketserver
import json
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['motor']
collection = db['palabras']

# Define the request handler
class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Display the contents of the database
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            palabras = collection.find()
            html = "<html><body><table>"
            html += "<tr><th>URL</th><th>palabras 1</th><th>Count 1</th><th>Rank 1</th><th>palabras 2</th><th>Count 2</th><th>Rank 2</th><th>palabras 3</th><th>Count 3</th><th>Rank 3</th></tr>"
            for palabras in palabras:
                html += "<tr>"
                html += f"<td>{palabras['url']}</td>"
                for w, c, r in palabras['palabras']:
                    html += f"<td>{w}</td><td>{c}</td><td>{r}</td>"
                html += "</tr>"
            html += "</table></body></html>"
            self.wfile.write(html.encode())
        else:
            # Serve static files
            super().do_GET()

# Start the server
port = 8000
with socketserver.TCPServer(("", port), MyRequestHandler) as httpd:
    print(f"Serving at port {port}")
    httpd.serve_forever()