import pandas as pd
df = pd.read_pickle('website/jd_backup.pkl')
df = pd.DataFrame(df)
print(df.shape)
df1 = df.iloc[0:6000,:]
df2 = df.iloc[6000:12000,:]
df3 = df.iloc[12000:,:]
print('one:\n', df1.shape)
print('two:\n', df2.shape)
print('three:\n', df3.shape)
df1.to_pickle('website/data1.pkl')
df2.to_pickle('website/data2.pkl')
df3.to_pickle('website/data3.pkl')