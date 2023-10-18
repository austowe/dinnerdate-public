from django.shortcuts import render, redirect
import json
import os
import datetime
import random
import requests
import string
from django.http import JsonResponse
from . import functions
import time
import keys

#input api keys, current version runs on yelp API
yelp_key = keys.yelp_key
google_key = keys.google_key

#input base url, i.e. http://10.0.0.52:8000
#composed of protocol, ip/url, port if not on 80/443, do not end with /
base_url = keys.base_url

def indexView(request):
    if request.method == 'GET':
        return render(request, "dinnerpicker/index.html")
    else:
        zip = request.POST.get("zip")
        opennow = request.POST.get("opennow")
        type = request.POST.get("type")
        distanceMiles = request.POST.get("distance")
        distance = int(round(float(distanceMiles) * 1609.34,0))


        if opennow != 'true':
            opennow = 'false'

        potitionstack_key = keys.potitionstack_key
        google_key = keys.google_key
        yelp_key = keys.yelp_key
        geoapify_key = keys.geoapify_key

        
        response = requests.get('https://api.geoapify.com/v1/geocode/search?text=' + str(zip) + '&lang=en&limit=1&type=postcode&format=json&apiKey=' + geoapify_key).json()
        places_response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword=' + type + '&location=' + str(response['results'][0]['lat']) + '%2C' + str(response['results'][0]['lon']) + '&opennow=' + opennow +'&rankby=distance&key=' + google_key).json()

        possible = []
        session_data = []
        for i in range(0,len(places_response['results'])):
            possible.append({'id':places_response['results'][i]['place_id'], 'title':places_response['results'][i]['name']})
            session_data.append(places_response['results'][i])
            #print(places_response['results'][i]['name'] + " : " + places_response['results'][i]['place_id'])
        try:
            time.sleep(2)
            places_response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=' + google_key + '&pagetoken=' + places_response['next_page_token']).json()
            for i in range(0,len(places_response['results'])):
                possible.append({'id':places_response['results'][i]['place_id'], 'title':places_response['results'][i]['name']})
                session_data.append(places_response['results'][i])
        except:
            print('one page only')

        #randomize output order to minimize future repeats
        random.shuffle(possible)

        #Set random session ID
        characters = string.ascii_letters + string.digits
        session_id = ''.join(random.choice(characters) for _ in range(6)).upper()

        cwd = os.getcwd()
        f = open(os.path.join(cwd, "progress.json"))
        progress = json.load(f)

        progress['session'].append({
            'id':session_id,
            "responses": [],
            "possible": possible
        })

        json_object = json.dumps(progress, indent=4)
        with open("progress.json", "w") as outfile:
            outfile.write(json_object)

        random.shuffle(session_data)

        json_object = json.dumps(session_data, indent=4)
        with open("session_data/" + session_id + ".json", "w") as outfile:
            outfile.write(json_object)
        print(places_response)

        url = base_url + '/picker/?session=' + session_id + '&item=0'
        join_url = base_url + '/join/?session=' + session_id

        context = {
            'url':url,
            'join_url':join_url,
            'session':session_id
        }

        return render(request, 'dinnerpicker/confirmation.html', context)


def pickerView(request):
    session = request.GET.get('session')
    try:
        person = int(request.GET.get('person'))
    except:
        person = None
    item = int(request.GET.get('item'))
    response = request.GET.get('response')
    id = request.GET.get('id')

    cwd = os.getcwd()
    f = open(os.path.join(cwd, "progress.json"))
    progress = json.load(f)
    cwd = os.getcwd()
    f = open(os.path.join(cwd, "session_data/" + session + ".json"))
    session_data = json.load(f)

    #need something better here, will be easy with db
    for i in range(len(progress['session'])):
        if progress['session'][i]['id'] == session:
            session_index = i

    #new responder
    if person is None:
        progress['session'][session_index]['responses'].append({
                "yay": []
            })
        person = len(progress['session'][i]['responses']) - 1
        item = 0
    person_responses = progress['session'][session_index]['responses'][person]
    
    if id is not None:
        for i in range(len(progress['session'][session_index]['possible'])):
            if progress['session'][session_index]['possible'][i]['id'] == id:
                id_index = i
        previous_title = progress['session'][session_index]['possible'][id_index]['title']

    if response == 'y':
        progress['session'][session_index]['responses'][person]['yay'].append({'id':id,'title':previous_title})
    

    if item == len(progress['session'][session_index]['possible']):
        #no more restaurants
        yay_lists = []
        for i in progress['session'][session_index]['responses']:
            yay_lists.append(i['yay'])

        matches = functions.find_common_elements(yay_lists)
        if len(matches) > 0:
            return redirect(base_url + '/location/?location=' + matches[0]['id'] + '&end=1&session=' + session)
        if len(matches) == 0:
            top_matches = functions.find_top_elements(yay_lists, 5)
            for i in top_matches:
                matches.append({'id':i[0]['id'],'title':i[0]['title'] + ' (' + str(int(round(i[1],0))) + '% Match)'})
            return redirect(base_url + '/location/?location=' + matches[0]['id'] + '&end=1&session=' + session)

    current_id = progress['session'][session_index]['possible'][item]['id']

    categories = ''
    current_item_data = session_data[item]
    print(current_item_data)
    for i in current_item_data['types']:
        categories += i + '; '
    address = ''
    address = current_item_data['vicinity']
    try:
        price = current_item_data['price_level']
    except:
        price = ''
    rating = current_item_data['rating']
    title = current_item_data['name']
    id = current_item_data['place_id']
    item += 1


    yay_lists = []
    for i in progress['session'][session_index]['responses']:
        yay_lists.append(i['yay'])

    matches = functions.find_common_elements(yay_lists)

    if len(matches) == 0 and item > 2:
        top_matches = functions.find_top_elements(yay_lists, 5)
        for i in top_matches:
            matches.append({'id':i[0]['id'],'title':i[0]['title'] + ' (' + str(int(round(i[1],0))) + '% Match)'})

    context = {
        'name':title,
        'categories':categories,
        'address':address,
        'phone':'test phone',
        'price':price,
        'rating':rating,
        'session_id':session,
        'id':id,
        'item':item,
        'person':person,
        'photo':'null',
        'matches':matches,
        'style': 'display:block;'
    }

    json_object = json.dumps(progress, indent=4)
    with open("progress.json", "w") as outfile:
        outfile.write(json_object)

    return render(request, 'dinnerpicker/picker.html', context)

