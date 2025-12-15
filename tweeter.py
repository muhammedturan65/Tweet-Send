"""
X.com Tweet Module - Official Twitter API v2 with Tweepy
"""

import tweepy
import os


class XTweeter:
    """X.com için resmi API tabanlı tweet gönderici"""
    
    def __init__(self):
        """
        Environment variables:
            API_KEY: Twitter API Key
            API_SECRET: Twitter API Key Secret
            ACCESS_TOKEN: Twitter Access Token
            ACCESS_SECRET: Twitter Access Token Secret
        """
        self.api_key = os.environ.get("API_KEY")
        self.api_secret = os.environ.get("API_SECRET")
        self.access_token = os.environ.get("ACCESS_TOKEN")
        self.access_secret = os.environ.get("ACCESS_SECRET")
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            missing = []
            if not self.api_key: missing.append("API_KEY")
            if not self.api_secret: missing.append("API_SECRET")
            if not self.access_token: missing.append("ACCESS_TOKEN")
            if not self.access_secret: missing.append("ACCESS_SECRET")
            raise ValueError(f"Eksik environment variables: {', '.join(missing)}")
        
        # Tweepy Client (API v2)
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_secret
        )
        
    def send_tweet(self, text: str) -> dict:
        """Tweet gönder"""
        if len(text) > 280:
            text = text[:277] + "..."
            
        try:
            response = self.client.create_tweet(text=text)
            
            if response.data:
                tweet_id = response.data['id']
                return {"success": True, "tweet_id": tweet_id}
            else:
                return {"success": False, "error": "Tweet oluşturulamadı"}
                
        except tweepy.TweepyException as e:
            error_msg = str(e)
            
            # Common error handling
            if "duplicate" in error_msg.lower():
                return {"success": False, "error": "Bu tweet daha önce gönderilmiş (duplicate)"}
            elif "rate limit" in error_msg.lower():
                return {"success": False, "error": "Rate limit aşıldı, biraz bekleyin"}
            elif "403" in error_msg:
                return {"success": False, "error": "Erişim reddedildi - API izinlerini kontrol edin"}
            else:
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
