# app/chat/viz_engine.py

import matplotlib.pyplot as plt
import base64
from io import BytesIO


def _save_plot():
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode()


def generate_column_plot(df, column):

    plt.figure()
    df[column].hist(bins=20)
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")

    return _save_plot()


def generate_agg_plot(value, column, agg):

    plt.figure()
    plt.bar([column], [value])
    plt.title(f"{agg.upper()} of {column}")
    plt.ylabel(agg)

    return _save_plot()


def generate_group_plot(df, group_col, value_col, agg):

    plt.figure()
    plt.bar(df[group_col].astype(str), df[value_col])
    plt.title(f"{agg.upper()} {value_col} by {group_col}")
    plt.xlabel(group_col)
    plt.ylabel(value_col)
    plt.xticks(rotation=45)

    return _save_plot()
