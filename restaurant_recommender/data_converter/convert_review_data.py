import json
import sqlite3
from pathlib import Path
from sqlite3 import Error
from tkinter import filedialog, Tk

import pandas as pd

from restaurant_recommender.data_collector import BusinessDataSet


def get_filepath():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilename()


def rows(ff, chunk_size=2048, sep='\n'):
    curr_row = ''
    while True:
        chunk = ff.read(chunk_size)
        if chunk == '':  # End of file
            yield curr_row
            break
        while True:
            i = chunk.find(sep)
            if i == -1:
                break
            yield curr_row + chunk[:i]
            curr_row = ''
            chunk = chunk[i + 1:]
        curr_row += chunk


def create_connection(path):
    conn = None
    try:
        conn = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return conn


def execute_query(conn, query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
        print('Successful query execution')
    except Error as e:
        print(f'The error {e} occurred')


def get_req_ids(cat: str = 'restaurant', state: str = 'ON') -> set:
    ds = BusinessDataSet(cat, state)
    ids = set(ds.data.index)
    return ids


create_table = """
CREATE TABLE IF NOT EXISTS REVIEWS (
  REVIEW_ID TEXT PRIMARY KEY NOT NULL,
  USER_ID TEXT,
  BUSINESS_ID TEXT,
  STARS NUMERIC,
  USEFUL NUMERIC,
  FUNNY NUMERIC,
  COOL NUMERIC,
  REVIEW TEXT,
  DATE TEXT
);
"""

database_path = Path(__file__).parents[2] / 'data/reviews.sqlite'

connection = create_connection(database_path)
execute_query(connection, create_table)

download_path = get_filepath()
local_ids = get_req_ids()

with open(download_path, 'r') as f:
    total_rows = 0
    total_errors = 0
    for row in rows(f):
        conv_list = error_list = list()
        conv = row.split('\n')

        for c in conv:
            try:
                j = json.loads(c)
                conv_list.append(j)
            except:
                error_list.append(c)

        total_errors += len(error_list)

        if len(conv_list) > 0 and all([isinstance(c, dict) for c in conv_list]):
            df = pd.DataFrame(conv_list)
            df.columns = [_.upper() for _ in df.columns]
            df = df.rename(columns={'TEXT': 'REVIEW'})
            # df = df[df.BUSINESS_ID.isin(local_ids)]
            if len(df) > 0:
                df.to_sql(name='REVIEWS', con=connection, index=False, if_exists='append')
                total_rows += df.shape[0]
