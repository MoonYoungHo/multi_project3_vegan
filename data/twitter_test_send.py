import tweepy
import json
import socket


tweet_list = list()

API_KEY = "VuHYXeojsfYT1bNF3Q5YDeqIC"
API_SECRET = "dG7T69UtUO7juX03nPXUNAgKdxr9gubTSdXIwSzabZLkZz8x8k"

ACCESS_TOKEN = "1560428327264915456-q6jNbupBXPhfIWmkFnDDZRcvepGKuX"
ACCESS_SECRET = "iSagmqx98ltFhvEL3beBs2X8d1iI48aEkm16jKHjL7wgD"

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAPLxggEAAAAAEuPi0BJKhaGD3OtAzB%2BfEq6MPHQ%3DNMDgsGP2POmNQn0hghqw23Ilgz134UjZXfYHCpbaU2QYXxtwG2"


# tweepy.StreamClient 클래스를 상속받는 클래스
class TwitterStream(tweepy.StreamingClient):
    def __init__(self, c_socket, bearer_token, user_agent):
        super().__init__(bearer_token)
        self.client_socket = c_socket
        self.bearer_token = bearer_token
        self.user_agent = user_agent
        
    def on_data(self, data):
        tweet = json.loads(data)
        
        if '@' not in tweet['data']['text'] and tweet['data']['lang'] == 'en':
            self.client_socket.send(data)
            print(tweet)
            return True


# 규칙 제거 함수
def delete_all_rules(rules):
    # 규칙 값이 없는 경우 None으로 들어옴
    if rules is None or rules.data is None:
        return None
    stream_rules = rules.data
    client.delete_rules(ids=list(map(lambda rule: rule.id, stream_rules)))


# 스트리밍
def send_data(keyword):
    print("Start getting data from Twitter")
    
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    
    client = TwitterStream(c_socket=c_socket, bearer_token=BEARER_TOKEN, user_agent=USER_AGENT)    # 스트림 클라이언트 인스턴스 생성
    # delete_all_rules(client.get_rules())    # 모든 규칙 제거
    client.add_rules(tweepy.StreamRule(keyword))          # 스트림 규칙 추가
    client.filter(tweet_fields=['lang', 'created_at'])    # 스트림 시작


if __name__ == "__main__":
    # 소켓 생성
    new_socket = socket.socket()
    host = "localhost"
    port = 5555
    new_socket.bind((host, port))
    print(f'Socket is established')
    print(new_socket)
    
    # 소켓 listen (클라이언트의 접속을 허용)
    new_socket.listen()
    print('Socket is listening')
    
    # accept 함수에서 대기하다가 클라이언트가 접속하면 새로운 소켓을 리턴
    c_socket, addr = new_socket.accept()
    print(f'Received request: {addr}')
    # print(c_socket)
    
    # Send data to client via socket for selected keyword
    send_data(keyword='#vegan')



    # new_socket.close()