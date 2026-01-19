from .forms import GameAnalysisForm, SignUpForm
from .services.rawg_api import RawgAPIService
from .analytics.game_analyzer import GameAnalyzer
from .utils.charts import create_yearly_releases_chart, create_rating_distribution_chart
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .models import Game, Genre, Platform
from datetime import datetime


def home(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            if request.session.get('guest_analysis_used'):
                messages.error(
                    request,
                    'Гости могут выполнить только один анализ за сессию. '
                    'Войдите или зарегистрируйтесь для неограниченного доступа.'
                )
                return render(request, 'tracker/home.html', {'form': GameAnalysisForm()})

    if request.method == 'POST':
        form = GameAnalysisForm(request.POST)
        if form.is_valid():
            genre_ids = [int(g) for g in form.cleaned_data['genres']]
            year_from = form.cleaned_data['year_from']
            year_to = form.cleaned_data['year_to']

            if not request.user.is_authenticated:
                request.session['guest_analysis_used'] = True

            service = RawgAPIService()
            api_data = service.get_all_games(
                genre_ids=genre_ids,
                year_from=year_from,
                year_to=year_to
            )

            games_data = []
            if api_data and 'results' in api_data:
                for game_data in api_data['results']:
                    release_date_str = game_data.get('released', '')
                    release_date_parsed = None
                    if release_date_str:
                        try:
                            release_date_parsed = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                        except:
                            pass

                    genres_list = []
                    genres_ids = []
                    for genre_raw in game_data.get('genres', []):
                        genre_id = genre_raw.get('id')
                        genre_name = genre_raw.get('name', '')
                        if genre_id:
                            genre_obj, _ = Genre.objects.get_or_create(
                                rawg_id=genre_id,
                                defaults={'name': genre_name, 'slug': str(genre_id)}
                            )
                            genres_list.append(genre_name)
                            genres_ids.append(genre_id)

                    platforms_list = []
                    platforms_data = game_data.get('platforms') or []
                    for platform_raw in platforms_data:
                        plat_data = platform_raw.get('platform', {})
                        plat_id = plat_data.get('id')
                        plat_name = plat_data.get('name', '')
                        if plat_id:
                            plat_obj, _ = Platform.objects.get_or_create(
                                rawg_id=plat_id,
                                defaults={'name': plat_name, 'slug': str(plat_id)}
                            )
                            platforms_list.append(plat_name)

                    rawg_game_id = game_data.get('id')
                    if rawg_game_id:
                        game_obj, created = Game.objects.get_or_create(
                            rawg_id=rawg_game_id,
                            defaults={
                                'title': game_data.get('name', 'Unknown'),
                                'release_date': release_date_parsed,
                                'rating': float(game_data.get('rating', 0) or 0),
                                'metacritic': int(game_data.get('metacritic') or 0),
                                'image_url': game_data.get('background_image', ''),
                                'slug': str(rawg_game_id),
                            }
                        )
                        if created or not game_obj.genres.exists():
                            game_obj.genres.set(Genre.objects.filter(rawg_id__in=genres_ids))
                        if created or not game_obj.platforms.exists():
                            game_obj.platforms.set(Platform.objects.filter(
                                rawg_id__in=[p.rawg_id for p in Platform.objects.filter(name__in=platforms_list)]))

                    games_data.append({
                        'title': game_data.get('name', 'Unknown'),
                        'rating': game_data.get('rating', 0),
                        'metacritic': game_data.get('metacritic', 0) or 0,
                        'release_date': release_date_str or 'Неизвестно',
                        'genres': genres_list,
                        'genres_ids': genres_ids,
                        'platforms': platforms_list,
                        'image_url': game_data.get('background_image', '')
                    })

            filtered_games = []
            for game in games_data:
                game_genre_ids = set(str(gid) for gid in game.get('genres_ids', []))
                selected_genre_ids = set(str(gid) for gid in genre_ids)
                if game_genre_ids.intersection(selected_genre_ids):
                    filtered_games.append(game)
            games_data = filtered_games

            all_genres_set = set()
            for game in games_data:
                all_genres_set.update(game['genres'])
            all_genres = sorted(all_genres_set)

            genre_choices = [
                (4, 'Action'),
                (5, 'RPG'),
                (2, 'Shooter'),
                (15, 'Sports'),
                (40, 'Casual'),
                (51, 'Indie'),
                (14, 'Simulation'),
                (11, 'Arcade'),
                (7, 'Puzzle'),
                (3, 'Adventure'),
                (6, 'Fighting'),
            ]
            genre_choices_for_template = [(str(id), name) for id, name in genre_choices]

            analyzer = GameAnalyzer(games_data)
            genre_names = []
            for genre_id in genre_ids:
                for choice in form.fields['genres'].choices:
                    if choice[0] == genre_id:
                        genre_names.append(choice[1])
                        break

            recommendations = analyzer.generate_recommendations(genre_names, year_from, year_to)
            trend_data = analyzer.get_genre_trends()
            rating_data = analyzer.get_rating_analysis()

            yearly_chart = create_yearly_releases_chart(trend_data['yearly_data']) if trend_data else ""
            rating_chart = create_rating_distribution_chart(rating_data['distribution']) if rating_data else ""

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
        form = GameAnalysisForm()

    return render(request, 'tracker/home.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})