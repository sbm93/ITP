import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection  import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier

import numpy
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.utils import np_utils

class ClassificationModels:
    
    def __init__(self,X,Y):
        self.X=X
        self.Y=Y
    
    def variableCreation(self):
        
        labelcoder=LabelEncoder()
        self.Y=labelcoder.fit_transform(self.Y)
        X_train, X_test, Y_train, Y_test = train_test_split(self.X, self.Y, test_size = 0.25, random_state = 0,shuffle=False)
    
        sc = StandardScaler()
        X_train = sc.fit_transform(X_train)
        X_test = sc.transform(X_test)
        
        return X_train, X_test, Y_train, Y_test
        
    def confusionMatrixScore(self,Y_test,Y_pred): #Validation Function
        cm=confusion_matrix(Y_test,Y_pred)
        
        TP=cm[1,1]
        TN=cm[0,0]
        FP=cm[0,1]
        FN=cm[1,0]
    
        Accuracy=(TP+TN)/float(TP+TN+FP+FN)
        MisClassificationRate=(FP+FN)/float(TP+TN+FP+FN)
        Sensitivity=(TP)/float(TP+FN)
        Specificity=(TN)/float(TN+FP)   
        
        return Accuracy,MisClassificationRate,Sensitivity,Specificity
    
    def logisticRegression(self):
        
        X_train, X_test, Y_train, Y_test=self.variableCreation()
               
        classifier = LogisticRegression(multi_class='multinomial', solver='newton-cg',random_state=0)
        classifier.fit(X_train, Y_train)
        
        Y_pred = classifier.predict(X_test)
        prediction=[round(i) for i in Y_pred]
        
        #Confusion Matrix    
        confusionScore=self.confusionMatrixScore(Y_test,prediction)
        
        return accuracy_score(Y_test,prediction),confusion_matrix(Y_test,prediction)       
    
    def kNN_Classification(self):
        
        X_train, X_test, Y_train, Y_test=self.variableCreation()
            
        classifier = KNeighborsClassifier(n_neighbors = 3, metric = 'minkowski', p = 1)
        classifier.fit(X_train, Y_train)
        
        params = {'n_neighbors':[3,4,5,6,7,8,9,10],'metric':['euclidean','manhattan']}
        
        model = GridSearchCV(classifier, params,cv=3)
        gs_results=model.fit(X_train,Y_train)
        gs_results.best_params_
        gs_results.best_score_
        
        classifier = KNeighborsClassifier(n_neighbors = gs_results.best_params_['n_neighbors'], metric = gs_results.best_params_['metric'])
        classifier.fit(X_train, Y_train)
    
        Y_pred = classifier.predict(X_test)
        prediction=[round(i) for i in Y_pred]
    
        confusionScore=self.confusionMatrixScore(Y_test,prediction)
    
        return accuracy_score(Y_test,prediction),confusion_matrix(Y_test,prediction)    
    
    def randomForestClassifier(self):
        
        X_train, X_test, Y_train, Y_test=self.variableCreation()
        
        classifier=RandomForestRegressor(n_estimators=100,random_state=0)
        classifier.fit(X_train,Y_train)
        
        Y_pred=classifier.predict(X_test)
        prediction=[round(i) for i in Y_pred]
        
        confusionScore=self.confusionMatrixScore(Y_test,prediction)
    
        return accuracy_score(Y_test,prediction),confusion_matrix(Y_test,prediction)
    
    
    def naiveBayesClassifier(self):
        
        X_train, X_test, Y_train, Y_test=self.variableCreation()
        
        classifier=GaussianNB()
        classifier.fit(X_train,Y_train)
        
        Y_pred=classifier.predict(X_test)
        prediction=[round(i) for i in Y_pred]
        
        confusionScore=self.confusionMatrixScore(Y_test,prediction)
    
        return accuracy_score(Y_test,prediction),confusion_matrix(Y_test,prediction)
    
    def xgBoostClassifier(self):
        
        X_train, X_test, Y_train, Y_test=self.variableCreation()
        
        classifier=XGBClassifier(learning_rate =0.1, n_estimators=1000, max_depth=5,min_child_weight=1,gamma=0,subsample=0.8,
                                 colsample_bytree=0.8,objective= 'multi:softprob',nthread=4,scale_pos_weight=1,seed=27)
        classifier.fit(X_train,Y_train)
        
        params = {'max_depth':[4,5,6],'min_child_weight':[4,5,6]}
        
        model = GridSearchCV(classifier, params,cv=3, n_jobs=4,iid=False)
        gs_results=model.fit(X_train,Y_train)
        gs_results.best_params_
        gs_results.best_score_
        
        classifier=XGBClassifier(learning_rate =0.1, n_estimators=1000, max_depth=gs_results.best_params_['max_depth'],
                                 min_child_weight=gs_results.best_params_['min_child_weight'],gamma=0,subsample=0.8,colsample_bytree=0.8,
                                 objective= 'multi:softprob',nthread=4,scale_pos_weight=1,seed=27)
        classifier.fit(X_train,Y_train)
        
        Y_pred=classifier.predict(X_test)
        prediction=[round(i) for i in Y_pred]
        
        confusionScore=self.confusionMatrixScore(Y_test,prediction)
    
        return accuracy_score(Y_test,prediction),confusion_matrix(Y_test,prediction)

