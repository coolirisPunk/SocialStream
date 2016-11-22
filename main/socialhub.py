from instagram.client import InstagramAPI
import datetime
import facebook
import requests
from tweepy import OAuthHandler
from tweepy import API
from django.utils.encoding import smart_text
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SocialHub(object):
    EXTENDED_TOKEN_FACEBOOK = 'CAAZAHDZBd0zOkBAHrvHbRMi3zXiqKewGo8t7IasunEfHVWvWwzaTcG3quttqwExyZBjc645Mc6onEqb8BlLeeY6QBZAayXpVUUyXhJkkVvWQ2JNGmaF7bZCuaQAwdcL3HwYyBXTbVIx8GIU90vST6OZCOTPUCXArpi3NOKXyqAWWixy1QNd6BRJhgNiX2hW6UZD'
    CONSUMER_KEY_TWITTER = "MToutlg9vV08FKCQUoiwXFVmH"
    CONSUMER_SECRET_TWITTER = "b9jhnaJuHdhoNBhEv8N7XHOWgiPvvpNDuBHlNjR7UEV4DFqxig"
    ACCESS_TOKEN_TWITTER = "2167556856-RmZHrI1veXxozyuG07vNgm5V0q3pJHslTu7dCnI"
    ACCESS_TOKEN_SECRET_TWITTER = "QhAkahpiUzNSB6A1rlPn2slqyjh9xkD11dinJoQXIqabg"
    ACCESS_TOKEN_INSTAGRAM = "1296904443.e653774.41fb070a224e40fab914288678292b1d"
    CLIENT_SECRET_INSTAGRAM = "1580722098914ae19056e65ddb69d846"
    COUNT_NUMBER_POST = 15
    MAX_POSTS_BY_SOCIAL = 10

    def __init__(self, user_facebook, user_twitter, user_instagram, instagram_id):
        self.user_facebook = user_facebook
        self.user_twitter = user_twitter
        self.user_instagram = user_instagram
        self.instagram_id = instagram_id

    def get_picture_facebook(self, post_id):
        url = "https://graph.facebook.com/v2.6/" + post_id + "?fields=full_picture,link&access_token=" + self.EXTENDED_TOKEN_FACEBOOK
        r = requests.get(url)
        r_json = r.json()
        data = {'id': post_id, 'picture': r_json["full_picture"], 'link': r_json["link"]}
        return data

    def FeedFacebook(self):
	    graph = facebook.GraphAPI(self.EXTENDED_TOKEN_FACEBOOK)
	    profile = graph.get_object(self.user_facebook)
	    feed = graph.get_connections(profile['id'], 'posts')
	    posts = []
	    try:
	    	for p in feed['data'][:self.MAX_POSTS_BY_SOCIAL]:
	    		data_picture = self.get_picture_facebook(p["id"])
	    		posts.append({"post_id": p["id"], "created_time": datetime.datetime.strptime(p["created_time"], '%Y-%m-%dT%H:%M:%S+0000'),
	                       "text": p["message"], "post_type": "facebook", "image": data_picture["picture"],"post_url":data_picture["link"]})
	    except Exception, e:
	        print(str(e))

	    return posts

    def FeedTwitter(self):
	    auth = OAuthHandler(self.CONSUMER_KEY_TWITTER, self.CONSUMER_SECRET_TWITTER)
	    auth.set_access_token(self.ACCESS_TOKEN_TWITTER, self.ACCESS_TOKEN_SECRET_TWITTER)
	    api = API(auth)
	    feed = api.user_timeline(screen_name="@" + self.user_twitter, count=self.COUNT_NUMBER_POST, page=1, include_rts=True)
	    tweets = []
	    for t in feed[:self.MAX_POSTS_BY_SOCIAL]:
	        if t.in_reply_to_status_id is None:
	            try:
	                tweet = {"text": t.text, "post_type": "tweet", "created_time": t.created_at,
	                         "post_url": "https://twitter.com/" + self.user_twitter + "/status/" + str(t.id),
	                         "user":"@" + t.user.screen_name}
	                if "media" in t.entities:
	                    if t.entities['media'][0]['type'] == 'photo':
	                        tweet["image"] = t.entities['media'][0]['media_url']
	                tweets.append(tweet)
	            except Exception, e:
	                #print(str(e))
	                pass
	    return tweets

    def FeedInstragram(self):
	    api = InstagramAPI(access_token=self.ACCESS_TOKEN_INSTAGRAM, client_secret=self.CLIENT_SECRET_INSTAGRAM)
	    posts = []
	    feed, next_ = api.user_recent_media(user_id=self.instagram_id, count=self.COUNT_NUMBER_POST)
	    [posts.append(
	            {"created_time": p.created_time, "post_type": "instagram", "user": p.user.username,
	             "text": smart_text(p.caption.text), "media_type": p.type, "post_url": p.link,"image": p.get_standard_resolution_url()}) for p in feed[:self.MAX_POSTS_BY_SOCIAL]]
	    return posts


    def GetPosts(self):
	    lists = self.FeedFacebook() + self.FeedTwitter() + self.FeedInstragram()
	    feeds = sorted(lists, key=lambda k: k['created_time'], reverse=True)

	    return feeds[:10]
