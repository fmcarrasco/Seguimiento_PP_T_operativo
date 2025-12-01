import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
from ppora_mdb import extraer_precipitacion
from tempora_mdb import extraer_temp
#from mdb_tmin import extraer_tmin

class class_operativa:
    def __init__(self, fecha):
        self.archivo_guia = './datos/Estaciones_Seguimiento_PP_T.xlsx'
        self.fecha = fecha
        self.fecha_final = dt.datetime.strptime(fecha, '%d-%m-%Y') - dt.timedelta(days=1)
        self.fecha_ini_pp = dt.datetime(self.fecha_final.year-1, self.fecha_final.month,1)
        self.fecha_ini_t = self.fecha_final - relativedelta(years=1)
        self.get_precip_data()  # Obtenemos los datos
        self.get_temp_data()  # Calculamos datos de Tmax

    def get_precip_data(self):
        df = pd.read_excel(self.archivo_guia)
        actuales, conteos, f_repo = extraer_precipitacion(df, self.fecha_ini_pp, self.fecha_final)
        self.pp_estaciones = list(actuales.keys())
        self.pp_actuales = actuales
        self.pp_conteo = conteos
        self.ult_act = f_repo

    def get_temp_data(self):
        df = pd.read_excel(self.archivo_guia)
        actuales, tx_fecha, tx_repo = extraer_temp(df, self.fecha_ini_t, self.fecha_final)
        self.tx = actuales
        self.tx_uact = tx_repo
        self.tx_fecha = tx_fecha
        actuales, tm_fecha, tm_repo = extraer_temp(df, self.fecha_ini_t, self.fecha_final, 'tmin')
        self.tm = actuales
        self.tm_fecha = tm_fecha
        self.tm_uact = tm_repo
        self.temp_estaciones = list(actuales.keys())
