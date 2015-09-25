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
		for a in library:
			self.add_album(a)
		finalX = np.zeros(len(self.X),len(self.X[0]))
		for i in range(len(self.X)):
			finalX[i,:] = self.X[i]
		self.X = finalX

	def add_album(self,album):
		#print(album.images)
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
	    out = np.array(out).astype(np.float32)
	    out = np.ravel(out)
	    out -= out.mean()
	    out /= out.std()
	    return out

	def test_img(self,filename,thres=0.5):
		test = self.process_img(filename)
		test_cos = cosine_similarity(test,self.X)[0]
		return np.where(test_cos > thres)[0] # except we want in order of best fit first

	def meaningful_test(self,filename,thres=0.5):
		self.test_img(filename,thres)