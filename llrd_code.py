## SET UP
import pandas as pd
pd.set_option('display.max_columns', None)

## what years do you want to look back over?
years = ['2016', '2017', '2018', '2019']
years = pd.DataFrame(years)
years.columns = ['YEAR']


## ASSESSMENT DATA
## read in raw csv
asmt = pd.read_csv('/home/dan/Python/QueenCityCounts/llrd_code/data/2019-2020_Assessment_Roll.csv', dtype=object)
## select required columns only, and do some clean up
asmt = asmt[['PRINT KEY','PROPERTY CLASS','NEIGHBORHOOD', 'HOUSE NUMBER', 'STREET']].drop_duplicates()
asmt.rename(columns={'PRINT KEY':'SBL','PROPERTY CLASS':'PROP_TYPE','NEIGHBORHOOD':'NBHD', 'HOUSE NUMBER':'NUMBER'},inplace=True)
asmt['ADDRESS'] = asmt[['NUMBER','STREET']].apply(lambda x: ' '.join(x.values.astype(str)),axis=1)


## CODE VIOLATIONS DATA
## read in raw csv
vios = pd.read_csv('/home/dan/Python/QueenCityCounts/llrd_code/data/Code_Violations.csv', dtype=object)
## select required columns only, and do some clean up
vios = vios[['DATE', 'UNIQUEKEY', 'ADDRESS']].drop_duplicates()
vios['DATE'] = vios['DATE'].apply(lambda x: str(x).split(' ')[0])
vios['DATE'] = pd.to_datetime(vios['DATE'])
vios['NUMBER'] = vios['ADDRESS'].apply(lambda x: str(x).split(' ')[0])
vios['STREET'] = vios['ADDRESS'].apply(lambda x: ' '.join(str(x).split(' ')[1:]))
vios.rename(columns={'UNIQUEKEY':'VIOLATIONS'},inplace=True)
vios['YEAR'] = vios['DATE'].apply(lambda x: str(x.year))
vios = pd.pivot_table(vios, index=['NUMBER', 'STREET', 'YEAR'], values=['VIOLATIONS'], aggfunc='count')
vios.reset_index(inplace=True)


## RENTAL PROPERTY DATA
## read in raw csv
rent = pd.read_csv('/home/dan/Python/QueenCityCounts/llrd_code/data/Rental_Registry.csv', dtype=object)
## select required columns only, and do some clean up
rent = rent[['Print Key', 'Address', 'License Status', 'Issued Datetime', 'Expiration Datetime']].drop_duplicates()
rent = rent[rent['License Status']=='Active']
rent['NUMBER'] = rent['Address'].apply(lambda x: str(x).split(' ')[0])
rent['STREET'] = rent['Address'].apply(lambda x: ' '.join(str(x).split(' ')[1:]))
rent.rename(columns={'License Status':'STATUS','Issued Datetime':'ISSUED','Expiration Datetime':'EXPIRES','Print Key':'SBL','Address':'ADDRESS'},inplace=True)
rent['ISSUED'] = pd.to_datetime(rent['ISSUED'])
rent['EXPIRES'] = pd.to_datetime(rent['EXPIRES'])
rent['IS_RENTAL'] = int(1)


years = years.assign(key=1)
asmt = asmt.assign(key=1)

df = asmt.merge(years, on='key',how='inner').drop(columns=['key','ADDRESS'])
##df = df.sort_values(['YEAR','NUMBER','STREET'], ascending=True).reset_index(drop=True)

df = df.merge(rent[['NUMBER','STREET','IS_RENTAL']], on=['NUMBER','STREET'], how='left')
df['IS_RENTAL'].fillna(0, inplace=True)

df = df.merge(vios, on=['NUMBER','STREET','YEAR'], how='left')
df['VIOLATIONS'].fillna(0, inplace=True)

df = df.sort_values(['YEAR','NUMBER','STREET'], ascending=True).reset_index(drop=True)
