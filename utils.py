import pandas as pd


def queryset2df(query_set):
    columns = query_set[0].columns()
    rows = []
    for data in query_set:
        rows.append(data.get_values())
    return pd.DataFrame(rows, columns=columns)
