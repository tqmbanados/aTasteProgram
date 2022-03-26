import requests

from private_parameters import url


def put_score(score_string, score_type):
    if score_type == "score":
        extension = ""
        data = {'score_data': score_string}
    else:
        extension = "instrument"
        data = {'score_data': score_string,
                'instrumet': score_type}
    try:
        response = requests.put(url + extension, data=data)
    except requests.exceptions as exception:
        print(exception)
        return
    print(response.status_code)


def get_score(score_type):
    if score_type == "score":
        extension = ""
        data = {}
    else:
        extension = "instrument"
        data = {'instrumet': score_type}
    try:
        response = requests.get(url + extension, data=data)
    except requests.exceptions as exception:
        print(exception)
        return

    print(response.status_code)
    json = response.json()
    return json["score_data"]