from datetime import UTC, datetime, timedelta

import tweepy


class XClient:
    def __init__(self, access_token: str):
        self.client = tweepy.Client(bearer_token=access_token)

    def create_tweet(self, text: str):
        return self.client.create_tweet(user_auth=False, text=text)

    def get_user_tweets(self, user_id: str, max_results: int = 10):
        return self.client.get_users_tweets(user_id, max_results=max_results)

    def get_tweets_past_hour(self):
        one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
        one_hour_ago_str = one_hour_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

        tweets = self.client.search_recent_tweets(
            user_auth=False,
            query="*",
        )
        return tweets
