from .forms import GameAnalysisForm, SignUpForm
from .services.rawg_api import RawgAPIService
from .analytics.game_analyzer import GameAnalyzer
from .utils.charts import create_yearly_releases_chart, create_rating_distribution_chart
from django.shortcuts import render, redirect
from django.contrib.auth import login
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
            api_data = service.get_all_games(
                genre_ids=genre_ids,
                year_from=year_from,
                year_to=year_to
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
                    genres_ids = []
                    for genre in game_data.get('genres', []):
                        genres_list.append(genre.get('name', ''))
                        genres_ids.append(genre.get('id', 0))

                    # обработка платформ
                    platforms_list = []
                    platforms_data = game_data.get('platforms')
                    if platforms_data:
                        for platform in platforms_data:
                            if 'platform' in platform:
                                platforms_list.append(platform['platform'].get('name', ''))

                    games_data.append({
                        'title': game_data.get('name', 'Unknown'),
                        'rating': game_data.get('rating', 0),
                        'metacritic': game_data.get('metacritic', 0) or 0,
                        'release_date': release_date,
                        'genres': genres_list,
                        'genres_ids': genres_ids,
                        'platforms': platforms_list,
                        'image_url': game_data.get('background_image', '')
                    })

            all_genres_set = set()
            for game in games_data:
                all_genres_set.update(game['genres'])
            all_genres = sorted(all_genres_set)

            genre_choices = [
                (4, 'Action'),
                (5, 'RPG'),
                (15, 'Sports'),
                (40, 'Casual'),
                (51, 'Indie'),
                (14, 'Simulation'),
                (11, 'Arcade'),
                (7, 'Puzzle'),
                (3, 'Adventure'),
                (10, 'Sports'),
                (2, 'Shooter'),
                (6, 'Fighting'),
            ]

            genre_choices_for_template = [(str(id), name) for id, name in genre_choices]

            filtered_games = []
            for game in games_data:
                game_genre_ids = set(str(gid) for gid in game.get('genres_ids', []))
                selected_genre_ids = set(str(gid) for gid in genre_ids)

                if game_genre_ids.intersection(selected_genre_ids):
                    filtered_games.append(game)

            games_data = filtered_games

            analyzer = GameAnalyzer(games_data)

            # рекомендации
            genre_names = []
            for genre_id in genre_ids:
                for choice in form.fields['genres'].choices:
                    if choice[0] == genre_id:
                        genre_names.append(choice[1])
                        break

            recommendations = analyzer.generate_recommendations(genre_names, year_from, year_to)

            # графики
            trend_data = analyzer.get_genre_trends()
            rating_data = analyzer.get_rating_analysis()

            yearly_chart = ""
            rating_chart = ""

            if trend_data:
                yearly_chart = create_yearly_releases_chart(trend_data['yearly_data'])

            if rating_data:
                rating_chart = create_rating_distribution_chart(rating_data['distribution'])

            return render(request, 'tracker/results.html', {
                'form': form,
                'games': games_data,
                'year_from': year_from,
                'year_to': year_to,
                'genre_count': len(genre_ids),
                'recommendations': recommendations,
                'yearly_chart': yearly_chart,
                'rating_chart': rating_chart,
                'trend_data': trend_data,
                'rating_data': rating_data,
                'all_genres': all_genres,
                'genre_choices': genre_choices_for_template
            })
        else:
            pass
    else:
        form = GameAnalysisForm()
    return render(request, 'tracker/home.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})