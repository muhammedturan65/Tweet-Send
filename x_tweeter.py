"""
X.com (Twitter) Tweet Automation Bot
Cookie tabanlı kimlik doğrulama ile tweet gönderme
API kullanmadan doğrudan web arayüzü üzerinden çalışır
"""

import requests
import json
import random
import time
import logging
import sys
import io
from datetime import datetime
from pathlib import Path

# Windows için UTF-8 encoding ayarı
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tweet_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class XTweeter:
    """X.com için cookie tabanlı tweet gönderici"""
    
    # X.com GraphQL endpoint'i - Güncel
    GRAPHQL_URL = "https://twitter.com/i/api/graphql/znq7jUAqRjmPj7IszLem5Q/CreateTweet"
    
    # Gerekli headers
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
    
    def __init__(self, auth_token: str, ct0: str):
        """
        Args:
            auth_token: X.com auth_token cookie değeri
            ct0: X.com ct0 cookie değeri (CSRF token)
        """
        self.auth_token = auth_token
        self.ct0 = ct0
        self.session = requests.Session()
        self._setup_session()
        
    def _setup_session(self):
        """Session'ı cookie ve header'larla ayarla"""
        # Cookie'leri ayarla - hem x.com hem twitter.com için
        for domain in [".x.com", ".twitter.com"]:
            self.session.cookies.set("auth_token", self.auth_token, domain=domain)
            self.session.cookies.set("ct0", self.ct0, domain=domain)
        
        # Header'ları ayarla
        headers = self.BASE_HEADERS.copy()
        headers["x-csrf-token"] = self.ct0
        self.session.headers.update(headers)
        
    def send_tweet(self, text: str) -> dict:
        """
        Tweet gönder
        
        Args:
            text: Tweet metni (max 280 karakter)
            
        Returns:
            API yanıtı (dict)
        """
        if len(text) > 280:
            logger.warning(f"Tweet 280 karakteri aşıyor ({len(text)} karakter), kırpılacak")
            text = text[:277] + "..."
            
        # GraphQL payload - Güncellenmiş
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
            
            logger.info(f"📡 API Yanıt Kodu: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and "create_tweet" in result["data"]:
                    tweet_result = result["data"]["create_tweet"]["tweet_results"]["result"]
                    tweet_id = tweet_result.get("rest_id", "unknown")
                    logger.info(f"✅ Tweet başarıyla gönderildi! ID: {tweet_id}")
                    logger.info(f"   Tweet: {text[:50]}...")
                    return {"success": True, "tweet_id": tweet_id, "response": result}
                elif "errors" in result:
                    logger.error(f"❌ API Hatası: {result['errors']}")
                    return {"success": False, "error": result['errors'], "response": result}
                else:
                    logger.error(f"❌ Beklenmeyen API yanıtı: {result}")
                    return {"success": False, "error": "Unexpected response", "response": result}
            elif response.status_code == 403:
                logger.error("❌ Erişim reddedildi (403). Cookie'ler geçersiz olabilir.")
                return {"success": False, "error": "Access Denied - Cookie expired?", "response": response.text}
            else:
                logger.error(f"❌ HTTP Hatası: {response.status_code}")
                logger.error(f"   Yanıt: {response.text[:500]}")
                return {"success": False, "error": f"HTTP {response.status_code}", "response": response.text}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ İstek hatası: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def verify_auth(self) -> bool:
        """Cookie'lerin geçerli olup olmadığını kontrol et"""
        try:
            # Güncel doğrulama endpoint'i
            verify_url = "https://twitter.com/i/api/1.1/account/settings.json"
            response = self.session.get(verify_url, timeout=10)
            
            logger.info(f"📡 Doğrulama yanıt kodu: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get("screen_name", "Unknown")
                logger.info(f"✅ Kimlik doğrulama başarılı! Kullanıcı: @{username}")
                return True
            elif response.status_code == 403:
                logger.error("❌ Cookie'ler geçersiz veya süresi dolmuş!")
                return False
            else:
                logger.warning(f"⚠️ Doğrulama atlanıyor (HTTP {response.status_code}), tweet göndermeyi deneyeceğiz...")
                return True  # Devam et, tweet gönderirken göreceğiz
                
        except Exception as e:
            logger.error(f"❌ Doğrulama hatası: {str(e)}")
            logger.info("⚠️ Doğrulama atlanıyor, tweet göndermeyi deneyeceğiz...")
            return True  # Yine de dene


class TweetScheduler:
    """Tweet zamanlayıcı"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.tweets = self._load_tweets()
        self.tweeter = None
        self.tweet_index = 0
        
    def _load_config(self) -> dict:
        """Konfigürasyonu yükle"""
        if not self.config_path.exists():
            logger.error(f"❌ Konfigürasyon dosyası bulunamadı: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _load_tweets(self) -> list:
        """Tweet listesini yükle"""
        tweets_file = Path(self.config.get("tweets_file", "tweets.txt"))
        
        if not tweets_file.exists():
            logger.error(f"❌ Tweet dosyası bulunamadı: {tweets_file}")
            raise FileNotFoundError(f"Tweets file not found: {tweets_file}")
            
        with open(tweets_file, "r", encoding="utf-8") as f:
            tweets = [line.strip() for line in f if line.strip()]
            
        logger.info(f"📝 {len(tweets)} tweet yüklendi")
        return tweets
    
    def _is_within_hours(self) -> bool:
        """Şu anki saat çalışma saatleri içinde mi?"""
        settings = self.config.get("settings", {})
        start_hour = settings.get("start_hour", 0)
        end_hour = settings.get("end_hour", 24)
        
        current_hour = datetime.now().hour
        return start_hour <= current_hour < end_hour
    
    def _get_next_tweet(self) -> str:
        """Sıradaki tweet'i al"""
        if not self.tweets:
            return None
            
        tweet = self.tweets[self.tweet_index]
        self.tweet_index = (self.tweet_index + 1) % len(self.tweets)
        return tweet
    
    def start(self):
        """Zamanlayıcıyı başlat"""
        cookies = self.config.get("cookies", {})
        auth_token = cookies.get("auth_token")
        ct0 = cookies.get("ct0")
        
        if not auth_token or not ct0 or auth_token.startswith("BURAYA"):
            logger.error("❌ Cookie bilgileri eksik! config.json dosyasını düzenleyin.")
            return
            
        self.tweeter = XTweeter(auth_token, ct0)
        
        # Kimlik doğrulama
        if not self.tweeter.verify_auth():
            logger.error("❌ Kimlik doğrulama başarısız! Cookie'leri kontrol edin.")
            return
            
        settings = self.config.get("settings", {})
        interval = settings.get("interval_minutes", 60)
        random_delay = settings.get("random_delay_minutes", 5)
        
        logger.info("🚀 Tweet botu başlatıldı!")
        logger.info(f"   Aralık: {interval} dakika (+/- {random_delay} dakika rastgele)")
        
        while True:
            try:
                if not settings.get("enabled", True):
                    logger.info("⏸️ Bot devre dışı, bekleniyor...")
                    time.sleep(60)
                    continue
                    
                if not self._is_within_hours():
                    logger.info("🌙 Çalışma saatleri dışında, bekleniyor...")
                    time.sleep(300)  # 5 dakika bekle
                    continue
                
                # Tweet gönder
                tweet = self._get_next_tweet()
                if tweet:
                    logger.info(f"📤 Tweet gönderiliyor...")
                    result = self.tweeter.send_tweet(tweet)
                    
                    if not result.get("success"):
                        logger.warning("⚠️ Tweet gönderilemedi, bir sonraki deneme için bekleniyor...")
                
                # Sonraki tweet için bekle
                delay = interval + random.randint(-random_delay, random_delay)
                delay_seconds = max(delay * 60, 60)  # Minimum 1 dakika
                
                logger.info(f"⏰ Sonraki tweet: {delay} dakika sonra")
                time.sleep(delay_seconds)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot durduruldu (Ctrl+C)")
                break
            except Exception as e:
                logger.error(f"❌ Beklenmeyen hata: {str(e)}")
                time.sleep(60)


def send_single_tweet(text: str, config_path: str = "config.json"):
    """Tek bir tweet gönder (test için)"""
    config_path = Path(config_path)
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    cookies = config.get("cookies", {})
    auth_token = cookies.get("auth_token")
    ct0 = cookies.get("ct0")
    
    if not auth_token or not ct0:
        print("❌ Cookie bilgileri eksik!")
        return
        
    tweeter = XTweeter(auth_token, ct0)
    
    if tweeter.verify_auth():
        result = tweeter.send_tweet(text)
        return result
    else:
        print("❌ Kimlik doğrulama başarısız!")
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Komut satırından tweet gönder
        tweet_text = " ".join(sys.argv[1:])
        print(f"📤 Tweet gönderiliyor: {tweet_text}")
        send_single_tweet(tweet_text)
    else:
        # Zamanlayıcıyı başlat
        scheduler = TweetScheduler()
        scheduler.start()
