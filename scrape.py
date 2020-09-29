from datetime import datetime
import billboard, json, pickle

def string_to_date(x):
    return datetime.strptime(x, '%Y-%m-%d')
def chart_to_dict(chart):
    return (chart.title, chart.date, [{'title': i.title, 'artist': i.artist, 'rank': i.rank} for i in chart.entries])
    
class ChartList:
    def __init__(self):
        self.charts = []
        self.retries = 0
        self.off = False
    def get_chart(self, name, date):
        try:
            chart = billboard.ChartData(name, date)
            print (name, date)
            self.charts.append(chart_to_dict(chart))
            self.retries = 0
            return chart.previousDate
        except:
            if self.retries >= 5:
                print ('Timed out five times, ending run')
                self.off = True
                self.retries = 0
            self.retries += 1
    def get_charts(self, name, end, start = None):
        if start:
            current = end
            def get_chart_and_iterate(d):
                return self.get_chart(name, d)
            # method 1: pulling from inception to end date
            if start == 'inception':
                while current:
                    current = get_chart_and_iterate(current)
                    if self.off: break
            # method 2: pulling from start date to end date
            else:
                while string_to_date(current) > string_to_date(start):
                    current = get_chart_and_iterate(current)
                    if self.off: break
        elif start == None:
            # method 3 - pulling a list of individual dates
            if type(end) == list:
                for date in end: self.get_chart(name, date)
            # method 4 - pulling an individual date
            else: self.get_chart(name, end)
    def to_pickle(self, filename):
        with open (filename, 'wb') as f: pickle.dump(self.charts, f)
    def to_json(self, filename):
        with open (filename, 'w') as f: json.dump(self.charts, f)
        
if __name__ == '__main__':
    chartlist = ChartList()
#    chartlist.get_charts('Social-50', '2011-01-01', start = 'inception') # 4 (?) charts
#    chartlist.get_charts('Hot-100', '2020-09-26', start = '2020-08-01')
#    chartlist.get_charts('Artist-100', ['2020-07-01', '2015-07-01']) # 2 charts
#    chartlist.get_charts('Billboard-200', '2020-08-01') # 1 chart
    chartlist.get_charts('Hot-100', '2009-10-03', start = 'inception')
    chartlist.to_pickle('pickle/hot100.pkl')
#    chartlist.to_json('json/chartlist.json')