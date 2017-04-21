import sklearn
import csv
from sklearn import linear_model
import numpy as np
import math
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
import cPickle

x_data = []
y_data = []
with open("push_up_records.csv", "rb") as f:
    reader = csv.reader(f)
    for row in reader:
        row = map(float, row)
        x_data.append(row)
        y_data.append(1)

with open("nonpush_up_records.csv", "rb") as f:
    reader = csv.reader(f)
    for row in reader:
        row = map(float, row)
        x_data.append(row)
        y_data.append(0)


features_x=np.array(x_data)
values_y=np.array(y_data)

np.random.seed(0)
indices = np.arange(features_x.shape[0])
np.random.shuffle(indices)
features_x, values_y = features_x[indices], values_y[indices]


features_x_train = features_x[:-20]
features_x_test = features_x[-20:]

values_y_train = values_y[:-20]
values_y_test = values_y[-20:]

print(features_x_train.shape)
print(values_y_train.shape)
print(features_x_test.shape)
print(values_y_test.shape)

regr = linear_model.LinearRegression()
regr.fit(features_x_train, values_y_train)

print('Coefficients:', regr.coef_)

values_y_pred = regr.predict(features_x_test)
# values_y_pred = map(int, regr.predict(features_x_test))
# values_y_test = map(int, values_y_test)
print(values_y_pred)
print(values_y_test)
# target_names = ['class 0', 'class 1']
# print classification_report(values_y_test, values_y_pred, target_names=target_names)
with open('pushup_detector.pkl', 'wb') as fid:
    cPickle.dump(regr, fid)



