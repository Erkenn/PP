from django.shortcuts import render
from .forms import GameAnalysisForm
from .services.rawg_api import RawgAPIService
from .analytics.game_analyzer import GameAnalyzer
from .utils.charts import create_yearly_releases_chart, create_rating_distribution_chart
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
                'rating_data': rating_data
            })
        else:
            pass
    else:
        form = GameAnalysisForm()
    return render(request, 'tracker/home.html', {'form': form})