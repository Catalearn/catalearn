# Catalearn

## Run your code on a GPU with zero setup

__Catalearn__ is a python module that allows you to run code on a cloud gpu. It allows you to easily leverage the computing power of GPUs without having to manage and maintain the infrastructure. 

## Installation

__Note:__ Catalearn only works on python3

`pip3 install catalearn`

or

`python3 -m pip install catalearn`

## Update
`pip3 install -U catalearn`

or

`python3 -m pip install -U catalearn`

## Usage

### Run and return result
 - First register for a key on www.catalearn.com.
 - Then replace <YOUR_API_KEY> with the key you generated.
```
import catalearn
catalearn.login(<YOUR_API_KEY>)

@catalearn.run_on_gpu
def gpu_function(data):
    print('Doing some serious computation')
    return 'here is the result'

result = gpu_function('a lot of data')
print(result)
# prints "here is the result"
```

### Run and save to file
Anything you save in the current directory will be downloaded to your local machine.
 - Replace <YOUR_API_KEY> with the key you generated from [Catalearn](www.catalearn.com "Title")
 - Run the following code and the file "something.txt" will appear.
```
import catalearn
catalearn.login(<YOUR_API_KEY>)

@catalearn.run_on_gpu
def save():
    with open('something.txt', 'w') as file:
        file.write('hello world')

save()
```

## Example: Train a Convolutional Neural Network on the GPU 
 - First run `sudo pip3 install keras tensorflow pandas` to install the modules needed.
 - Replace <YOUR_API_KEY> with the key you generated from [Catalearn](www.catalearn.com "Title")

```
from keras.datasets import mnist
import pandas as pd

import catalearn
# login to catalearn
catalearn.login(<YOUR_API_KEY>)

# load the MNIST dataset
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# process the data
x_train_reshape = x_train.reshape(x_train.shape[0], 28, 28, 1)
x_test_reshape = x_test.reshape(x_test.shape[0], 28, 28, 1)
y_train_onehot = pd.get_dummies(y_train).as_matrix()
y_test_onehot = pd.get_dummies(y_test).as_matrix()

# this decorator runs the function in a cloud GPU
@catalearn.run_on_gpu
def train(x_train_reshape, x_test_reshape, y_train_onehot, y_test_onehot):

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

    model.compile(loss='categorical_crossentropy', optimizer='Adadelta', metrics=['accuracy'])
    model.fit(x_train_reshape, y_train_onehot, epochs=1, batch_size=32)

    # the model will be downloaded to your local machine
    model.save('model.h5')

    loss_and_metrics = model.evaluate(x_test_reshape, y_test_onehot, batch_size=2048)

    return loss_and_metrics

loss_and_metrics = train(x_train_reshape, x_test_reshape, y_train_onehot, y_test_onehot)
print("Trained model has cost %s and test accuracy %s" % tuple(loss_and_metrics))
```
 - After running the code, you will find 'model.h5' in your current directory, this is the trained CNN model!

## Any Questions or Suggestions?
Please email _info@catalearn.com_ if you have any questions or suggestions.

