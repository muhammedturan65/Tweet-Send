"""
X.com Tweet Module - Vercel Serverless Functions için
"""

import requests
import os


class XTweeter:
    """X.com için cookie tabanlı tweet gönderici"""
    
    GRAPHQL_URL = "https://twitter.com/i/api/graphql/znq7jUAqRjmPj7IszLem5Q/CreateTweet"
    
    BASE_HEADERS = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "content-type": "application/json",
        "origin": "https://twitter.com",
        "referer": "https://twitter.com/compose/tweet",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-twitter-active-user": "yes",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "tr"
    }
    
    def __init__(self, auth_token: str = None, ct0: str = None):
        """
        Args:
            auth_token: X.com auth_token cookie (veya AUTH_TOKEN env var)
            ct0: X.com ct0 cookie (veya CT0 env var)
        """
        self.auth_token = auth_token or os.environ.get("AUTH_TOKEN")
        self.ct0 = ct0 or os.environ.get("CT0")
        
        if not self.auth_token or not self.ct0:
            raise ValueError("AUTH_TOKEN ve CT0 gerekli!")
        
        self.session = requests.Session()
        self._setup_session()
        
    def _setup_session(self):
        """Session'ı cookie ve header'larla ayarla"""
        for domain in [".x.com", ".twitter.com"]:
            self.session.cookies.set("auth_token", self.auth_token, domain=domain)
            self.session.cookies.set("ct0", self.ct0, domain=domain)
        
        headers = self.BASE_HEADERS.copy()
        headers["x-csrf-token"] = self.ct0
        self.session.headers.update(headers)
        
    def send_tweet(self, text: str) -> dict:
        """Tweet gönder"""
        if len(text) > 280:
            text = text[:277] + "..."
            
        payload = {
            "variables": {
                "tweet_text": text,
                "dark_request": False,
                "media": {
                    "media_entities": [],
                    "possibly_sensitive": False
                },
                "semantic_annotation_ids": [],
                "disallowed_reply_options": None
            },
            "features": {
                "communities_web_enable_tweet_community_results_fetch": True,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "creator_subscriptions_quote_tweet_preview_enabled": False,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "articles_preview_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "rweb_tipjar_consumption_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_enhance_cards_enabled": False
            },
            "queryId": "znq7jUAqRjmPj7IszLem5Q"
        }
        
        try:
            response = self.session.post(
                self.GRAPHQL_URL,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and "create_tweet" in result["data"]:
                    tweet_result = result["data"]["create_tweet"]["tweet_results"]["result"]
                    tweet_id = tweet_result.get("rest_id", "unknown")
                    return {"success": True, "tweet_id": tweet_id}
                elif "errors" in result:
                    return {"success": False, "error": result['errors']}
                else:
                    return {"success": False, "error": "Unexpected response"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
