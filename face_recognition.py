# -*- coding: utf-8 -*-
"""FACE RECOGNITION.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DxUu8RfcYj5mZwhkHb3YKfzpKO9EiQOQ
"""

import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import fetch_lfw_people
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import confusion_matrix
import tensorflow as tf

# Step 1: Load dataset and preprocess images
faces = fetch_lfw_people(min_faces_per_person=100, color=True)
image_count, image_height, image_width, _ = faces.images.shape
class_count = len(faces.target_names)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(image):
    gray = (image * 255).astype(np.uint8)
    gray = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    face_regions = [image[y:y+h, x:x+w] for (x, y, w, h) in faces]
    return face_regions, faces

fig, ax = plt.subplots(3, 8, figsize=(18, 10))
for i, axi in enumerate(ax.flat):
    img = (faces.images[i] * 255).astype(np.uint8)
    detected_faces, boxes = detect_faces(img)
    for (x, y, w, h) in boxes:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    axi.imshow(img)
    axi.set(xticks=[], yticks=[], xlabel=faces.target_names[faces.target[i]])
plt.show()

# Step 2: Prepare dataset
x_faces = faces.images / 255.0
x_faces = x_faces.reshape((x_faces.shape[0], image_width * image_height * 3))
y_faces = to_categorical(faces.target, num_classes=class_count)
x_train, x_test, y_train, y_test = train_test_split(x_faces, y_faces, train_size=0.8, stratify=y_faces, random_state=42)

# Step 3: Define MLP Model
model = Sequential()
model.add(Dense(128, activation='relu', input_shape=(image_width * image_height * 3,)))
model.add(Dense(class_count, activation='softmax'))
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Step 4: Train model
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
hist = model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=10, batch_size=20)

def show_history(hist):
    acc = hist.history['accuracy']
    val_acc = hist.history['val_accuracy']
    epochs = range(1, len(acc) + 1)

    plt.figure(figsize=(8, 6))
    plt.plot(epochs, acc, '-', label='Training Accuracy')
    plt.plot(epochs, val_acc, ':', label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.show()

show_history(hist)

# Step 5: Evaluate model
y_predicted = model.predict(x_test)
mat = confusion_matrix(y_test.argmax(axis=1), y_predicted.argmax(axis=1))

sns.heatmap(mat, square=True, annot=True, fmt='d', cbar=False, cmap='Blues',
            xticklabels=faces.target_names,
            yticklabels=faces.target_names)

plt.xlabel('Predicted label')
plt.ylabel('Actual label')
plt.show()