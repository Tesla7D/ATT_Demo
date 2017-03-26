import pydotplus

from sklearn import tree
from sklearn.externals.six import StringIO


dot_data = StringIO()


def export_pdf(classifier, feature_names, target_names, filename="graph.pdf"):
    tree.export_graphviz(classifier,
                         out_file=dot_data,
                         feature_names=feature_names,
                         class_names=target_names,
                         filled=True,
                         rounded=True,
                         impurity=False)

    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
    graph.write_pdf(filename)
    print("PDF export done")
