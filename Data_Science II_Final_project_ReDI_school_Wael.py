#!/usr/bin/env python
# coding: utf-8

# # Implementing Modern Geophysical Well Log Data Analysis and Visualisation Techniques for Accurate Gap Prediction, Interpretation and Intervention to Eliminate Catastrophes

# # Abstract 
# Well log data collected in the field often include gaps and out of range readings , which means that data have missing values and outliers for many reasons, for instance due to noise. This makes it hard to rely on it for the interpretation of lithological properties. To address the gaps and out of range data issue, I present ansd compare different gap-fill algorithms. The proposed methods predict missing values of each measurement separately based on data points around the missing data point from the same well. The algorithms were applied on a LAS data file from BAUMAN #3 in Kansas.The data used in this work is a free dataset provided by the University of Kansas. In this paper I will be using Python 3 version for coding.

# 
# # 1 Introduction

# Well data are the geophysical measurements acquired along a borehole, providing direct information about the reservoir characterization. The data is collected during any phase of a well history: drilling, completing, producing, or abandoning. The data collected by logging wells can have significant economic consequences, due to the costs inherent to drilling wells, and the potential return of oil deposits. The quality of acquired data as well as data processing and interpretation techniques are crucial for taking drilling / production decisions and eliminating catastrophes. 
# The aim of this work is to develop a well log data processing, data cleaning, analysis and interpretation model to have a precise understanding of the well geological properties and test the functionality of the measurement tools. In this paper, I will focus on data cleaning, gap filling and visualization methods based on the collected data from the same well. The data used in this work is a free dataset provided by the University of Kansas.
# The first section will explain a method for reading Log ASCII Standard (LAS) files and the required libraries. The second section covers data cleaning and fixing missed data using different approaches. The last section will cover data visualization and interpretation aspects.

# # 2 Reading LAS file

# Log ASCII Standard (LAS) file format is the most commonly used format to store well log data. Since LAS files cannot be read by the common library in python such as Numpy and Pandas, a special library should be used for this purpose. The most commonly used libraries for this purpose in Python are: libLAS, laspy and lasio.
# 
# **Install lasio**
# 
# 
# 
# 

# In[1]:


get_ipython().system('pip install lasio')
get_ipython().system('pip install -r optional-packages.txt')
get_ipython().system('pip install --upgrade lasio')
get_ipython().system('pip install missingno')


# **Import Libraries:**

# In[3]:


import pandas as pd
import numpy as np
import lasio
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno
from sklearn.impute import SimpleImputer
from sklearn.impute import KNNImputer
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import MinMaxScaler
get_ipython().run_line_magic('matplotlib', 'inline')


# **Read LAS file:**

# In[4]:


las = lasio.read(r'1051661161.las')


# **Checking the header description:**
# 
# Using this command, we get fundamental information about our log data such as units and the quality of our data points in the file.

# In[5]:


las.curves


# **Coverting data into a data frame:**
# 
# For the sake of this project and in order to be able to apply the main libraries we have studied during the Data Science II course, I will convert our data to a data frame.

# In[53]:


df = las.df()


# **Checking the header:**

# In[ ]:


df.head()


# **Check the tailer:**

# In[ ]:


df.tail()


# **Check the description:**

# In[ ]:


df.describe()


# In[ ]:


df.columns


# # 3 Data cleaning
# Since out of range and null values are inevitable in well logs, developing precise and practical solutions to overcome these issues is crucial to ensure the credibility of the collected data. From my own experience, the most common technique to solve these issues was to eliminate the line of measurements source of the problem completely, which I think is inappropriate since it affects the data resolution, implies the risk of eliminating vital data and increase the  risk of well catastrophes such as: missing the targeted zone, reaching an unexpected formation amateurly during the drilling practice.
# The objectives of this section are:
# *   Use a data cleaning algorithm for data filtering to eliminate outliers.
# *   Develop and compare different techniques to deal with missing data using data from the same well.
# 

# # 3.1 Cleaning Outliers
# Measurement normalization identifies and removes systematic errors from well log data so that reliable results may be obtained for reservoir evaluation, solving difficult correlation and seismic modeling problems. For that, plenty of techniques and algorithms were developed to provide an accurate data normalization, most of which use machine learning models to correlate data from different adjacent wells at the same reservoir. However, in this section I will introduce a simple technique to convert outliers to NaN values and leave it to be processed as a missing data in the next section.
# The lithological properties of different formations have a normal range. The readings out of that range should not be accounted for. The normal range of essential measurements is described in the following table:
# 
# ![Normal range.jpeg](data:image/jpeg;base64,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)

