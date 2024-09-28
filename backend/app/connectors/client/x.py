import asyncio
import tweepy
from app.models.integrations.x import Tweet, XSendTweetRequest
from functools import partial

class XClient:
    def __init__(self, access_token: str):
        self.client = tweepy.Client(bearer_token=access_token)

    async def send_tweet(self, request: XSendTweetRequest) -> Tweet:
        loop = asyncio.get_event_loop()
        create_tweet_partial = partial(self.client.create_tweet, text=request.text, user_auth=False)
        response = await loop.run_in_executor(None, create_tweet_partial)
        return Tweet.model_validate(response.data)

    # def get_user_tweets(self, user_id: str, max_results: int = 10):
    #     return self.client.get_users_tweets(user_id, max_results=max_results)

    # def get_tweets_past_hour(self):
    #     one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
    #     one_hour_ago_str = one_hour_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

    #     tweets = self.client.search_recent_tweets(
    #         user_auth=False,
    #         query="*",
    #     )
    #     return tweets
