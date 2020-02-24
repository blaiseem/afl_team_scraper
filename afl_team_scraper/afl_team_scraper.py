"""
Code to scrape AFL team selections for a given season and round.
"""
import requests


class AFLTeamSelectionScraper:
    """
    Class to scrape AFL team selections for a given season and round
    """
    def __init__(self,season='2020'):
        self.season = season
        self.competition_id = 1 #hard coded. Will need to change for other competitions

        self.session = requests.session()
        self.TOKEN_URL = 'https://api.afl.com.au/cfs/afl/WMCTok'
        self.response_token = self.session.post(self.TOKEN_URL)
        self.token = self.response_token.json()['token']
        self.headers = {'x-media-mis-token': self.token}

        #cache that stores responses by url
        self.response_cache = {} 

        self.comp_season_id = self.get_comp_season_id()

        #url to get match ids for a round.
        self.url_fixture_round = 'https://aflapi.afl.com.au/afl/v2/matches?competitionId={}&compSeasonId={}&pageSize=300&roundNumber={}'.format(self.competition_id,self.comp_season_id,'{}')

        self.url_team_selections = 'https://api.afl.com.au/cfs/afl/matchPlayers/{}'

    def call_api(self, url, headers):

        if url in self.response_cache.keys():
            response = self.response_cache[url]
        else:
            response = self.session.get(url, headers=headers).json()
            self.response_cache[url] = response

        return response

    def get_comp_season_id(self):
        url = 'https://aflapi.afl.com.au/afl/v2/competitions/{}/compseasons'.format(self.competition_id)
        response = self.call_api(url,self.headers)
        comp_seasons = response['compSeasons']
        comp_season = [cs for cs in comp_seasons if self.season in cs['providerId']]

        if len(comp_season) == 1:
            comp_season_id = comp_season[0].get('id')
        elif len(comp_season) == 0:
            print('No comp season id for season {}'.format(self.season))
            comp_season_id = None
        else:
            print('More than one comp season id for season'.format(self.season))
            comp_season_id = None

        return comp_season_id


    def get_match_details_for_round(self, round_number):
        url = self.url_fixture_round.format(round_number)
        try:
            response = self.call_api(url,self.headers)
            matches = response['matches']
            match_ids = [m['providerId'] for m in matches]

            home_teams = [(m['home']['team']['providerId'], m['home']['team']['name']) for m in matches]
            away_teams = [(m['away']['team']['providerId'], m['away']['team']['name']) for m in matches]
            teams = home_teams + away_teams
            team_id_mapping = dict(teams)

        except Exception as e:
            print(e)
            print('Scraping match ids failed for round {}'.format(round_number))
            match_ids = []
            team_id_mapping = {}

        return match_ids, team_id_mapping

    def get_team_selections_for_matchids(self, matchids, team_id_mapping):
        round_selected_players = {}

        for match_id in matchids:
            url = self.url_team_selections.format(match_id)
            response = self.session.get(url, headers=self.headers).json()

            match_selected_players = {}

            for team in ['home', 'away']:
                team_id = response['{}TeamPlayers'.format(team)]['teamId']
                players = response['{}TeamPlayers'.format(team)]['players']
                selected_players = []

                for player in players:
                    position = player['player']['position']
                    if position != 'EMERG':
                        selected_players.append({
                            'player_id': player['player']['player']['playerId'],
                            'player_name': player['player']['player']['playerName']['givenName'] + ' ' + player['player']['player']['playerName']['surname'],
                            'position': player['player']['position'],
                            'jumper_number': player['jumperNumber']
                        })

                match_selected_players[team] = {
                    'team_id': team_id,
                    'team_name': team_id_mapping.get(team_id),
                    'selected_players': selected_players
                }


            round_selected_players[match_id] = match_selected_players

        return round_selected_players

    def run_scraper_for_round(self, round_number):
        match_ids, team_id_mapping = self.get_match_details_for_round(round_number)
        round_selected_players = self.get_team_selections_for_matchids(match_ids, team_id_mapping)

        return round_selected_players
