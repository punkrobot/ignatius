#!/usr/bin/env python3
"""
Simple HTTP server to serve the chat web application
Run with: python server.py
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Change to webapp directory
    webapp_dir = Path(__file__).parent
    os.chdir(webapp_dir)
    
    with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
        print(f"Serving chat app at http://localhost:{PORT}")
        print("Make sure the Ignatius API is running on http://localhost:5001")
        print("Press Ctrl+C to stop the server")
        
        # Open browser automatically
        try:
            webbrowser.open(f"http://localhost:{PORT}")
        except:
            pass
            
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()