from sklearn import linear_model
from pprint import pprint
import json, re

def processepisodenumber(string):
	numbers = re.findall(r'\d+',string[1])
	return list([string[0],(int(numbers[0])*100+int(numbers[1]))/100.0])

with open('../app/static/breaking_bad.json','rt') as f:
	#since we are loading from a file, we use load
	#instead of loads
	json_data = json.load(f)
	pprint(json_data)
	result = [list([x['episodeRating'],x['episode']]) for x in json_data]
	result = map(processepisodenumber,result)
	result.sort(key=lambda x: x[1])
	result = [[x[0],i+1] for i,x in enumerate(result)]
	print result
	y = [x[0] for x in result]
	x = [[z[1]] for z in result]
	print x 
	print y

clf = linear_model.LinearRegression(copy_X=True, fit_intercept=True, normalize=False)
clf.fit(x,y)
print clf.coef_*(len(result)+1)