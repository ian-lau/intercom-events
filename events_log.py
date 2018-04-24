import requests
import urllib
import pandas as pd
import matplotlib.pyplot as plt

# Enter API Key below
headers = {
	'Authorization': '',
	'Accept': 'application/json'
	}

#Enter Segment ID below
segment_id = ''

url = 'https://api.intercom.io/users?segment_id='+segment_id
events_url_a = 'https://api.intercom.io/events?type=user&per_page=100&user_id='

user_list = []
events_log = []

def fetch_users():
	r = requests.get(url, headers=headers)
	global data
	data = r.json()
	for user in range(len(data['users'])):
		user_list.append(str(data['users'][user]['user_id']))
	print ('Fetching Users... Page '+str(data['pages']['page'])+' of '+str(data['pages']['total_pages']))

def fetch_events():
	events_url = events_url_a+urllib.quote_plus(user_list[user])
	r = requests.get(events_url, headers=headers)
	global data
	data = r.json()
	for event in range(1,len(data['events'])):
		events_log.append([
			data['events'][event]['type'],
			data['events'][event]['id'],
			data['events'][event]['created_at'],
			data['events'][event]['event_name'],
			data['events'][event]['user_id'],
			data['events'][event]['email'],
			data['events'][event]['intercom_user_id']
		])
	print ('Fetching Events.... '+str(user_list[user])+' '+str(user)+'/'+str(len(user_list))+' '+str(len(events_log)))

print ('*** Segment: '+requests.get('https://api.intercom.io/segments/'+segment_id, headers=headers).json()['name']+' ***')

fetch_users()

while (data['pages']['next'] is not None):
	global url
	url = data['pages']['next']
	fetch_users()

print ('*** user_list is ready. ***')

for user in range(len(user_list)):
	fetch_events()
	while ('next' in data['pages'] == True):
		global events_url
		events_url = data['pages']['next']
		fetch_events()

print ('*** events_log is ready. ***')

df = pd.DataFrame(events_log, columns=['type','id','created_at','event_name','user_id','email','intercom_user_id'])
df = df[df['event_name'].str.contains('reacted') == False]
df['created_at'] = pd.to_datetime(df['created_at'],unit='s')
df.to_csv('raw_log.csv')

for type in df['event_name'].unique():
	print ('Generating reports... '+str(type))
	rs = df.loc[df['event_name'] == type]
	group_by_month = pd.DataFrame(rs.groupby([rs['created_at'].dt.year, rs['created_at'].dt.month]).agg('count'), columns=['event_name'])
	group_by_month.plot(title=type,rot=45,legend=False)
	plt.tight_layout()
	plt.savefig(type+' - monthly.png')
	group_by_day = pd.DataFrame(rs.groupby([rs['created_at'].dt.year, rs['created_at'].dt.month, rs['created_at'].dt.day]).agg('count'), columns=['event_name'])
	group_by_day.plot(title=type,rot=45,legend=False)
	plt.tight_layout()
	plt.savefig(type+' - daily.png')
	group_by_week = pd.DataFrame(rs.groupby([rs['created_at'].dt.year, rs['created_at'].dt.week]).agg('count'), columns=['event_name'])
	group_by_week.plot(title=type,rot=45,legend=False)
	plt.tight_layout()
	plt.savefig(type+' - weekly.png')
	plt.close('all')
	rs.to_csv(type+'.csv', index=False)
	group_by_month.to_csv(type+' - monthly.csv')
	group_by_day.to_csv(type+' - daily.csv')
	group_by_week.to_csv(type+' - weekly.csv')
