import pyodbc
import pandas as pd
from DBUtils.PooledDB import PooledDB
import googlemaps
import pickle
from app import general_pool_criteria

# use the googlemaps pacakages to geocode locations
# Please use the google map api key for geocoding services
# fengyang's API key: 'AIzaSyAfGrfnJVQH1V0hU3sBKxgydYMH107Jx2M'
gmap_api_key = ''
gmaps = googlemaps.Client(key=gmap_api_key)

conn = general_pool_criteria.connection()
cur = conn.cursor()
sql = '''
        select nct_id, facilities_and_contacts
        from dbo.aact_trial_info
        '''
cur.execute(sql)
trial_data = cur.fetchall()
conn.close()
cur.close()

def split_locs_into_list(x):
    loc_list = []
    if x is not None:
        loc_list = x.split('|')
    return loc_list

i = 0
nct_locs_dict = {}
nct_address_dict = {}  # nct: address: latlng
for nct_item in trial_data:
    i = i + 1
    nct_id = nct_item[0]
    all_loc = nct_item[1]
    all_loc_split = split_locs_into_list(all_loc)  # None -> []
    this_nct_latlng = []
    current_nct_address_dict = {}  # nct: address: latlng
    if len(all_loc_split) > 0:
        for loc in all_loc_split:
            this_loc_result = gmaps.geocode(loc)
            if len(this_loc_result) != 0:  # if there are searched results, empty result = []
                this_loc_latlng = this_loc_result[0]['geometry']['location']
            else:
                this_loc_latlng = None
            this_nct_latlng.append(this_loc_latlng)
            current_nct_address_dict[loc] = this_loc_latlng
    nct_locs_dict[nct_id] = this_nct_latlng
    nct_address_dict[nct_id] = current_nct_address_dict  # nct: address: latlng

    # count
    if i % 50 == 0:
        print(i)

# pickle.dump(nct_locs_dict, open('./nct_latlng_dict.pkl', 'wb'), protocol=2)
# pickle.dump(nct_address_dict, open('./nct_loc_latlng_dict.pkl', 'wb'), protocol=2)
pickle.dump(nct_locs_dict, open('../dquest-flask/app/resources/nct_latlng_dict.pkl', 'wb'), protocol=2)
pickle.dump(nct_address_dict, open('../dquest-flask/app/resources/nct_loc_latlng_dict.pkl', 'wb'), protocol=2)