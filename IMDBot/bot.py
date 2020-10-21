import tweepy

#bearer token(not sure what this is, we might need it): AAAAAAAAAAAAAAAAAAAAAPXtHwEAAAAA0QTHI4KZeeEcCkQR56sjTrh5WrM%3D2FD9RvoDyxSNUcDXCXpqVzKDDdYucawdQQ19pmIGDlkSwl3sUM
consumer_key='e4ZTLy8v3jvbtGxx2hlOcaBxC'
consumer_secret='riue79WC26fcuhGWFWop9MCDLLg6gHWhvFWcrgxtFa50yOZ5pG'

key='1308843607152111617-XGq5PvcStSSQymUBtUcVFLc08HeM8N'
secret='EL7WL88PTNN3FjMK8xd703dobk9LnS5pKkGyxMXJ5LGtb'

auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)

api = tweepy.API(auth)
#api.update_status('The Bot is LIVE my dudes!') #(this just tweets the msg.)

def getmentions():
    "This gets the recent tweets that mention the bot. returns a list of 20 most recent tweet IDs."
    tweets=api.mentions_timeline()
    mentions=[]
    for i in range(len(tweets)):
        mentions.append(tweets[i].id)
    return mentions

def getusers():
    "Returns a list of IDs of users that mentioned the bot."
    mentions=getmentions()
    users=[]
    for i in range(len(mentions)):
        user=api.get_status(mentions[i]).user.id
        users.append(user)
    return users









