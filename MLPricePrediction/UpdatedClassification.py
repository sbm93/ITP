import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelEncoder
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


class ClassificationModels:
    
    def __init__(self,X,Y):
        self.X=X
        self.Y=Y
    
    def variableCreation(self):
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
               
        classifier = LogisticRegression(random_state=0)
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
        
        classifier=XGBClassifier()
        classifier.fit(X_train,Y_train)
        
        Y_pred=classifier.predict(X_test)
        prediction=[round(i) for i in Y_pred]
        
        confusionScore=self.confusionMatrixScore(Y_test,prediction)
    
        return accuracy_score(Y_test,prediction),confusion_matrix(Y_test,prediction)
    

    
    def lSTM():
        
        pass
    
####################################################################################################################################    
df=pd.read_csv("FCPO3-OHLCV.csv")
def classification_Y_Finder(df,UpTrend=5,DownTrend=5):
    Close_X=df.iloc[:,4:5].values
    
    Close_XPercentage=[(((Close_X[i+5]-Close_X[i])/Close_X[i])*100) for i in range(0,len(Close_X)-5)]+[1,1,1,1,1]
    Y=[]
    for eV in Close_XPercentage:
        if eV > UpTrend: Y.append("Up Trand")
        elif eV <  -(DownTrend): Y.append("Down Trand")
        else: Y.append("No Trand")
        
    Finaldf=pd.concat([df,pd.DataFrame(Y,columns=["Trend"])],  axis=1)
    
    return Finaldf
    
Newdf=classification_Y_Finder(df,3,2)

X=Newdf.iloc[:,1:-1].values 
Y=Newdf.iloc[:,-1:].values 

labelcoder=LabelEncoder()
Y=labelcoder.fit_transform(Y)
        
Object1=ClassificationModels(X,Y)

T1=Object1.naiveBayesClassifier()
T2=Object1.randomForestClassifier()
T3=Object1.xgBoostClassifier()