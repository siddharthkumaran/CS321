import bot
import re
import time

while(True):
    mentions = bot.getmentions()  #Grab list of mentions
    print(mentions)
    if len(mentions) > 0:   #Check if the list of mentions is empty.
        for i in range(len(mentions)):
            #For loop through the list.
            print('In for loop\n')
            movie_id_list = []   #intialize movie_id_list which of all the suitable movie id computed from user tweets.
            flag = 0             #flag to keep track of condition where replying with movie is not needed.
            text_reply =''       #Text to reply with.
            ment_tweet_id = mentions[i]     #The current mention id.
            user_id = bot.getSingleUserId(ment_tweet_id)    #Grab the user id of the current mention id.
            ment_text = bot.getSingleStatus(ment_tweet_id)  #Grab the text of the mention id.
            user_tweets = bot.getUserTweets(user_id)        #Grab the user of the mention id last 50 tweets.
            user_keywords = bot.getListOfKeywordsFromTweets(user_tweets)    #Compute the important keywords of the 50 tweets.
            user_keyword_Id = bot.keywordIdFromTweets(user_keywords)        #Grab keyword id of each keywords from the movie database.
            youtube_url = 'https://www.youtube.com/watch?v='            #Set up th url for trailer to reply with.
            print('\nMentioned Tweet: ' + ment_text + '\n')
            if (('#help' in ment_text) or ('#instructions' in ment_text)) :     #Check if #help is in tweet.
                text_reply = bot.getInstructions()                                   # if it is, set text_reply to instructions to use bot.
                print('\nGetting instructions....\n')
                bot.replyToTweet(text_reply, ment_tweet_id)
            elif '#genrelist' in ment_text:                               #Check to see if user used #genrelist in the mention tweet.
                text_reply = bot.getGenreList()                             #If they did, set text_reply to a list of genre.
                print('\nGetting genre list....\n')
                bot.replyToTweet(text_reply, ment_tweet_id)
            elif '#genre' in ment_text:                                 #If they use #genre in the mention.
                genre = ment_text.lower()
                genre = re.sub('@botimd #genre[0-9]* ', '', genre)
                genre_id = bot.getGenreId(genre)                            #Grab the genre id from the movie database.
                if(genre_id == -1):                                        #If that genre doesn't exist in the database, set flag to 1 and text_reply to appropriate message.
                    flag = 1
                    text_reply = 'Unable to find the genre. Make sure you enter the correct genre. Use #genrelist to get the list of genre, or #help for help'
                else:
                    print('\nSelected Genre: ' + genre + '\n')                                                #Else grab the list of movie_id using that genre id and keyword_id list from user tweets.
                    movie_id_list = bot.getMovieIdsFromKeywordIdAndGenreId(user_keyword_Id, genre_id)
            elif '#similar' in ment_text:                               #If they use #similar in mentions
                title = ment_text.lower()
                title = re.sub('@botimd #similar[0-9]* ', '', title)    #Grab the title of movie from mention tweet.
                movie_id = bot.getMovieIdFromTitle(title)                   #Search and grab the movie id from the first of the search.
                if(movie_id == -1):                                     #If the movie title doesnt exist in the database.
                    flag = 1
                    text_reply = 'Unable to find the title. Make sure you enter the correct title.\nUse #help for help.'   #Set text_reply to appropriate message.
                else:                                                   #Else grab a list of movie_id that is similar to the movie in the mention.
                    print('\nSelected title: ' + title + '\n')
                    movie_id_list = bot.getSimilarMovieId(movie_id)

            elif '#popular' in ment_text:                               # if they want a popular trending movie for this week in the top 10
                print("Looking for popular movie this week")
                result = bot.popular()                                      # call the popular movie
                movie_id_list.append(result)                            # append it to the movie id list

            elif '#rated' in ment_text:
                print("Looking for top rated movies of all time")
                result = bot.rated()
                #print(topmoviesid)
                for movie in result:
                    url_end = ''
                    text_reply = ''
                    youtube_url = 'https://www.youtube.com/watch?v='
                    mov= bot.tmdb.Movies(movie)
                    m_info = mov.info()
                    #print(mov.title)
                    text_reply = mov.title + ' '
                    url_end = bot.getYouTubeTrailer(mov)
                    if (url_end == ''):
                        print('Printing movie with no link.\n')
                        bot.replyToTweet(text_reply, ment_tweet_id)
                    else:
                        print('Printing movie with link.\n')
                        youtube_url = youtube_url + url_end
                        text_reply = text_reply + '\n' + youtube_url
                        bot.replyToTweet(text_reply, ment_tweet_id)


            else:                                                       #Else if only they only @BotImd with no other hashtag
                movie_id_list = bot.getMovieIdsFromKeywordId(user_keyword_Id)        #Grab the list of movie id using the keyword_id only.

            if (flag == 1 ) :                                        #The rest is just figure out which branch of reply to the mention tweet.
                print('Printing error.\n')
                bot.replyToTweet(text_reply, ment_tweet_id)
            elif (len(movie_id_list) == 0 and text_reply==''):
                print('Printing couldnt find none.\n')
                text_reply = 'Sorry, unable to find a movie for you.\nUse #help for help.'
                bot.replyToTweet(text_reply, ment_tweet_id)
            elif (text_reply==''):
                mov=bot.chooseMovie(movie_id_list)     #Randomly choose a movie from the list of movies that matched the user.
                m_info = mov.info()
                print('\nRecommend: ' + mov.title + '\n')
                text_reply += mov.title + ' '
                url_end = bot.getYouTubeTrailer(mov)
                if (url_end == ''):
                    print('Replying with no trailer link....\n')
                    bot.replyToTweet(text_reply, ment_tweet_id)
                else:
                    print('Replying with trailer link....\n')
                    youtube_url += url_end
                    text_reply = text_reply + '\n' + youtube_url
                    bot.replyToTweet(text_reply, ment_tweet_id)
            print('Sleeping....')
    time.sleep(20)
