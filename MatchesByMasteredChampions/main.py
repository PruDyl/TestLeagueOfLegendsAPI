import argparse
import datetime
import json
import os
import requests

parser = argparse.ArgumentParser(description='Program descriptiom.')
parser.add_argument('--key', help="Riot api key")
parser.add_argument('--champion', help="Champion's name")
parser.add_argument('--summoner', help="Summoner's name")

args = parser.parse_args()

APIKEY = args.key
PREFIX_URL = 'https://euw1.api.riotgames.com/'


def request_api(endpoint, query_params={}):
    query_params.update({
        'api_key': APIKEY
    })
    url = PREFIX_URL+endpoint
    return requests.get(url, params=query_params)


def get_all_champions():
    champions = {}
    if os.path.exists('./data/champions.json'):
        with open('./data/champions.json', 'r+') as f:
            champions = json.loads(f.read())
    else:
        endpoint = 'lol/static-data/v3/champions'
        query_params = {
            'locale': 'en_US'
        }
        response = request_api(endpoint, query_params)
        champions = response.json()['data']
        with open('./data/champions.json', 'w+') as f:
            f.write(json.dumps(champions))
    return champions


def find_champion(champions, name=None, champ_id=None):
    if (name is None and champ_id is None) or (
            name is not None and champ_id is not None):
        raise Exception('Should use only one argument')
    parse_key = 'name' if name else 'id'
    condition_value = name if name else champ_id
    return [champions[key] for key in champions.keys()
            if champions[key][parse_key] == condition_value][0]


def get_summoner_infos(summoner_name):
    endpoint = 'lol/summoner/v3/summoners/by-name/%s' % summoner_name
    response = request_api(endpoint)
    return response.json()


def get_champions_masteries(champions, summoner_id, index=3):
    endpoint = 'lol/champion-mastery/v3/champion-masteries/by-summoner/%s' % (
        summoner_id)
    response = request_api(endpoint)
    champions_masteries = response.json()[:index]
    for champ in champions_masteries:
        champ.update({
            'name': find_champion(
                champions, champ_id=champ['championId'])['name']
        })
    return champions_masteries


def get_match_with_champions_masteries(champions_masteries, account_id):
    endpoint = 'lol/match/v3/matchlists/by-account/%s' % (
        account_id)
    index_time = datetime.datetime.today() - datetime.timedelta(days=60)
    scheduler = get_scheduler(index_time)
    matches = []
    for s in scheduler:
        begin_time, end_time = s
        query_params = {
            'beginTime': begin_time,
            'endTime': end_time,
            'champion': [champ['championId'] for champ in champions_masteries]
        }
        response = request_api(endpoint, query_params)
        matches.extend(response.json().get('matches', []))
    return matches


def get_scheduler(index_time):
    scheduler = []
    end_time = datetime.datetime.today()
    begin_time = end_time - datetime.timedelta(days=7)
    while begin_time > index_time:
        t = (begin_time.strftime('%s')+'000', end_time.strftime('%s')+'000')
        scheduler.append(t)
        end_time = begin_time
        begin_time = end_time - datetime.timedelta(days=7)
    return scheduler


def run():
    print('Starting league of legends script')
    start_time = datetime.datetime.now()
    champions = get_all_champions()
    summoner_name = args.summoner
    summoner_infos = get_summoner_infos(summoner_name)
    champions_masteries = get_champions_masteries(
        champions, summoner_infos['id'])
    print('Champions masteries: ', champions_masteries)
    matches = get_match_with_champions_masteries(
        champions_masteries, summoner_infos['accountId'])
    end_time = datetime.datetime.now() - start_time
    print('Finished script in %s seconds' % str(end_time.total_seconds()))
    print('Matches: ', matches)


if __name__ == "__main__":
    run()
