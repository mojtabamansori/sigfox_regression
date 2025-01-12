import pandas as pd
import numpy as np
import time
from itertools import product
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, median_absolute_error
from sklearn.metrics.pairwise import haversine_distances
from math import radians
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

dataset = pd.read_csv('sigfox_dataset_rural (1).csv')

X = dataset.iloc[:, :137]
y = dataset[['Latitude', 'Longitude']]

# Split the dataset
for ks in range(35,42):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=ks)


    X_train = np.array(X_train)
    X_test = np.array(X_test)
    y_train = np.array(y_train)
    y_test = np.array(y_test)
    k = 1
    errors = [0]
    print(y_train.shape,X_train.shape)
    for n,i in enumerate(range(len(X_test))):
        print(f'\r{ks},{n}/{len(X_test)}', end='')
        all_distances = np.sqrt(np.sum(np.abs(X_train - X_test[i]) ** 2, axis=1))

        k_indexes = np.argsort(all_distances)[0:k]
        centroids = np.mean(y_train[k_indexes, :], axis=0)
        error = haversine_distances(np.reshape(np.radians(y_test[i]), (1, -1)), np.reshape(np.radians(centroids), (1, -1)))* 6371000
        errors.append(error)

    filtered_df = pd.DataFrame(np.expand_dims(errors, axis=1))
    file_name = file_name = f"error/org_{ks}_error.csv"
    filtered_df.to_csv(file_name, index=False)

