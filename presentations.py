from graph import export_pdf
from sklearn import tree

feature_names = ["slides", "colour"]
target_names = ["Sean", "Norbert", "Other"]

# Training data
training_data = [[40, 0xff8000],
                 [10, 0x9BB7FF],
                 [8, 0x9BB7FF],
                 [37, 0xff8000],
                 [35, 0xff8000],
                 [20, 0x2AFF28],
                 [12, 0x9BB7FF],
                 [20, 0x9BB7FF],
                 [23, 0xFF5272],
                 [21, 0x1A3BFF],
                 [29, 0xff8000]]
training_target = [0, 1, 1, 0, 0, 2, 1, 1, 2, 2, 0]

# Test data
test_data = [[33, 0xff8000],
             [11, 0x9BB7FF],
             [19, 0xF91FFF],
             [12, 0x88A6FF]]
test_target = [0, 1, 2, 1]

clf = tree.DecisionTreeClassifier()
clf.fit(training_data, training_target)

print(test_target)
print(clf.predict(test_data))

export_pdf(clf, feature_names, target_names, "pres.pdf")
