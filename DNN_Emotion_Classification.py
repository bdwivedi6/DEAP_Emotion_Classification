# -*- coding: utf-8 -*-
"""DNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1A8PopzM2HOJbkxC339zsLDpEhgG_BnWz
"""



print(emotion_label.size)
print(emotion_label)

from __future__ import absolute_import, division, print_function, unicode_literals


import tensorflow as tf

from tensorflow.keras import datasets, layers, models

from __future__ import absolute_import, division, print_function, unicode_literals

import _pickle as cPickle
import numpy as np
import argparse
from tempfile import TemporaryFile
#import tensorflow as tf



#outfile = TemporaryFile()

print("\nLabels: Valence, Arousal, Dominance, Liking\n")

num_users=6
num_entries=40 * num_users



VA=np.empty([num_entries, 2]) #Valence, Arousal
emotion=[0]*num_entries
k=0
entry =0

electrodes = [3,6,10,13,16,19,20,28]#np.arange(0,32)# [3,6,10,13,16,19,20,28]# np.arange(0,32)
num_electrodes = len(electrodes)
#num_electrodes = 32
new_data= np.empty([num_entries,num_electrodes,8064]) # [40, 8 * 8064]

for name in [7,8,10,16,19,20]:#range(1,num_users+1):

  if(name<10):
    file='/content/drive/My Drive/data_preprocessed_python/s0'+str(name)+'.dat'
  else:
    file='/content/drive/My Drive/data_preprocessed_python/s'+str(name)+'.dat'
  print(file)
  x = cPickle.load(open(file, 'rb'),encoding='latin1')


  for i in range(0,40):
    VA[i][0]=(x["labels"][i][0]) #Valence
    VA[i][1]=(x["labels"][i][1]) #Arousal
    if(VA[i][1] <= 4.5):
      if ( VA[i][0] <= 4.5 ) :
        emotion[entry] = 0 #"Sad"
      else:
        emotion[entry] = 1
			#elif(VA[i][1] <=6.34):
				#emotion[entry]= 1 #"Frustrated"
			#else:
				#emotion[entry]=2 #"Fear"
    if ( VA[i][1] > 4.5 ) :
      if(VA[i][0] <= 4.5):
        emotion[entry]=2#Satisfied"
      else:
        emotion[entry]=3
			#elif(VA[i][1] <=6.34):
				#emotion[entry]= 4 #"Pleasant"
			#else:
				#emotion[entry]=5 #"Happy"

    for j in electrodes: #range(0,32):#[1,3,4,6,7,19,21,26]:# range(0,num_electrodes):
      #print(x["data"][i][j],"\n")
      for l in range(0,8064):
        new_data[entry][k][l]=x["data"][i][j][l]
      k+=1
		#	print("\nk,j:",k, j)
    k=0
    entry+=1
emotion_label=np.asarray(emotion)
print(emotion_label)
print(new_data.shape)

'''
We divide the 8064 readings per channel, into 10
batches of approximately 807 readings each. For each batch
we extract the mean, median, maximum, minimum, standard
deviation, variance, range, skewness and kurtosis values for
the 807 readings. Hence for each of the 10 batches of a single channel we extract 9 values mentioned above, we get 90
values as our processed dataset. We further add the net mean,
median, maximum, minimum, standard deviation, variance,
range, skewness and kurtosis values for the entire 8064 readings along with the experiment and participant number to
our dataset, bringing it up to 101 values per channel.
'''
import scipy
from scipy import stats, optimize, interpolate
new_data_processed = np.empty([num_entries,num_electrodes,99])
index = 0
print("\nNew_data original shape:",new_data.shape)
for i in range(0,num_entries):
  for j in range(0,num_electrodes):
    index = 0
    for k in range(0,7264,807):
      if k!=7263:
        chunk = new_data[i][j][k:k+807]
      else:
        chunk = new_data[i][j][k:8065]
      #print("\nChunk shape:",chunk.shape)

      new_data_processed[i][j][index] = np.mean(chunk)
      index += 1
      new_data_processed[i][j][index] = np.median(chunk)
      index += 1
      new_data_processed[i][j][index] = np.max(chunk)
      index += 1
      new_data_processed[i][j][index] = np.min(chunk)
      index += 1
      new_data_processed[i][j][index] = np.std(chunk)
      index += 1
      new_data_processed[i][j][index] = np.var(chunk)
      index += 1
      new_data_processed[i][j][index] = np.max(chunk) - np.min(chunk)
      index += 1
      new_data_processed[i][j][index] = scipy.stats.skew(chunk)
      index += 1
      new_data_processed[i][j][index] = scipy.stats.kurtosis(chunk)
      index += 1

    new_data_processed[i][j][index] = np.mean(new_data[i][j][:])
    index += 1
    new_data_processed[i][j][index] = np.median(new_data[i][j][:])
    index += 1
    new_data_processed[i][j][index] = np.max(new_data[i][j][:])
    index += 1
    new_data_processed[i][j][index] = np.min(new_data[i][j][:])
    index += 1
    new_data_processed[i][j][index] = np.std(new_data[i][j][:])
    index += 1
    new_data_processed[i][j][index] = np.var(new_data[i][j][:])
    index += 1
    new_data_processed[i][j][index] = np.max(new_data[i][j][:]) - np.min(new_data[i][j][:])
    index += 1
    new_data_processed[i][j][index] = scipy.stats.skew(new_data[i][j][:])
    index += 1
    new_data_processed[i][j][index] = scipy.stats.kurtosis(new_data[i][j][:])
    index += 1
    #print(index)

print("\nNew data processed shape:", new_data_processed.shape)

#new_data_preprocessed= new_data
import tensorflow as tf
import math
from tensorflow import keras
from tensorflow.keras import models, layers
from keras import optimizers
from keras.models import Sequential
from keras.optimizers import SGD
from keras.layers import Dense, Dropout, Activation

from sklearn.utils import shuffle
train_size = math.floor(new_data_processed.shape[0] * 0.8)
test_size = new_data_processed.shape[0] - train_size
new_data_processed,emotion_label=shuffle(new_data_processed,emotion_label)
test_y= emotion_label[train_size:train_size+test_size]
r=0
for i in range(0,len(emotion_label)):
  if emotion_label[i]==0:
    #print(emotion[i])
    r+=1
print(r)

#@title Default title text

train_x= new_data_processed[0:train_size][:][:]
train_y= emotion_label[0:train_size]
test_x= new_data_processed[train_size:train_size+test_size][:][:]
test_y= emotion_label[train_size:train_size+test_size]

print("\nTraining shape:",train_x.shape)
print("\nTesting shape:",test_x.shape)

model = models.Sequential([
    layers.Flatten(input_shape=(8, 99)),
    layers.Dropout(0.25),
    layers.Dense(5000, activation=tf.nn.relu),
    layers.Dropout(0.5),
    layers.Dense(500, activation=tf.nn.relu),
    layers.Dropout(0.5),
    layers.Dense(1000, activation=tf.nn.relu),
    layers.Dropout(0.5),
    layers.Dense(4, activation=tf.nn.softmax)
])

model.compile(optimizer=keras.optimizers.SGD(lr=1e-5),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy']) #'adam'

model.fit(train_x, train_y, epochs=100, batch_size=100)

test_loss, test_acc = model.evaluate(test_x, test_y)

print('Test accuracy:', test_acc)

predictions = model.predict(test_x)

for i in range(0,10):
	print("\nPredictions:", np.argmax(predictions[i]))

print("\n",test_y)

model.summary()