from django import forms


class GameAnalysisForm(forms.Form):
    GENRE_CHOICES = [
        (4, 'Action'),
        (5, 'Adventure'),
        (12, 'RPG'),
        (40, 'Strategy'),
        (51, 'Indie'),
        (14, 'Simulation'),
        (11, 'Racing'),
        (7, 'Puzzle'),
        (3, 'Platformer'),
        (10, 'Sports'),
        (15, 'Shooter'),
        (2, 'Fighting'),
    ]

    genres = forms.MultipleChoiceField(
        choices=GENRE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        label="Выберите жанры для анализа"
    )

    year_from = forms.IntegerField(
        min_value=1970,
        max_value=2025,
        initial=2018,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 2018'}),
        label="Год начала периода"
    )

    year_to = forms.IntegerField(
        min_value=1970,
        max_value=2025,
        initial=2025,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 2025'}),
        label="Год окончания периода"
    )

    def clean(self):
        cleaned_data = super().clean()
        year_from = cleaned_data.get('year_from')
        year_to = cleaned_data.get('year_to')

        if year_from and year_to and year_from > year_to:
            raise forms.ValidationError("Год начала не может быть больше года окончания")

        return cleaned_data