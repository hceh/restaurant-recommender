import http.client
import re
import urllib.parse
from collections import Counter
from os.path import exists

import pandas as pd
import yaml

try:
    with open('../access-keys.yaml') as y:
        access_key = yaml.load(y, Loader=yaml.FullLoader).get('position-stack', '')
except FileNotFoundError:
    with open('access-keys.yaml') as y:
        access_key = yaml.load(y, Loader=yaml.FullLoader).get('position-stack', '')


class BusinessDataSet:
    def __init__(self, category: str = None, state: str = None):
        self.data = self.get_data(category, state)
        self.add_ranking_col()

    @staticmethod
    def read_full_data() -> pd.DataFrame:
        if exists('data/yelp_academic_dataset_business.json'):
            location = 'data/yelp_academic_dataset_business.json'
        elif exists('../data/yelp_academic_dataset_business.json'):
            location = '../data/yelp_academic_dataset_business.json'
        else:
            raise FileNotFoundError("Can't find the data file, please run data converter")
        return pd.read_json(location, orient='records')

    @staticmethod
    def get_coord_from_address(address: str):
        conn = http.client.HTTPConnection('api.positionstack.com')
        params = urllib.parse.urlencode({'access_key': access_key, 'query': address})
        conn.request('GET', f'/v1/forward?{params}')
        res = conn.getresponse()
        data = res.read()
        data.decode('utf-8')
        out = data.decode('utf-8')
        d = pd.read_json(out).data.apply(pd.Series)
        d = d[(d.country_code == 'CAN') & (d.region_code == 'ON')].reset_index(drop=True)
        if d.shape[0] > 0:
            return d.at[0, 'latitude'], d.at[0, 'longitude']
        return 'Not found', 'Not found'

    @property
    def n_listings(self) -> int:
        return self.data.shape[0]

    def add_ranking_col(self):
        self.data['rank_value'] = self.data.review_count / (5.1 - self.data.stars)

    def get_data(self, category: str = None, state: str = None, df: pd.DataFrame = None) -> pd.DataFrame:
        df = df if df is not None else self.read_full_data()
        if category:
            df = df[df.categories.fillna('none').str.lower().str.contains(category.lower())]
        if state:
            df = df[df.state == state]
        return df

    def get_full_attribute_options(self) -> set:
        options = set()
        print('Collecting attributes')
        for ix, row in self.data.iterrows():
            try:
                new_attrs = set(row.attributes.keys())
                options.update(new_attrs)
            except AttributeError:  # no attributes
                pass

        print('Converting attributes from camelCase to Title Case')
        pattern = re.compile(r'(?<=[a-z])(?=[A-Z])')

        def convert_attr_to_text(text: str):
            return pattern.sub(' ', text)

        options = {convert_attr_to_text(_) for _ in options}

        return options

    def get_categories(self) -> list:
        categories = [_.split(', ') for _ in set(self.data.categories) if _ is not None]
        categories = [item for sublist in categories for item in sublist]
        return categories

    def get_categories_summary(self) -> pd.DataFrame:
        categories = self.get_categories()
        return (pd.DataFrame
                .from_dict(dict(Counter(categories)), orient='index', columns=['count'])
                .sort_values('count', ascending=False))

    def fix_values(self, col_name: str, replacements_dict: dict):
        self.data[col_name] = self.data[col_name].replace(replacements_dict)

    def get_cities(self) -> list:
        cities = self.data.city.value_counts()
        return list(cities.index)
