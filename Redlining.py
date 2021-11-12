import requests
import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.path import Path
import random as random
import re
from collections import Counter, OrderedDict
from operator import itemgetter



# loading thisDict from local json file
# note the difference between json.load() and json.loads()

#with open('thisDict.json') as f:
#    thisDict = json.load(f)



# json parsing

response = requests.get('https://dsl.richmond.edu/panorama/redlining/static/downloads/geojson/MIDetroit1939.geojson')
json_str = response.text
json_dicts = json.loads(json_str)['features']

#thisDict ={
#    'Coordinates': [], lists of coordinates for each district
#    'Holc_Grade': [], grades for each district
#    'Holc_Color': [], appropriate color for each district
#    'name': [], the name of the district (numbered)
#    'Qualitative Description': [], a qualitative, text description called Section 8 in the json file for each district.
#}

#### some districts are non-contiguous – in this case we take only the first set of coordinates.

coordinates = []
name = []
holc_grade = []
holc_color = []
qualitative = []

for entry in json_dicts:
    coordinates.append(entry['geometry']['coordinates'][0][0])
    #name.append(entry['properties']['name'])
    holc_grade.append(entry['properties']['holc_grade'])
    qualitative.append(entry['properties']['area_description_data']['8'])
    
for i in range(238):
    name.append(str(i+1))
    
for grade in holc_grade:
    if grade == 'A':
        holc_color.append('darkgreen')
    elif grade == 'B':
        holc_color.append('cornflowerblue')
    elif grade == 'C':
        holc_color.append('gold')
    elif grade == 'D':
        holc_color.append('maroon')
        
thisDict = {}
thisDict['Coordinates'] = coordinates
thisDict['Holc_Grade'] = holc_grade
thisDict['Holc_Color'] = holc_color
thisDict['name'] = name
thisDict['Qualitative Description'] = qualitative



# mapping

districts = []

for i in range(238):
    districts.append(Polygon(np.array(thisDict['Coordinates'][i]), facecolor = thisDict['Holc_Color'][i], edgecolor = 'black'))

fig, ax = plt.subplots()

for u in districts:
    ax.add_patch(u)
    
ax.autoscale()
plt.rcParams["figure.figsize"] = (15,15)
plt.show()

            

# random coordinates

random.seed(33)

# np.arange(start, stop, step): returns an even-spaced array between the specified start and stop (you could also specify the step/spacing)
xgrid = np.arange(-83.5,-82.8,.004)
ygrid = np.arange(42.1, 42.6, .004)

# np.meshgrid(arrays*): returns coordinate matrices from coordinate vectors
xmesh, ymesh = np.meshgrid(xgrid,ygrid)

# np.vstack(arrays*): stacks the given arrays in sequence vertically (row-wise)
# np.ndarray.flatten(): returns a copy of an ndarray flattened into one dimension
# .T is the same as transpose
points = np.vstack((xmesh.flatten(),ymesh.flatten())).T

# Path objects: polylines
# Path.contains_points(points): checks if the Path object contains the given points (returns a boolean array)
# np.where(condition, x, y): returns x where condition = True, otherwise returns y
coors = []

for j in range(238):
    p = Path(thisDict['Coordinates'][j])
    grid = p.contains_points(points)
    coors.append(points[random.choice(np.where(grid)[0])])

census_tract = []

for coor in coors:
    lat = coor[1]
    long = coor[0]
    param_dict = {'lat': lat, 'lon': long, 'format': 'json'}
    response = requests.get('https://geo.fcc.gov/api/census/area', param_dict)
    json_str = response.text
    #census_tract.append(json.loads(json_str)['results'][0]['block_fips'][5:11])
    census_tract.append(json.loads(json_str)['results'][0]['block_fips'])
    
thisDict['Census_Tract'] = census_tract



# median income

median_income = []

#for tract in census_tract:
#census_param_dict = {'get': 'NAME,B19013_001E', 'for': 'county:163', 'in': 'state:26'}
#    response = requests.get(f'https://api.census.gov/data/2015/acs/acs5?get=NAME,B19013_001E&for=tract:{tract}&in=state:26&in=county:163')
#    json_str = response.text
#    median_income.append(json_str[1][1])

response = requests.get('https://api.census.gov/data/2015/acs/acs5?get=NAME,B19013_001E&for=tract:*&in=state:26&in=county:*')
json_str = response.text

for tract in thisDict['Census_Tract']:
    for entry in json.loads(json_str):
        if entry[3] == tract[2:5] and entry[4] == tract[5:11]:
            median_income.append(entry[1])

thisDict['median_income'] = median_income



# mean and median of the median income of each district grade

A_income = []
B_income = []
C_income = []
D_income = []

for i in range(238):
    if thisDict['Holc_Grade'][i] == 'A':
        A_income.append(int(thisDict['median_income'][i]))
    elif thisDict['Holc_Grade'][i] == 'B':
        B_income.append(int(thisDict['median_income'][i]))
    elif thisDict['Holc_Grade'][i] == 'C':
        C_income.append(int(thisDict['median_income'][i]))
    elif thisDict['Holc_Grade'][i] == 'D':
        D_income.append(int(thisDict['median_income'][i]))
        
