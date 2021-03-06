# -*- coding: utf-8 -*-
"""ZFNet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gUkPanUvwTMXAw54n2Uiqcs97XaiQvkP

ZFNet implementation
"""

print(tf.__version__)
print(tf.keras.__version__)
print(numpy.__version__)

'''
ZFNet uses deconvolutional networks known as deconvnet to visualize features.
Deconvnet is the reverse of convolutional network that shows where the extracted feature comes from.
'''

import tensorflow as tf

#import mnist data
mnist = tf.keras.datasets.mnist

#divide training and test data
(training_images, training_labels), (test_images, test_labels) = mnist.load_data()

training_images = training_images[:1000]
training_labels = training_labels[:1000]
test_images = test_images[:100]
test_labels = test_labels[:100]

training_images = tf.map_fn(lambda i: tf.stack([i]*3, axis=-1), training_images).numpy()
test_images = tf.map_fn(lambda i: tf.stack([i]*3, axis=-1), test_images).numpy()

#resize/reshape data 
training_images = tf.image.resize(training_images, [224, 224]).numpy()
test_images = tf.image.resize(test_images, [224, 224]).numpy()

training_images = training_images.reshape(1000, 224, 224, 3)
training_images = training_images / 255.0 
test_images = test_images.reshape(100, 224, 224, 3)
test_images = test_images / 255.0

#one-hot encoding
training_labels = tf.keras.utils.to_categorical(training_labels, num_classes=10)
test_labels = tf.keras.utils.to_categorical(test_labels, num_classes=10)

num_len_train = int(0.8 * len(training_images))

ttraining_images = training_images[:num_len_train]
ttraining_labels = training_labels[:num_len_train]

valid_images = training_images[num_len_train:]
valid_labels = training_labels[num_len_train:]

training_images = ttraining_images
training_labels = ttraining_labels

#model
model = tf.keras.models.Sequential([
    #96 convolutions with 7x7 with a stride of 2, relu activation
    #3x3 max pooling with stride 2, and local contrast normalization                                
		tf.keras.layers.Conv2D(96, (7, 7), strides=(2, 2), activation='relu',
			input_shape=(224, 224, 3)),
		tf.keras.layers.MaxPooling2D(3, strides=2),
    tf.keras.layers.Lambda(lambda x: tf.image.per_image_standardization(x)),

    #256 filters of 5x5, pooled, local contrast normalization
		tf.keras.layers.Conv2D(256, (5, 5), strides=(2, 2), activation='relu'),
		tf.keras.layers.MaxPooling2D(3, strides=2),
    tf.keras.layers.Lambda(lambda x: tf.image.per_image_standardization(x)),

    #384 filters of 3x3
		tf.keras.layers.Conv2D(384, (3, 3), activation='relu'),

    #384 filters of 3x3
		tf.keras.layers.Conv2D(384, (3, 3), activation='relu'),

    #256 filters of 3x3, maxpooling of 3x3 with stride 2
		tf.keras.layers.Conv2D(256, (3, 3), activation='relu'),
		tf.keras.layers.MaxPooling2D(3, strides=2),

    tf.keras.layers.Flatten(),
    #4096 neurons
		tf.keras.layers.Dense(4096),
    #4096 neurons
		tf.keras.layers.Dense(4096),
    #1000 neurons(=number of classes in ImageNet)
		tf.keras.layers.Dense(10, activation='softmax')
	])

'''
Local Contrast Normalization is a type of normalization that performs local subtraction and division normalizations, 
enforcing a sort of local competition between adjacent features in a feature map, 
and between features at the same spatial location in different feature maps.
'''

#compile model
model.compile(optimizer=tf.keras.optimizers.SGD(lr=0.01, momentum=0.9), 
              loss='categorical_crossentropy', 
              metrics=['accuracy', tf.keras.metrics.TopKCategoricalAccuracy(5)])

'''
TopK Categorical Accuracy calculates the percentage of records 
for which the targets are in the top K predictions.
'''

#callback
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', 
                                            		factor=0.1, patience=1, 
																								min_lr=0.00001)

#train model
model.fit(training_images, training_labels, batch_size=128, 
          validation_data=(valid_images, valid_labels), 
					epochs=50, callbacks=[reduce_lr])

#Evaluate model
print("\n Accuracy: %.4f" % (model.evaluate(test_images, test_labels)[1]))

