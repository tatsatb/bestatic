import http.server
import socketserver
import os
from datetime import datetime, timedelta

def bestatic_serv(*directory):
    PORT = 8080
    DIRECTORY = directory[0] if directory else "_output"

    class Handler(http.server.SimpleHTTPRequestHandler):
        extensions_map = {
            '': 'text/html',
            '.manifest': 'text/cache-manifest',
            '.html': 'text/html',
            '.png': 'image/png',
            '.jpg': 'image/jpg',
            '.svg': 'image/svg+xml',
            '.css': 'text/css',
            '.js': 'application/x-javascript',
            '.wasm': 'application/wasm',
            '.json': 'application/json',
            '.xml': 'application/xml',
        }        
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)

        def end_headers(self):
            self.send_my_headers()
            http.server.SimpleHTTPRequestHandler.end_headers(self)

        def send_my_headers(self):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            future = (datetime.utcnow() + timedelta(seconds=2))
            expires = future.strftime('%a, %d %b %Y %H:%M:%S GMT')
            self.send_header("Expires", expires)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Serving at port", PORT)
        print("Click http://localhost:8080 to visit the live website")
        print("Click Ctrl+C to shut down the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shutting down ...")
        finally:
            httpd.shutdown()

if __name__ == '__main__':
    bestatic_serv()
