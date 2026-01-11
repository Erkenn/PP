import pandas as pd
from datetime import datetime


class GameAnalyzer:
    def __init__(self, games_data):
        """games_data: список словарей с данными об играх"""
        if not games_data:
            self.df = pd.DataFrame()
            return

        df_data = []
        for game in games_data:
            release_year = None
            if game.get('release_date') and game['release_date'] != 'Неизвестно':
                try:
                    date_obj = datetime.strptime(game['release_date'], '%Y-%m-%d')
                    release_year = date_obj.year
                except:
                    release_year = None

            df_data.append({
                'title': game['title'],
                'rating': float(game['rating']),
                'metacritic': int(game['metacritic']) if game['metacritic'] else 0,
                'release_year': release_year,
                'genres': ', '.join(game.get('genres', [])),
                'platforms': len(game.get('platforms', []))
            })

        self.df = pd.DataFrame(df_data)

    def get_genre_trends(self):
        """Анализ трендов по жанрам"""
        if self.df.empty or self.df['release_year'].isna().all():
            return None

        yearly_releases = self.df.groupby('release_year').size().reset_index(name='releases')
        yearly_releases = yearly_releases.sort_values('release_year')

        if len(yearly_releases) >= 2:
            first_year = yearly_releases.iloc[0]['releases']
            last_year = yearly_releases.iloc[-1]['releases']
            trend = ((last_year - first_year) / first_year * 100) if first_year > 0 else 0
        else:
            trend = 0

        return {
            'yearly_data': yearly_releases.to_dict(orient='records'),
            'trend_percentage': round(trend, 1),
            'total_games': len(self.df)
        }

    def get_rating_analysis(self):
        """Анализ рейтингов"""
        if self.df.empty:
            return None

        avg_rating = self.df['rating'].mean()
        avg_metacritic = self.df[self.df['metacritic'] > 0]['metacritic'].mean()

        rating_distribution = {
            'excellent': len(self.df[self.df['rating'] >= 4.5]),
            'good': len(self.df[(self.df['rating'] >= 3.5) & (self.df['rating'] < 4.5)]),
            'average': len(self.df[(self.df['rating'] >= 2.5) & (self.df['rating'] < 3.5)]),
            'poor': len(self.df[self.df['rating'] < 2.5])
        }

        return {
            'avg_rating': round(avg_rating, 2),
            'avg_metacritic': round(avg_metacritic, 1) if not pd.isna(avg_metacritic) else 0,
            'distribution': rating_distribution,
            'total_games': len(self.df)
        }

    def generate_recommendations(self, genre_names, year_from, year_to):
        """Генерация рекомендаций для разработчиков"""
        recommendations = []

        if self.df.empty:
            return ["Недостаточно данных для анализа."]

        trend_data = self.get_genre_trends()
        if trend_data:
            trend = trend_data['trend_percentage']
            if trend > 10:
                recommendations.append(
                    f"Жанр(ы) {', '.join(genre_names)} показывает рост (+{trend}% релизов за период). Хорошее время для входа на рынок.")
            elif trend < -10:
                recommendations.append(
                    f"Жанр(ы) {', '.join(genre_names)} показывает спад ({trend}% релизов за период). Рассмотрите гибридные концепции.")
            else:
                recommendations.append(f"Жанр(ы) {', '.join(genre_names)} стабилен. Конкуренция умеренная.")

        rating_data = self.get_rating_analysis()
        if rating_data:
            avg_rating = rating_data['avg_rating']
            if avg_rating >= 4.0:
                recommendations.append(f"Средний рейтинг высокий ({avg_rating}/5). Игроки лояльны к этому жанру.")
            elif avg_rating >= 3.0:
                recommendations.append(
                    f"Средний рейтинг удовлетворительный ({avg_rating}/5). Есть пространство для качественного продукта.")
            else:
                recommendations.append(
                    f"Средний рейтинг низкий ({avg_rating}/5). Требуется уникальный подход для выделения.")

        if year_from and year_to:
            recommendations.append(
                f"Оптимальное окно релиза: Q2-Q3 {year_to + 1} (меньше конкуренции после рождественского периода).")

        return recommendations