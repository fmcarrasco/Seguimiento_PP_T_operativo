import pyodbc
import pandas as pd
import numpy as np
import numpy.ma as ma
import logging
from funciones_auxiliares import parse_config
import matplotlib.pyplot as plt
logging.basicConfig(filename='datos_historicos.log', level=logging.INFO)
# General parameters to read database
config = parse_config('./config_database.txt')
drv = config.get('drv')
pwd = config.get('pwd')
mdb = config.get('mdb')

def get_SQL_strings(temp='tmax'):
    if temp == 'tmax':
        SQL1 = """
                SELECT Fecha, Estacion, Tmax FROM DatoDiarioSMN
                ORDER by Fecha
                """
        SQL2 = """
                SELECT Fecha, Estacion, TempAbrigo150Max FROM DatoDiarioINTA
                ORDER by Fecha
                """
        SQL3 = """
                SELECT * FROM DatoInterpolado
                ORDER by Fecha
                """
    else:
        SQL1 = """
                SELECT Fecha, Estacion, Tmin FROM DatoDiarioSMN
                ORDER by Fecha
                """
        SQL2 = """
                SELECT Fecha, Estacion, TempAbrigo150Min FROM DatoDiarioINTA
                ORDER by Fecha
                """
        SQL3 = """
                SELECT * FROM DatoInterpolado
                ORDER by Fecha
                """

    return SQL1, SQL2, SQL3


def get_DataFrame(SQL_string):
    cnxn = pyodbc.connect('DRIVER={};DBQ={};PWD={}'.format(drv, mdb, pwd))
    cursor = cnxn.cursor()
    cursor.execute(SQL_string)

    cols = [c[0] for c in cursor.description]
    df0 = pd.DataFrame.from_records(cursor.fetchall(), columns=cols)
    cnxn.close()
    return df0

def concatena_DF(dfs):
    result = pd.concat(dfs, sort=True)
    result.index.name = 'Fecha'
    result.sort_values(by=['Fecha','IdEstado'], kind='mergesort', inplace=True)
    if result.index.has_duplicates:
        idc = np.logical_and(result.index.duplicated(keep='first'), result.IdEstado == 7)
        result = result.assign(idc=idc)
        if idc.sum() > 0.:
            result = result[np.logical_not(result.idc.to_numpy())]

    return result


def extraer_temp(df, fecha_i, fecha_f, temp='tmax'):
    '''
    df = Dataframe from excel file to guide
    '''
    if temp == 'tmax':
        nc = 2
        nvar = 'Tmax'
        nvarINTA = 'TempAbrigo150Max'
    else:
        nc = 3
        nvar = 'Tmin'
        nvarINTA = 'TempAbrigo150Min'
    SQL1, SQL2, SQL3 = get_SQL_strings(temp)
    df1 = get_DataFrame(SQL1) # Datos de SMN
    df2 = get_DataFrame(SQL2) # Datos de INTA
    df3 = get_DataFrame(SQL3) # Datos Interpolados
    # Cortamos la tabla en las fechas que necesitamos
    df1 = df1.loc[(df1['Fecha']>=fecha_i) & (df1['Fecha']<=fecha_f)]
    df2 = df2.loc[(df2['Fecha']>=fecha_i) & (df2['Fecha']<=fecha_f)]
    df3 = df3.loc[(df3['Fecha']>=fecha_i) & (df3['Fecha']<=fecha_f)]
    # Trabajamos con el DataFrame del excel guia
    df_temp = {}
    df_fecha = {}
    ultimo_reportado = {}
    for row in df.itertuples(index=False):
        id = row.Id
        idtipo = row.IdTipo
        if ('SMN' in idtipo) or ('Privado' in idtipo):
            condicion = df1['Estacion']==id
            df_d = df1[['Fecha', nvar]].loc[condicion].set_index('Fecha')
            df_d.dropna(inplace=True)
        elif 'INTA' in idtipo:
            condicion = df2['Estacion']==id
            df_d = df2[['Fecha', nvarINTA]].loc[condicion].set_index('Fecha')
            df_d.rename(columns={nvarINTA: nvar}, inplace=True)
            df_d.dropna(inplace=True)
        else:
            continue
        df_d = df_d.assign(IdEstado=5*np.ones(len(df_d))) # 5 --> Observados
        condicion = np.logical_and(df3['Estacion'].to_numpy()==id,
                                   df3['nombreCampo'].to_numpy()==nc)
        df_i = df3[['Fecha', 'valor']].loc[condicion].set_index('Fecha')
        df_i = df_i.assign(IdEstado=7*np.ones(len(df_i)))  #7--> Interpolados
        df_i.rename(columns={'valor': nvar}, inplace=True)
        # Concatenamos Matriz de Datos y de interpolados
        frames = [df_d, df_i]
        actual = concatena_DF(frames)
        vtemp = actual[nvar].to_numpy()
        mask = actual['IdEstado'].to_numpy() == 7
        df_temp[row.N_Plot] = ma.masked_array(vtemp, mask=mask)
        df_fecha[row.N_Plot] = actual.index.to_pydatetime()
        ultimo_reportado[row.N_Plot] = fecha_ultima_act(actual)
    return df_temp, df_fecha, ultimo_reportado

def fecha_ultima_act(df):
    fecha = df.loc[df.IdEstado == 5, :]
    try:
        aux = fecha.index.strftime('%d/%m/%Y')
        f1 = aux[-1]
    except:
        f1 = 'No Disp.'
    return f1
