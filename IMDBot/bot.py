import tweepy
import tmdbsimple as tmdb
from multi_rake import Rake
import enchant
import random
import requests

#Movie data base api key.
tmdb.API_KEY = '77a3f22cc7407bb2b409d69b58fc32ab'

#bearer token(not sure what this is, we might need it): AAAAAAAAAAAAAAAAAAAAAPXtHwEAAAAA0QTHI4KZeeEcCkQR56sjTrh5WrM%3D2FD9RvoDyxSNUcDXCXpqVzKDDdYucawdQQ19pmIGDlkSwl3sUM
consumer_key='e4ZTLy8v3jvbtGxx2hlOcaBxC'
consumer_secret='riue79WC26fcuhGWFWop9MCDLLg6gHWhvFWcrgxtFa50yOZ5pG'

key='1308843607152111617-XGq5PvcStSSQymUBtUcVFLc08HeM8N'
secret='EL7WL88PTNN3FjMK8xd703dobk9LnS5pKkGyxMXJ5LGtb'

auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)

#English dictionary to check each word of the tweet to see if it is a word.
En_dict = enchant.Dict("en_US")

#API Object to interact with Twitter.
api = tweepy.API(auth, wait_on_rate_limit=True)
#api.update_status('The Bot is LIVE my dudes!') #(this just tweets the msg.)

#Object from tmdb...probably going to use it to movie with keywords from user tweet, genre, similar.
Movie_Search = tmdb.Search()
Genre = tmdb.Genres()
Discover = tmdb.Discover()

#filename to store last seen mention id, so that we don't keep replying to the same request again.
LAST_SEEN_FILE = 'last_mention_id.txt'

#Object use to extract keywords from user tweets.
keywords_Extract = Rake(min_chars = 3, max_words = 1)

def get_last_mention_id(file_name):
    #Create to get the last seen mention for getmentions() to avoid grabbing the same mention again.
    last_read = open(file_name, 'r')
    id = int(last_read.read().strip())
    last_read.close()
    return id

def set_last_mention_id(last_id, file_name):
    #Create to write the last seen mention into a file.
    last_write = open(file_name, 'w')
    last_write.write(str(last_id))
    last_write.close()
    return

def getmentions( ):
    #This gets the recent tweets that mention the bot. returns a list of 20 most recent tweet IDs.
    last_seen_mention = get_last_mention_id(LAST_SEEN_FILE) #grabbing the last seen mention.
    tweets = api.mentions_timeline(last_seen_mention) #grab tweet after the last seen mention.
    mentions=[]
    if len(tweets) > 0:
        set_last_mention_id(tweets[0].id, LAST_SEEN_FILE) #write the last seen mention into a file.
        for i in range(len(tweets)):
            mentions.append(tweets[i].id)
    return mentions

def getusers():
    #Returns a list of IDs of users that mentioned the bot.
    mentions=getmentions()
    users=[]
    for i in range(len(mentions)):
        user=api.get_status(mentions[i]).user.id
        users.append(user)
    return users

def getUserTweets(userId: int):
    #Returns the user last 50 tweets in string.
    tweets = api.user_timeline(userId, count = 50)
    text=[]
    if len(tweets) > 0:
        for i in range(len(tweets)):
            split_txt = tweets[i].text.split()
            if len(split_txt) > 0:
                for word in split_txt:
                    if En_dict.check(word):
                        text.append(word)
    s_text = ' '.join(text).lower()
    return s_text

def getListOfKeywordsFromTweets(user_tweets):
    #Return a list of keywords from the user last 50 tweets.
    result = keywords_Extract.apply(user_tweets)
    keywords = []
    if len(result) > 0:
        for i in range(len(result)):
            keywords.append(result[i][0])
    return keywords

#Get a list of keyword_ids from the keywords from user tweets.
def keywordIdFromTweets(user_keywords):
    result = []
    if len(user_keywords) > 0:
        for i in user_keywords:
            key_id = Movie_Search.keyword(query = i)
            if len(key_id['results']) > 0:
                for key in key_id['results']:
                    result.append(key['id'])
    return result

