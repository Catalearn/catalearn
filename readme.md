# Catalearn

## Run your code on a GPU with zero setup

__Catalearn__ is a python module that allows you to run code on a cloud gpu. It allows you to easily leverage the computing power of GPUs without having to manage and maintain the infrastructure. 

## Installation

`python -m pip install catalearn`

## Update

`python -m pip install -U catalearn`

## Usage
First register for a key on www.catalearn.com.

Then replace <YOUR_API_KEY> with the key you generated.
```
import catalearn
catalearn.login(<YOUR_API_KEY>)

@catalearn.run_on_gpu
def gpu_function(data):
    print('Doing some serious computation')
    return 'here is the result'

result = gpu_function('a lot of data')
# This will run the function on a cloud gpu and return the result
```

## Example 
First run `sudo pip3 install keras pandas` to install the modules needed.

Replace <YOUR_API_KEY> with the key you generated from [Catalearn](www.catalearn.com "Title")

```
from keras.datasets import mnist
import pandas as pd
import catalearn
catalearn.login(<YOUR_API_KEY>)

(x_train, y_train), (x_test, y_test) = mnist.load_data()

x_train_reshape = x_train.reshape(x_train.shape[0], 28, 28, 1)
x_test_reshape = x_test.reshape(x_test.shape[0], 28, 28, 1)

y_train_onehot = pd.get_dummies(y_train).as_matrix()
y_test_onehot = pd.get_dummies(y_test).as_matrix()

@catalearn.run_on_gpu
def gpu_func(x_train_reshape, x_test_reshape, y_train_onehot, y_test_onehot):

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
    model.fit(x_train_reshape, y_train_onehot, epochs=5, batch_size=32)

    loss_and_metrics = model.evaluate(x_test_reshape, y_test_onehot, batch_size=512)
    print("\n\nTrained model has test accuracy {0}".format(loss_and_metrics[1]))

    return model

model = gpu_func(x_train_reshape, x_test_reshape, y_train_onehot, y_test_onehot)
```

## Any Questions or Suggestions?
Please email _info@catalearn.com_ if you have any questions or suggestions.

