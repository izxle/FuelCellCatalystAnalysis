import pickle
import pandas as pd
from os import path
from openpyxl import load_workbook

def save_object(obj, filename):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)


def save_to_excel(df, filename, sheet_name, startcol=0, startrow=0, index=True):

    append =  path.isfile(filename)

    if append:
        workbook = load_workbook(filename)

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        if append:
            writer.book = workbook
            writer.sheets = dict((ws.title, ws) for ws in workbook.worksheets)
        df.to_excel(writer, sheet_name=sheet_name, startcol=startcol, startrow=startrow, index=index)



