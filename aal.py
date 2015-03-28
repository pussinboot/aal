# thanks
# http://corpocrat.com/2014/10/10/tutorial-pybrain-neural-network-for-classifying-olivetti-faces/
# to-do
# DONE import last.fm albums 
# DONE album art in 4 diff sizes -> fft representation
# DONE this means input data needs to be resized, add 1 node for each album
# NEEDS WORK shitty gui
# aka fix ^

from sklearn 								import datasets
from sklearn.preprocessing					import normalize
from pybrain.datasets            			import ClassificationDataSet
from pybrain.utilities           			import percentError
from pybrain.tools.shortcuts     			import buildNetwork
from pybrain.supervised.trainers 			import BackpropTrainer
from pybrain.structure.modules   			import SoftmaxLayer
from pybrain.tools.customxml.networkwriter  import NetworkWriter
from pybrain.tools.customxml.networkreader  import NetworkReader
from aa 									import *
from PIL 									import Image
import os, numpy

datadim = 34
datasize = datadim**2 # feature size

class Brains():
	"""
	variables are: fnn - network state, trndata - training data, tstdata - testing data, datashape - shape of input data

	"""
	def __init__(self,library):
		# load data
		#olivetti = datasets.fetch_olivetti_faces()
		#X, y = olivetti.data, olivetti.target
		I = ImDb(library)
		X = I.get_X()
		y = I.get_y()
		# use I.get_name() with corresponding y to get test result??
		self.datashape = X.shape
		final_count = I.get_count()
		#print(X.shape)
		# create data set
		ds = ClassificationDataSet(datasize, 1 , nb_classes=final_count)
		for k in range(len(X)):
			ds.addSample(numpy.ravel(X[k]),y[k])
		# reshape data
		tstdata_temp, trndata_temp = ds.splitWithProportion( 0.25 )
		
		self.tstdata = ClassificationDataSet(datasize, 1, nb_classes=final_count)
		for n in range(0, tstdata_temp.getLength()):
			self.tstdata.addSample( tstdata_temp.getSample(n)[0], tstdata_temp.getSample(n)[1] )
		
		self.trndata = ClassificationDataSet(datasize, 1, nb_classes=final_count)
		for n in range(0, trndata_temp.getLength()):
			self.trndata.addSample( trndata_temp.getSample(n)[0], trndata_temp.getSample(n)[1] )
		
		#print( trndata['input'], trndata['target'], tstdata.indim, tstdata.outdim)
		# read or create network
		# check to see if the data is same as before
		# if it is, just load the network???
		if  os.path.isfile('saved_net.xml'): 
			self.fnn = NetworkReader.readFrom('saved_net.xml') 
		else:
			self.fnn = buildNetwork( self.trndata.indim, datadim , self.trndata.outdim, outclass=SoftmaxLayer )
	
	def train(self,n_iter=5):
		trainer = BackpropTrainer( self.fnn, dataset=self.trndata, momentum=0.1, verbose=True, weightdecay=0.01) 
		trainer.trainEpochs (n_iter)
		print( 'Percent Error on Test dataset: ' , percentError( trainer.testOnClassData (dataset=self.tstdata ) , self.tstdata['class'] ))
	
	def test(self,testdata):
		out = self.fnn.activateOnDataset(testdata)
		out = out.argmax(axis=1)
		out = out.reshape(self.datashape)
		return out

	def quit(self):
		# write network
		NetworkWriter.writeToFile(self.fnn, 'saved_net.xml')

class ImDb():
	"""
	image database for learning 
	properly handles image files from last.fm
	"""
 
	def __init__(self,library): 
		self.X = [] # images
		self.y = [] # classifier
		self.y_to_name = []
		self.count = 0
		for a in library:
			self.add(a)

	def add(self,album):
		# resize/fft the image and add to db
		# remember to add the name as well
		im_sizes = ['s','m','l','xl']
		self.y_to_name.append(str(album))
		for i in range(len(im_sizes)):
			try:
				temp_img = self.fix_img(album.get_img(im_sizes[i]))
				temp_img = self.throwaway(temp_img,datadim)
				temp_img = normalize(temp_img)
				self.X.append(temp_img)
				self.y.append(self.count)
			except:
				print(im_sizes[i],'missing from', album)
		self.count += 1

	def fix_img(self,file):
		try:
			i = Image.open(file)
		except:
			print('file not found (',file,')')
			return
		i = i.convert('L') # grayscale
		a = numpy.asarray(i) # read only :(
		b = abs(numpy.fft.rfft2(a)) # fft
		return b

	def throwaway(self,a,k): # randomly keep k of the array a (in each dim)
		if k > len(a):
			return a
		else:
			i = numpy.random.choice(len(a), k) 
			b = a[i]		
			c = numpy.empty([k,k])
			for i in range(k):
				#print(k-len(b[i]))

				if k < len(b[i]):
					c[i] = b[i][numpy.random.choice(len(b[i]), k)]
				else:
					c[i][:len(b[i])], c[i][len(b[i]):] = b[i],numpy.zeros(k-len(b[i]))
			return c

	def get_X(self):
		return numpy.asarray(self.X)

	def get_y(self):
		return numpy.asarray(self.y)

	def get_name(self,y):
		try:
			tor = self.y_to_name[y]
		except:
			tor = 'not found'
		return tor

	def get_count(self):
		return self.count

if __name__=='__main__':
	#b = Brains()
	#b.train(1)
	#b.quit()#
	I = ImDb()
	test_album = Album('Kitty Pryde', 'The Lizzie Mcguire Experience', [{'#text': 'http://userserve-ak.last.fm/serve/34s/78192478.jpg', 'size': 'small'}, {'#text': 'http://userserve-ak.last.fm/serve/64s/78192478.jpg', 'size': 'medium'}, {'#text': 'http://userserve-ak.last.fm/serve/126/78192478.jpg', 'size': 'large'}, {'#text': 'http://userserve-ak.last.fm/serve/300x300/78192478.jpg', 'size': 'extralarge'}])
	#print(test_album.get_img('s'))
	#temp_img = I.fix_img(test_album.get_img('s'))
	#print(len(temp_img),len(temp_img[0]))
	#print('throwaway')
	#temp_img = I.throwaway(temp_img,datadim)
	#print(len(temp_img),len(temp_img[0]))
	#print(temp_img)
	I.add(test_album)
	print(len(I.get_X()))
	#print(I.get_y())
	print(I.get_name(0))