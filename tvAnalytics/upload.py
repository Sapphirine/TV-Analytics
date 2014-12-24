import os,sys

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, streaming_bulk

import json

es = Elasticsearch()

def uploadtoES(filename):
	with open(filename) as f:
		data = json.load(f)
		for index,element in enumerate(data):
			episodeInfo = element['episode']
			episodeInfo = episodeInfo.split(',')
			seasonNo = episodeInfo[0].split()
			seasonNo = int(seasonNo[1]) 
			episodeNo = episodeInfo[1].split()
			episodeNo = int(episodeNo[1]) 
			element['seasonNo'] = seasonNo
			element['episodeNo'] = episodeNo
			new_element = dict()
			new_element['_op_type'] = 'create'
			new_element['_index'] = 'tvshows'
			new_element['_type'] = 'episodes'
			new_element['_source'] = element
			data[index] = new_element
		success, _ = bulk(es, data, index='tvshows', raise_on_error=True)
		print('Performed %d actions' % success)

uploadtoES("./app/static/30_rock.json")
uploadtoES("./app/static/how_i_met_your_mother.json")
uploadtoES("./app/static/the_mentalist.json")
uploadtoES("./app/static/breaking_bad.json")