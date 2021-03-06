# to-do
# settings, overall stats
# menu

# cute animations while stuff is happening lol

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkmessagebox
import tkinter.simpledialog as tksimpledialog
import tkinter.filedialog as tkfiledialog

import time
import os
from io import BytesIO
import pickle
from PIL import ImageTk, Image

from urllib.request import urlretrieve
import json
import requests 

import queue
import threading

try:
	from .tkdnd_wrapper import TkDND
	from .brains import *
except:
	from tkdnd_wrapper import TkDND
	from brains import *


debug = False

class AA:
	def __init__(self):
			self.ready_to_test = False
			if not os.path.exists('./saves/'):
				os.makedirs('./saves/')
			if not os.path.exists('./saves/savedata'):
				self.username = 'OJClock' # mine
				self.api_key = '874b1cf6420f724a52da51478cbf02f5' #public key no worries
				self.n_pages = 2
				self.total = 99
				self.n_correct = 0
				self.n_tested = 0
				self.save_data()
				self.load_library()

			else:
				read = open('./saves/savedata','rb')

				try:
					saved_dict = pickle.load(read)
					read.close()
					self.username = saved_dict['username'] # last user (or default)
					self.api_key = saved_dict['api_key']
					self.n_pages = saved_dict['n_pages']
					self.total = saved_dict['n_total']
					self.n_correct = saved_dict['n_correct']
					self.n_tested = saved_dict['n_tested']
					self.load_library()
					print('loaded {0}\'s library'.format(self.username))
					self.brains = Brains(self.library)
					self.ready_to_test = True 

				except:
					read.close()
					os.remove('./saves/savedata')
					self.__init__()
				
		

	def set_user(self,u):
		if u != '' and u != self.username:
			self.save_library()
			self.username = u
			self.load_library()
		#if not self.ready_to_test:
		self.init_db()

	def how_many(self,n):
		if n != self.total:
			self.ready_to_test = False
		self.n_pages = (n // 50) + 1
		self.total = n

	def stats(self):
		if self.n_tested > 0:
			return self.n_correct/self.n_tested
		else:
			return 0

	def correct(self):
		self.n_correct += 1

	def init_db(self):
		print('initializing db for',self.username)
		for i in range(self.n_pages):
			resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user="+ self.username +"&page="+str(i+1)+ "&api_key="+self.api_key+"&format=json")
			resp = resp.json()
			try:
				albums = resp['topalbums']['album']
			except:
				print('error with api call, invalid username?')
			to_end = self.total - i * 50
			if to_end <= 0: break
			for a in albums[:to_end]:
				new_alb = Album(a['artist']['name'],a['name'],a['image'])
				self.add_alb(new_alb)
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

	def add_alb(self,alb):
		if alb.__str__() not in self.library:
			self.library[alb.__str__()] = alb

	def add_to_brains(self,alb):
		self.add_alb(alb)
		if self.ready_to_test: self.brains.add_album_post_train(alb)

	def tester(self,img):
		if not self.ready_to_test: return
		self.n_tested += 1
		return self.brains.meaningful_test(img,0.66)

	def load_library(self):
		if not os.path.exists('./saves/'+self.username):
			self.library = {}
			self.ready_to_test = False
		else:
			savedlibrary = open('./saves/'+self.username,'rb')
			self.library = pickle.load(savedlibrary)
			savedlibrary.close()
			self.brains = Brains(self.library)

	def load_from_file(self,file):
		try:
			savedlibrary = open(file,'rb')
			self.library = pickle.load(savedlibrary)
			savedlibrary.close()
			self.brains = Brains(self.library)
			return True
		except:
			tkmessagebox.showerror('error','could not open library\n{0}'.format(file))
			return False
		

	def save_library(self):
		savedlibrary = open('./saves/'+self.username,'wb')
		pickle.dump(self.library,savedlibrary)
		savedlibrary.close()

	def save_data(self):
		new_dict = {}
		new_dict['username'] = self.username
		new_dict['api_key'] = self.api_key
		new_dict['n_pages'] = self.n_pages
		new_dict['n_total'] = self.total
		new_dict['n_correct'] = self.n_correct
		new_dict['n_tested'] = self.n_tested
		savedata = open('./saves/savedata','wb')
		pickle.dump(new_dict,savedata)
		savedata.close()

	def quit(self):
		self.save_data()
		self.save_library()

class Album:
	def __init__(self,artist,album,images):
		if not os.path.exists('./idb/'):
			os.makedirs('./idb/')
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
		return "".join(char for char in s if char not in "\/:*?<>|.")

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

class ThreadedTask(threading.Thread):
	def __init__(self, queue,task):
		threading.Thread.__init__(self)
		self.queue = queue
		self.task = task
	def run(self):
		try:
			self.task()
			self.queue.put("Task finished")
		except:
			raise
class Gui:
	def __init__(self, master):      

		# overarching vars

		self.dnd = TkDND(master)
		self.img_file = ""
		self.aa = None  

		self.user = tk.StringVar()
		self.n_total = tk.StringVar()
		
		# button functions

		def user_select(*args): # init db button
			self.queue = queue.Queue()
			userget = lambda : self.aa.set_user(self.user.get())
			toggle_disable()
			start_anim()
			ThreadedTask(self.queue,userget).start()
			master.after(100, process_queue)

		def n_select(*args): # number of albums entry
			try:
				self.aa.how_many(int(self.n_total.get()))
			except:
				return

		def image_select(): # test button
			if self.img_file == "":
				return
			response = self.aa.tester(self.img_file)
			TestResults(master,response,self.aa)

		def test_from_url(*args): # test from url button
			url = tksimpledialog.askstring("test from url","pls input url")
			if not url:
				return
			url = url.strip()
			try:
				try:
					response = requests.get(url)
				except: # i'd rather not but idk
					response = requests.get(url,verify=False)
				new_img = Image.open(BytesIO(response.content))
				new_img = new_img.resize((300, 300),Image.ANTIALIAS)
				new_img.save("current_test.png")
				self.img_file="current_test.png"
				self.new_img = ImageTk.PhotoImage(Image.open(self.img_file))
				img_canvas.create_image((0,0),image=self.new_img,anchor=tk.NW)
			except:
				self.img_file=""
				return
			image_select()

		def test_dnd(event,*args): # test button
			try: 
				if event.data[0] == '{': 
					self.img_file = event.data[1:-1]
				else:
					self.img_file = event.data
				self.new_img = ImageTk.PhotoImage(Image.open(self.img_file).resize((300, 300),Image.ANTIALIAS))
				self.albumart = img_canvas.create_image((0,0),image=self.new_img,anchor=tk.NW)
			except:
				self.img_file=""

		# tk elements

		img_canvas = tk.Canvas(master,width=300,height=300)
		self.new_img = ImageTk.PhotoImage(Image.open('test.png')) # standard image (says drag-n-drop here)
		self.albumart = img_canvas.create_image((0,0),image=self.new_img,anchor=tk.NW)

		start_frame = tk.Frame(master)
		init_but = tk.Button(start_frame,text='init database', width = 30, height = 5,command = user_select)
		user_frame = tk.Frame(start_frame)
		user_label = tk.Label(user_frame,text='username:')
		user_entry = tk.Entry(user_frame,textvariable=self.user,width=11,justify='center')
		no_label = tk.Label(user_frame,text='# albums:')
		no_entry = tk.Spinbox(user_frame,from_=0,to=250,textvariable=self.n_total,justify=tk.RIGHT,width=3)
		
		test_frame = tk.Frame(master)
		test_but = tk.Button(test_frame,text='test',width = 30, height = 5,command = image_select)
		test_from_url_but = tk.Button(test_frame,text='from url', width = 10, height = 5, command = test_from_url)

		# tk binding
		self.n_total.trace('w',n_select)
		self.dnd.bindtarget(img_canvas, test_dnd, 'text/uri-list')

		# tk packing (layout)

		img_canvas.pack(side=tk.TOP)
		
		test_frame.pack()
		test_but.pack(side=tk.LEFT)
		test_from_url_but.pack()

		init_but.pack(side=tk.LEFT)
		user_label.pack()
		user_entry.pack()
		no_label.pack()
		no_entry.pack()
		user_frame.pack(side=tk.RIGHT)
		start_frame.pack()

		# animations

		self.loading_texts = []
		self.loading_rects = []
		for i in range(4):
			datext = 'loading'+ '.'*i
			loading_text = img_canvas.create_text((150,150),text=datext,font="-weight bold -size 16")
			loading_rect = img_canvas.create_rectangle(img_canvas.bbox(loading_text),fill="gray")
			img_canvas.tag_lower(loading_rect,loading_text)
			self.loading_texts.append(loading_text)
			self.loading_rect = loading_rect # want largest bounding

		img_canvas.tag_raise(self.albumart)

		def loading_anim():
			if self.anim_counter >= 0: 
				img_canvas.tag_raise(self.loading_rect)
				img_canvas.tag_raise(self.loading_texts[self.anim_counter])
				img_canvas.update()
				#time.sleep(0.5)
				self.anim_counter = (self.anim_counter + 1) % 4
				master.after(100, loading_anim)

		def start_anim():
			self.anim_counter = 0
			loading_anim()

		def stop_anim():
			self.anim_counter = -1
			img_canvas.tag_raise(self.albumart)
		
		# menubar functions

		def album_searcher():
			AlbumSearch(self.aa)

		def stat_display():
			StatDisp(self.aa)

		def open_lib():
			# first save current
			self.aa.save_library()
			# keep track if this works or no
			self.load_success = False
			# then ask for new and open it
			filename = tkfiledialog.askopenfilename(initialdir="./saves")
			if filename:
				self.queue = queue.Queue()

				def load_file():
					self.load_success = self.aa.load_from_file(filename)

				toggle_disable()
				start_anim()
				username = filename[filename.rfind('/')+1:]
				ThreadedTask(self.queue,load_file).start()
				p_q = lambda : process_queue_open_lib(username)
				master.after(100, p_q)

		# menubar

		menubar = tk.Menu(master)
		filemenu = tk.Menu(menubar,tearoff=0)
		filemenu.add_command(label="open saved library",command=open_lib)
		filemenu.add_separator()
		filemenu.add_command(label="about",command=StatDisp)
		menubar.add_cascade(label='file',menu=filemenu)
		librarymenu = tk.Menu(menubar,tearoff=0)
		librarymenu.add_command(label='stats',command=stat_display)
		librarymenu.add_command(label='search for album to add',command=album_searcher)
		menubar.add_cascade(label='library',menu=librarymenu)

		master.config(menu=menubar)

		# extra functions
		def toggle_disable():
			e_or_d = init_but['state'] == 'normal'
			for but in [init_but,test_but,test_from_url_but,user_entry,no_entry]:
				if e_or_d:
					but.config(state='disabled')
				else:
					but.config(state='normal')
			if e_or_d:
				menubar.entryconfig("file",state='disabled')
				menubar.entryconfig("library",state='disabled')
			else:
				menubar.entryconfig("file",state='normal')
				menubar.entryconfig("library",state='normal')

		def start_aa():
			self.queue = queue.Queue()

			def make_aa():
				self.aa = AA()

			toggle_disable()
			start_anim()
			ThreadedTask(self.queue,make_aa).start()
			master.after(100,process_queue_start)

		def quitter():
			self.aa.quit()
			master.destroy()

		master.protocol("WM_DELETE_WINDOW", quitter)
		filemenu.add_command(label="quit",command=quitter)

		# threading functions
		
		def process_queue(): # for init db
			try:
				msg = self.queue.get(0)
				stop_anim()
				toggle_disable()
			except queue.Empty:
				master.after(100, process_queue)

		def process_queue_open_lib(username): # for open lib (in menu)
			try:
				msg = self.queue.get(0)
				if self.load_success:
					self.user.set(username)
					self.aa.username = username
					print('loaded {0}\'s library'.format(username))
				else:
					self.aa.load_library()
				stop_anim()
				toggle_disable()
			except queue.Empty:
				do_again = lambda : process_queue_open_lib(username)
				master.after(100, do_again)

		def process_queue_start():
			try:
				msg = self.queue.get(0)
				self.user.set(self.aa.username) 
				self.n_total.set(self.aa.total) 
				stop_anim()
				toggle_disable()
			except queue.Empty:
				master.after(100, process_queue_start)

		#test_it = tk.Button(master,text='just f my s up',width = 42, height = 5,command = toggle_disable)
		#stop_it = tk.Button(master,text='just s my f up',width = 42, height = 5,command = stop_anim)
		#test_it.pack()
		#stop_it.pack()

		# ok now everything is rdy
		#self.aa = AA() # thread me
		start_aa()

		master.mainloop()

class TestResults:
	def __init__(self,master,response,aa):			
		"""
		popup with album u got, asks if this is right or not, if not go to next img, if closed close out
		if exhaust the list ask if you want to add the album? - that'll take some finnagling -.-
		
		looks like
		[] (album art)
		artist- album
		is this ur album
		y/n
		"""
		# vars
		self.responses = response
		self.aa = aa

		self.guess = next(self.responses) # first guess
		first_album_art = self.aa.library[self.guess].get_img('xl')
		# tk stuff
		self.top = tk.Toplevel()
		self.top.title('test')
		self.top.wm_resizable(0,0)
		img = ImageTk.PhotoImage(Image.open(first_album_art))
		self.img_label = tk.Label(self.top,image=img)
		self.img_label.image = img
		self.img_label.pack()
		self.albumname = tk.Label(self.top,text=self.guess)
		self.albumname.pack()
		tk.Label(self.top, text='is this your album?').pack()
		yesnoframe = tk.Frame(self.top)
		yes = tk.Button(yesnoframe,text="yes",command=self.quit_success)
		no = tk.Button(yesnoframe,text="no",command=self.go_next)
		yes.pack(side=tk.LEFT,expand=tk.YES)
		no.pack(side=tk.RIGHT)
		yesnoframe.pack()

	def go_next(self,*args):
		try:
			self.next_alb()
		except:
			self.quit_fail()
			return
		new_album_art = self.aa.library[self.guess].get_img('xl')
		new_img = ImageTk.PhotoImage(Image.open(new_album_art))
		self.img_label.config(image=new_img)
		self.img_label.image = new_img
		self.albumname.config(text=self.guess)

	def next_alb(self):
		self.guess = next(self.responses)

	def quit_success(self):
		self.aa.correct()
		self.top.destroy()

	def quit_fail(self):
		# ask if want 2 look it up + add 2 library
		self.top.destroy()
		if tkmessagebox.askokcancel("lookup","want to search for this album and add it to the database?"):
		# open up new search thing
			AlbumSearch(self.aa)

class AlbumSearch:
	def __init__(self,aa):
		self.aa = aa

		# tk
		self.top = tk.Toplevel()
		self.top.title('search')
		self.search_query = tk.StringVar()
		self.entry_frame = tk.Frame(self.top)
		self.search_field = tk.Entry(self.entry_frame,textvariable=self.search_query)
		self.search_button = tk.Button(self.entry_frame,text='srch',command=self.search)
		self.entry_frame.pack()
		self.search_frame = tk.Frame(self.top)
		self.search_tree = ttk.Treeview(self.search_frame,selectmode='browse', show='tree')#, height = 20)
		self.search_field.bind("<Return>",self.search)
		self.search_field.pack(side=tk.LEFT,anchor=tk.N,fill=tk.X)
		self.search_button.pack()
		self.search_tree.pack(side=tk.LEFT,anchor=tk.N,fill=tk.BOTH,expand=tk.Y)#.grid(row=2,column=1,sticky=tk.N) 
		self.ysb = ttk.Scrollbar(self.search_frame, orient='vertical', command=self.search_tree.yview)
		self.search_tree.configure(yscrollcommand=self.ysb.set)
		self.ysb.pack(side=tk.RIGHT,anchor=tk.N,fill=tk.Y)
		self.search_frame.pack(side=tk.TOP,anchor=tk.N,fill=tk.BOTH,expand=tk.Y)
		self.search_tree.bind('<Double-1>',self.select_album)


	def select_album(self,*args):
		item = self.search_tree.selection()[0]
		name = self.search_tree.item(item,"text")
		ind = int(self.search_tree.item(item,"values")[0])
		
		artist = self.last_search_res[ind]['artist']
		album = self.last_search_res[ind]['name']
		images = self.last_search_res[ind]['image']
		
		new_alb = Album(artist,album,images)
		self.aa.add_to_brains(new_alb)
		self.aa.n_tested -= 1
		self.top.destroy()

	def search(self,*args):
		query = self.search_query.get()
		resp = requests.get("http://ws.audioscrobbler.com/2.0/?method=album.search&album="+ query + "&api_key="+self.aa.api_key+"&format=json")
		resp = resp.json()
		self.last_search_res = resp['results']['albummatches']['album']
		# delete everything in search tree
		self.search_tree.delete(*self.search_tree.get_children())
		# insert new albums
		for ind,album in enumerate(self.last_search_res):
			name = "{0} - {1}".format(album['artist'],album['name'])
			self.search_tree.insert('', 'end', text=name,values=ind)

class StatDisp():
	"""
	small popup with overall stats
	overall test accuracy: __%
	user's library with # of albums learned
	if no aa supplied then this functions as about box : ^)
	"""
	def __init__(self,aa=None):
		self.top = tk.Toplevel()

		if aa == None: # info
			self.top.title('about')
			text1 = 'aal by mc escherr'
			text2 = 'test images against your top last.fm albums'
		else:
			self.top.title('stats')
			text2 = 'overall test accuracy {0}%'.format(round(100*aa.stats(),1))
			text1 = '{0}\'s library has {1} albums learned'.format(aa.username,len(aa.library))

		tk.Label(self.top,text=text1).pack()
		tk.Label(self.top,text=text2).pack()

def main(*args):
	root = tk.Tk()
	root.wm_resizable(0,0)
	root.title('aal')
	test = Gui(root)

if __name__=='__main__':
	main()
	
	
	
