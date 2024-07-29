def bestatic_serv(*directory):
    import http.server
    import socketserver

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
            self.send_header("Expires", "0")

        # def do_GET(self):
        #     if self.path == '/':
        #         self.path = '/index.html'
        #     return Handler.do_GET(self)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Serving at port", PORT)
        print("Click http://localhost:8080 to visit the live website")
        print("Click Ctrl+C to shut down the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server shutting down ...")
            httpd.shutdown()
            httpd.server_close()

    return None


if __name__ == '__main__':
    bestatic_serv()
