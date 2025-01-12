from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from vincenty import vincenty


def preproces(x, number):
    X_current = None
    if number == 0:
        X_current = (x - np.min(x)) / np.min(x) * -1
    elif number == 1:
        X_current = np.exp((x - np.min(x)) / 24) / np.exp(np.min(x) * -1 / 24)
    elif number == 2:
        X_current = (x - np.min(x)) / np.min(x) * -1
        X_current = X_current ** np.e
    return X_current, number


def evaluation(Y_test_combined, pred, i2, number):
    errors = []
    for range_longitude in range(len(pred)):
        centroids = pred[range_longitude]
        error = vincenty(centroids, Y_test_combined[range_longitude])
        errors.append(error)

    mean_error = np.mean(errors) * 1000
    median_error = np.median(errors) * 1000
    R2_score = r2_score(Y_test_combined, pred)

    print(f"{i2}_Mean Error: {mean_error} meters")
    print(f"{i2}_Median Error: {median_error} meters")
    print(f"{i2}_R2 Score: {R2_score}\n")

    results_df = pd.DataFrame({
        'Random': i2,
        'Mean Error (meters)': [mean_error],
        'Median Error (meters)': [median_error],
        'R2 Score': [R2_score],
        'Pre process': number
    })

    # Save results to CSV
    results_df.to_csv(f'result/evaluation_results_{number}_{i2}.csv', index=False)

list_fualt_not = [9, 10, 11, 12, 17, 19, 20, 22, 26, 30, 58, 61, 66, 70, 71, 72, 75, 82, 83, 84, 85,86, 88, 89, 90, 91 ,
          92, 94, 96, 97, 99, 100, 101, 103, 104, 105, 107, 110, 118, 119,
                  28, 24, 18, 62, 102, 126,
                  0, 1, 2, 4, 6, 7, 8, 13, 14, 15, 16, 21, 29, 31, 32, 33, 36, 37, 38, 39, 40, 43, 44, 59, 60, 64, 68, 73, 109]

k = [3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2]
for i2 in range(50, 60, 1):
    regressor = RandomForestRegressor()
    X_train_combined, Y_train_combined = [], []
    X_test_combined, Y_test_combined = [], []
    for range_longitude in k:
        file_name = f"session/data_{range_longitude:.1f}_to_{(range_longitude + 0.1):.1f}.csv"
        df = pd.read_csv(file_name)
        data_array = df.to_numpy()
        X_current = data_array[:, :137]
        Y_current = data_array[:, 137:]
        X_train_temp, X_test_temp, Y_train_temp, Y_test_temp = train_test_split(X_current, Y_current, test_size=0.3,
                                                                                random_state=i2)

        # Impute missing values
        imputer = SimpleImputer(strategy='mean')
        X_train_temp_imputed = imputer.fit_transform(X_train_temp)
        X_test_temp_imputed = imputer.transform(X_test_temp)

        X_train_combined.append(X_train_temp_imputed)
        Y_train_combined.append(Y_train_temp)
        X_test_combined.append(X_test_temp_imputed)
        Y_test_combined.append(Y_test_temp)

    X_train_combined = np.concatenate(X_train_combined, axis=0)
    Y_train_combined = np.concatenate(Y_train_combined, axis=0)
    X_test_combined = np.concatenate(X_test_combined, axis=0)
    Y_test_combined = np.concatenate(Y_test_combined, axis=0)

    for iii, number_col in enumerate(list_fualt_not):
        if iii == 0:
            X_Train_1 = X_train_combined[:, number_col].reshape(-1, 1)
            X_test_1 = X_test_combined[:, number_col].reshape(-1, 1)
        else:
            X_Train_1 = np.concatenate((X_Train_1, X_train_combined[:, number_col].reshape(-1, 1)), axis=1)
            X_test_1 = np.concatenate((X_test_1, X_test_combined[:, number_col].reshape(-1, 1)), axis=1)
    X_train_combined = X_Train_1
    X_test_combined = X_test_1


    for i_pre in [0, 1, 2]:
        X_train_combined_p, t = preproces(X_train_combined, i_pre)
        X_test_combined_p, t = preproces(X_test_combined, i_pre)

        regressor.fit(X_train_combined_p, Y_train_combined)
        pred = regressor.predict(X_test_combined_p)
        evaluation(Y_test_combined, pred, i2, i_pre)
