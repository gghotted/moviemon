from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from .data_management import Data
from django.conf import settings
import random
import pickle
import os

class TitleScreen(TemplateView):
    template_name = 'moviemon/title_screen.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_enable'] = {
            'left': False,
            'right': False,
            'up': False,
            'down': False,
            'select': False,
            'a': True,
            'b': True
        }
        return context

class WorldMap(TemplateView):
    template_name = 'moviemon/world_map.html'
    movieball_appeared = False
    moviemon_appeared = False
    newgame = False

    def get(self, request, *args, **kwargs):
        if request.GET.get('newgame'):
            self.newgame = True
        else:
            self.newgame = False

        gamedata = self.get_user_game_data(request, self.newgame)
        '''
        0 1 2 3 4
        1
        2
        3
        '''
        if request.GET.get('cmd') == 'up' and gamedata.pos['y'] > 0:
            gamedata.pos['y'] -= 1
        elif request.GET.get('cmd') =='down' and gamedata.pos['y'] < gamedata.map_size['y'] - 1:
            gamedata.pos['y'] += 1
        elif request.GET.get('cmd') == 'left' and gamedata.pos['x'] > 0:
            gamedata.pos['x'] -= 1
        elif request.GET.get('cmd') == 'right' and gamedata.pos['x'] < gamedata.map_size['x'] - 1:
            gamedata.pos['x'] += 1
#        print('cmd: ', request.GET.get('cmd'))
#        print('x: ', gamedata.pos['x'])
        if len(gamedata.moviemons) == len(gamedata.movie_get):
            return redirect('win')

        if request.GET.get('cmd'):
            eventlist = ['ball', 'non', 'non']
            if len(gamedata.moviemons) != len(gamedata.movie_get):
                eventlist.append('moviemon')

            event = random.choice(eventlist)
            if event == 'non':
                self.movieball_appeared = False
                self.moviemon_appeared = False
            elif event == 'ball':
                self.movieball_appeared = True
                gamedata.movie_ball_count += 1
            elif event == 'moviemon':
                self.moviemon_appeared = True

        # self.gamedata.save(request.session['filepath'])
        request.session['gamedata'] = pickle.dumps(gamedata).hex()
        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gamedata = self.get_user_game_data(self.request, newgame=False)
        context['btn_enable'] = {
            'left': True,
            'right': True,
            'up': True,
            'down': True,
            'select': True,
            'start': True,
            'a': False,
            'b': False
        }
        context['map_size'] = {
            'y': range(0, gamedata.map_size['y']),
            'x': range(0, gamedata.map_size['x'])
        }
        context['player_pos'] = gamedata.pos
        context['movieball_cnt'] = gamedata.movie_ball_count
        context['movieball_appeared'] = self.movieball_appeared
        context['moviemon_appeared'] = self.moviemon_appeared

        if gamedata.pos['y'] == 0:
            context['btn_enable']['up'] = False
        if gamedata.pos['y'] == gamedata.map_size['y'] - 1:
            context['btn_enable']['down'] = False
        if gamedata.pos['x'] == 0:
            context['btn_enable']['left'] = False
        if gamedata.pos['x'] == gamedata.map_size['x'] - 1:
            context['btn_enable']['right'] = False

        context['moviemon_id'] = "None"
        if self.moviemon_appeared == True:
            context['btn_enable']['a'] = True
            movie = gamedata.get_random_movie()
            context['moviemon_id'] = gamedata.movies_detail[movie]['imdbID']
        return context

    def get_user_game_data(self, request, newgame: bool):
        if newgame == True and request.session.get('gamedata'):
            del request.session['gamedata']
        try:
            hexdata = request.session['gamedata']
        except:
            hexdata = pickle.dumps(Data()).hex()
        return pickle.loads(bytes.fromhex(hexdata))


