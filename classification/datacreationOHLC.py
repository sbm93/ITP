import pandas as pd
import numpy as np
df=pd.read_csv("C:/Users/pooja.bhati/Downloads/GApoc/Classification/FCPO3-OHLCV.csv")


T1=df.iloc[:,1:].shift(1, axis=0)
T2=df.iloc[:,1:].shift(2, axis=0)
T3=df.iloc[:,1:].shift(3, axis=0)
T4=df.iloc[:,1:].shift(4, axis=0)

NewT=pd.concat([df,T1,T2,T3,T4],axis=1)

NewT.columns=['Date', 'Open(t)', 'High(t)', 'Low(t)', 'Close(t)', 'Total Trade Quantity(t)',
        'Open(t-1)', 'High(t-1)', 'Low(t-1)', 'Close(t-1)', 'Total Trade Quantity(t-1)',
        'Open(t-2)', 'High(t-2)', 'Low(t-2)', 'Close(t-2)', 'Total Trade Quantity(t-2)',
        'Open(t-3)', 'High(t-3)', 'Low(t-3)', 'Close(t-3)', 'Total Trade Quantity(t-3)',
        'Open(t-4)', 'High(t-4)', 'Low(t-4)', 'Close(t-4)', 'Total Trade Quantity(t-4)']

def rsi(values):
    up = values[values>0].mean()
    down = -1*values[values<0].mean()
    return 100 * up / (up + down)

NewT['Momentum_1D'] = (NewT['Close(t)']-NewT['Close(t)'].shift(1)).fillna(0)
NewT['RSI_14D'] = NewT['Momentum_1D'].rolling(center=False, window=5).apply(rsi).fillna(0)

def bbands(price, length=5, numsd=2):
    """ returns average, upper band, and lower band"""
    #ave = pd.stats.moments.rolling_mean(price,length)
    ave = price.rolling(window = length, center = False).mean()
    #sd = pd.stats.moments.rolling_std(price,length)
    sd = price.rolling(window = length, center = False).std()
    upband = ave + (sd*numsd)
    dnband = ave - (sd*numsd)
    return np.round(ave,3), np.round(upband,3), np.round(dnband,3)

NewT['BB_Middle_Band'], NewT['BB_Upper_Band'], NewT['BB_Lower_Band'] = bbands(NewT['Close(t)'], length=5, numsd=1)
NewT['BB_Middle_Band'] = NewT['BB_Middle_Band'].fillna(0)
NewT['BB_Upper_Band'] = NewT['BB_Upper_Band'].fillna(0)
NewT['BB_Lower_Band'] = NewT['BB_Lower_Band'].fillna(0)

def STOK(df, n):
    df['STOK'] = ((df['Close(t)'] - df['Low(t)'].rolling(window=n, center=False).mean()) / (df['High(t)'].rolling(window=n, center=False).max() - df['Low(t)'].rolling(window=n, center=False).min())) * 100
    df['STOD'] = df['STOK'].rolling(window = 3, center=False).mean()
    
STOK(NewT, 5)   


NewT['26_ema'] = NewT['Close(t)'].ewm(span=26,min_periods=0,adjust=True,ignore_na=False).mean()
NewT['12_ema'] = NewT['Close(t)'].ewm(span=12,min_periods=0,adjust=True,ignore_na=False).mean()
NewT['MACD'] = NewT['12_ema'] - NewT['26_ema']


def stationarity(NewT, window):
    NewT['roll_mean'] = NewT['Close(t)'].rolling(window).mean()
    
    
stationarity(NewT, 5)  

def classification_Y_Finder(df,UpTrend=5,DownTrend=5):
    Close_X=df.iloc[:,4:5].values
    
    Close_XPercentage=[(((Close_X[i+5]-Close_X[i])/Close_X[i])*100) for i in range(0,len(Close_X)-5)]+[1,1,1,1,1]
    print(Close_XPercentage)
    Y=[]
    for eV in Close_XPercentage:
        if eV > UpTrend: Y.append("Up Trand")
        elif eV <  -(DownTrend): Y.append("Down Trand")
        else: Y.append("No Trand")
        
    Finaldf=pd.concat([df,pd.DataFrame(Y,columns=["Trend"])],  axis=1)
    
    return Finaldf
    
Newdf=classification_Y_Finder(NewT,3,3)
MergeDF=Newdf.iloc[6:,:]
MergeDF.to_csv("C:/Users/pooja.bhati/Downloads/GApoc/Classification/UpdatedData.csv")