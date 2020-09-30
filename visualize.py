import pandas as pd
import plotly.express as px, plotly.graph_objects as go

def render_bar(y_variable, graph_title, y_title, filename):
    bar = px.bar(
        metrics, 
        x = 'year', 
        y = y_variable, 
        color = 'decade_str', 
        color_discrete_sequence = seq1, 
        template = 'simple_white')
    bar.update_layout(
        title = graph_title,
        title_x = 0.5,
        xaxis_title = 'Year',
        yaxis_title = y_title,
        font = dict(size = 16, family = 'Arial'),
        showlegend = False)
    return bar

seq1 = [px.colors.sequential.Cividis[i] for i in [0, 0, 2, 4, 6, 8, 9]]

metrics = pd.read_pickle('pickle/test_metrics_backup.pkl')
monthlies = pd.read_pickle('pickle/test_monthlies_backup.pkl')

metrics = metrics[metrics.year.apply(lambda x: x not in [1958, 2020])]
monthlies['year_rank'] = monthlies.groupby('year').song_releases.rank(ascending = False)

decades = [1960, 1970, 1980, 1990, 2000, 2010]
values = [(
    i, 
    j + 1, 
    - monthlies[(monthlies.decade == i) & (monthlies.month == j + 1)].song_releases.median(),
    - monthlies[(monthlies.decade == i) & (monthlies.month == j + 1)].song_releases.mean(),
    - monthlies[(monthlies.decade == i) & (monthlies.month == j + 1)].song_releases.sum(),
    monthlies[(monthlies.decade == i) & (monthlies.month == j + 1)].year_rank.median(),
    monthlies[(monthlies.decade == i) & (monthlies.month == j + 1)].year_rank.mean()
) for i in decades for j in range(12)]

monthstr = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


bumpdf = pd.DataFrame(values, columns = ['Decade', 
                                         'Month', 
                                         'Median Song Debuts', 
                                         'Mean Song Debuts',
                                         'Total Song Debuts',
                                         'Median Annual Rank', 
                                         'Mean Annual Rank'])
bumpdf['Decade Rank v1'] = - bumpdf.groupby('Decade')['Mean Annual Rank'].rank('min')

def ties(row):
    if (row.Decade == 1990) & (row.Month == 2): return -8
    elif (row.Decade == 2000) & (row.Month == 12): return -5
    elif (row.Decade == 2000) & (row.Month == 9): return -10
    else: return row['Decade Rank v1']
bumpdf['Decade Rank v1 adj'] = bumpdf.apply(ties, axis = 1)
bumpdf['Decade Rank v2'] = - bumpdf.groupby('Decade')['Median Annual Rank'].rank('min')
bumpdf['Decade Rank v3'] = - bumpdf.groupby('Decade')['Total Song Debuts'].rank('min')
bumpdf['Decade Rank v4'] = - bumpdf.groupby('Decade')['Median Song Debuts'].rank('min')
bumpdf['Month_str'] = bumpdf.Month.apply(lambda x: monthstr[x - 1])

bump = px.scatter(
    bumpdf, 
    x = 'Decade', 
    y = 'Decade Rank v1 adj', 
    color = 'Month_str', 
    text = 'Month_str', 
    template = 'simple_white', width = 1000, height = 750,
    color_discrete_sequence = px.colors.qualitative.Set3)
bump.update_yaxes(visible = False)
bump.update_traces(
    mode = 'lines+markers+text',
    marker = dict(size = 27),
    line = dict(width = 8))
bump.update_layout (
    title = "Which Month Has the Most New Music Releases?",
    title_x = 0.5, 
    font = dict(family = 'Arial'),
    showlegend = False)

bar1 = render_bar(
    'num_different_artists',
    'How Many Different Artists Make the Hot 100 Each Year?', 
    '# Different Artists', 
    'num_diff_artists_per_year')
bar2 = render_bar(
    'num_different_songs',
    'How Many Different Songs Make the Hot 100 Each Year?',
    '# Different Songs',
    'num_diff_songs_per_year')
bar3 = render_bar(
    'mean_num_songs_per_artist',
    'How Many Songs Does a Hot 100 Artist Have Chart Each Year?',
    '# Songs Per Hot 100 Artist (Mean)',
    'num_songs_per_artist_per_year')
bar4 = render_bar(
    'median_debut_length',
    'How Long does a Song Stay on the Hot 100 When it Debuts?',
    '# Consecutive Weeks on the Hot 100 (Median) ',
    'weeks_on_chart_per_year')

renders = [bump, bar1, bar2, bar3, bar4]

for n, chart in enumerate(renders):
    filepath = 'svg/{}.svg'.format(n)
    chart.write_image(filepath)

for n, chart in enumerate(renders):
    filepath = 'svg/{}.png'.format(n)
    chart.write_image(filepath)