import time
import os
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from class_operativa import class_operativa
from plot_functions import precipitacion_plot_v2, temp_plot
import sys


# Parametros de entrada
fecha = sys.argv[1]
#fecha = '21-04-2021'

# ------------------------------------
# Aca comienza el codigo
# Codigo para generar los graficos
# ------------------------------------

def get_data_estacion(nest):
    dest = pd.read_excel('./historicos/Estaciones_Seguimiento_PP_T.xlsx')
    nombre = dest.loc[dest.N_Plot == nest, 'Nombre' ].values
    provincia = dest.loc[dest.N_Plot == nest, 'Prov' ].values
    tipo_est = dest.loc[dest.N_Plot == nest, 'IdTipo'].values
    id = dest.loc[dest.N_Plot == nest, 'Id'].values
    return nombre[0], provincia[0], tipo_est[0], str(id[0])

from plot_functions import stat_temp_data
# $$$ Initial data to work
start = time.time()
f_dt = dt.datetime.strptime(fecha, '%d-%m-%Y')

carpeta_figuras = './figuras/'
os.makedirs(carpeta_figuras, exist_ok=True)

print(' --- Generando datos para seguimiento ---')
print(' --- para la fecha: ' + fecha + ' ---')
a = class_operativa(fecha)
# Fechas iniciales y finales para seguimiento
te1 = a.fecha_ini_t.strftime('%d-%m-%Y')
pp1 = a.fecha_ini_pp.strftime('%d-%m-%Y')
te2 = a.fecha_final.strftime('%d-%m-%Y')


print(' --- Periodo seguimiento temp: ', te1, ' hasta ', te2)
print(' --- Graficando seguimientos de temperatura ---')


for estacion in a.temp_estaciones:
    dest = {}
    tx = a.tx[estacion]
    tx_fecha = a.tx_fecha[estacion]
    dest['utx_act'] = a.tx_uact[estacion]
    tm = a.tm[estacion]
    tm_fecha = a.tm_fecha[estacion]
    dest['utm_act'] = a.tm_uact[estacion]
    nest, prov, tipo, id = get_data_estacion(estacion)
    dest['nombre'] = nest
    dest['prov'] = prov
    dest['tipo'] = tipo
    fig, ax = temp_plot(f_dt, estacion, tx_fecha, tx, tm_fecha, tm, dest)
    fig.savefig('./figuras/t_' + id + '.jpg')
    plt.close(fig)

print(' --- Periodo seguimiento pp acum: ', pp1, ' hasta ', te2)
print(' --- Graficando seguimientos de precipitaciones ---')


for estacion in a.pp_estaciones:
    dest = {}
    datos = a.pp_actuales[estacion]
    cdatos = a.pp_conteo[estacion]
    dest['u_act'] = a.ult_act[estacion]
    nest, prov, tipo, id = get_data_estacion(estacion)
    dest['nombre'] = nest
    dest['prov'] = prov
    dest['tipo'] = tipo
    fig, ax = precipitacion_plot_v2(a.fecha_final, estacion, datos, cdatos, dest)
    f_act = 'Actualizado el: ' + f_dt.strftime('%d/%m/%Y')
    fig.text(0.67, 0.95, f_act, fontsize=10)
    fig.savefig('./figuras/pp_' + id + '.jpg')
    plt.close(fig)

#estacion = 'chepes'
#datos = a.pp_actuales[estacion]
#cdatos = a.pp_conteo[estacion]
#print(datos)


print(' --- Fin del script ---')
# ---------------------------
end = time.time()
print('Tiempo demora script: ', np.round((end - start)/60,2), ' minutos.')
