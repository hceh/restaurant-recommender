import pandas as pd
import re


class BusinessDataSet:
    def __init__(self, category: str = None):
        self.data = self.get_data(category)

    @staticmethod
    def read_full_data() -> pd.DataFrame:
        location = 'data/yelp_academic_dataset_business.json'
        return pd.read_json(location, orient='records')

    @property
    def n_listings(self):
        return self.data.shape[0]

    def get_data(self, category: str = None, df: pd.DataFrame = None) -> pd.DataFrame:
        df = df if df is not None else self.read_full_data()
        if category:
            return df[df.categories.fillna('none').str.lower().str.contains(category.lower())]
        return df

    def get_full_attribute_options(self):
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
