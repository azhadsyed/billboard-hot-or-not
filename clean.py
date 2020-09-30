import pandas as pd, numpy as np
import pickle, json, re
from datetime import datetime

def tuple_to_dict(t):
    chart_name, chart_date, chart_entries = t
    df = pd.DataFrame.from_dict(chart_entries)
    df['chart_name'] = chart_name
    df['chart_date'] = chart_date
    return df
def split_artist_from_features(x): 
    return re.split(r" Featuring | Ft. | Feat. ", x)
def get_main_artists(x):
    return tuple(re.split(r" With |, | x | & | + |/", split_artist_from_features(x)[0]))
def get_featured_artists(x):
    x = split_artist_from_features(x)
    if len (x) > 1: 
        return tuple(re.split(r" With | & |, | x ", x[1]))
    else: 
        return np.NaN
def clean(df):
    clean = df
    clean['chart_date_64'] = clean.chart_date.apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    clean['year'] = clean.chart_date_64.apply(lambda x: x.year)
    clean['main_artist'] = clean.artist.apply(get_main_artists)
    clean['featured_artist'] = clean.artist.apply(get_featured_artists)
    clean.drop_duplicates(keep = 'first', inplace = True)
    return clean

class Cleaner:
    def __init__(self, file):
        with open(file, 'rb') as f: self.tuples = pickle.load(f) 
    def clean(self):
        self.data = pd.concat([tuple_to_dict(i) for i in self.tuples])
        self.clean_data = clean(self.data)
    def to_pickle(self, outfile):
        self.clean_data.to_pickle(outfile)

if __name__ == '__main__':
    cleaner = Cleaner('pickle/hot100.pkl')
    cleaner.clean()
    cleaner.to_pickle('pickle/hot100_clean.pkl')