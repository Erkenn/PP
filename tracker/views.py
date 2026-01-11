from django.shortcuts import render
from django.http import JsonResponse
from .forms import GameAnalysisForm
from .services.rawg_api import RawgAPIService
import logging


logger = logging.getLogger(__name__)


def home(request):
    if request.method == 'POST':
        form = GameAnalysisForm(request.POST)
        if form.is_valid():
            # получаем данные из формы
            genre_ids = [int(g) for g in form.cleaned_data['genres']]
            year_from = form.cleaned_data['year_from']
            year_to = form.cleaned_data['year_to']

            # запрашиваем данные из API
            service = RawgAPIService()
            api_data = service.search_games(
                genre_ids=genre_ids,
                year_from=year_from,
                year_to=year_to,
                page_size=20
            )

            games_data = []
            if api_data and 'results' in api_data:
                for game_data in api_data['results']:
                    # обработка даты релиза
                    release_date = game_data.get('released', '')
                    if not release_date:
                        release_date = 'Неизвестно'

                    # обработка жанров
                    genres_list = []
                    for genre in game_data.get('genres', []):
                        genres_list.append(genre.get('name', ''))

                    # обработка платформ
                    platforms_list = []
                    for platform in game_data.get('platforms', []):
                        if 'platform' in platform:
                            platforms_list.append(platform['platform'].get('name', ''))

                    games_data.append({
                        'title': game_data.get('name', 'Unknown'),
                        'rating': game_data.get('rating', 0),
                        'metacritic': game_data.get('metacritic', 0) or 0,
                        'release_date': release_date,
                        'genres': genres_list,
                        'platforms': platforms_list,
                        'image_url': game_data.get('background_image', '')
                    })

            return render(request, 'tracker/results.html', {
                'form': form,
                'games': games_data,
                'year_from': year_from,
                'year_to': year_to,
                'genre_count': len(genre_ids)
            })
    else:
        form = GameAnalysisForm()

    return render(request, 'tracker/home.html', {'form': form})