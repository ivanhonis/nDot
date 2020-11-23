# # TensorFlow CNN model training example
# # based on https://www.tensorflow.org/tutorials/images/cnn
# from __future__ import absolute_import, division, print_function, unicode_literals
#
# from random import randrange
# import tensorflow as tf
#
#
# from tensorflow.keras import datasets, layers, models
# import matplotlib.pyplot as plt
#
# from tensorflow.keras.models import load_model
# import numpy as np
# import sys
#
#
#
#
# (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()
#
#
# # train_images_one_layer = (0.2989*train_images[:,:,:,0]+0.5870*train_images[:,:,:,1]+0.1140*train_images[:,:,:,2])
# # test_images_one_layer = (0.2989*test_images[:,:,:,0]+0.5870*test_images[:,:,:,1]+0.1140*test_images[:,:,:,2])
# # train_images_one_layer, test_images_one_layer = train_images_one_layer / 255.0, test_images_one_layer / 255.0
#
# #
# # print (train_images_one_layer)
# #
# # # Normalize pixel values to be between 0 and 1
# train_images, test_images = train_images / 255.0, test_images / 255.0
# #
# class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
#                'dog', 'frog', 'horse', 'ship', 'truck']
#
# # plt.figure(figsize=(10,10))
# # for i in range(100):
# #     plt.subplot(10,10,i+1)
# #     plt.xticks([])
# #     plt.yticks([])
# #     plt.grid(False)
# #     plt.imshow(train_images_one_layer[i], cmap=plt.cm.binary)
# #     # The CIFAR labels happen to be arrays,
# #     # which is why you need the extra index
# #     plt.xlabel(class_names[train_labels[i][0]])
# # plt.show()
#
# # sys.exit()
#


# model = models.Sequential()
# model.add(layers.InputLayer(input_shape=(32, 32,3)))
# # model.add(layers.Conv2D(32, (3, 3), activation='relu'))
# # model.add(layers.MaxPooling2D((2, 2)))
# # model.add(layers.Conv2D(64, (3, 3), activation='relu'))
# # model.add(layers.MaxPooling2D((2, 2)))
# # model.add(layers.Conv2D(64, (3, 3), activation='relu'))
# model.add(layers.Flatten())
# model.add(layers.Dense(2048, activation='relu'))
# model.add(layers.Dense(1024, activation='relu'))
# model.add(layers.Dense(512, activation='relu'))
# model.add(layers.Dense(256, activation='relu'))
# model.add(layers.Dense(128, activation='relu'))
#
# # model.add(layers.Dense(256, activation='relu'))
# # model.add(layers.Dense(128, activation='relu'))
# model.add(layers.Dense(10, activation='softmax'))
# model.summary()
#
# model.compile(optimizer='Adamax',
#               loss='sparse_categorical_crossentropy',
#               metrics=['accuracy'])
#
# history = model.fit(train_images, train_labels, epochs=25,
#                     validation_data=(test_images, test_labels))
#
# model.save('my_model.h5')
#
# # print("itt")
# # print (history.history)
# #
# # plt.plot(history.history['accuracy'], label='accuracy')
# # plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
# # plt.xlabel('Epoch')
# # plt.ylabel('Accuracy')
# # plt.ylim([0, 2])
# # plt.legend(loc='lower right')
# # plt.show()
# #
# # test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)
# # print(test_acc)
# #
# #
#
#
# model = load_model('my_model.h5')
#
# (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()
#
# # train_images_one_layer = (0.2989*train_images[:,:,:,0]+0.5870*train_images[:,:,:,1]+0.1140*train_images[:,:,:,2])
# # test_images_one_layer = (0.2989*test_images[:,:,:,0]+0.5870*test_images[:,:,:,1]+0.1140*test_images[:,:,:,2])
# # train_images, test_images = train_images_one_layer / 255.0, test_images_one_layer / 255.0
#
#
#
# # Normalize pixel values to be between 0 and 1
# train_images, test_images = train_images / 255.0, test_images / 255.0
#
# class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
#                'dog', 'frog', 'horse', 'ship', 'truck']
#
# def plot_image(i, predictions_array, true_label, img):
#   predictions_array, true_label, img = predictions_array, true_label[i][0], img[i]
#   plt.grid(False)
#   plt.xticks([])
#   plt.yticks([])
#
#   plt.imshow(img, cmap=plt.cm.binary)
#
#   predicted_label = np.argmax(predictions_array)
#   if predicted_label == true_label:
#     color = 'blue'
#   else:
#     color = 'red'
#
#   plt.xlabel("{} {:2.0f}% ({})".format(class_names[predicted_label],
#                                 100*np.max(predictions_array),
#                                 class_names[true_label]),
#                                 color=color)
#
# def plot_value_array(i, predictions_array, true_label):
#   predictions_array, true_label = predictions_array, true_label[i][0]
#   plt.grid(False)
#   plt.xticks(range(10))
#   plt.yticks([])
#   thisplot = plt.bar(range(10), predictions_array, color="#777777")
#   plt.ylim([0, 1])
#   predicted_label = np.argmax(predictions_array)
#
#   thisplot[predicted_label].set_color('red')
#   thisplot[true_label].set_color('blue')
#
#
# for ix in range(10):
#     i = randrange(50)
#     predictions = model.predict(train_images[i:i+1])
#     print(predictions)
#
#     plt.figure(figsize=(6,3))
#     plt.subplot(1,2,1)
#     plot_image(i, predictions[0], train_labels, train_images)
#     plt.subplot(1,2,2)
#     plot_value_array(i, predictions[0],  train_labels)
#     plt.show()
#
# for ix in range(10):
#     i = randrange(50)
#     predictions = model.predict(test_images[i:i+1])
#     print(predictions/10)
#
#     plt.figure(figsize=(6,3))
#     plt.subplot(1,2,1)
#     plot_image(i, predictions[0], test_labels, test_images)
#     plt.subplot(1,2,2)
#     plot_value_array(i, predictions[0],  test_labels)
#     plt.show()
