import pandas as pd
df = pd.read_pickle('website/jd_backup.pkl')
df = pd.DataFrame(df)
print(df.shape)
df1 = df.iloc[0:9000,:]
df2 = df.iloc[9000:,:]
print('one:\n', df1.shape)
print('two:\n', df2.shape)
df1.to_pickle('website/data1.pkl')
df2.to_pickle('website/data2.pkl')