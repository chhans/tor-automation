from sklearn import svm

clf = svm.LinearSVC()

def train(X, Y):
	clf.fit(X, Y)

def predict(X):
	return clf.predict(X)