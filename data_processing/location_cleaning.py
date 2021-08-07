def get_country_state():
	import pandas as pd
	import requests
	from bs4 import BeautifulSoup

	try:
		contry_dict = pd.read_csv('country_abbrev.csv', index_col=0)
	except:
		url = 'https://sustainablesources.com/resources/country-abbreviations/'
		raw = requests.get(url)
		soup = BeautifulSoup(raw.text, 'lxml')
		country_abb = soup.find_all('table')[1]
		contents=[[y.text for y in x.find_all('td')] for x in country_abb.find_all('tr')]
		contents = contents[2:]
		country_df = pd.DataFrame(contents, columns=['country', 'abbr'])
		country_dict = country_df.set_index('abbr').to_dict()['country']

	state_abb = pd.read_csv('state_abbrev.csv', header=None)
	state_abb = state_abb.set_index(0).to_dict()[1]
	state_abb['RHODE ISLAND'] = 'RI'

	return country_dict, state_abb



def get_country(x, country_dict):    
    if x in country_dict:
        return country_dict[x]
    else:
        return x


def state_clean(x):
    if x!='UNITED STATES' and len(x)>2:
        correct = x.split()[0].strip()
        if len(correct)==2:
            return correct
        else:
            return x
    else:
        return x


def get_state_abbrev(x):
    if x.upper() in state_abb:
        return state_abb[x.upper()]
    else:
        return x
    

def clean_location_db():
	import pymysql.cursors
	import pandas as pd

	connection = pymysql.connect(host="job-market.chfeqjbmewii.us-west-1.rds.amazonaws.com",
	                             user="root",password="mads_capstone",database="capstone",
	                             port=3306,charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	cursor = connection.cursor()

	sql = """select state, city, country, location, id from jd;"""
	cursor.execute(sql)
	data = cursor.fetchall()
	connection.close()

	data = pd.DataFrame(data)
	data.state = data.state.fillna(data.location)
	country_dict, state_abb = get_country_state()

	def get_state(x):
	    return x.split(',')[-1].strip()

	def get_city(x):
	    return x.split(',')[0].strip()

	data.country = data.country.fillna("")  
	data.country = data.country.apply(lambda x: get_country(x.upper(), country_dict))

	data['state'] = data['state'].fillna('')

	temp = data[data['state'].str.len()>2]
	## clean long state
	temp = data[data['state'].str.contains(',')]
	temp['city'] = temp['state'].apply(get_city)
	temp['state'] = temp['state'].apply(get_state)

	temp.state = temp.state.str.upper()
	temp.state = temp.state.str.replace('NEW YORK STATE', 'NEW YORK')
	temp.state = temp.state.str.replace('WASHINGTON STATE', 'WASHINGTON')

	temp.state = temp.state.apply(get_state_abbrev)
	temp.state = temp.state.apply(state_clean)


	connection = pymysql.connect(host="job-market.chfeqjbmewii.us-west-1.rds.amazonaws.com",
	                             user="root",password="mads_capstone",database="capstone",
	                             port=3306,charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	cursor = connection.cursor()

	for i in tqdm(range(len(temp))):
	    country = temp.iloc[i]['country']
	    state = temp.iloc[i]['state']
	    city = temp.iloc[i]['city']
	    id_ = temp.iloc[i]['id']
	    cursor.execute(f"""UPDATE jd SET state='{state}', city='{city}', country='{country}' WHERE id={id_};""")
	    connection.commit()
	    
	connection.close()
















