"""
Vercel Serverless Function - Health Check
"""

import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "service": "x-tweet-bot",
            "version": "2.0"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
