import os
import http.client, urllib.parse
import re
import json
import requests
from requests.structures import CaseInsensitiveDict
from itertools import permutations
import requests
from requests.structures import CaseInsensitiveDict

# Global variables
API_positionstack = '1e57ed874449552fae4422aeb9074bc4'
API_geoapify = '6f6e5a24827946c9951b3f6d4338f44f'

# Country code
def get_code(country):
    f = open('country_code.json')
    data = json.load(f)
    cc = [c['alpha-2'] for c in data if c['name'] == country][0]
    return cc

# Get coordinates of locations
def get_coordinates(location_string):
    conn = http.client.HTTPConnection('api.positionstack.com')
    destination = location_string.split(',')
    city = destination[0]
    country = get_code(destination[1][1:])
    params = urllib.parse.urlencode({
        'access_key': API_positionstack,
        'query': city,
        'country': country,
        'limit': 1,
        })
    conn.request('GET', '/v1/forward?{}'.format(params))
    res = conn.getresponse()
    data = res.read()
    data_dc = data.decode('utf-8')
    reg_ex = '-?[0-9]+.[0-9]+'
    re_list = re.findall(reg_ex, data_dc)
    location = re_list[:2][::-1]
    return (location)

# Get user input of cities
print('Enter locations with following format: City, Country')
print('Example: Sydney, Australia\n')
print('When you are finished, just write "done"')
loc_list = []
def enter_city(n):
        msg = 'Please enter location no. {}: '.format(n)
        loc = input(msg)
        if loc == 'done':
            exit
        else:
            loc_list.append(loc)
            enter_city(n + 1)
              
      
enter_city(1)
print(loc_list)
    
# Get coordinates of locations
coords_dict = {}
for loc in loc_list:
    coords = get_coordinates(loc)
    coords = [float(c) for c in coords]
    coords_dict[loc] = coords

# Request data
def get_data(locs):
    url = "https://api.geoapify.com/v1/routematrix?apiKey={}".format(API_geoapify)
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    coordinates = []
    for k, v in locs.items():
        d = {"location": v}
        coordinates.append(d)
    ndatad = {"mode": "drive", "sources": coordinates, "targets": coordinates}
    ndata = str(ndatad).replace("'", '"')
    ndata = ndata.replace(' ', '')
    ndata = ndata.replace(', Ellipsis', '')
    resp = requests.post(url, headers=headers, data=ndata)
    return resp.text

# Turn data into dictionary
data = json.loads(get_data(coords_dict))
st = data.get('sources_to_targets')
st_dicts = {}

# Add location to nested dictionaries
for i in range(len(st)):
    lt = st[i]
    for n in range(len(lt)):
        d = lt[n]
        d['location'] = loc_list[n]
    st_dicts[loc_list[i]] = st[i]
print(st_dicts)

for k, v in st_dicts.items():
    n = 0
    for i in range(len(v)):
        el = v[i]
        l = el['location']
        if l == k:
            n = i
    v = v.remove(v[n])

# Create list of distances
dist_list = []    
for k, v in st_dicts.items():
    for el in v:
        dl = [k, el['location'], el['distance']]
        dist_list.append(dl)
        
print(dist_list)

# List permutations of locations and get the smallest total distance
perms = list(permutations(loc_list))
print(perms)
lowest_dist = 100000000000000
best_perm = 0
for perm in perms:
    n = 0
    total_dist = 0
    for i in range(len(perm)-1):
        done = [perm[i]]
        for ndl in dist_list:
            if perm[i] == ndl[0] and perm[i+1] == ndl[1]:
                total_dist += ndl[2]
    if total_dist < lowest_dist:
        lowest_dist = total_dist
        perm_no = n
    n += 1

# Print results
route = perms[best_perm]
print('\nBEST ROUTE:\n')
for i in range(len(route)):
    if i == 0:
        print('Start at: ', route[i])
    elif i == len(route) + 1:
        print('Finish at: ', route[i+1] + '\n')
    else:
        print('Location {}: {}'.format((i+1), route[i]))
print('Total distance: ', lowest_dist/1000, ' km')