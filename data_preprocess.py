import numpy as np
import pandas as pd
import pytz
from tzwhere import tzwhere
import datetime
import pysolar

def load_roundhill_data():
    df1=pd.read_excel("RHILL1Update01.XLS",sheet_name=0,skiprows=5,header=2,usecols=[1,2],
                      names=['Run','Q(g/s)'],index_col=0)
    df2=pd.read_excel("RHILL1Update01.XLS",sheet_name=1,skiprows=15,header=1).drop(0)
    df2.columns=df2.columns.str.strip()
    df2=df2.set_index('Run').drop('Unnamed: 0',axis=1)
    df3=pd.read_excel("RHILL1Update01.XLS",sheet_name=2)
    
    st=df3.to_csv(index=False,na_rep='-999')
    theta=[]
    R=[]
    wd=[]
    C=[]
    Run=[]
    Time=[]
    Date=[]
    for i in st.split('\n')[15:-2]:
        n=0
        r=i.split()
        if len(r)==2:
            if r[1].split(',')[0]!='(%)':
                d=','.join(r[0].split(',')[:3])
                e=(r[1].split(',')[0])
                t=r[1].split(',')[1][:2] +':'+ r[1].split(',')[1][2:4]
        elif len(r)==1:
            if r[0].split(',')[2] != "Sum(WD)":
                for i in range(3):
                    theta.append(r[0].split(',')[2])
                    wd.append(r[0].split(',')[3])
                    C.append(r[0].split(',')[4+i])
                n+=1
        for i in range(n):
            for j in range(3):
                Run.append(e)
                Time.append(t)
                Date.append(d)
            R.append(50)
            R.append(100)
            R.append(200)

    df4=pd.DataFrame({'Run':Run,'r':R,'theta':theta,'wd':wd,'Date':Date,'Time':Time,'C(mg/m3)':C})
    df4.set_index('Run',inplace=True)
    df4.index=df4.index.astype('int64')
    
    df5=pd.merge(df1,df2,'inner',left_index=True,right_index=True)
    df6=pd.merge(df5,df4,'inner',left_index=True,right_index=True)

    df1=pd.read_excel("RHILL2Update01.XLS",sheet_name=0,skiprows=4,header=2,usecols=[1,2],
                      names=['Run','Q(g/s)'],index_col=0)
    df1=df1[:10]
    df2=pd.read_excel("RHILL2Update01.XLS",sheet_name=1,skiprows=17,header=1)
    df2.columns=df2.columns.str.strip()
    df2=df2.set_index('Run').drop('Unnamed: 0',axis=1)
    
    df3=pd.read_excel("RHILL2Update01.XLS",sheet_name=2,usecols=[0,1,2,3,4,5,6])
    st=df3.to_csv(index=False,na_rep='-999')
    theta=[]
    R=[]
    wd=[]
    C=[]
    Run=[]
    Time=[]
    Date=[]
    for i in st.split('\n')[11:]:
        n=0
        r=i.split()
        if len(r)==2:
            if r[1].split(',')[0]!='Azimuth' and r[1].split(',')[0]!='(%)':
                d=','.join(r[0].split(',')[:3])
                e=r[1].split(',')[0]
                t=r[1].split(',')[1][:2] +':'+ r[1].split(',')[1][2:4]
        elif len(r)==1:
            if r[0].split(',')[2] != "Sum(WD)":
                for i in range(3):
                    theta.append(r[0].split(',')[2])
                    wd.append(r[0].split(',')[3])
                    C.append(r[0].split(',')[4+i])
                n+=1
        for i in range(n):
            for j in range(3):
                Run.append(e)
                Time.append(t)
                Date.append(d)
            R.append(50)
            R.append(100)
            R.append(200)

    df4=pd.DataFrame({'Run':Run,'r':R,'theta':theta,'wd':wd,'Date':Date,'Time':Time,'C(mg/m3)':C})
    df4.set_index('Run',inplace=True)
    df4.index=df4.index.astype('int64')
    
    df5=pd.merge(df1,df2,'inner',left_index=True,right_index=True)
    df7=pd.merge(df5,df4,'inner',left_index=True,right_index=True)
    df7.columns=['Q(g/s)', 'U2', 'Sa2', 'U1.5', 'U3.0', 'U6.0', 'U12.0', 'T1.5',
           'T3.0', 'T6.0', 'T12.0', 'r', 'theta', 'wd', 'Date', 'Time', 'C(mg/m3)']
    df7.index=df7.index+29
    ls=[df6,df7]
    df8=pd.concat(ls,join='outer',ignore_index=False)
    
    
    lat=41.542325
    lon= -70.94018611111112
    tz=tzwhere.tzwhere().tzNameAt(lat,lon)
    rad=[]
    for i,j in zip(df8['Date'],df8['Time']):
        dt=pytz.timezone(tz).localize(datetime.datetime.strptime(i+' '+j,'%d,%B,%Y %H:%M'))
        alt=pysolar.solar.get_altitude_fast(lat,lon,dt)
        rad.append(pysolar.radiation.get_radiation_direct(dt,alt))
    df8['Irradiation(W/m2)']=rad
    
    df8['theta']=df8['theta'].astype('float64')
    df8=df8[df8['theta']>=0]
    th=[]
    X=[]
    Y=[]
    for i in df8.index.unique():
        mf=df8.loc[i]
        tm=mf.iloc[int(len(mf['theta'].unique())/2)*3]['theta']    
        for k,l in zip(mf['theta'],mf['r']):

            X.append(l*np.cos((tm-k)*(np.pi/180)))
            Y.append(l*np.sin((tm-k)*(np.pi/180)))

    df8['X']=X
    df8['Y']=Y
    
    features=['Q(g/s)', 'U2','Sa2','Irradiation(W/m2)','wd', 'X', 'Y','C(mg/m3)']
    df=df8[features].astype('float64')
    df=df[df['C(mg/m3)']>=0]
    df=df[df['wd']>=0]
    
    return df