#A_mean_income = np.mean(A_income)
#A_median_income = np.median(A_income)
#B_mean_income = np.mean(B_income)
#B_median_income = np.median(B_income)
#C_mean_income = np.mean(C_income)
#C_median_income = np.median(C_income)
#D_mean_income = np.mean(D_income)
#D_median_income = np.median(D_income)

# dropping negative values
A_mean_income = np.mean(np.array(A_income)[np.array(A_income) > 0])
A_median_income = np.median(np.array(A_income)[np.array(A_income) > 0])
B_mean_income = np.mean(np.array(B_income)[np.array(B_income) > 0])
B_median_income = np.median(np.array(B_income)[np.array(B_income) > 0])
C_mean_income = np.mean(np.array(C_income)[np.array(C_income) > 0])
C_median_income = np.median(np.array(C_income)[np.array(C_income) > 0])
D_mean_income = np.mean(np.array(D_income)[np.array(D_income) > 0])
D_median_income = np.median(np.array(D_income)[np.array(D_income) > 0])



# top 10 common words in the qualitative descriptions of each district grade

A_words = []
B_words = []
C_words = []
D_words = []

#for i in range(238):
#    if thisDict['Holc_Grade'][i] == 'A':
#        A_words[0] += thisDict['Qualitative Description'][i] + ' '
#    elif thisDict['Holc_Grade'][i] == 'B':
#        B_words[0] += thisDict['Qualitative Description'][i] + ' '
#    elif thisDict['Holc_Grade'][i] == 'C':
#        C_words[0] += thisDict['Qualitative Description'][i] + ' '
#    elif thisDict['Holc_Grade'][i] == 'D':
#        D_words[0] += thisDict['Qualitative Description'][i] + ' '

A_words = [thisDict['Qualitative Description'][i] for i in range(238) if thisDict['Holc_Grade'][i] == 'A']
B_words = [thisDict['Qualitative Description'][i] for i in range(238) if thisDict['Holc_Grade'][i] == 'B']
C_words = [thisDict['Qualitative Description'][i] for i in range(238) if thisDict['Holc_Grade'][i] == 'C']
D_words = [thisDict['Qualitative Description'][i] for i in range(238) if thisDict['Holc_Grade'][i] == 'D']

A_string = ''
B_string = ''
C_string = ''
D_string = ''

for i in A_words:
    A_string += i + ' '
for i in B_words:
    B_string += i + ' '
for i in C_words:
    C_string += i + ' '
for i in D_words:
    D_string += i + ' '


def split_text(text):
    text = text.lower()
    string_no_punctuation = re.sub("[^\w\s]", "", text)
    wordlist = string_no_punctuation.split()
    
    return wordlist


A_wordlist = split_text(A_string)
B_wordlist = split_text(B_string)
C_wordlist = split_text(C_string)
D_wordlist = split_text(D_string)

A_counts = Counter(A_wordlist).most_common()
B_counts = Counter(B_wordlist).most_common()
C_counts = Counter(C_wordlist).most_common()
D_counts = Counter(D_wordlist).most_common()

A_unique = [i for i in A_counts if (i[0] not in B_wordlist) and (i[0] not in C_wordlist) and (i[0] not in D_wordlist)]
B_unique = [i for i in B_counts if (i[0] not in A_wordlist) and (i[0] not in C_wordlist) and (i[0] not in D_wordlist)]
C_unique = [i for i in C_counts if (i[0] not in A_wordlist) and (i[0] not in B_wordlist) and (i[0] not in D_wordlist)]
D_unique = [i for i in D_counts if (i[0] not in A_wordlist) and (i[0] not in B_wordlist) and (i[0] not in C_wordlist)]

A_10_Most_Common = A_unique[:10]
B_10_Most_Common = B_unique[:10]
C_10_Most_Common = C_unique[:10]
D_10_Most_Common = D_unique[:10]



# color gradient map based on median income

color_gradients = []
fraction = 0
for i in range(238):
    color_gradients.append(1/238 * (i+1))
    
income_dict = {}
for i in range(238):
    income_dict[i] = thisDict['median_income'][i]
    
ordered = OrderedDict(sorted(income_dict.items(), key = itemgetter(1)))

gradient_dict = {}

index = 0
for i in ordered.keys():
    gradient_dict[i] = color_gradients[index]
    index += 1
    
gradient_districts = []

for i in range(238):
    gradient_districts.append(Polygon(np.array(thisDict['Coordinates'][i]), facecolor = 'grey', edgecolor = thisDict['Holc_Color'][i], alpha = gradient_dict[i]))

fig, ax = plt.subplots()

for u in gradient_districts:
    ax.add_patch(u)
    
ax.autoscale()
plt.rcParams["figure.figsize"] = (15,15)
plt.show()



# downloading thisDict into a local json file

thisDict_json = json.dumps(thisDict)
with open('thisDict.json', 'w') as f:
    f.write(thisDict_json)
