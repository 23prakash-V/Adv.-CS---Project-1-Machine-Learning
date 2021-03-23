# -*- coding: utf-8 -*-
"""Machine Learning Project

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1z6-IrD_0YY7q0ZK4R8zmd_AXc1Kkx6py
"""

from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import model_selection
from sklearn.metrics import accuracy_score
from collections import Counter
import keras
from keras.models import Sequential
from keras.layers import Dense, Conv2D
from keras.layers import Activation, MaxPooling2D, Dropout, Flatten, Reshape
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def categorical_to_numpy(labels_in):
  labels = []
  for label in labels_in:
    if label == 'dog':
      labels.append(0)
    else:
      labels.append(1)
  return np.array(labels)

def one_hot_encoding(input):
  output = np.array(input)
  output = np.zeros((input.size, input.max()+1))
  output[np.arange(input.size),input] = 1
  
  return output


def load_data():
  import gdown
  gdown.download('https://drive.google.com/uc?id=1-BjeqccJdLiBA6PnNinmXSQ6w5BluLem','cifar_data','True'); # dogs v road;

  import pickle
  data_dict = pickle.load(open( "cifar_data", "rb" ));
  
  data   = data_dict['data']
  labels = data_dict['labels']
  
  return data, labels

def plot_one_image(data, labels, img_idx):
  from google.colab.patches import cv2_imshow
  import cv2
  import matplotlib.pyplot as plt
  my_img   = data[img_idx, :].squeeze().reshape([32,32,3]).copy()
  my_label = labels[img_idx]
  print('label: %s'%my_label)
  plt.imshow(my_img)
  plt.show()
  
def CNNClassifier(num_epochs=30, layers=5, dropout=0.5):
  def create_model():
    model = Sequential()
    model.add(Reshape((32, 32, 3)))
    
    for i in range(layers):
      model.add(Conv2D(32, (3, 3), padding='same'))
      model.add(Activation('relu'))
    
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout / 2.0))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(dropout / 2.0))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(dropout))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    opt = keras.optimizers.RMSprop(lr=0.0001, decay=1e-6)
    model.compile(loss='binary_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy'])
    return model
  return KerasClassifier(build_fn=create_model, epochs=num_epochs, batch_size=10, verbose=2)

def plot_acc(history, ax = None, xlabel = 'Epoch #'):
    history = history.history
    history.update({'epoch':list(range(len(history['val_accuracy'])))})
    history = pd.DataFrame.from_dict(history)

    best_epoch = history.sort_values(by = 'val_accuracy', ascending = False).iloc[0]['epoch']

    if not ax:
      f, ax = plt.subplots(1,1)
    sns.lineplot(x = 'epoch', y = 'val_accuracy', data = history, label = 'Validation', ax = ax)
    sns.lineplot(x = 'epoch', y = 'accuracy', data = history, label = 'Training', ax = ax)
    ax.axhline(0.5, linestyle = '--',color='red', label = 'Chance')
    ax.axvline(x = best_epoch, linestyle = '--', color = 'green', label = 'Best Epoch')  
    ax.legend(loc = 1)    
    ax.set_ylim([0.4, 1])

    ax.set_xlabel(xlabel)
    ax.set_ylabel('Accuracy (Fraction)')
    
    plt.show()


data, labels = load_data() 

label_counter = Counter(labels)
print(label_counter)
NUM_DOGS = label_counter['dog']
NUM_ROADS = label_counter['road']
print('Number of dogs: ', NUM_DOGS)
print('Number of roads: ', NUM_ROADS)

for i in range(0, 5): #storing images as pixels
  plot_one_image(data, labels, i)
print(set(labels))  #dataset labeled images as DOG or ROAD



inputs_train, inputs_test, labels_train, labels_test = model_selection.train_test_split(data, labels, test_size=0.2)

#KNN MODEL

knn = KNeighborsClassifier(n_neighbors=3) # Defining classifier
knn.fit(inputs_train, labels_train)
predictions = knn.predict(inputs_test)
print("KNN Testing Set Accuracy:")
print(accuracy_score(labels_test, predictions)*100)

# Random image test
image_id = 100
plot_one_image(inputs_test, labels_test, image_id)
print('prediction:', knn.predict([inputs_test[image_id]])[0])

true_positives = 0
false_positives = 0
true_negatives = 0
false_negatives = 0

for i in range(len(labels_test)):
  prediction = knn.predict([inputs_test[i]])[0] 

  # True positive.
  if prediction == labels_test[i] and prediction == 'dog':
    print('True positive:')
    plot_one_image(inputs_test, labels_test, i)
    true_positives += 1
    
  # True negative.
  elif prediction == labels_test[i] and prediction == 'road':
    print('True negative:')
    plot_one_image(inputs_test, labels_test, i)
    true_negatives += 1
  
  # False positive.
  elif prediction != labels_test[i] and prediction == 'dog':
    print('False positive:')
    plot_one_image(inputs_test, labels_test, i)
    false_positives += 1
  
  # False negative.
  elif prediction != labels_test[i] and prediction == 'road':
    print('False negative:')
    plot_one_image(inputs_test, labels_test, i)
    false_negatives += 1
  

  if true_positives >= 1 and false_positives >= 1 and \
    true_negatives >= 1 and false_negatives >= 1:
    break

for i in [1, 3, 5, 10, 20, 30]:

  knn = KNeighborsClassifier(n_neighbors=i)


  knn.fit(inputs_train, labels_train)
  
  predictions = knn.predict(inputs_test)

  # Print the score on the testing data
  print("KNN Testing Set Accuracy for %d neighbors:"%i)
  print(accuracy_score(labels_test, predictions)*100)


#SNN
nnet = MLPClassifier(hidden_layer_sizes=(3), max_iter= 10000000)  
nnet.fit(inputs_train, labels_train)

predictions = nnet.predict(inputs_test)

print("MLP Testing Set Score:")
print(accuracy_score(labels_test, predictions)*100)