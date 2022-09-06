import tweepy
import json

tweet_list = list()

# tweepy.StreamClient 클래스를 상속받는 클래스
class TwitterStream(tweepy.StreamingClient):
    def on_data(self, data):
        tweet = json.loads(data)
        if '@' not in tweet['data']['text']:
            tweet_list.append(tweet)
            print(tweet)

# 규칙 제거 함수
def delete_all_rules(rules):
    # 규칙 값이 없는 경우 None으로 들어옴
    if rules is None or rules.data is None:
        return None
    stream_rules = rules.data
    client.delete_rules(ids=list(map(lambda rule: rule.id, stream_rules)))

# 스트림 클라이언트 인스턴스 생성
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAPLxggEAAAAAEuPi0BJKhaGD3OtAzB%2BfEq6MPHQ%3DNMDgsGP2POmNQn0hghqw23Ilgz134UjZXfYHCpbaU2QYXxtwG2'
client = TwitterStream(BEARER_TOKEN)

# 모든 규칙 제거
delete_all_rules(client.get_rules())

# 스트림 규칙 추가
client.add_rules(tweepy.StreamRule("#plantbased"))

# 스트림 시작
client.filter(tweet_fields=['lang', 'created_at', 'public_metrics'])