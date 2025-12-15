"""
Vercel Serverless Function - Quotes Info Endpoint
"""

import json
import os
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            quotes_path = os.path.join(os.path.dirname(__file__), '..', 'quotes.json')
            with open(quotes_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            quotes = data.get('quotes', [])
            
            response = {
                "total": len(quotes),
                "sample": quotes[0] if quotes else None
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
