import os

import pandas as pd
import numpy as np
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine
import statsmodels.api as sm
import streamlit as st
import datetime

load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOSTNAME = os.getenv("DB_HOSTNAME")
DB_NAME = os.getenv("DB_NAME")
connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}"
engine = create_engine(connection_string)

# Preparing data for the questions on review data
# Decided to aggregate on city+date level in SQL as that is the lowest level needed for the assignments
# This keeps the local data as small as possible


st.write("### Oefenen met streamlit")

df_reviews = pd.read_sql_query(
    """
    select
        DATE(datetime) as review_date,
        location_city,
        count(*) as n_reviews,
        AVG(rating_delivery) as avg_del_score,
        AVG(rating_food) as avg_food_score
    from
        reviews revs
    left join
    restaurants rests
    on
        revs.restaurant_id = rests.restaurant_id
    where
        datetime >= '2022-01-01'
        and datetime < '2023-02-01'
        and location_city in ('Groningen', 'Amsterdam', 'Rotterdam')
    group by
        DATE(datetime),
        location_city
    """,
    con=engine
)

d_start = st.date_input("Begindatum", datetime.date(2022, 1, 1),min_value=datetime.date(2022, 1, 1),max_value=datetime.date(2023, 1, 31))
d_end = st.date_input("Einddatum", datetime.date(2023, 1, 31),min_value=datetime.date(2022, 1, 1),max_value=datetime.date(2023, 1, 31))
df_filtered = df_reviews.loc[(df_reviews.review_date>=d_start)&(df_reviews.review_date<=d_end)]

# The average number of reviews per day in each city (calculated as one number per city over the entire year)
avg_reviews = df_filtered.groupby(["location_city"], as_index=False)["n_reviews"].mean()

barchart = px.bar(
    avg_reviews,
    x="location_city",
    y="n_reviews",
    labels={
        "n_reviews": "No. of reviews / Day",
        "location_city": "",
    },
    title = 'Average number of reviews per city per day',
    width=600
)

st.plotly_chart(barchart, use_container_width=True)

# The average delivery rating per day in each city

timeline = px.line(df_filtered, x='review_date', y='avg_del_score', color='location_city')
st.plotly_chart(timeline, use_container_width=True)