#Get list of movie id of movie using Keyword_id from user tweet.
def getMovieIdsFromKeywordId(Keyword_Id):
    result = []
    if len(Keyword_Id) > 0:
        for k_id in Keyword_Id:
            #Note the list will contain only movie with average rating of 7 or higher and number of rating of 5 or higher, and will be sorted by rating.
            kwargs = {'with_keywords' : k_id, 'vote_average.gte': 7, 'vote_count.gte' : 5, 'include_video': True, 'sort_by':'vote_average.dec'}
            movies = Discover.movie(**kwargs)
            if (len(movies) > 200): movies=movies[0:200]     #get only top 200 movies if more than 200 were found.
            if len(movies['results']) > 0:
                for m_id in movies['results']:
                    result.append(m_id['id'])
    return result

#Get list of movie id of movie using Keyword_id from user tweet and genre id.
def getMovieIdsFromKeywordIdAndGenreId(Keyword_Id, Genre_Id):
    result = []
    if len(Keyword_Id) > 0:
        for k_id in Keyword_Id:
            #Note the list will contain only movie with average rating of 7 or higher and number of rating of 5 or higher, and will be sorted by rating.
            kwargs = {'with_keywords' : k_id, 'vote_average.gte': 7, 'vote_count.gte' : 5, 'with_genres': Genre_Id, 'include_video': True, 'sort_by':'vote_average.dec'}
            movies = Discover.movie(**kwargs)
            if (len(movies) > 200): movies=movies[0:200]    #get only top 200 movies if more than 200 were found.
            if len(movies['results']) > 0:
                for m_id in movies['results']:
                    result.append(m_id['id'])
    return result

def getSingleUserId(tweetId: int):
    #Getting the user id of a tweet id.
    return api.get_status(tweetId).user.id

def getSingleStatus(tweetId: int):
    #Getting the text from a tweet id.
    return api.get_status(tweetId).text.lower()

#Get Genre id from genre name.
def getGenreId(genre):
    res = Genre.movie_list()
    genres = res['genres']
    g_id = -1
    for g in genres:
        if g['name'].lower() == genre:
            g_id = g['id']
    return g_id

#Get list of Genre.
def getGenreList():
    genre_list = []
    res = Genre.movie_list()
    res = res['genres']
    for genre in res:
        genre_list.append(genre['name'])
    txt = ', '.join(genre_list)
    return txt

#Get instructions to use bot, couldn'tbe as detailed as I would've liked due to character limit in tweets, but this should be readable.
def getInstructions():
    txt="""
    1- Personalized Recommendation: @ botImd
2- Genre Specific Recommendation: @ botImd #genre [genre name]
3- Similar movie: @ botImd #similar [movie title]
4- List of accepted genres: @ botImd #genrelist
5- Top rated movie: @ botImd #rated
6- Weekly popular movie: @ botImd #popular
    """
    return txt

#Get movie id from title.
def getMovieIdFromTitle(title):
    movie_id = -1
    res = Movie_Search.movie(query = title)
    res = res['results']
    if len(res) > 0:
        res = res[0]
        movie_id = res['id']
    return movie_id

#Reply to mention tweet.
def replyToTweet(text, ment_id):
    api.update_status(status = text, in_reply_to_status_id = ment_id,  auto_populate_reply_metadata = True)
    return

#Get a list of similar movie.
def getSimilarMovieId(movie_id):
    movie = tmdb.Movies(movie_id)
    res = movie.similar_movies()['results']
    sim_id_list = []
    for movie in res:
        sim_id_list.append(movie['id'])
    return sim_id_list

#Get the key_id of youtube video url from the database.
def getYouTubeTrailer(movie):
    url = ''
    res = movie.videos()['results']
    for vid in res:
        if (vid['type'] == 'Trailer' and vid['site'] == 'YouTube'):
            url += vid['key']
            break
    return url

#Randomly choose movie with trailer from list, gives up after 10 tries.
def chooseMovie(movie_list):
    url=''
    count=0
    while(url=='' and count<10):
        random_movie_id = random.choice(movie_list)
        mov = tmdb.Movies(random_movie_id)
        url=getYouTubeTrailer(mov)
        count+=1
    return mov

# does an API calll to grab a trending movie
def popular():
    results = requests.get("https://api.themoviedb.org/3/trending/movie/week?api_key=77a3f22cc7407bb2b409d69b58fc32ab") # the actual call to the database
    results = results.json() # grabs the json
    movie_id = results['results'][0]['id']  # grabs the movie_id
    return movie_id

def rated():
    movie_list = []
    results = requests.get("https://api.themoviedb.org/3/movie/top_rated?api_key=77a3f22cc7407bb2b409d69b58fc32ab&language=en-US&page=1")
    results = results.json()
    for i in range(10):
        movie_list.append(results['results'][i]['id'])
    return movie_list
