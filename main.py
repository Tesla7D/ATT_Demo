import numpy as np

from graph import export_pdf
from sklearn import tree
from sklearn.datasets import load_iris

iris = load_iris()
test_idx = [0, 50, 100]

# training data
training_target = np.delete(iris.target, test_idx)
training_data = np.delete(iris.data, test_idx, axis=0)

# testing data
test_target = iris.target[test_idx]
test_data = iris.data[test_idx]

clf = tree.DecisionTreeClassifier()
clf.fit(training_data, training_target)

print(test_target)
print(clf.predict(test_data))

# visualize
export_pdf(clf, iris.feature_names, iris.target_names)