def emptyList(request):
    empty = {
        "session": []
    }
    json_object = json.dumps(empty, indent=4)
    with open("progress.json", "w") as outfile:
        outfile.write(json_object)
    return JsonResponse({'response':'ok'})

def locationView(request):
    id = request.GET.get('location')

    try:
        if int(request.GET.get('end')) == 1:
            modal = True
            modalText = "You've completed all your restaurants! Take some time to browse your matches, or just pick the first one. Bon Appétit!"
        else:
            modal = False
            modalText = ''
    except:
        modal = False
        modalText = ''

    cwd = os.getcwd()
    f = open(os.path.join(cwd, "progress.json"))
    progress = json.load(f)

    if id is None:
        session = request.GET.get('session')
        
        for i in range(len(progress['session'])):
            if progress['session'][i]['id'] == session:
                session_index = i
        yay_lists = []
        for i in progress['session'][session_index]['responses']:
            yay_lists.append(i['yay'])

        matches = functions.find_common_elements(yay_lists)
        if len(matches) > 0:
            id = matches[0]['id']
        else:
            id = 'err'


    if id != 'err':

        yelp_key = keys.yelp_key
        headers = {"accept": "application/json", "Authorization": "Bearer " + yelp_key}

        yelp_response = requests.get('https://api.yelp.com/v3/businesses/' + id, headers=headers).json()
        categories = ''
        for i in yelp_response['categories']:
            categories += i['title'] + '; '
        address = ''
        for i in yelp_response['location']['display_address']:
            address += i + '\n'
        address = address.strip()
        photo = yelp_response['image_url']
        phone = yelp_response['display_phone']
        try:
            price = yelp_response['price']
        except:
            price = 'No data'
        rating = yelp_response['rating']
        title = yelp_response['name']
        id = yelp_response['id']

        session = request.GET.get('session')
        
        for i in range(len(progress['session'])):
            if progress['session'][i]['id'] == session:
                session_index = i

        yay_lists = []
        for i in progress['session'][session_index]['responses']:
            yay_lists.append(i['yay'])

        matches = functions.find_common_elements(yay_lists)
        if len(matches) == 0:
            top_matches = functions.find_top_elements(yay_lists, 5)
            for i in top_matches:
                matches.append({'id':i[0]['id'],'title':i[0]['title'] + ' (' + str(int(round(i[1],0))) + '% Match)'})

        context = {
            'name':title,
            'categories':categories,
            'address':address,
            'phone':phone,
            'price':price,
            'rating':rating,
            'id':id,
            'session_id':session,
            'photo':photo,
            'matches':matches,
            'style': 'display:block;',
            'modal': modal,
            'modalText': modalText,
            'modalMatches': True
        }

        return render(request, 'dinnerpicker/location.html', context)
    
    else:
        session = request.GET.get('session')
        for i in range(len(progress['session'])):
            if progress['session'][i]['id'] == session:
                session_index = i

        yay_lists = []
        for i in progress['session'][session_index]['responses']:
            yay_lists.append(i['yay'])

        matches = functions.find_common_elements(yay_lists)
        modalText = "Hmm, it looks like you've completed all of your restaurants and there are no current matches. Wait for your group to finish to see if you get any matches, or restart your session with different parameters to get a new list of restaurants."
        context = {
            'name':'-',
            'categories':'',
            'address':'',
            'phone':'',
            'price':'',
            'rating':'',
            'id':'',
            'session_id':session,
            'photo':'',
            'matches':matches,
            'style': 'display:block;',
            'modal': True,
            'modalText': modalText,
            'modalMatches': False
        }
        return render(request, 'dinnerpicker/location.html', context)
    

def joinView(req):
    session_id = req.GET.get('session')
    url = base_url + '/picker/?session=' + session_id + '&item=0'
    join_url = base_url + '/join/?session=' + session_id
    context = {
        'session':session_id,
        'url':url,
        'join_url': join_url
    }
    return render(req, 'dinnerpicker/join.html', context)