import pulp as pl
import pandas as pd
import numpy as np

####################################### Walk Forward Testing Split##########################
IN_Sample_Size = 500
Out_Sample_Size = 10

df = pd.read_csv("C:/Users/pooja.bhati/Downloads/GApoc/IP/return_cons.csv")

result = pd.DataFrame(columns=['IN_Sample_Start_Date', 'IN_Sample_End_Date','Out_Sample_Start_Date', 'Out_Sample_End_Date'])

In_Sample_Start_Date = [df.iloc[x]['Datetime'] for x in range(0, len(df), Out_Sample_Size)]
In_Sample_End_Date = [df.iloc[x]['Datetime'] for x in range(IN_Sample_Size-1, len(df), Out_Sample_Size)]
Out_Sample_Start_Date = [df.iloc[x]['Datetime'] for x in range(IN_Sample_Size, len(df), Out_Sample_Size)]
Out_Sample_End_Date = [df.iloc[x]['Datetime'] for x in range((IN_Sample_Size+Out_Sample_Size)-1, len(df), Out_Sample_Size)]

df_wft = pd.DataFrame(list(zip(In_Sample_Start_Date, In_Sample_End_Date, Out_Sample_Start_Date, Out_Sample_End_Date)), 
               columns =['In_Sample_Start_Date', 'In_Sample_End_Date', 'Out_Sample_Start_Date', 'Out_Sample_End_Date'])

df_wft.to_csv("C:/Users/pooja.bhati/Downloads/GApoc/IP/walkforward.csv", index=False)

###############################################

class IntegerProgrammingWts:

    def __init__(self,df,df_wft):
        self.df=df
        self.df_wft=df_wft
        self.DateTime_df = self.df.set_index("Datetime")
    
    
    
    def TrainingForStratgy(self,startDate,EndDate):  
        dfNew=self.DateTime_df[startDate:EndDate]
        X=dfNew.iloc[:,:-1]
        Y=dfNew.iloc[:,-1]
        
        problem = pl.LpProblem("Strategy Problem",pl.LpMaximize)
        
        df1_cum = np.exp(np.log1p(dfNew).cumsum())
        
        R_CumSum=[((df1_cum.iloc[len(dfNew)-1,i]-df1_cum.iloc[0,i])/df1_cum.iloc[0,i]) for i in range(len(X.columns)+1)]
        X_cum=R_CumSum[:-1]
        Y_cum=R_CumSum[-1:]
        
        
        #Define Interger variables for each strategy
        variables=[]
        for i in range(len(X_cum)):
            s = pl.LpVariable(f's{i+1}',0,5,pl.LpInteger)
            variables.append(s)
            
        # Create the objective function
        problem += pl.lpSum([variables[a]* X_cum[a] for a in range(len(X_cum))])
        
        
        # Create constraints 
        problem += pl.lpSum([variables[a]* X_cum[a] for a in range(len(X_cum))]) <= Y_cum[0] #C1
        problem += pl.lpSum([variables[a] for a in range(len(X_cum))]) == 15 #C2
        
        # Run problem 
        problem.solve()
        
        #Getting Solution
        solution = []
        solve=[]
        for i, x in enumerate(variables):
              solution.append(x.value())
        solve.append(problem.objective.value())        
              
        return solution,solve  
    
    ####################### Get Cummulative List from Testing data############################
    def TestingCumList(self,startDate,EndDate):
        dfTest=self.DateTime_df[startDate:EndDate]
        dfTestCum = np.exp(np.log1p(dfTest).cumsum())
        RTestCumSum=[((dfTestCum.iloc[len(dfTest)-1,i]-dfTestCum.iloc[0,i])/dfTestCum.iloc[0,i]) for i in range(len(dfTest.columns)-1)]
        return RTestCumSum
    #################################Calling Training and Testing functions#####################################
    def IPWeightsClaculation(self):
        TrainingData=[]
        TestValue=[]
        ObjectiveList=[]
        for i in range(len(df_wft)):
            strategyList=self.TrainingForStratgy(self.df_wft.iloc[i,0],self.df_wft.iloc[i,1])
            TrainingData.append(strategyList[0])
            ObjectiveList.append(strategyList[1])
            CumList=self.TestingCumList(self.df_wft.iloc[i,2],self.df_wft.iloc[i,3])
            TestValue.append([sum(x * y for x, y in zip(strategyList[0], CumList))])
            
            #######################Creating and merging DataFrame#############################
            TrainingStrategy=pd.DataFrame(TrainingData, columns=df.columns[1:-1])
            TrainingObjective=pd.DataFrame(ObjectiveList,columns=['Training Objective'])
            TesingDf=pd.DataFrame(TestValue,columns=['Testing Result'])
                    
            FinalResult=pd.concat([self.df_wft,TrainingObjective,TesingDf,TrainingStrategy],axis=1)
        return FinalResult
    

object_1=IntegerProgrammingWts(df,df_wft)
z=object_1.IPWeightsClaculation()

z.to_csv("C:/Users/pooja.bhati/Downloads/GApoc/IP/IPStrategy.csv", index=False)
