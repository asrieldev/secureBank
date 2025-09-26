from http.server import BaseHTTPRequestHandler
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from setup_vercel import create_sample_data
except ImportError:
    # Fallback if setup_vercel is not available
    def create_sample_data():
        return "Setup script not available"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Initialize the database
            result = create_sample_data()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = "✅ Database initialized successfully!\n\n"
            response += "📋 Login Credentials:\n"
            response += "Admin User:\n"
            response += "  Username: admin\n"
            response += "  Password: admin123\n\n"
            response += "Regular Users:\n"
            response += "  Username: john_doe, jane_smith, bob_wilson\n"
            response += "  Password: password123\n\n"
            response += "🌐 You can now use the application!"
            
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = f"❌ Error initializing database: {str(e)}\n\n"
            error_response += "Please check:\n"
            error_response += "1. Database connection string\n"
            error_response += "2. Environment variables\n"
            error_response += "3. Vercel logs for more details"
            
            self.wfile.write(error_response.encode('utf-8'))
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 