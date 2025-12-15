"""
Vercel Serverless Function - Tweet Endpoint
Cron job ile çağrılarak random söz paylaşır
"""

import json
import random
import os
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Check environment variables first
            import os
            auth_token = os.environ.get("AUTH_TOKEN")
            ct0 = os.environ.get("CT0")
            
            if not auth_token or not ct0:
                missing = []
                if not auth_token:
                    missing.append("AUTH_TOKEN")
                if not ct0:
                    missing.append("CT0")
                self._send_response(500, {
                    "success": False,
                    "error": f"Environment variables eksik: {', '.join(missing)}. Vercel Dashboard > Settings > Environment Variables'dan ekleyin."
                })
                return
            
            # Import here to avoid cold start issues
            from tweeter import XTweeter
            
            # Load quotes
            quotes_path = os.path.join(os.path.dirname(__file__), '..', 'quotes.json')
            with open(quotes_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            quotes = data.get('quotes', [])
            if not quotes:
                self._send_response(400, {"error": "No quotes found"})
                return
            
            # Random quote seç
            quote = random.choice(quotes)
            tweet_text = f'"{quote["text"]}" — {quote["author"]}'
            
            # Tweet gönder
            tweeter = XTweeter()
            result = tweeter.send_tweet(tweet_text)
            
            if result.get("success"):
                self._send_response(200, {
                    "success": True,
                    "tweet_id": result.get("tweet_id"),
                    "quote": tweet_text
                })
            else:
                self._send_response(500, {
                    "success": False,
                    "error": result.get("error")
                })
                
        except Exception as e:
            self._send_response(500, {"error": str(e)})
    
    def _send_response(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
