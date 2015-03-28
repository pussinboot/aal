# album art
import tkinter # default?
import json
import requests # dependancy
# tkdnd
from urllib.request import urlretrieve
import os
os.environ['TKDND_LIBRARY'] = 'C:/Python34/Lib/tkdnd2.8/'
from tkdnd_wrapper import TkDND
from aal import *


debug = False
class AA:
	def __init__(self):
		self.username = 'OJClock' # mine
		self.api_key = '874b1cf6420f724a52da51478cbf02f5' #public key no worries
		self.n_pages = 2
		self.library = []
		self.ready_to_learn = False

	def set_user(self,u):
		self.user = u

	def how_many(self,n):
		self.n_pages = n // 50

	def init_db(self):
		print('initializing db')
		for i in range(self.n_pages):
			resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user="+ self.username +"&page="+str(i+1)+ "&api_key="+self.api_key+"&format=json")
			resp = resp.json()
			#print(resp)
			albums = resp['topalbums']['album']	
			for a in albums:
				self.library.append(Album(a['artist']['name'],a['name'],a['image']))
		if debug:
			for x in self.library:
				print(x)
				print(x.get_img('s'))
				print(x.get_img('m'))
				print(x.get_img('l'))
				print(x.get_img('xl'))
		self.ready_to_learn = True
		print('done')

	def learn(self):
		if not self.ready_to_learn:
			print('not ready to learn')
			return
		else:
			self.brain = Brains(self.library)
			self.brain.train()
			print('woo')

	def quit(self):
		self.brain.quit()

class Album:
	def __init__(self,artist,album,images):
		self.artist = self.safe(artist)
		self.album = self.safe(album)
		self.images = {}
		self.imagesource = images
		for i in images:
			localpath = "./idb/"+self.artist+"/"+self.album+"/"
			filepath = localpath+i['size']+".png"
			if not os.path.exists(localpath): os.makedirs(localpath)
			if not os.path.isfile(filepath): urlretrieve(i['#text'],filepath)
			self.images[i['size']] = filepath

	def safe(self,s):
		return "".join(x for x in s if x.isalnum() or x == ' ')

	def __str__(self):
		return str(self.artist) + ' - ' + str(self.album)

	def get_img(self,size):
		if size == 's':
			return self.images['small']
		elif size == 'l':
			return self.images['large']
		elif size == 'xl':
			return self.images['extralarge']
		else:
			return self.images['medium']
	def get_src(self):
		return self.imagesource

class Gui:
	def __init__(self, master, aa):        
		self.aa = aa

		def quitter():
			self.aa.quit()
			master.quit()

		canvas = tkinter.Canvas(master,width=300,height=600)
		canvas.grid(row = 0, column = 0)
		canvas.grid_propagate(False)
		#canvas.create_image(0,0, anchor=tkinter.NW, image = tkinter.PhotoImage(file = library[1].get_img('xl')))
		textbox = tkinter.Text(height=1)
		dnd = TkDND(master)
		textbox.place(x=0,y=327,width=300)

		self.button1 = tkinter.Button(canvas,text='init database', width = 300, height = 75,command = aa.init_db, anchor=tkinter.NW)
		self.button2 = tkinter.Button(canvas,text='learn',width = 300, height = 75,command = aa.learn,anchor=tkinter.NW)
		self.button3 = tkinter.Button(canvas,text='exit',width = 300, height = 75,command = quitter,anchor=tkinter.NW)
		self.button1.place(x=0,y=375) 
		self.button2.place(x=0,y=450)
		self.button3.place(x=0,y=525)

		def test(content):
			if content[:8] == 'http://' or content[:9] == 'https://':
				urlretrieve(content,'/idb/temp.png') # use PIL here to convert image to correct size/type
			elif os.path.isfile(content): #open the file
				canvas.create_image(0,0, anchor=tkinter.NW, image = tkinter.PhotoImage(file = content))
			if debug: print(content)

		def handle(event):
			event.widget.insert(tkinter.END, event.data)
			content = textbox.get("0.0",tkinter.END)
			test(content)
			# do something


		dnd.bindtarget(textbox, handle, 'text/uri-list')

if __name__=='__main__':
	aa = AA()
	root = tkinter.Tk()
	root.wm_resizable(0,0)
	test = Gui(root,aa)
	root.mainloop()