class NeuralNetwork:
    
    def __init__(self,X,Y):
        self.X=X
        self.Y=Y
    
    def lSTM(self):
        labelcoder=LabelEncoder()
        Y[:,0]=labelcoder.fit_transform(Y)
        
        X_train, X_test, Y_train, Y_test = train_test_split(self.X,self.Y, test_size = 0.25, random_state = 0,shuffle=False)
        Cm_Y=Y_test

        
        onehotencoder = OneHotEncoder(categorical_features = [0])
        Y_test = onehotencoder.fit_transform(Y_test).toarray()

        onehotencoder = OneHotEncoder(categorical_features = [0])
        Y_train = onehotencoder.fit_transform(Y_train).toarray()


        sc = StandardScaler()
        X_train = sc.fit_transform(X_train)
        X_test = sc.transform(X_test) 
        
        X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
        X_test = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
        Y_train = Y_train.reshape((Y_train.shape[0], 1, Y_train.shape[1]))
        Y_test = Y_test.reshape((Y_test.shape[0], 1, Y_test.shape[1]))
        
        model = Sequential()
        model.add(LSTM(32, return_sequences=True,input_shape=(X_train.shape[1], X_train.shape[2])))  
        model.add(LSTM(32, return_sequences=True)) 
        model.add(Dense(3, activation='softmax'))

        model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
        
        history=model.fit(X_train, Y_train, batch_size=64, epochs=50, validation_data=(X_test, Y_test))
        
        score, acc = model.evaluate(X_test, Y_test, batch_size=70)
       
        Y_Probability = model.predict(X_test)
        Y_Pred=[]
        for i,j in enumerate(Y_Probability):
           Y_Pred.append(np.where(j[0]==max(j[0]))[0][0])
           
        Cm_Y1=[]
        for i in Cm_Y:
            Cm_Y1.append(i[0])
        confusionScore=confusion_matrix(Cm_Y1,Y_Pred)
        
        return acc,confusionScore

####################################################################################################################################    
df=pd.read_csv("UpdatedData.csv")

X=df.iloc[:,2:-1].values 
Y=df.iloc[:,-1:].values 

Object1=ClassificationModels(X,Y)

T1=Object1.logisticRegression()
T2=Object1.randomForestClassifier()
T3=Object1.naiveBayesClassifier()
T4=Object1.xgBoostClassifier()
T5=Object1.kNN_Classification()

Object2=NeuralNetwork(X,Y)
T6=Object2.lSTM()

