# album art
import tkinter as tk
import json
import requests 
import pickle

from urllib.request import urlretrieve
import os
#os.environ['TKDND_LIBRARY'] = 'C:/Python34/Lib/tkdnd2.8/'
from tkdnd_wrapper import TkDND
from aal2 import *
from mbox import MessageBox
from io import BytesIO
from PIL import ImageTk, Image

debug = False
class AA:
	def __init__(self):
			self.ready_to_test = False

			if not os.path.exists('./idb/savedata'):
				self.username = 'OJClock' # mine
				self.api_key = '874b1cf6420f724a52da51478cbf02f5' #public key no worries
				self.n_pages = 2
				self.total = 99
				self.save_data()
				self.load_library()
			else:
				read = open('./idb/savedata','rb')
				try:
					saved_dict = pickle.load(read)
					read.close()
					self.username = saved_dict['username'] # last user (or default)
					self.api_key = saved_dict['api_key']
					self.n_pages = saved_dict['n_pages']
					self.total = saved_dict['n_total']
					self.load_library()
					print('loaded',self.username,'\'s library')
					self.brains = Brains(self.library)
					self.ready_to_test = True 

				except:
					read.close()
					os.remove('./idb/savedata')
					self.__init__()
				
		

	def set_user(self,u):
		if u != '' and u != self.username:
			self.save_library()
			self.username = u
			self.load_library()
		if not self.ready_to_test:
			self.init_db()

	def how_many(self,n):
		if n != self.total:
			self.ready_to_test = False
		self.n_pages = (n+1) // 50
		self.total = n

	def init_db(self):
		print('initializing db')
		for i in range(self.n_pages):
			resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user="+ self.username +"&page="+str(i+1)+ "&api_key="+self.api_key+"&format=json")
			resp = resp.json()
			albums = resp['topalbums']['album']
			to_end = self.total - i * 50
			if to_end <= 0: break
			for a in albums[:to_end]:
				new_alb = Album(a['artist']['name'],a['name'],a['image'])
				if new_alb.__str__() not in self.library:
					self.library[new_alb.__str__()] = new_alb
		if debug:
			for x in self.library.values():
				print(x)
				print(x.get_img('s'))
				print(x.get_img('m'))
				print(x.get_img('l'))
				print(x.get_img('xl'))
		self.brains = Brains(self.library)
		self.ready_to_test = True 
		print('done')


	def tester(self,img):
		if not self.ready_to_test: return
		self.brains.test_img(img)

	def load_library(self):
		if not os.path.exists('./idb/'+self.username):
			self.library = {}
			self.ready_to_test = False
		else:
			savedlibrary = open('./idb/'+self.username,'rb')
			self.library = pickle.load(savedlibrary)
			savedlibrary.close()

	def save_library(self):
		savedlibrary = open('./idb/'+self.username,'wb')
		pickle.dump(self.library,savedlibrary)
		savedlibrary.close()

	def save_data(self):
		new_dict = {}
		new_dict['username'] = self.username
		new_dict['api_key'] = self.api_key
		new_dict['n_pages'] = self.n_pages
		new_dict['n_total'] = self.total
		savedata = open('./idb/savedata','wb')
		pickle.dump(new_dict,savedata)
		savedata.close()

	def quit(self):
		self.save_data()
		self.save_library()



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
			try:
				if not os.path.isfile(filepath): urlretrieve(i['#text'],filepath)
				self.images[i['size']] = filepath
			except:
				pass

	def safe(self,s):
		#return "".join(x for x in s if x.isalnum() or x == ' ')
		return "".join(char for char in s if char not in "\/:*?<>|")

	def __str__(self):
		return str(self.artist) + ' - ' + str(self.album)

	def get_img(self,size):
		lookup = {'s':'small','m':'medium','l':'large','xl':'extralarge'}
		try:
			return self.images[lookup[size]]
		except:
			if debug: print('failed to find',size)
	def get_src(self):
		return self.imagesource

class Gui:
	def __init__(self, master, aa):        
		self.aa = aa

		def quitter():
			self.aa.quit()
			master.destroy()

		master.protocol("WM_DELETE_WINDOW", quitter)
		
		self.user = tk.StringVar()
		self.user.set(self.aa.username)

		self.n_total = tk.StringVar()
		self.n_total.set(self.aa.total)

		def user_select(*args):
			self.aa.set_user(self.user.get())

		def n_select(*args):
			#print(self.n_total.get())
			try:
				self.aa.how_many(int(self.n_total.get()))
			except:
				return

		self.n_total.trace('w',n_select)

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

		img_canvas = tk.Canvas(master,width=300,height=300)
		#canvas.grid_propagate(False)
		#img = tkinter.PhotoImage(file = 'test.png')
		#self.panel = tkinter.Label(canvas,anchor=tkinter.NW)#, image = img)
		#self.panel.image = img
		#self.panel.place(x=0,y=0)
		img_canvas.pack(side=tk.TOP)

		start_frame = tk.Frame(master)
		init_but = tk.Button(start_frame,text='init database', width = 30, height = 5,command = user_select)
		user_frame = tk.Frame(start_frame)
		user_label = tk.Label(user_frame,text='username:')
		user_entry = tk.Entry(user_frame,textvariable=self.user,width=11)
		no_label = tk.Label(user_frame,text='# albums:')
		no_entry = tk.Spinbox(user_frame,from_=0,to=250,textvariable=self.n_total,justify=tk.RIGHT,width=3)

		init_but.pack(side=tk.LEFT)
		user_label.pack()
		user_entry.pack()
		no_label.pack()
		no_entry.pack()
		user_frame.pack(side=tk.RIGHT)
		start_frame.pack()

		test_but = tk.Button(master,text='test',width = 42, height = 5,command = image_select)
		quit_but = tk.Button(master,text='exit',width = 42, height = 5,command = quitter)
		
		test_but.pack()
		quit_but.pack()
		master.mainloop()
		
	def mbox(self,msg, b1='OK', b2='Cancel', frame=True, t=False, entry=False):
		msgbox = MessageBox(msg, b1, b2, frame, t, entry)
		msgbox.root.mainloop()
		msgbox.root.destroy()
		return msgbox.returning

if __name__=='__main__':
	aa = AA()
	root = tk.Tk()
	root.wm_resizable(0,0)
	test = Gui(root,aa)
	root.mainloop()
	#aa.set_user('theVerm1n')
	#aa.quit()
