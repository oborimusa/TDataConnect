from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Test endpoint
        if self.path == "/test":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Server is working!")
        
        # Health check endpoint
        elif self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps({"status": "OK", "message": "Server is running"})
            self.wfile.write(response.encode())
        
        # Root endpoint
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"T Data Connect Payment Server is running")
        
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 - Endpoint not found")
    
    def do_POST(self):
        if self.path == "/api/initialize-payment":
            try:
                length = int(self.headers["Content-Length"])
                data = self.rfile.read(length)
                print("Payment received:", data)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                response = json.dumps({
                    "authorization_url": "https://paystack.com/pay/test"
                })
                self.wfile.write(response.encode())
                print("Payment URL sent")
            except Exception as e:
                print(f"Error: {e}")
                self.send_response(500)
                self.end_headers()
        
        elif self.path == "/api/verify-payment":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = json.dumps({"success": True, "amount": 1000})
            self.wfile.write(response.encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"Request: {args[0]}")

print("=" * 50)
print("T Data Connect Payment Server")
print("=" * 50)
print("Server running on http://localhost:3000")
print("Test: http://localhost:3000/test")
print("Health: http://localhost:3000/api/health")
print("=" * 50)

server = HTTPServer(("localhost", 3000), Handler)
server.serve_forever()