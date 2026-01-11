import requests
from django.conf import settings


class RawgAPIService:
    BASE_URL = "https://api.rawg.io/api"

    def __init__(self):
        self.api_key = settings.RAWG_API_KEY

    def search_games(self, genre_ids=None, year_from=None, year_to=None, page_size=20):
        params = {
            'key': self.api_key,
            'page_size': min(page_size, 40),
            'ordering': '-metacritic'
        }

        if genre_ids:
            params['genres'] = ','.join(str(g) for g in genre_ids)

        if year_from and year_to:
            params['dates'] = f"{year_from}-01-01,{year_to}-12-31"
        elif year_from:
            params['dates'] = f"{year_from}-01-01,2025-12-31"
        elif year_to:
            params['dates'] = f"1970-01-01,{year_to}-12-31"

        try:
            response = requests.get(f"{self.BASE_URL}/games", params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"RAWG API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"API request failed: {e}")
            return None