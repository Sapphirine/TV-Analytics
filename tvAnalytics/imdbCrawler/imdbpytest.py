import imdb

ia = imdb.IMDb()
series =  ia.get_movie("0496424")
print series['episodes']