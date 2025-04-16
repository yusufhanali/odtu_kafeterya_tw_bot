import tweepy
import creds
import datetime
import sys

def get_twitter_client():
    
    client = tweepy.Client(
        bearer_token=creds.BEARER,
        consumer_key=creds.API_KEY,
        consumer_secret=creds.API_KEY_SECRET,
        access_token=creds.ACCES_TOKEN,
        access_token_secret=creds.ACCESS_TOKEN_SECRET
    )

    return client

if __name__ == "__main__":
    sys.stdout = open("/home/alihahn/Desktop/atolye/odtu_kafeterya_tw_bot/stdout.txt", "a")
    sys.stderr = sys.stdout
    
    client = get_twitter_client()

    ogle_dk = 11*60 + 30
    aksam_dk = 17*60

    now = datetime.datetime.now()
    time_minutes = now.hour * 60 + now.minute

    ids = open("/home/alihahn/Desktop/atolye/odtu_kafeterya_tw_bot/to_be_retweeted.txt", "r")
    kahv_id = ids.readline()
    ogle_id = ids.readline()
    aksam_id = ids.readline()

    kahv_id = int(kahv_id.strip())
    ogle_id = int(ogle_id.strip())
    aksam_id = int(aksam_id.strip())

    print(f"Retweeting: {datetime.datetime.now()}\n")

    if abs(time_minutes - ogle_dk) < abs(time_minutes - aksam_dk):
        print(f"Retweeting Ogledin: {ogle_id}\n")
        #client.retweet(ogle_id)
    else:
        print(f"Retweeting Aksam: {aksam_id}\n")
        #client.retweet(aksam_id)

    print(f"Retweeted Successfully {datetime.datetime.now()}\n")
    sys.stdout.close()
    ids.close()