# In[20]:


# Boxplot shows GR readings range (normal range is 0 - 250)
sns.boxplot( x= 'GR', data = df)


# **Removing outliers:**

# In[ ]:


# Before
df.describe()


# The following method is commonly used in the field to eliminate outliers. As we can see, even though this method eliminates outliers, it completely gets rid of the whole measurement line containing the outlier and eventually drastically reduces the density and the quality of our measurements.

# In[ ]:


# Method 1: Filter out outliers (Old method used in the field)
df_clean_outliers = df[(df.CNPOR > -15)&(df.CNPOR <= 50)]
df_clean_outliers = df_clean_outliers[(df_clean_outliers.GR > 0) & (df_clean_outliers.GR  <= 250)]
df_clean_outliers = df_clean_outliers[(df_clean_outliers.RHOB> 1) & (df_clean_outliers.RHOB<= 3)]
df_clean_outliers = df_clean_outliers[(df_clean_outliers.DT > 30) & (df_clean_outliers.DT <= 140)]
df_clean_outliers = df_clean_outliers[(df_clean_outliers.SPOR > -10) & (df_clean_outliers.SPOR <= 50)]
df_clean_outliers.describe()


# In the following method, the outliers are converted into  null values. This way we guarantee eliminating the outliers and maintain the density of the measurements which has a remarkable impact on the quality. 

# In[ ]:


# Method 2: convert outliers to NaN values

def clean_outliers(data):
  for x in data['CNPOR']:
    if  x < -15 or x > 50:
      data['CNPOR'] = data['CNPOR'].replace(x, np.nan)
  
  for x in data['GR']:
    if  x < 0 or x > 250:
      data['GR'] = data['GR'].replace(x, np.nan)

  for x in data['RHOB']:
    if  x < 1 or x > 3:
      data['RHOB'] = data['RHOB'].replace(x, np.nan)
  
  for x in data['DT']:
    if  x < 30 or x > 140:
      data['DT'] = data['DT'].replace(x, np.nan)
  
  for x in data['SPOR']:
    if  x < -10 or x > 50:
      data['SPOR'] = data['SPOR'].replace(x, np.nan)
  for x in data['RILM']:
    if  x  > 1000:
      data['RILM'] = data['RILM'].replace(x, np.nan)
  for x in data['RILD']:
    if  x  > 1000:
      data['RILD'] = data['RILD'].replace(x, np.nan)
  for x in data['RLL3']:
    if  x  > 1000:
      data['RLL3'] = data['RLL3'].replace(x, np.nan)
  return data

df = clean_outliers(df)
df.isna().sum()


# In[23]:


# Boxplot shows GR readings range after removing outliers (normal range is 0 - 250)
sns.boxplot( x= 'GR', data = df)


# # 3.2 Handling missing values
# 
# Well lithological properties are random and aperiodic and depend on factors like mineral composition or lithology, porosity, cementation and compaction, presence of fluids etc. Null values in Well data are very common issues. Measurement data can contain a non zero amount of missing values for plenty of reasons. This eventually leads to  a great impact on the quality of our data, so do repair methods. Thus, based on the essence of measurement gap, we should be critical when we decide which, where and how the reading gap should be handled. For example: we should consider the sensor offset, size of the gap, and whether the gap interval is logged or not. The common methods for handling missing values in the field are: relogging the missing interval or simply getting rid of it. In this section I will introduce five methods for handling missing data and compare the impact of each method on the quality of our data.

# In[ ]:


df.isna().sum()


# In[55]:


# A plot shows missing values
sns.heatmap(df.isnull(), cbar=True)
#msno.matrix(df)


# **3.2.1 Eliminating null values:**
# 
# Although it's apparent inefficiency and dangers, getting rid of the missing data is still a very common method. This method reduces the quality of our model as it reduces sample size because it deletes all other observations where any of the variable is missing.The higher the amount of missing data, the greater the impact of this method.

# In[34]:


# Drop rows of missing data
df_eliminate_na = df.dropna(axis=0, how='any')
df_eliminate_na.isna().sum().sum()


# In[57]:


