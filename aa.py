# album art
import tkinter # default?
import json
import requests # dependancy
# tkdnd
from urllib.request import urlretrieve
import os
os.environ['TKDND_LIBRARY'] = 'C:/Python34/Lib/tkdnd2.8/'
from tkdnd_wrapper import TkDND

api_key = '874b1cf6420f724a52da51478cbf02f5' #public key no worries
user = 'OJClock'
n_pages = 2
debug = False

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
	def __init__(self, master):        

		canvas = tkinter.Canvas(master,width=300,height=600)
		canvas.grid(row = 0, column = 0)
		canvas.grid_propagate(False)
		library = []
		for i in range(n_pages):
			resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user="+ user +"&page="+str(i+1)+ "&api_key="+api_key+"&format=json")
			resp = resp.json()
			#print(resp)
			albums = resp['topalbums']['album']
			
			for a in albums:
				#print(a)
				library.append(Album(a['artist']['name'],a['name'],a['image']))
		if debug:
			for x in library:
				print(x)
				print(x.get_img('s'))
				print(x.get_img('m'))
				print(x.get_img('l'))
				print(x.get_img('xl'))

		print(library[0],library[0].get_src())
		#canvas.create_image(0,0, anchor=tkinter.NW, image = tkinter.PhotoImage(file = library[1].get_img('xl')))
		textbox = tkinter.Text(height=1)
		dnd = TkDND(master)
		textbox.place(x=0,y=327,width=300)

		self.button1 = tkinter.Button(canvas,text='init database', width = 300, height = 75,command = lambda: print('a'),anchor=tkinter.NW)
		self.button2 = tkinter.Button(canvas,text='test picture',width = 300, height = 75,command = lambda: print('b'),anchor=tkinter.NW)
		self.button3 = tkinter.Button(canvas,text='exit',width = 300, height = 75,command = lambda: master.quit(),anchor=tkinter.NW)
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
	root = tkinter.Tk()
	root.wm_resizable(0,0)
	test = Gui(root)
	root.mainloop()
