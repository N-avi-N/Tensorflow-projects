import json
import tensorflow as tf
import csv
import random
import numpy as np
import pandas as pd
import requests

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import regularizers

embedding_dim = 100
max_length = 16
trunc_type = 'post'
padding_type = 'post'
oov_tok = '<OOV>'
training_size = 160000
test_portion = 0.1

corpus = []

# download and save cleaned training corpus
# text = pd.read_csv('https://storage.googleapis.com/laurencemoroney-blog.appspot.com/training_cleaned.csv')
# text.to_csv('C:\\Users\\navin\\Desktop\\PyCharm Projects\\TF projects\\training_cleaned.csv', index= False)

num_sentences = 0

text_path = 'C:\\Users\\navin\\Desktop\\PyCharm Projects\\TF projects\\training_cleaned.csv'
text = pd.read_csv(text_path)

# get text and labels from csv
# data is at location 5, label is at location 0
# labels is of value 0 and 4, convert label value 4 to 1


with open(text_path, encoding='utf8', errors='ignore') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        # noinspection PyListCreation
        list_item = []
        list_item.append(row[5])
        this_label = row[0]
        if this_label == '0':
            list_item.append(0)
        else:
            list_item.append(1)
        num_sentences = num_sentences + 1
        corpus.append(list_item)

print(num_sentences)
print(len(corpus))
print(corpus[0])

# shuffle the corpus
sentences = []
labels = []
random.shuffle(corpus)
for x in range(training_size):
    sentences.append(corpus[x][0])
    labels.append(corpus[x][1])

# fit tokenizer on the whole corpus
# convert sentences to sequences, and pad them
tokenizer = Tokenizer()
tokenizer.fit_on_texts(sentences)

word_index = tokenizer.word_index
vocab_size = len(word_index)

sequences = tokenizer.texts_to_sequences(sentences)
padded = pad_sequences(sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)

# split data to test and train
split = int(test_portion * training_size)
test_sequences = padded[0:split]
training_sequences = padded[split:]
test_labels = labels[0:split]
training_labels = labels[split:]

print(vocab_size)
print(word_index['i'])


# Download and import the Glove weights(from stanford)
# this Glove version has 100 dimensions

# txt_link = 'https://storage.googleapis.com/laurencemoroney-blog.appspot.com/glove.6B.100d.txt'
# txt = requests.get(txt_link)
# with open('C:\\Users\\navin\\Desktop\\PyCharm Projects\\TF projects\\glove.txt', 'wb') as f:
#    f.write(txt.content)

# import Glove file
# split word and embeddings
embeddings_index = {}
with open("C:\\Users\\navin\\Desktop\\PyCharm Projects\\TF projects\\glove.txt", encoding="utf8") as f:
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs

# define matrix of the shape of embedding matrix + 1 extra column to accommodate the word
# create embedding matrix and insert the embedding weight of a word to what the words word_index is
embedding_matrix = np.zeros((vocab_size+1, embedding_dim))
for word, i in word_index.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        embedding_matrix[i] = embedding_vector

print(len(embedding_matrix))

# define model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size+1, embedding_dim, input_length=max_length, weights=[embedding_matrix], trainable=False),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Conv1D(64, 5, activation='relu'),
    tf.keras.layers.MaxPool1D(pool_size=4),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['acc'])
model.summary()

num_epochs = 10

training_padded = np.array(training_sequences)
training_labels = np.array(training_labels)
testing_padded = np.array(test_sequences)
testing_labels = np.array(test_labels)

history = model.fit(training_padded, training_labels, epochs=num_epochs, validation_data=(testing_padded, testing_labels), verbose=2)
print('Training complete !!!')

# plot training vs test accuracy and loss
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

# -----------------------------------------------------------
# Retrieve a list of list results on training and test data
# sets for each training epoch
# -----------------------------------------------------------
acc = history.history['acc']
val_acc = history.history['val_acc']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc)) # Get number of epochs

# ------------------------------------------------
# Plot training and validation accuracy per epoch
# ------------------------------------------------
plt.plot(epochs, acc, 'r')
plt.plot(epochs, val_acc, 'b')
plt.title('Training and validation accuracy')
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend(["Train Accuracy", "Validation Accuracy"])

plt.show()

# ------------------------------------------------
# Plot training and validation loss per epoch
# ------------------------------------------------
plt.plot(epochs, loss, 'r')
plt.plot(epochs, val_loss, 'b')
plt.title('Training and validation loss')
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend(["Train Loss", "Validation Loss"])

plt.show()


# Expected Output
# A chart where the validation loss does not increase sharply!