class Battle(TemplateView):
    template_name = 'moviemon/battle.html'
    moviemon_id = ''
    moviemon_title = ''
    moviemon_strength = float()
    missed = False
    catched = False

    def get(self, request, *args, **kwargs):
        self.moviemon_id = kwargs['moviemon_id']
        gamedata = Data.get_user_game_data(self.request, newgame=False)

        for title in gamedata.movies_detail:
            if gamedata.movies_detail[title]['imdbID'] == self.moviemon_id:
                self.moviemon_title = title
        self.moviemon_strength = float(gamedata.movies_detail[title]['imdbRating'])

        if request.GET.get('cmd') == 'a' and gamedata.movie_ball_count > 0:
            gamedata.movie_ball_count -= 1
            win_ratio = self.calculate_ratio(gamedata, self.moviemon_id) * 0.01
            mis_ratio = 1 - win_ratio
            if random.choices(
                [True, False],
                weights=[win_ratio, mis_ratio], k=1)[0]:
                self.catched = True
                gamedata.movie_get.add(self.moviemon_title)
            else:
                self.missed = True

        request.session['gamedata'] = pickle.dumps(gamedata).hex()
        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        gamedata = Data.get_user_game_data(self.request, newgame=False)
        context = super().get_context_data(**kwargs)
        context['btn_enable'] = {
            'left': False,
            'right': False,
            'up': False,
            'down': False,
            'select': False,
            'start': False,
            'a': True,
            'b': True
        }
        context['movieball_cnt'] = gamedata.movie_ball_count
        context['player_strength'] = gamedata.get_strength()
        context['moviemon_strength'] = self.moviemon_strength
        context['catched'] = self.catched
        context['missed'] = self.missed
        context['win_ratio'] = self.calculate_ratio(gamedata, self.moviemon_id)
        context['moviemon_poster'] = gamedata.movies_detail[self.moviemon_title]['Poster']

        if self.catched or gamedata.movie_ball_count == 0:
            context['btn_enable']['a'] = False

        return context

    def calculate_ratio(self, data, moviemon_id):
        ratio = 50 - (self.moviemon_strength * 10) + (data.get_strength() * 5)
        if ratio in range(1, 91):
            return ratio
        elif ratio < 1:
            return 1
        else:
            return 90


class Moviedex(TemplateView):
    template_name = 'moviemon/moviedex.html'
    moviemons = []
    selected_idx = 0
    selected_id = 'None'
    moviemons_cnt = 0

    def get(self, request, *args, **kwargs):
        gamedata = Data.get_user_game_data(self.request, newgame=False)
        self.selected_idx = int(request.GET.get('selected_idx', 0))
        self.moviemons = []
        for title in gamedata.movies_detail:
            if title in gamedata.movie_get:
                moviemon = gamedata.movies_detail[title]
                self.moviemons.append(moviemon)
        self.moviemons_cnt = len(self.moviemons)

        if request.GET.get('cmd') == 'left' and self.selected_idx > 0:
            self.selected_idx -= 1
        if request.GET.get('cmd') == 'right' and self.selected_idx < self.moviemons_cnt - 1:
            self.selected_idx += 1
        if self.moviemons_cnt > 0:
            self.selected_id = self.moviemons[self.selected_idx]['imdbID']

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['btn_enable'] = {
            'left': True,
            'right': self.moviemons_cnt != 0,
            'up': False,
            'down': False,
            'select': True,
            'start': False,
            'a': self.selected_id != 'None',
            'b': False
        }
        context['selected_id'] = self.selected_id
        context['moviemons'] = self.moviemons
        context['selected_idx'] = self.selected_idx
        if self.selected_idx == 0:
            context['btn_enable']['left'] = False
        if self.selected_idx == self.moviemons_cnt - 1:
            context['btn_enable']['right'] = False
        return context


class MoviedexDetail(TemplateView):
    template_name = 'moviemon/moviedex_detail.html'
    moviemon_id = ''

    def get(self, request, *args, **kwargs):
        self.moviemon_id = kwargs['moviemon_id']
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gamedata = Data.get_user_game_data(self.request, newgame=False)
        context.update({
            'btn_enable': {
                'b': True
            }
        })
        for movie in gamedata.movies_detail:
            if gamedata.movies_detail[movie]['imdbID'] == self.moviemon_id:
                context['moviemon'] = gamedata.movies_detail[movie]
        return context


class Options(TemplateView):
    template_name = 'moviemon/options.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'btn_enable': {
                'start': True,
                'a': True,
                'b': True
            }
        })
        return context


