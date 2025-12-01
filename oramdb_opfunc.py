import pyodbc
import pandas as pd
import numpy as np

import logging
# General parameters to read database
from funciones_auxiliares import parse_config

config = parse_config('./config_database.txt')
drv = config.get('drv')
pwd = config.get('pwd')
mdb = config.get('mdb')


def pp_sql_string(id, idtipo, fecha_i, fecha_f, idemp=None):
    """
    This function generate the strings to get data from the
    database of ORA (ora.mdb)
    """
    SQL_pp = '''
            SELECT Fecha, Precipitacion, IdEstadoPrecip FROM DatoDiario
            WHERE Estacion = {}
            AND (((DatoDiario.Fecha)>=#{}#))
            AND (((DatoDiario.Fecha)<=#{}#))
            ORDER BY Fecha
            '''.format(id, fecha_i, fecha_f)
    SQL_ipp = '''
            SELECT Fecha, Valor FROM DatoInterpolado
            WHERE Estacion = {}
            AND (((DatoInterpolado.Fecha)>=#{}#))
            AND (((DatoInterpolado.Fecha)<=#{}#))
            AND (((DatoInterpolado.nombreCampo)=1))
            ORDER BY Fecha
            '''.format(id, fecha_i, fecha_f)
    if idemp is not None:
        SQL_epp = '''
                SELECT Fecha, Precipitacion, IdEstadoPrecip FROM DatoDiario
                WHERE Estacion = {}
                AND (((DatoDiario.Fecha)>=#{}#))
                AND (((DatoDiario.Fecha)<=#{}#))
                ORDER BY Fecha
                '''.format(idemp, fecha_i, fecha_f)
        return SQL_pp, SQL_ipp, SQL_epp
    else:
        return SQL_pp, SQL_ipp
