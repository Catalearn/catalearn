# Catalearn

## Run your code on a GPU with zero setup

__Catalearn__ is a python module that allows you to run code on a cloud gpu. It allows you to easily leverage the computing power of GPUs without having to manage and maintain the infrastructure. 

## Installation

__Note:__ Catalearn only works on python 3

`pip3 install catalearn`

or

`python3 -m pip install catalearn`

## Update
`pip3 install -U catalearn`

or

`python3 -m pip install -U catalearn`

## Usage

### Register for an access key
An access key is required for using the catalearn module, you can register for one at www.catalearn.com

### Import and login
Before using the module, you need to login with you access key. Replace __ACCESS_KEY__ below with the access key you just generated.
```
import catalearn
catalearn.login(ACCESS_KEY)
```

### Run code the the GPU
Use the `catalearn.run_on_gpu` decorator to run functions on the GPU
```
@catalearn.run_on_gpu
def gpu_function(data):
    return data + 1

result = gpu_function(1)
print(result) 
# 2
```

### Writing to files
Anything you save in the current directory will be downloaded to your local current directory. This is useful for saving models.

The following code will create the file 'something.txt'
```
@catalearn.run_on_gpu
def save():
    with open('something.txt', 'w') as file:
        file.write('hello world')

save()
```

### Saving and loading data
Saving data to the cloud and loading it from the cloud can prevent multiple data uploads.
```
import numpy as np

data = np.array([1,2,3,4,5])
catalearn.save(data, 'my_data')

delete data

data = catalearn.load('my_data')
print(data) 
# [1 2 3 4 5]
```

## Example: Train a Convolutional Neural Network on the GPU 
This example uses catalearn to train a CNN on the MNIST dataset.

Don't forget to replace __ACCESS_KEY__ with your own key
```
from keras.datasets import mnist
import pandas as pd

import catalearn
# login to catalearn
catalearn.login(ACCESS_KEY) # replace with your own access key

# load the MNIST dataset
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# process the data
x_train_reshape = x_train.reshape(x_train.shape[0], 28, 28, 1)
x_test_reshape = x_test.reshape(x_test.shape[0], 28, 28, 1)
y_train_onehot = pd.get_dummies(y_train).as_matrix()
y_test_onehot = pd.get_dummies(y_test).as_matrix()

# upload the datasets to catalearn
# this way we don't have to upload the data again every time we train a model
catalearn.save(x_train_reshape, 'x_train')
catalearn.save(x_test_reshape, 'x_test')
catalearn.save(y_train_onehot, 'y_train')
catalearn.save(y_test_onehot, 'y_test')

# defined the function to be run
@catalearn.run_on_gpu
def train(epochs):

    # need to import the libraries in the function to use the GPU accelerated versions
    from keras.models import Sequential
    from keras.layers import Dense, Activation, Conv2D, Flatten, MaxPooling2D

    import catalearn
    catalearn.login(ACCESS_KEY)

    x_train = catalearn.load('x_train')
    x_test = catalearn.load('x_test')
    y_train = catalearn.load('y_train')
    y_test = catalearn.load('y_test')

    model = Sequential()
    model.add(Conv2D(32, (3, 3), input_shape=(28, 28, 1)))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(64, (3, 3)))
    model.add(Flatten())
    model.add(Activation('relu'))
    model.add(Dense(units=10))
    model.add(Activation('softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='Adadelta', metrics=['accuracy'])
    model.fit(x_train_reshape, y_train_onehot, epochs=epochs, batch_size=32)

    # the model will be downloaded to your local machine
    model.save('model.h5')

    loss_and_metrics = model.evaluate(x_test_reshape, y_test_onehot, batch_size=2048)

    return loss_and_metrics

loss_and_metrics = train(5)
print("Trained model has cost %s and test accuracy %s" % tuple(loss_and_metrics))
```

## Any Questions or Suggestions?
Please email _info@catalearn.com_ if you have any questions or suggestions.

