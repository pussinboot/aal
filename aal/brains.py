import numpy as np

from skimage import io
from skimage.transform import resize
from sklearn.metrics.pairwise import cosine_similarity


class Brains():
	"""
	store representations of albums, test new albums, add new ones as needed
	"""
	def __init__(self,library):
		self.X = []
		self.y = []
		self.y_to_name = []
		for a in library.values():
			self.add_album(a)
		finalX = np.zeros((len(self.X),len(self.X[0])))
		for i in range(len(self.X)):
			finalX[i,:] = self.X[i]
		self.X = finalX
		self.y = np.asarray(self.y)

	def add_album(self,album):
		fnames = album.images.values()
		if len(fnames) == 0: return
		this_y = len(self.y_to_name) # new y index 
		self.y_to_name.append(album.__str__())
		for fname in fnames:
			self.y.append(this_y)
			self.X.append(self.process_img(fname))

	def add_album_post_train(self,album): # since we have numpy arrays, have to append (this is slower but what wil u do)
		fnames = album.images.values()
		if len(fnames) == 0: return
		this_y = len(self.y_to_name)
		self.y_to_name.append(album.__str__())
		for fname in fnames:
			self.y = np.append(self.y,this_y)
			self.X = np.vstack((self.X,self.process_img(fname)))
			
	def process_img(self,filename):
	    testim = io.imread(filename,as_grey=True)
	    out = resize(testim,(25,25))
	    out = np.ravel(out)
	    out -= out.mean()
	    out /= out.std()
	    return out[:625] # without this sometimes if an album cover is animated things break

	def test_img(self,filename,thres=0.5):
		test = self.process_img(filename)
		test_cos = cosine_similarity(test,self.X)[0]
		test_ind = self.y[np.where(test_cos > thres)[0]] # except we want in order of best fit first
		n_albums = len(set(test_ind))
		# something to note, what if an album has all 4 of its sizes match closely but less than just 1 size of another?
		# wouldn't that be a better choice? yes, but that ignores the fact that if something matches better, and it is actually correct
		# then its other sizes should also match well. so i have thought about this issue and decided in most cases looking at the mode 
		# first offers no benefits for increased computation.
		largest = np.argpartition(test_cos, -4*n_albums)[-4*n_albums:]
		largest_in_order = largest[np.argsort(test_cos[largest])][::-1]
		# unique, in order 
		tor = []
		[tor.append(y) for y in self.y[largest_in_order] if not tor.count(y)]
		return tor

	def meaningful_test(self,filename,thres=0.5):
		# generator for album titles
		nos = self.test_img(filename,thres)
		i = 0
		while i < len(nos) and i < 3: # artificial limit on epic results
			yield self.y_to_name[nos[i]]
			i += 1

if __name__ == '__main__':
	
	from .aal import *

	test_aa = AA()
	test_aa.init_db()
	my_brain = Brains(test_aa.library)
	print(my_brain.test_img("./MyBloodyValentineLoveless.jpg"))
	mbv = my_brain.meaningful_test("./MyBloodyValentineLoveless.jpg")
	for name in mbv:
		print(name)
	#print(next(mbv))
