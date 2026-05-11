from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error

# ==================== PAYSTACK CONFIGURATION ====================
# REPLACE WITH YOUR ACTUAL PAYSTACK SECRET KEY
# Get it from: https://dashboard.paystack.com/#/settings/developer
PAYSTACK_SECRET_KEY = "sk_test_db8bb39e4ef84a303b4bf63b7137a86a831fbc0e"  # Your test secret key

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
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        
        # Initialize payment endpoint
        if self.path == "/api/initialize-payment":
            try:
                # Parse request data
                data = json.loads(post_data.decode('utf-8'))
                email = data.get("email")
                amount = data.get("amount")
                
                print(f"📝 Payment request: {email} - ₦{amount}")
                
                # Prepare Paystack API request
                paystack_data = json.dumps({
                    "email": email,
                    "amount": amount * 100,  # Convert to kobo
                    "currency": "NGN",
                    "callback_url": "http://localhost:3000/callback"
                }).encode('utf-8')
                
                # Call Paystack API
                req = urllib.request.Request(
                    "https://api.paystack.co/transaction/initialize",
                    data=paystack_data,
                    headers={
                        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
                        "Content-Type": "application/json"
                    }
                )
                
                with urllib.request.urlopen(req) as response:
                    response_data = json.loads(response.read().decode('utf-8'))
                    
                    if response_data.get("status"):
                        auth_url = response_data["data"]["authorization_url"]
                        reference = response_data["data"]["reference"]
                        
                        print(f"✅ Payment initialized: {reference}")
                        print(f"🔗 Authorization URL: {auth_url}")
                        
                        # Send response back to frontend
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "authorization_url": auth_url,
                            "reference": reference
                        }).encode())
                    else:
                        raise Exception(response_data.get("message", "Unknown error"))
                
            except urllib.error.HTTPError as e:
                error_msg = e.read().decode('utf-8')
                print(f"❌ Paystack API Error: {error_msg}")
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Payment initialization failed"}).encode())
                
            except Exception as e:
                print(f"❌ Error: {e}")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        # Verify payment endpoint
        elif self.path == "/api/verify-payment":
            try:
                data = json.loads(post_data.decode('utf-8'))
                reference = data.get("reference")
                
                print(f"🔍 Verifying payment: {reference}")
                
                # Call Paystack verification API
                req = urllib.request.Request(
                    f"https://api.paystack.co/transaction/verify/{reference}",
                    headers={"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
                )
                
                with urllib.request.urlopen(req) as response:
                    response_data = json.loads(response.read().decode('utf-8'))
                    
                    if response_data.get("status"):
                        transaction = response_data["data"]
                        status = transaction["status"]
                        amount = transaction["amount"] / 100
                        
                        if status == "success":
                            print(f"✅ Payment verified: ₦{amount} from {transaction['customer']['email']}")
                            self.send_response(200)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({
                                "success": True,
                                "amount": amount,
                                "reference": reference,
                                "customer": transaction["customer"]
                            }).encode())
                        else:
                            print(f"❌ Payment not successful: {status}")
                            self.send_response(200)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": False, "error": f"Status: {status}"}).encode())
                    else:
                        raise Exception(response_data.get("message", "Verification failed"))
                
            except urllib.error.HTTPError as e:
                error_msg = e.read().decode('utf-8')
                print(f"❌ Verification API Error: {error_msg}")
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Verification failed"}).encode())
                
            except Exception as e:
                print(f"❌ Error: {e}")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
        
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
    
    def log_message(self, format, *args):
        print(f"📡 {args[0]}")

# ==================== START SERVER ====================
print("=" * 50)
print("💳 T Data Connect Payment Server")
print("=" * 50)
print(f"🔑 Paystack Key: {PAYSTACK_SECRET_KEY[:10]}...")
print("📍 Server running on http://localhost:3000")
print("🧪 Test: http://localhost:3000/test")
print("❤️ Health: http://localhost:3000/api/health")
print("=" * 50)
print("")

server = HTTPServer(("localhost", 3000), Handler)
server.serve_forever()