# TO-DO
# fix up data management so can tell if network has been trained already 
# also check if same user as before ?
# what is the testing actually doing :v)

# album art
import tkinter # default?
import json
import requests # dependancy
import pickle
# tkdnd
from urllib.request import urlretrieve
import os
os.environ['TKDND_LIBRARY'] = 'C:/Python34/Lib/tkdnd2.8/'
from tkdnd_wrapper import TkDND
from aal import *
from mbox import MessageBox
from io import BytesIO
from PIL import ImageTk, Image

debug = False
class AA:
	def __init__(self):
			self.ready_to_learn = False
			self.ready_to_test = False
			self.library = []

			if not os.path.exists('savedata'):
				self.savedata = open('savedata','wb')
				self.username = 'OJClock' # mine
				self.api_key = '874b1cf6420f724a52da51478cbf02f5' #public key no worries
				self.n_pages = 2
				
			else:
				read = open('savedata','rb')
				try:
					saved_dict = pickle.load(read)
					read.close()
					self.username = saved_dict['username']
					print('loaded',self.username,'\'s library')
					self.api_key = saved_dict['api_key']
					self.n_pages = saved_dict['n_pages']
					self.savedata = open('savedata','wb')
				except:
					read.close()
					os.remove('savedata')
					self.__init__()
				
		

	def set_user(self,u):
		if u != '': self.username = u

	def how_many(self,n):
		self.n_pages = n // 50

	def init_db(self):
		print('initializing db')
		for i in range(self.n_pages):
			resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user="+ self.username +"&page="+str(i+1)+ "&api_key="+self.api_key+"&format=json")
			resp = resp.json()
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
		self.brain = Brains(self.library,self.username)
		self.ready_to_learn = True
		self.ready_to_test = True # only if has been trained before .-.
		print('done')

	def learn(self,n):
		if not self.ready_to_learn:
			print('not ready to learn')
			return
		else:
			self.brain.train(n)

	def tester(self,img):
		if not self.ready_to_test: return
		#out = self.brain.test(img)
		#print(out)
		self.brain.test_acc()

	def quit(self):
		if self.ready_to_learn:	self.brain.quit()
		new_dict = {}
		new_dict['username'] = self.username
		new_dict['api_key'] = self.api_key
		new_dict['n_pages'] = self.n_pages
		#new_dict['library'] =  self.library
		pickle.dump(new_dict,self.savedata)
		self.savedata.close()



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
			master.destroy()

		master.protocol("WM_DELETE_WINDOW", quitter)

		def user_select():
			self.aa.set_user(self.user.get())
			self.aa.init_db()

		def image_select():
			content = self.mbox('drag an image or paste url',entry=True)
			if content:
				content = content.strip()
				if content[0]=='{':	content = content[1:-1]
				print(content)
				if content[:7] == 'http://' or content[:8] == 'https://':
					response = requests.get(content)
					img = Image.open(BytesIO(response.content))
				elif os.path.isfile(content): #open the file
					img = Image.open(content)
				else:
					return
				imgn = img.resize((300,300), Image.NEAREST)
				imgn = ImageTk.PhotoImage(img)
				self.panel.configure(image = imgn)
				self.panel.image = imgn
				self.aa.tester(img)
			if debug: print(content)

		def trainer():
			num = self.n_iter.get()
			try:
				n = int(num)
				aa.learn(n)
			except ValueError:
				self.n_iter.set(5)
				return
			#print(num)

		canvas = tkinter.Canvas(master,width=300,height=600)
		canvas.grid_propagate(False)
		#img = tkinter.PhotoImage(file = 'test.png')
		self.panel = tkinter.Label(canvas,anchor=tkinter.NW)#, image = img)
		#self.panel.image = img
		self.panel.place(x=0,y=0)
		button1 = tkinter.Button(master,text='init database', width = 30, height = 5,command = user_select)
		self.user = tkinter.StringVar()
		self.n_iter = tkinter.StringVar()
		self.n_iter.set('5')
		userentry = tkinter.Entry(master,textvariable=self.user,width=11)
		button2 = tkinter.Button(master,text='train',width = 30, height = 5,command = trainer)
		iterspin = tkinter.Spinbox(master,from_=1,to=100,textvariable=self.n_iter,justify=tkinter.RIGHT,width=3)
		button3 = tkinter.Button(master,text='test',width = 42, height = 5,command = image_select)
		button4 = tkinter.Button(master,text='exit',width = 42, height = 5,command = quitter)
		button1.place(x=0,y=300) 
		userentry.place(x=221,y=328)
		button2.place(x=0,y=375)
		iterspin.place(x=270,y=403)
		button3.place(x=0,y=450)
		button4.place(x=0,y=525)
		canvas.pack()
		master.mainloop()
		
	def mbox(self,msg, b1='OK', b2='Cancel', frame=True, t=False, entry=False):
		msgbox = MessageBox(msg, b1, b2, frame, t, entry)
		msgbox.root.mainloop()
		msgbox.root.destroy()
		return msgbox.returning

if __name__=='__main__':
	aa = AA()
	root = tkinter.Tk()
	root.wm_resizable(0,0)
	test = Gui(root,aa)
	root.mainloop()
