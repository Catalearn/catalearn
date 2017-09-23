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
Before using the module, you need to login with your access key. Replace __ACCESS_KEY__ below with the access key you just generated.
```
import catalearn
catalearn.login(ACCESS_KEY)
```

### Run code on the GPU
Use the `catalearn.run_on_gpu` decorator to run functions on the GPU. Everything the function prints will be streamed back.
```
@catalearn.run_on_gpu
def gpu_function(data):
    print('calculating...')
    return data + 1

result = gpu_function(1)
# calculating...
print(result) 
# 2
```

### Writing to files
Anything you save in the current directory will be downloaded to your local current directory. This is useful for saving models.

The following code will create the file 'something.txt'.
```
@catalearn.run_on_gpu
def save():
    with open('something.txt', 'w') as file:
        file.write('hello world')

save()
```

### Saving and loading data
Use `catalearn.save` and `catalearn.load` to store the data in the cloud and download it from there. This removes the need for multiple data uploads when training models.
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

We recommend running the example in a __Jupyter Notebook__ cell by cell to get the best result, but you can also put them together into a script.

__Dependencies:__ keras, pandas

### Load the dependencies
```
from keras.datasets import mnist
import pandas as pd
import catalearn
```

### Login to catalearn
```
catalearn.login(ACCESS_KEY) # replace with your own access key.
```

### Load and process the MNIST dataset
Here we use keras to load the MNIST dataset. We reshape the 28x28 images to 28x28x1, making them compatible with keras. We also apply onehot encoding to the labels.
```
(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train_reshape = x_train.reshape(x_train.shape[0], 28, 28, 1)
x_test_reshape = x_test.reshape(x_test.shape[0], 28, 28, 1)

y_train_onehot = pd.get_dummies(y_train).as_matrix()
y_test_onehot = pd.get_dummies(y_test).as_matrix()
```

### Upload the datasets to catalearn
Next we save the data to the cloud. This way we won't have to upload the data every time we tweak the model. You'll see what this means in a second.
```
catalearn.save(x_train_reshape, 'x_train')
catalearn.save(x_test_reshape, 'x_test')
catalearn.save(y_train_onehot, 'y_train')
catalearn.save(y_test_onehot, 'y_test')
```
### Define the model
We will use a convolutional model with three layers. Note that we need to import the libraries within ```get_model()``` to use the GPU accelerated versions.

```
def get_model():

    # need to import the libraries in the function to use the GPU accelerated versions
    from keras.models import Sequential
    from keras.layers import Dense, Activation, Conv2D, Flatten, MaxPooling2D

    model = Sequential()
    model.add(Conv2D(32, (3, 3), input_shape=(28, 28, 1)))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(64, (3, 3)))
    model.add(Flatten())
    model.add(Activation('relu'))
    model.add(Dense(units=10))
    model.add(Activation('softmax'))

    return model
```

### Defined a function to train the model
Here we define a function that trains the keras model on the dataset.

The line ```@catalearn.run_on_gpu``` transforms the function to run in the cloud.

 Note that we can just use ```catalearn.load``` to load the datasets. This way we don't need to upload them again, saving a lot of time.
```
@catalearn.run_on_gpu
def train(epochs):

    x_train = catalearn.load('x_train')
    x_test = catalearn.load('x_test')
    y_train = catalearn.load('y_train')
    y_test = catalearn.load('y_test')

    model = get_model()
    model.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['accuracy'])
    model.fit(x_train_reshape, y_train_onehot, epochs=epochs, batch_size=32)

    # the model will be downloaded to your local machine
    model.save('model.h5')

    loss_and_metrics = model.evaluate(x_test_reshape, y_test_onehot, batch_size=2048)
    return loss_and_metrics
```

### Train the model
We can now use the function ```train()``` as a normal function. This will print all the output of the function and download the ```model.h5``` file we created into your local directory.

```
loss_and_metrics = train(5)
print("Trained model has cost %s and test accuracy %s" % tuple(loss_and_metrics))
```

Training with 5 epochs would take around 5 minutes on a CPU, but with Catalearn, it only takes a little over 1 minute. The difference gets bigger as you use more data and a more complex model.

## Any Questions or Suggestions?
Please email _info@catalearn.com_ if you have any questions or suggestions.

