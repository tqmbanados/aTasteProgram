import requests

from param import url


def put_score(score_string, score_type, duration=6):
    if score_type == "score":
        extension = ""
        data = {'score_data': score_string}
    else:
        extension = "instrument"
        data = {'score_data': score_string,
                'instrument': score_type,
                'duration': duration}
    try:
        response = requests.put(url + extension, data=data)
    except requests.exceptions as exception:
        print(exception)
        return
    return response


def get_score(score_type):
    if score_type == "score":
        extension = ""
        data = {}
    else:
        extension = "instrument"
        data = {'instrument': score_type}
    try:
        response = requests.get(url + extension, data=data)
    except requests.exceptions as exception:
        print(exception)
        return

    return response


def put_actor(actor_string, stage):
    data = {'action': actor_string,
            'stage': stage}
    extension = 'url'
    try:
        response = requests.put(url + extension, data=data)
    except requests.exceptions as exception:
        print(exception)
        return
    return response


def get_actor():
    extension = 'actor'
    try:
        response = requests.get(url + extension)
    except requests.exceptions as exception:
        print(exception)
        return
    return response
