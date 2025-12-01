import pyodbc
import pandas as pd
import numpy as np

import logging

import matplotlib.pyplot as plt
logging.basicConfig(filename='datos_historicos.log', level=logging.INFO)
# General parameters to read database
drv = '{Microsoft Access Driver (*.mdb, *.accdb)}'
pwd = 'pw'
mdb = 'c:/Felix/ORA/base_datos/BaseNueva/ora.mdb'

def get_DataFrame(SQL_string):
    cnxn = pyodbc.connect('DRIVER={};DBQ={};PWD={}'.format(drv, mdb, pwd))
    #df0 = pd.read_sql_query(SQL_string, cnxn)
    cursor = cnxn.cursor()
    cursor.execute(SQL_string)

    cols = [c[0] for c in cursor.description]
    df0 = pd.DataFrame.from_records(cursor.fetchall(), columns=cols)
    cnxn.close()

    return df0

def concatena_DF(dfs):
    result = pd.concat(dfs, sort=True)
    result.index.name = 'Fecha'
    result.sort_values(by=['Fecha','IdEstadoPrecip'], kind='mergesort', inplace=True)
    if result.index.has_duplicates:
        idc = np.logical_and(result.index.duplicated(keep='first'), result.IdEstadoPrecip == 7)
        result = result.assign(idc=idc)
        if idc.sum() > 0.:
            result = result[np.logical_not(result.idc.to_numpy())]

    return result


def extraer_precipitacion(df, fecha_i, fecha_f):
    '''
    df = Dataframe from excel file to guide
    '''
    SQL1 = """
            SELECT * FROM DatoDiario
            ORDER by Fecha
            """
    SQL2 = """
            SELECT * FROM DatoInterpolado
            ORDER by Fecha
            """
    df1 = get_DataFrame(SQL1)
    df2 = get_DataFrame(SQL2)
    # Cortamos la tabla en las fechas que necesitamos
    df1 = df1.loc[(df1['Fecha']>=fecha_i) & (df1['Fecha']<=fecha_f)]
    df2 = df2.loc[(df2['Fecha']>=fecha_i) & (df2['Fecha']<=fecha_f)]
    # Trabajamos con el DataFrame del excel guia
    df_precip = {}
    cdatos = {}
    ultimo_reportado = {}
    for row in df.itertuples(index=False):
        id = row.Id
        idtipo = row.IdTipo
        condicion = np.logical_and(df1['Estacion']==id, df1['IdEstadoPrecip']==5)
        df_d = df1[['Fecha', 'Precipitacion', 'IdEstadoPrecip']].loc[condicion].set_index('Fecha')
        condicion = np.logical_and(df2['Estacion'].to_numpy()==id,
                                   df2['nombreCampo'].to_numpy()==1)
        df_i = df2[['Fecha', 'valor']].loc[condicion].set_index('Fecha')
        df_i = df_i.assign(IdEstadoPrecip=7*np.ones(len(df_i)))  #7--> Interpolados
        df_i.rename(columns={'valor': 'Precipitacion'}, inplace=True)
        # Concatenamos Matriz de Datos y de interpolados}
        #if id == 28:
        #    df_d.to_excel('chepes_dato.xlsx')
        #    df_i.to_excel('chepes_int.xlsx')
        frames = [df_d, df_i]
        actual = concatena_DF(frames)
        actual = actual.assign(month=pd.DatetimeIndex(actual.index).month)
        actual = actual.assign(year=pd.DatetimeIndex(actual.index).year)
        actual = actual.fillna(0)
        grupos = actual.groupby(by=[actual.year, actual.month])
        df_precip[row.N_Plot] = grupos['Precipitacion'].sum().values
        cdatos[row.N_Plot] = grupos['IdEstadoPrecip'].apply(cuenta_datos).values
        ultimo_reportado[row.N_Plot] = fecha_ultima_act(actual)
    return df_precip, cdatos, ultimo_reportado

def cuenta_datos(x):
    return np.sum(x==7)

def fecha_ultima_act(df):
    fecha = df.loc[df.IdEstadoPrecip == 5, :]
    try:
        aux = fecha.index.strftime('%d/%m/%Y')
        f1 = aux[-1]
    except:
        f1 = 'No Disp.'
    return f1