#msno.matrix(df_eliminate_na)
sns.heatmap(df_eliminate_na.isnull(), cbar=True)


# **3.2.2 Replace missing values with mean using Univariate feature imputation**
# 
# This method provides a basic strategy for imputing missing values. Missing values are imputed with using the statistics mean of each column in which the missing values are located. This method lacks the accuracy since it replaces all missing values using one value and neither take into consideration the change in formation properties nor unlogged intervals and sensors offset.

# In[58]:


df_Simple_impute = df
imp = SimpleImputer(missing_values=np.nan, strategy='mean')
imp.fit(df_Simple_impute)
SimpleImputer(missing_values=np.nan)
X_test = df_Simple_impute
df_Simple_impute = pd.DataFrame(imp.transform(X_test), columns = [ 'AVTX', 'BVTX', 'CILD', 'CNDL', 'CNLS', 'CNPOR', 'CNSS', 'GR', 'LSPD',
       'LTEN', 'RILD', 'RILM', 'RLL3', 'RXORT', 'SP', 'MCAL', 'MI', 'MN',
       'ITT', 'DT', 'SPOR', 'DCAL', 'RHOB', 'RHOC', 'DPOR'])

df_Simple_impute['Depth'] = df.index
df_Simple_impute.set_index(df.index, inplace=True)

df_Simple_impute.isna().sum().sum()


# In[37]:


#msno.matrix(df_Simple_impute)
sns.heatmap(df_Simple_impute.isnull(), cbar=True)


# **3.2.3 Impute Missing Values using Interpolation Method:**
# 
# Imputation fills in the missing value with some number. The imputed value won't be exactly right in most cases, but it usually gives more accurate models than dropping the column entirely. Since well logs are continuous data with reference to depth, often the average of previous and next values gives a better estimate of the missing value. This method is efficient in avoiding missing data on top and the bottom of the well log since this gap has to do with the sensor offset, and the interval from / to which the measurement tool is used.

# In[59]:


mask = df.interpolate(axis=0, limit_area='inside', limit=6, limit_direction='backward').isna()
df_imput_interpol = df.interpolate(axis=0, limit_area='inside', limit=6).mask(mask)
df_imput_interpol.isna().sum().sum()


# In[60]:


#msno.matrix(df_imput_mean)
sns.heatmap(df_imput_interpol.isnull(), cbar=True)


# **3.2.4 K-nearest-neighbour Imputation:**
# 
# In this method, the missing values get imputed based on the K-nearest-neighbour algorithm. With this algorithm, the missing values are replaced by the nearest neighbor estimated values. This method weights samples using the mean squared difference on features for which two rows both have observed data. This method is efficient in predicting the gaps inside the log data, in the other hand it has proven it's insufficiency in predicting the unlogged intervals such as the log top and bottom readings.

# In[62]:


impute_KNN_train = df
lis = []
for i in range(0, impute_KNN_train.shape[1]):
     
    if(impute_KNN_train.iloc[:,i].dtypes == 'object'):
        impute_KNN_train.iloc[:,i] = pd.Categorical(impute_KNN_train.iloc[:,i])
        impute_KNN_train.iloc[:,i] = impute_KNN_train.iloc[:,i].cat.codes 
        impute_KNN_train.iloc[:,i] = impute_KNN_train.iloc[:,i].astype('object')
         
        lis.append(impute_KNN_train.columns[i])

impute_KNN_train = pd.DataFrame(KNNImputer(n_neighbors = 4).fit_transform(impute_KNN_train), columns = impute_KNN_train.columns)
impute_KNN_train
imputer = KNNImputer(n_neighbors=4, weights="uniform")

df_imput_KNN = imputer.fit_transform(df)
df_imput_KNN = pd.DataFrame(df_imput_KNN, columns = [ 'AVTX', 'BVTX', 'CILD', 'CNDL', 'CNLS', 'CNPOR', 'CNSS', 'GR', 'LSPD',
       'LTEN', 'RILD', 'RILM', 'RLL3', 'RXORT', 'SP', 'MCAL', 'MI', 'MN',
       'ITT', 'DT', 'SPOR', 'DCAL', 'RHOB', 'RHOC', 'DPOR'])

df_imput_KNN['Depth'] = df.index
df_imput_KNN.set_index(df.index, inplace=True)

df_imput_KNN.isna().sum().sum()


