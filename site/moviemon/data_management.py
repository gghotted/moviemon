from django.conf import settings
import random
import requests
import pickle

class Data:
    def __init__(self):
        self.load_default_settings()
        self.movie_ball_count = 0
        self.movie_get = set()
        self.strength = 0

    def load(self, data):
        self.pos = data.pos
        self.movie_ball_count = data.movie_ball_count
        self.movie_get = data.movie_get
        self.moviemons = data.moviemons
        return self

    def dump(self):
        return self

    def get_random_movie(self):
        rem_moviemons = self.moviemons - self.movie_get
        return random.sample(rem_moviemons, 1)[0]

    def request_movie_detail(self):
        details = {}
        for name in self.moviemons:
            url = 'http://www.omdbapi.com'
            params = {
                'apikey': '379dc929',
                't': name
            }
            res = requests.get(url, params=params)
            if res.status_code != 200:
                raise Exception('OMDB server not ready!')
            details[name] = res.json()
        return details

    def load_default_settings(self):
        self.map_size = list(settings.MAP_SIZE)
        self.moviemons = settings.MOVIES
        self.pos = settings.PLAYER_POS
        self.movies_detail = self.request_movie_detail()
        return self

    def get_strength(self):
        self.strength = 10 + (len(self.movie_get) * 2)
        return self.strength

    def get_movie(self, movie_name):
        return self.movies_detail[movie_name]

    @staticmethod
    def get_user_game_data(request, newgame: bool):
        if newgame == True and request.session.get('gamedata'):
            del request.session['gamedata']
        try:
            hexdata = request.session['gamedata']
        except:
            hexdata = pickle.dumps(Data()).hex()
        return pickle.loads(bytes.fromhex(hexdata))

'''
data = Data()
data.load(pickle.load(filepath))
pickle.dump(data.dump())
'''

# if __name__ == '__main__':
#     data = Data()
#     for detail in data.movies_detail:
#         print(detail['Title'])