class Save(TemplateView):
    template_name = 'moviemon/save.html'
    slot_idx = 'a'

    def get(self, request, *args, **kwargs):
        gamedata = Data.get_user_game_data(self.request, newgame=False)
        self.slot_idx = request.GET.get('slot_idx', 'a')
        cmd = request.GET.get('cmd')

        if cmd == 'up' and self.slot_idx != 'a':
            self.slot_idx = chr(ord(self.slot_idx) - 1)
        elif cmd == 'down' and self.slot_idx != 'c':
            self.slot_idx = chr(ord(self.slot_idx) + 1)
        elif cmd == 'a':
            self.save_gamedata(gamedata)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'btn_enable': {
                'up': True,
                'down': True,
                'a': True,
                'b': True
            }
        })
        context['slots_state'] = {
            'a': self.parse_slot_score('a'),
            'b': self.parse_slot_score('b'),
            'c': self.parse_slot_score('c')
        }
        context['slot_idx'] = self.slot_idx
        if self.slot_idx == 'a': context['btn_enable']['up'] = False
        if self.slot_idx == 'c': context['btn_enable']['down'] = False
        return context

    def parse_slot_score(self, slot_idx):
        filename = self.get_filename(slot_idx)
        if not filename:
            return 'free'
        else:
            return filename[6:-4].replace('_', '/')

    def save_gamedata(self, data):
        filename = self.get_filename(self.slot_idx)
        if filename:
            os.remove(f'{settings.BASE_DIR}/moviemon/saved_game/{filename}')

        score = f'{len(data.movie_get)}_{len(data.moviemons)}'

        path = f'{settings.BASE_DIR}/moviemon/saved_game/slot{self.slot_idx}_{score}.mmg'
        with open(path, 'wb') as file:
            pickle.dump(data, file)

    def get_filename(self, slot_idx):
        root = f'{settings.BASE_DIR}/moviemon/saved_game'
        for file in os.listdir(root):
            if file.startswith(f'slot{slot_idx}'):
                return file
        return None


class Load(TemplateView):
    template_name = 'moviemon/load.html'
    slot_idx = 'a'
    loaded = False

    def get(self, request, *args, **kwargs):
        self.slot_idx = request.GET.get('slot_idx', 'a')
        cmd = request.GET.get('cmd')

        if cmd == 'up' and self.slot_idx != 'a':
            self.slot_idx = chr(ord(self.slot_idx) - 1)
        elif cmd == 'down' and self.slot_idx != 'c':
            self.slot_idx = chr(ord(self.slot_idx) + 1)
        elif cmd == 'a' and self.parse_slot_score(self.slot_idx) != 'free':
            self.load_gamedata()
            self.loaded = True
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'btn_enable': {
                'up': True,
                'down': True,
                'a': True,
                'b': True
            }
        })
        context['slots_state'] = {
            'a': self.parse_slot_score('a'),
            'b': self.parse_slot_score('b'),
            'c': self.parse_slot_score('c')
        }
        context['slot_idx'] = self.slot_idx
        context['loaded'] = self.loaded
        if context['slots_state'][self.slot_idx] == 'free':
            context['btn_enable']['a'] = False
        if self.slot_idx == 'a': context['btn_enable']['up'] = False
        if self.slot_idx == 'c': context['btn_enable']['down'] = False
        return context

    def parse_slot_score(self, slot_idx):
        filename = self.get_filename(slot_idx)
        if not filename:
            return 'free'
        else:
            return filename[6:-4].replace('_', '/')

    def load_gamedata(self):
        path = f'{settings.BASE_DIR}/moviemon/saved_game/{self.get_filename(self.slot_idx)}'
        with open(path, 'rb') as file:
            self.request.session['gamedata'] = file.read().hex()

    def get_filename(self, slot_idx):
        root = f'{settings.BASE_DIR}/moviemon/saved_game'
        for file in os.listdir(root):
            if file.startswith(f'slot{slot_idx}'):
                return file
        return None

class Win(TemplateView):
    template_name = 'moviemon/win.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'btn_enable': {
                'a': True,
                'b': True
            }
        })
        return context