# In[63]:


#msno.matrix(df_imput_KNN)
sns.heatmap(df_imput_KNN.isnull(), cbar=True)


# **3.2.5 Nearest Neighbors Regression:**
# 
# Neighbors-based regression is a practical imputation method when the data labels are continuous rather than discrete variables, which is the case in well log data. Nearest neighbors regression uses uniform weights thereby, each point in the local neighborhood contributes uniformly to the classification of a query point. However, this method is advantageous to weight points such that nearby points contribute more to the regression than faraway points. Therefore, this method also is efficient in avoiding missing data on top and the bottom of the well log.
# 

# In[64]:


def impute_model_progressive(df):
  cols_nan = df.columns[df.isna().any()].tolist()
  cols_no_nan = df.columns.difference(cols_nan).values
  while len(cols_nan)>0:
      col = cols_nan[0]
      test_data = df[df[col].isna()]
      train_data = df.dropna()
      knr = KNeighborsRegressor(n_neighbors=4).fit(train_data[cols_no_nan], train_data[col])
      df.loc[df[col].isna(), col] = knr.predict(test_data[cols_no_nan])
      cols_nan = df.columns[df.isna().any()].tolist()
      cols_no_nan = df.columns.difference(cols_nan).values
  return df

df_imput_progressive = impute_model_progressive(df)
df_imput_progressive.isna().sum().sum()


# In[65]:


#msno.matrix(df_imput_progressive)
sns.heatmap(df_imput_progressive.isnull(), cbar=True)


# # 3.3 Comparison between different gap filling methods:
# 
# In this section I will compare the different gap filling techniques introduced earliers taking an example of Gamma Ray log since it implies a plenty of gaps and it's the most frequently used measurement in detecting formation features. 
# As we can observe in the graph below, eliminating null values method has an unignorable impact on the quality of our data. Not only that, it also eliminates a plenty of good readings present at the same row together will null values. 
# Having a look at the heatmaps below each technique we realise that imputing missing values using interpolation method has succeeded in detecting and avoiding gaps occured due to reading start depth and sensor offset at top and bottom of the log. It also gave us an accurate prediction of the missed values. Even though the other methods gave almost the same accurate prediction results, these methods failed in avoiding gaps at the top and bottom of the log. However, this problem could be solved manually by determining which interval of interest, but this will interfere with the sole purpose of this paper in empowering automation in order to save time, provide accurat solutions and avoid human errors.

# In[66]:


df['GR'].plot( figsize=(20, 10), label = 'Original log')
df_eliminate_na['GR'].plot( figsize=(20, 10) , label = 'Eliminating null values')
df_Simple_impute['GR'].plot( figsize=(20, 10), label = 'Univariate feature imputation')
df_imput_interpol['GR'].plot(figsize=(20, 10) , label = 'Interpolation')
df_imput_KNN['GR'].plot(figsize=(20, 10), label = 'K-nearest-neighbour Imputation')
df_imput_progressive['GR'].plot( figsize=(20, 10), label = 'Nearest Neighbors Regression')
plt.title('Comparison between different gap filling methods on GR log')
plt.legend()


# # 4 Data Visualisation and Interpretation:
# 
# In this section I will introduce different data visualisation techniques that will help checking the quality of our measurements and detecting sensor failures, provide a better interpretation of formation lithologies and formation fluids.

# # 4.1 Quality Check and failure detection:
# 
# In this section I will group readings of the same measurement from different sensors together and see if the readings have the same trend. This method will help us to check the occuracy of measurement correction models, the functionality and quality of the readings from different sensors and detect failed sensors.

# **Resistivity measurement:**
# 
# Resistivity logs determine what types of fluids are present in the reservoir
# formation by measuring how effective these rocks are at conducting electricity. Conventional resistivity logs were made by means of electrodes in contact with the formation through the drilling mud. Several sondes were capable of measuring to different distances (Short Normal (RLL3), medium Normal (RILM) and deep (RILD)). Comparing different resistivity logs gives us indication about the validity of our correction models and sensors functionality.
# The log below shows that resistivity readings from the different sensors have the same trend, which means all sensors are functioning well and the correction model is accurate.

# In[67]:


