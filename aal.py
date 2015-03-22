# thanks
# http://corpocrat.com/2014/10/10/tutorial-pybrain-neural-network-for-classifying-olivetti-faces/

from sklearn 								import datasets
from pybrain.datasets            			import ClassificationDataSet
from pybrain.utilities           			import percentError
from pybrain.tools.shortcuts     			import buildNetwork
from pybrain.supervised.trainers 			import BackpropTrainer
from pybrain.structure.modules   			import SoftmaxLayer
from pybrain.tools.customxml.networkwriter  import NetworkWriter
from pybrain.tools.customxml.networkreader  import NetworkReader
from numpy 									import ravel
import os

class Brains():
	"""
	so far working with olivetti faces data example
	variables are: fnn - network state, trndata - training data, tstdata - testing data, datashape - shape of input data

	"""
	def __init__(self):
		# load data
		olivetti = datasets.fetch_olivetti_faces()
		X, y = olivetti.data, olivetti.target
		self.datashape = X.shape
		#print(X.shape)
		# create data set
		ds = ClassificationDataSet(4096, 1 , nb_classes=40)
		for k in range(len(X)):
			ds.addSample(ravel(X[k]),y[k])
		# reshape data
		tstdata_temp, trndata_temp = ds.splitWithProportion( 0.25 )
		
		self.tstdata = ClassificationDataSet(4096, 1, nb_classes=40)
		for n in range(0, tstdata_temp.getLength()):
			self.tstdata.addSample( tstdata_temp.getSample(n)[0], tstdata_temp.getSample(n)[1] )
		
		self.trndata = ClassificationDataSet(4096, 1, nb_classes=40)
		for n in range(0, trndata_temp.getLength()):
			self.trndata.addSample( trndata_temp.getSample(n)[0], trndata_temp.getSample(n)[1] )
		
		#print( trndata['input'], trndata['target'], tstdata.indim, tstdata.outdim)
		# read or create network
		if  os.path.isfile('oliv.xml'): 
			self.fnn = NetworkReader.readFrom('oliv.xml') 
		else:
			self.fnn = buildNetwork( self.trndata.indim, 64 , self.trndata.outdim, outclass=SoftmaxLayer )
	
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
		NetworkWriter.writeToFile(self.fnn, 'oliv.xml')

if __name__=='__main__':
	b = Brains()
	b.train(1)
	b.quit()