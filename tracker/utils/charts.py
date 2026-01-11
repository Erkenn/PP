import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd


def create_yearly_releases_chart(yearly_data):
    """Создание графика релизов по годам"""
    if not yearly_data:
        return ""

    df = pd.DataFrame(yearly_data)
    fig = px.line(
        df,
        x='release_year',
        y='releases',
        title='Динамика количества релизов по годам',
        labels={'release_year': 'Год', 'releases': 'Количество игр'},
        markers=True
    )

    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode='x unified'
    )

    return pio.to_html(fig, full_html=False)


def create_rating_distribution_chart(distribution_data):
    """Создание диаграммы распределения рейтингов"""
    if not distribution_data:
        return ""

    labels = ['Отлично (4.5+)', 'Хорошо (3.5-4.4)', 'Средне (2.5-3.4)', 'Плохо (<2.5)']
    values = [
        distribution_data.get('excellent', 0),
        distribution_data.get('good', 0),
        distribution_data.get('average', 0),
        distribution_data.get('poor', 0)
    ]

    filtered_labels = [label for label, value in zip(labels, values) if value > 0]
    filtered_values = [value for value in values if value > 0]

    if not filtered_values:
        return ""

    fig = go.Figure(data=[go.Pie(labels=filtered_labels, values=filtered_values, hole=.3)])
    fig.update_layout(
        title='Распределение игр по рейтингу',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return pio.to_html(fig, full_html=False)