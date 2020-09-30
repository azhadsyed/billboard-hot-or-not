from datetime import datetime, timedelta
from math import floor
from tqdm import tqdm
from statistics import mean, median
import pandas as pd, numpy as np
import pickle

tqdm.pandas()

class ChartMetrics:
    def __init__(self, dataframe = None, debug = False, songs = None):
        self.data = dataframe
        self.songs = songs
        self.artists = None
        self.metrics = None
        self.monthlies = None
        self.debug = debug
    def import_songs(self, file):
        with open (file, 'rb') as f: self.songs = pickle.load(f)
    def import_artists(self, file):
        with open (file, 'rb') as f: self.artists = pickle.load(f)
    def import_data(self, file):
        with open(file, 'rb') as f: self.data = pickle.load(f)
    def calc_song_debut_start(self, row): 
        return self.data[(self.data.title == row.title) & (self.data.main_artist == row.main_artist)].chart_date_64.min()
    def calc_song_debut_end(self, row):
        sample = self.data[(self.data.title == row.title) & (self.data.main_artist == row.main_artist)]
        x = row.debut_date
        m = list(sample.chart_date_64)
        while True:
            y = x + timedelta(days = 7)
            if y in m: x = y
            else: return x
    def calc_song_chart_weeks(self, row):
        return self.data[(self.data.title == row.title) & (self.data.main_artist == row.main_artist)].shape[0]
    def calc_artist_debut_date(self, artist):
        return self.songs[self.songs.main_artist.apply(lambda x: artist in x)].debut_date.min()
    def get_debut_song(self, a):
        f = self.songs.main_artist.apply(lambda x: a in x)
        s = self.songs[f].sort_values(by = 'debut_date')
        i = s.iloc[0]
        t = i.title
        return t
    def calc_avg_songs_per_chart_artist(self, year):
        sample = self.songs[self.songs.debut_year == year]
        sample_artists = list(set([j for i in sample.main_artist for j in i]))
        sample_artists_count = [int(sample.main_artist.apply(lambda x: i in x).sum()) for i in sample_artists]
        return mean(sample_artists_count)
    def calc_artist_debuts_per_month(self, row):
        return self.artists[(self.artists.debut_year == row.year) & (self.artists.debut_month == row.month)].shape[0]
    def calc_song_releases_per_month(self, row):
        return self.songs[(self.songs.debut_year == row.year) & (self.songs.debut_month == row.month)].shape[0]
    def create_songs_data(self):
        self.songs = self.data[['title', 'main_artist']].drop_duplicates()
        self.songs['debut_date'] = self.songs.progress_apply(self.calc_song_debut_start, axis = 1)
        self.songs['debut_year'] = self.songs.debut_date.progress_apply(lambda x: x.year)
        self.songs['debut_month'] = self.songs.debut_date.progress_apply(lambda x: x.month)
        self.songs['debut_end'] = self.songs.progress_apply(self.calc_song_debut_end, axis = 1)
        self.songs['debut_streak'] = self.songs.debut_end - self.songs.debut_date
        self.songs['debut_weeks'] = self.songs.debut_streak.progress_apply(lambda x: x.days/7+1)
        self.songs['chart_weeks'] = self.songs.progress_apply(self.calc_song_chart_weeks, axis = 1)
        self.songs['sleeper_hit'] = self.songs.chart_weeks - self.songs.debut_weeks
        if self.debug:
            with open ('pickle/test_songs_backup.pkl', 'wb') as f: pickle.dump(self.songs, f)
    def create_artists_data(self):
        self.labels = ['one-hit wonder', '2-10 songs', '11-50 songs', '51+ songs']
        self.artists = pd.DataFrame(set([j for i in self.songs.main_artist for j in i]), columns = ['artist'])
        self.artists['debut_date'] = self.artists.artist.progress_apply(self.calc_artist_debut_date)
        self.artists['debut_year'] = self.artists.debut_date.progress_apply (lambda x: x.year)
        self.artists['debut_month'] = self.artists.debut_date.progress_apply (lambda x: x.month)
        self.artists['charted_songs'] = self.artists.artist.progress_apply(lambda x: sum(x in item for item in self.songs.main_artist))
        self.artists['bin'] = pd.cut(self.artists.charted_songs, bins = np.array([0, 2, 10, 50, 200]), labels = self.labels).astype('str')
        self.artists['debut_song'] = self.artists.artist.progress_apply(self.get_debut_song)
        if self.debug:
            with open ('pickle/test_artists_backup.pkl', 'wb') as f: pickle.dump(self.artists, f)
    def create_annual_metrics(self):
        self.metrics = pd.DataFrame()
        self.metrics['year'] = list(set([int(i) for i in self.data.year]))
        self.metrics['decade'] = self.metrics.year.progress_apply (lambda x: floor(x / 10)*10)
        self.metrics['decade_str'] = self.metrics.decade.progress_apply(lambda x: str(x))
        self.metrics['num_different_artists'] = self.metrics.year.progress_apply(lambda x: len(set([j for i in self.data[self.data.year == x].main_artist for j in i])))
        self.metrics['num_debut_artists'] = self.metrics.year.progress_apply(lambda x: self.artists[self.artists.debut_year == x].debut_year.value_counts()[x])
        self.metrics['perc_debut_artists'] = self.metrics.num_debut_artists / self.metrics.num_different_artists
        self.metrics['median_debut_length'] = self.metrics.year.progress_apply(lambda x: self.songs[self.songs.debut_year == x].debut_weeks.median())
        self.metrics['num_different_songs'] = self.metrics.year.progress_apply(lambda x: self.songs[self.songs.debut_year == x].shape[0])
        self.metrics['mean_num_songs_per_artist'] = self.metrics.year.progress_apply(self.calc_avg_songs_per_chart_artist)
        if self.debug:
            with open ('pickle/test_metrics_backup.pkl', 'wb') as f: pickle.dump(self.metrics, f)
    def create_monthly_metrics(self):
        year = [int(i) for i in self.metrics.year]
        month = [i + 1 for i in range(12)]
        rows = [(i, j) for i in year for j in month]
        self.monthlies = pd.DataFrame(rows, columns = ['year', 'month'])
        self.monthlies['decade'] = self.monthlies.year.apply(lambda x: floor(x/10)*10)
        self.monthlies['artist_debuts'] = self.monthlies.apply(self.calc_artist_debuts_per_month, axis = 1)
        self.monthlies['song_releases'] = self.monthlies.apply(self.calc_song_releases_per_month, axis = 1)
        if self.debug:
            with open ('pickle/test_monthlies_backup.pkl', 'wb') as f: pickle.dump(self.monthlies, f)
    def create_all_metrics(self):
        self.create_songs_data()
        self.create_artists_data()
        self.create_annual_metrics()
        self.create_monthly_metrics()
    def all_to_pickle(self):
        with open ('pickle/songs.pkl', 'wb') as f: pickle.dump(self.songs, f)
        with open ('pickle/artists.pkl', 'wb') as f: pickle.dump(self.artists, f)
        with open ('pickle/metrics.pkl', 'wb') as f: pickle.dump(self.metrics, f)
        with open ('pickle/monthlies.pkl', 'wb') as f: pickle.dump(self.monthlies, f)