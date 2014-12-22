import re

def processSeriesString(seriesName):
	searchString = re.sub("\s\s+", " ", seriesName).strip().encode('ascii','ignore')
	saveString = "_".join(searchString.split(" ")).encode('ascii','ignore').lower()
	return [searchString,saveString]
