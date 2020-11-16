import tweepy
import tmdbsimple as tmdb
from multi_rake import Rake
import time
import enchant
import random
import re
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
    1- Personalized Recommendation: @ botImd [anything]
2- For movie from particular genre: @ botImd #genre [genre name]
3- For similar movie: @ botImd #similar [movie title]
4- For list of accepted genres: @ botImd #genrelist
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
def chooseMovie(list):
    url=''
    count=0
    while(url=='' and count<10):
        random_movie_id = random.choice(movie_id_list)
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

# Main loop to keep the bot running.
# All the print statements in here are for testing.
while(True):
    mentions = getmentions()  #Grab list of mentions
    print(mentions)
    if len(mentions) > 0:   #Check if the list of mentions is empty.
        for i in range(len(mentions)):
            #For loop through the list.
            print('In for loop\n')
            movie_id_list = []   #intialize movie_id_list which of all the suitable movie id computed from user tweets.
            flag = 0             #flag to keep track of condition where replying with movie is not needed.
            text_reply =''       #Text to reply with.
            ment_tweet_id = mentions[i]     #The current mention id.
            user_id = getSingleUserId(ment_tweet_id)    #Grab the user id of the current mention id.
            ment_text = getSingleStatus(ment_tweet_id)  #Grab the text of the mention id.
            user_tweets = getUserTweets(user_id)        #Grab the user of the mention id last 50 tweets.
            user_keywords = getListOfKeywordsFromTweets(user_tweets)    #Compute the important keywords of the 50 tweets.
            user_keyword_Id = keywordIdFromTweets(user_keywords)        #Grab keyword id of each keywords from the movie database.
            youtube_url = 'https://www.youtube.com/watch?v='            #Set up th url for trailer to reply with.
            if (('#help' in ment_text) or ('#instructions' in ment_text)) :     #Check if #help is in tweet.
                text_reply = getInstructions()                                   # if it is, set text_reply to instructions to use bot.
                print('printing instructions.\n')
                replyToTweet(text_reply, ment_tweet_id)
            elif '#genrelist' in ment_text:                               #Check to see if user used #genrelist in the mention tweet.
                text_reply = getGenreList()                             #If they did, set text_reply to a list of genre.
                print('Printing genre list.\n')
                replyToTweet(text_reply, ment_tweet_id)
            elif '#genre' in ment_text:                                 #If they use #genre in the mention.
                genre = ment_text.lower()
                genre = re.sub('@botimd #genre[0-9]* ', '', genre)
                genre_id = getGenreId(genre)                            #Grab the genre id from the movie database.
                if(genre == -1):                                        #If that genre doesn't exist in the database, set flag to 1 and text_reply to appropriate message.
                    flag = 1
                    text_reply = 'Unable to find the genre. Make sure you enter the correct genre. Use #genrelist to get the list of genre, or #help for help'
                else:                                                   #Else grab the list of movie_id using that genre id and keyword_id list from user tweets.
                    print('Printing movies from genre.\n')
                    movie_id_list = getMovieIdsFromKeywordIdAndGenreId(user_keyword_Id, genre_id)
            elif '#similar' in ment_text:                               #If they use #similar in mentions
                title = ment_text.lower()
                title = re.sub('@botimd #similar[0-9]* ', '', title)    #Grab the title of movie from mention tweet.
                movie_id = getMovieIdFromTitle(title)                   #Search and grab the movie id from the first of the search.
                if(movie_id == -1):                                     #If the movie title doesnt exist in the database.
                    flag = 1
                    text_reply = 'Unable to find the title. Make sure you enter the correct title.\nUse #help for help.'   #Set text_reply to appropriate message.
                else:                                                   #Else grab a list of movie_id that is similar to the movie in the mention.
                    movie_id_list = getSimilarMovieId(movie_id)

            elif '#popular' in ment_text:                               # if they want a popular trending movie for this week in the top 10
                print("Looking for popular movie this week")
                result = popular()                                      # call the popular movie
                movie_id_list.append(result)                            # append it to the movie id list

            elif '#rated' in ment_text:
                print("Looking for top rated movies of all time")
                result = rated()
                topmoviesid = result
                print(topmoviesid)
                count_r = 0
                for movie in topmoviesid:
                    if (count == 9):
                        break
                    print(movie)
                    time.sleep(5)
                    url_end = ''
                    text_reply = ''
                    youtube_url = 'https://www.youtube.com/watch?v='
                    movie_id_list = []
                    movie_id_list.append(movie)
                    mov=chooseMovie(movie)
                    m_info = mov.info()
                    print(mov.title)
                    text_reply = mov.title + ' '
                    url_end = getYouTubeTrailer(mov)
                    if (url_end == ''):
                        print('Printing movie with no link.\n')
                        replyToTweet(text_reply, ment_tweet_id)
                    else:
                        print('Printing movie with link.\n')
                        youtube_url = youtube_url + url_end
                        text_reply = text_reply + '\n' + youtube_url
                        replyToTweet(text_reply, ment_tweet_id)
                    count++


            else:                                                       #Else if only they only @BotImd with no other hashtag
                movie_id_list = getMovieIdsFromKeywordId(user_keyword_Id)        #Grab the list of movie id using the keyword_id only.

            if (flag == 1 ) :                                        #The rest is just figure out which branch of reply to the mention tweet.
                print('Printing error.\n')
                replyToTweet(text_reply, ment_tweet_id)
            elif (len(movie_id_list) == 0 and text_reply==''):
                print('Printing couldnt find none.\n')
                text_reply = 'Sorry, unable to find a movie for you.\nUse #help for help.'
                replyToTweet(text_reply, ment_tweet_id)
            elif (text_reply==''):
                mov=chooseMovie(movie_id_list)     #Randomly choose a movie from the list of movies that matched the user.
                m_info = mov.info()
                text_reply += mov.title + ' '
                url_end = getYouTubeTrailer(mov)
                if (url_end == ''):
                    print('Printing movie with no link.\n')
                    replyToTweet(text_reply, ment_tweet_id)
                else:
                    print('Printing movie with link.\n')
                    youtube_url += url_end
                    text_reply = text_reply + '\n' + youtube_url
                    replyToTweet(text_reply, ment_tweet_id)
            print('Sleeping....')
    time.sleep(20)