def load_prairie_data():
    with open("prairie.txt","r") as f:
        ls=f.readlines()
    
    Exp_no=[]
    Time=[]
    X=[]
    Y=[]
    Q=[]
    C=[]
    z=[]
    D=[]
    for i in ls[1:]:
        n=0
        r=i.split()

        if len(r)==6:
            e=(int(r[0][:-1]))
            t=r[3][3:5]+':'+r[3][5:7]
            d=r[2][:-2]+'19'+r[2][-2:]
        elif len(r)==11:
            q=float(r[7][:-1])
        elif len(r)==4:
            X.append(int(r[2]))
            Y.append(int(r[1]))
            C.append(float(r[3]))
            n+=1

        for j in range(n):
            Q.append(q)
            Exp_no.append(e)
            Time.append(t)
            D.append(d)
    df=pd.DataFrame({
        'Exp':Exp_no,
        'Q(g/s)':Q,
        'Date':D,
        'time(H)':Time,
        'r(m)':X,
        'theta(degree)':Y,
        'C(g/m3)':C

    })
    df.set_index(['Exp'],inplace=True)
    
    df_mixH=pd.read_excel("PGrassDaytimeZi.xls")[9:].iloc[:,0:2].astype('float64')
    df_mixH.columns=['Exp','MixingHeight(m)']
    df_mixH.set_index(['Exp'],inplace=True)
    df_mixH=df_mixH[df_mixH>0]
    df_mixH=df_mixH.fillna(df_mixH.min()-20)
    
    df2=pd.merge(df,df_mixH,how='inner',left_index=True,right_index=True)
    
    d={}
    with open("Wind&Temp.txt","r") as f:
        ls=f.readlines()
    for i in ls[13:]:
        r=i.split()
        if len(r)==2:
            if 'Exp' not in d:
                d['Exp']=[]  
            d['Exp'].append(int(r[1]))
        elif len(r)==3:
            if 'U'+r[0]+'(m/s)' not in d:
                d['U'+r[0]+'(m/s)']=[]
            if 'T'+r[0]+'(C)' not in d:
                d['T'+r[0]+'(C)']=[]
            d['U'+r[0]+'(m/s)'].append(r[2])
            d['T'+r[0]+'(C)'].append(r[1])
    dfw=pd.DataFrame(d).set_index(['Exp'])
    
    df3=pd.merge(df2,dfw,how='inner',left_index=True,right_index=True)
    
    lat=42.49333333333333
    lon= -98.57166666666667 
    tz=tzwhere.tzwhere().tzNameAt(lat,lon)
    rad=[]
    for i,j in zip(df3['Date'],df['time(H)']):
        dt=pytz.timezone(tz).localize(datetime.datetime.strptime(i+' '+j,'%m/%d/%Y %H:%M'))
        alt=pysolar.solar.get_altitude_fast(lat,lon,dt)
        rad.append(pysolar.radiation.get_radiation_direct(dt,alt))
    df3['Irradiation(W/m2)']=rad
    
    th=[]
    X=[]
    Y=[]
    for i in df3.index.unique():
        #print(df3.loc[i])
        mf=df3.loc[i]
        for j in mf['r(m)'].unique():
            mf2=mf[mf['r(m)']==j]
            tm=mf2.iloc[int(mf2['theta(degree)'].count()/2)]['theta(degree)']
            for k,l in zip(mf2['theta(degree)'],mf2['r(m)']):
                X.append(l*np.cos((tm-k)*(np.pi/180)))
                Y.append(l*np.sin((tm-k)*(np.pi/180)))

    df3['X']=X
    df3['Y']=Y
    
    features=['Q(g/s)','MixingHeight(m)','U0.50(m/s)','T0.50(C)','X','Y','C(g/m3)','Irradiation(W/m2)']
    df=df3[features].astype('float64')
    df=df[df['C(g/m3)']>=0]
    df=df[df['U0.50(m/s)']>=0]
    
    return df

