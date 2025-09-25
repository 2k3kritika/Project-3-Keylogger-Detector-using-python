# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

df = pd.read_csv("dataset.csv")
feature_cols = ["open_files","connections","path_in_temp","path_in_user","age_seconds","cmdline_len","suspicious_cmd_kw","in_startup"]
X = df[feature_cols].fillna(0)
y = df["label"].astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

clf = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))
print("Confusion matrix:")
print(confusion_matrix(y_test, y_pred))

joblib.dump(clf, "model.pkl")
print("Saved model.pkl")
