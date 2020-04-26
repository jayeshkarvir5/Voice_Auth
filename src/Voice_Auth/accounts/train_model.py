#train_models.py
import os
import pickle
import numpy as np
from scipy.io.wavfile import read
from sklearn.mixture import GaussianMixture
from accounts.extract_mfcc import extract_features
#from speakerfeatures import extract_features
import warnings
warnings.filterwarnings("ignore")
import time
from Voice_Auth import settings


def createGMM(username):
	print("creating GMM for "+username)
	#path to training data
	source   = settings.MEDIA_ROOT + "\\"

	#path where training speakers will be saved
	dest = settings.MEDIA_ROOT + "\\" + "speaker_models\\"

	train_file = settings.MEDIA_ROOT + "\\" + "dev_set.txt"
	file_paths = open(train_file,'r')

	# Extracting features for each speaker (5 files per speakers)
	features = np.asarray(())
	for path in file_paths:
		path = path.strip()
		print(path)

		# read the audio
		sr,audio = read(source + path)

		# extract 40 dimensional MFCC & delta MFCC features
		vector   = extract_features(audio,sr)

		if features.size == 0:
			features = vector
		else:
			features = np.vstack((features, vector))

	gmm = GaussianMixture(n_components = 16, covariance_type='diag',n_init = 3)
	gmm.fit(features)

	# dumping the trained gaussian model
	picklefile = path.split("-")[0]+".gmm"
	pickle.dump(gmm,open(dest + picklefile,'wb'))
	print('+ modeling completed for speaker:',picklefile," with data point = ",features.shape)
