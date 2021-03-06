import datetime
import json
import os
import requests

PREFIX_URL = 'https://euw1.api.riotgames.com/'
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
args = {}


def request_api(endpoint, query_params={}):
    query_params.update({
        'api_key': args.get('api_key')
    })
    url = PREFIX_URL+endpoint
    return requests.get(url, params=query_params)


def get_all_champions():
    champions = {}
    champion_data_path = os.path.join(BASE_PATH, 'data/champions.json')
    if os.path.exists(champion_data_path):
        with open(champion_data_path, 'r+') as f:
            champions = json.loads(f.read())
    else:
        endpoint = 'lol/static-data/v3/champions'
        query_params = {
            'locale': 'en_US'
        }
        response = request_api(endpoint, query_params)
        champions = response.json()['data']
        with open(champion_data_path, 'w+') as f:
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
    # We can miss some games if last begin time is different from index time
    if index_time != begin_time:
        last_schedule = (
            index_time.strftime('%s')+'000', end_time.strftime('%s')+'000')
        scheduler.append(last_schedule)
    return scheduler


def run(api_key, summoner_name):
    print('Starting league of legends script')
    # If script is imported by module, override arguments
    args.update({
        'api_key': api_key
    })
    start_time = datetime.datetime.now()
    champions = get_all_champions()
    summoner_infos = get_summoner_infos(summoner_name)
    champions_masteries = get_champions_masteries(
        champions, summoner_infos['id'])
    print('Champions masteries: ', champions_masteries)
    matches = get_match_with_champions_masteries(
        champions_masteries, summoner_infos['accountId'])
    end_time = datetime.datetime.now() - start_time
    print('Matches: ', matches)
    print('Finished script in %s seconds' % str(end_time.total_seconds()))
    response_dict = {
        'summoner': summoner_name,
        'matches': matches,
        'champions': champions_masteries,
        'date': datetime.datetime.fromtimestamp(
            float(matches[-1]['timestamp'])/1000).strftime('%d/%m/%Y %H:%M:%S')
    }
    return response_dict


if __name__ == "__main__":
    run()