df_imput_interpol['RILD'].plot(figsize=(20, 10) , label = 'RILD')
df_imput_interpol['RILM'].plot(figsize=(20, 10) , label = 'RILM')
df_imput_interpol['RLL3'].plot(figsize=(20, 10) , label = 'RLL3')
plt.title('Comparison between Resistivity readings from different sensors')
plt.legend()


# ****

# In[46]:


df_imput_interpol.columns


# **Porosity measurement:**
# 
# Porosity logs work by bombarding a formation with high energy epithermal neutrons that lose energy through elastic scattering to near thermal levels before being absorbed by the nuclei of the formation atoms. In the following log we can observe that different porosity logs have the same trend which indicates the functionality of the correction model used in this well.

# In[68]:


df_imput_interpol['CNDL'].plot(figsize=(20, 10) , label = 'CNDL')
df_imput_interpol['CNLS'].plot(figsize=(20, 10) , label = 'CNLS')
df_imput_interpol['CNPOR'].plot(figsize=(20, 10) , label = 'CNPOR')
df_imput_interpol['CNSS'].plot(figsize=(20, 10) , label = 'CNSS')
plt.title('Comparison between Porosity readings using different corrections')
plt.legend()


# # 4.2 Log Interpretation:
# 
# Different log data show different formation properties. Gamma ray and Poisson’s ratio are excellent lithology indicators, while others like Density and P-wave velocity logs are useful for understanding the rock type, types of pore fluids as well as the pressure and compaction trends in the deposited sediments. Density porosity, a physical property that is derived from density logs gives a measure of the amount of pore space in the same rock type or different rock-type. 
# The log responses with respect to bed boundaries are different for different lithologies. Lower GR, Poisson’s ratio, density, velocity values and higher porosity values are characteristics of clean sands. Shales tend to have higher GR values compared to sand. The porosity is extremely low compared to sands, while density, Poisson’s ratio and velocity values are higher. Salt has properties in between sand and shales.
# 

# In[80]:


df_plot = df_imput_interpol.rename_axis('Depth').reset_index()


# In[91]:


def measurement_log(data):
    data = data.sort_values(by='Depth')
    top = data.Depth.min()
    bot = data.Depth.max()
    
    f, ax = plt.subplots(nrows=1, ncols=5, figsize=(12,8))
    ax[0].plot(data.GR, data.Depth, color='green')
    ax[1].plot(data.CNPOR, data.Depth, color='red')
    ax[2].plot(data.DT, data.Depth, color='black')
    ax[3].plot(data.MCAL, data.Depth, color='blue')
    ax[4].plot(data.RHOB, data.Depth, color='c')
        
    for i in range(len(ax)):
        ax[i].set_ylim(top,bot)
        ax[i].invert_yaxis()
        ax[i].grid()
        
    ax[0].set_xlabel("GR")
    ax[0].set_xlim(data.GR.min(),data.GR.max())
    ax[0].set_ylabel("Depth(ft)")
    ax[1].set_xlabel("CNPOR")
    ax[1].set_xlim(data.CNPOR.min(),data.CNPOR.max())
    ax[2].set_xlabel("DT")
    ax[2].set_xlim(data.DT.min(),data.DT.max())
    ax[3].set_xlabel("MCAL")
    ax[3].set_xlim(data.MCAL.min(),data.MCAL.max())
    ax[4].set_xlabel("RHOB")
    ax[4].set_xlim(data.RHOB.min(),data.RHOB.max())
    
    ax[1].set_yticklabels([]); ax[2].set_yticklabels([]);
    ax[3].set_yticklabels([])
    ax[4].set_yticklabels([])
    
    f.suptitle('Well: BAUMAN #3', fontsize=14,y=0.94)


# In[92]:


measurement_log(df_plot)


# # 5 Conclusion:
# 
# Conclusion
# This paper attempted to address the most encountered issues in the field of geophysical well log data processing, proposed, explained and compared different data cleaning, gap filling, quality check and interpretation techniques using data collected from BAUMAN #3 well. The study showed how poowerfull and promising Python tools and libraries can serve in this field. 
# 

# # 6 Future work:
# In the next work I will  work on developing and comparing different supervised and unsupervised ML models for for gaps filling and interpreting well lithological properties automatically based on a collective amount of training well log data from the same reservoir. This includes collecting a high amount of logs, analyse the gaps on a log-by-log basis, define and fine tune each algorithm, cluster samples by log similarity and develop different models for the same well  in order to improve the prediction performance. 
