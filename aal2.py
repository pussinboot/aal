import numpy as np

from skimage import io
from skimage.transform import resize
from sklearn.metrics.pairwise import cosine_similarity

from aa import *

class Brains():
	"""
	store representations of albums, test new albums, add new ones as needed
	"""
	def __init__(self,library):
		self.X = []
		self.y = []
		self.y_to_name = []
		for a in library:
			self.add_album(a)
		finalX = np.zeros((len(self.X),len(self.X[0])))
		for i in range(len(self.X)):
			finalX[i,:] = self.X[i]
		self.X = finalX
		self.y = np.asarray(self.y)

	def add_album(self,album):
		fnames = album.images.values()
		nsamp = len(fnames)
		if nsamp == 0: return
		this_y = len(self.y_to_name) # new y index 
		self.y_to_name.append(album.__str__())
		for fname in fnames:
			self.y.append(this_y)
			self.X.append(self.process_img(fname))

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
		largest = np.argpartition(test_cos, -4*n_albums)[-4*n_albums:]
		largest_in_order = largest[np.argsort(test_cos[largest])][::-1]
		#print(self.y[largest_in_order])
		return list(set(self.y[largest_in_order]))

	def meaningful_test(self,filename,thres=0.5):
		# generator for album titles
		nos = self.test_img(filename,thres)
		i = 0
		while i < len(nos):
			yield self.y_to_name[nos[i]]
			i += 1

if __name__ == '__main__':

	test_aa = AA()
	test_aa.init_db()
	my_brain = Brains(test_aa.library)
	print(my_brain.test_img("./MyBloodyValentineLoveless.jpg"))
	mbv  = my_brain.meaningful_test("./MyBloodyValentineLoveless.jpg")
	for name in mbv:
		print(name)
	#print(next(mbv))
