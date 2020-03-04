from Voice_Auth import settings
import os
import pickle
import numpy as np
from scipy.io.wavfile import read
from accounts.extract_mfcc import extract_features
import warnings
warnings.filterwarnings("ignore")


def identify_speaker(uname):
    # path to training data
    source = settings.MEDIA_ROOT + "\\"

    modelpath = settings.MEDIA_ROOT + "\\speaker_models\\"

    test_file = settings.MEDIA_ROOT + "\\test_set.txt"

    file_paths = open(test_file, 'r')

    print(source)
    print(modelpath)
    print(test_file)

    gmm_files = [os.path.join(modelpath, fname) for fname in
                 os.listdir(modelpath) if fname.endswith('.gmm')]

    # Load the Gaussian gender Models
    models = [pickle.load(open(fname, 'rb')) for fname in gmm_files]
    speakers = [fname.split("\\")[-1].split(".gmm")[0] for fname
                in gmm_files]

    # Read the test directory and get the list of test audio files
    s = {}
    for i in speakers:
        s[i] = 0

    for path in file_paths:
        # print(1)
        path = path.strip()
        print(path)
        sr, audio = read(source + path)
        vector = extract_features(audio, sr)

        log_likelihood = np.zeros(len(models))

        for i in range(len(models)):
            gmm = models[i]  # checking with each model one by one
            scores = np.array(gmm.score(vector))
            log_likelihood[i] = scores.sum()

        winner = np.argmax(log_likelihood)
        print(speakers[winner])
        print("\tdetected as - ", speakers[winner])
        print('Here')
        s[speakers[winner]] += 1

    print(s)
    max_count = max(s.values())
    for i in s.keys():
        if s[i] == max_count:
            return i
        # time.sleep(1.0)
