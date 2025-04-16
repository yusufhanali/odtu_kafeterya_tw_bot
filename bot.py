#ODTÜ tablBOT
import requests
from bs4 import BeautifulSoup
import datetime
import cv2
import numpy as np

import tweepy
import creds
import tempfile
import sys

URL = "https://kafeterya.metu.edu.tr/"

def turn_str_universal(str):
    mapping = {
      'Ç': 'C',
      'Ö': 'O',
      'Ş': 'S',
      'İ': 'I',
      'I': 'i',
      'Ü': 'U',
      'Ğ': 'G',
      'ç': 'c',
      'ö': 'o',
      'ş': 's',
      'ı': 'i',
      'ü': 'u',
      'ğ': 'g'
    }

    mapping_keys = mapping.keys()

    str_list = list(str)
    universal = [mapping[char] if char in mapping_keys else char for char in str_list]
    universal_str = "".join(universal)
    return universal_str

def get_url_content(url):

    page = requests.get(URL)

    if page.status_code == 200:
        return page.text
    
    return None

def get_meals(website):

    meals = []

    page_text = get_url_content(website)

    soup = BeautifulSoup(page_text, 'html.parser')

    meal_divs = soup.find_all('div', class_='view-content')

    for div in meal_divs:
        #print("--------------")
        articles = div.find_all('article', class_="node node-yemek-listesi node-promoted clearfix")
        meal_name = div.find('h3')

        if not meal_name:
            continue

        meal_name = meal_name.text
        #print(meal_name)
        meal = {"name": meal_name}

        food = []

        if not articles:
            meal_name_universal = turn_str_universal(meal_name).lower()
            contents = div.find_all('div', class_=meal_name_universal)

            #for cntnt in contents:
                #print(cntnt.text)

            food = [content.text for content in contents]

            if len(food) > 0:
                meal["food"] = food   

            if meal:
                meals.append(meal)

            continue    

        images = []

        for article in articles:

            name = article.find('h2')
            img = article.find('img')

            food.append(name.text)
            images.append(img['src'])

            #print(name.text)
            #print(img['src'])

        if len(food) > 0:
            meal["food"] = food
        if len(images) > 0:
            meal["images"] = images

        vegeterian = div.find('div', class_='vejeteryan')
        if vegeterian:
            #print(vegeterian.text)
            meal["vegetarian"] = vegeterian.text

        if meal:
            meals.append(meal)
    
    return meals
        
def url_to_image(url):
    req = requests.get(url, stream=True)
    arr = np.asarray(bytearray(req.content), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)

    return img

def prepare_tweets(meals):

    months = {
        1: "Ocak",
        2: "Şubat",
        3: "Mart",
        4: "Nisan",
        5: "Mayıs",
        6: "Haziran",
        7: "Temmuz",
        8: "Ağustos",
        9: "Eylül",
        10: "Ekim",
        11: "Kasım",
        12: "Aralık"
    }

    tweets = []

    for meal in meals:

        now = datetime.datetime.now() 
        
        tweet_text = str(now.day) + " " + months[now.month] + " " + str(now.year) + " "
        tweet_picture = None

        keys = meal.keys()

        if "name" in keys:
            tweet_text += meal["name"] + ":\n"
        else:
            return
        
        if "food" in keys:
            for fod in meal["food"]:
                tweet_text += fod + "\n"
        else:
            return
        
        if "vegetarian" in keys:
            tweet_text += meal["vegetarian"] + "\n"
        
        if "images" in keys:

            images = [url_to_image(img) for img in meal["images"]]

            resized_images = [cv2.resize(img, (300, 300)) for img in images]
            amt_images = len(resized_images)

            stitched_image = np.zeros((300, amt_images*300, 3), dtype=np.uint8)

            for idx, img in enumerate(resized_images):
                stitched_image[0:300, idx * 300:(idx + 1) * 300] = img

            tweet_picture = stitched_image
        
        tweets.append((tweet_text, tweet_picture))

    return tweets

def get_tweets_w_assumption():
    meals = get_meals(URL)
    tweets = prepare_tweets(meals)
    return tweets

def get_twitter_client():
    
    client = tweepy.Client(
        bearer_token=creds.BEARER,
        consumer_key=creds.API_KEY,
        consumer_secret=creds.API_KEY_SECRET,
        access_token=creds.ACCES_TOKEN,
        access_token_secret=creds.ACCESS_TOKEN_SECRET,
    )

    return client

def get_old_twitter_api():
    auth = tweepy.OAuth1UserHandler(creds.API_KEY, creds.API_KEY_SECRET, creds.ACCES_TOKEN, creds.ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)

    return api_v1

def send_tweet(client: tweepy.Client, old_api: tweepy.API, tweet_text, tweet_picture):

    if tweet_picture is not None:
        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
            cv2.imwrite(temp_file.name, tweet_picture)
            media = old_api.media_upload(filename=temp_file.name)
        return client.create_tweet(text=tweet_text, media_ids=[media.media_id]).data["id"]
    else:
        return client.create_tweet(text=tweet_text).data["id"]

if __name__ == "__main__":
    sys.stdout = open("/home/alihahn/Desktop/atolye/odtu_kafeterya_tw_bot/stdout.txt", "a")
    sys.stderr = sys.stdout

    tweets = get_tweets_w_assumption()
    #print(tweets)

    client = get_twitter_client()
    old_api = get_old_twitter_api()

    to_be_retweeted = open("/home/alihahn/Desktop/atolye/odtu_kafeterya_tw_bot/to_be_retweeted.txt", "w")
    print(f"Tweeting: {datetime.datetime.now()}\n")

    for tw in tweets:

        tweet_text, tweet_picture = tw

        print(send_tweet(client, old_api, tweet_text, tweet_picture), file=to_be_retweeted)
        print(f"Tweeted: {tweet_text}\n")

    print(f"Tweeted Successfully {datetime.datetime.now()}\n")

    to_be_retweeted.close()
    sys.stdout.close()