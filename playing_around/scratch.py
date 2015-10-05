import sys
import json
import requests 


username = 'OJClock' # mine
api_key = '874b1cf6420f724a52da51478cbf02f5' #public key no worries

search = 'My Bloody Valentine - Loveless'

#resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=album.search&album="+ search + "&api_key="+api_key+"&limit=3&format=json")
#resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user="+ username + "&api_key="+api_key+"&format=json")
resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user=OJClock&page=1&api_key=874b1cf6420f724a52da51478cbf02f5&format=json")
resp = resp.json()
print(str(resp).encode(sys.stdout.encoding, 'replace'))
#albums = resp['topalbums']['album']

print(albums)
#albums = resp['results']['albummatches']['album']
#
#for a in albums:
#	for i in a['image']:
#		print(i['size'])
	#print(a['artist'],a['name'])
# 	new_alb = Album(a['artist']['name'],a['name'],a['image'])
# 	if new_alb.__str__() not in self.library:
# 		self.library[new_alb.__str__()] = new_alb