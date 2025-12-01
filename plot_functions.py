import numpy as np
import numpy.ma as ma
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import locale
import seaborn as sbn
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib as mpl
from matplotlib.dates import DateFormatter
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU
from matplotlib.ticker import MultipleLocator
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

archivo_historico = './datos/DatosHistoricos.xlsx'

def reordena_medianas(valores,mes):
    medianas = np.empty(13)
    medianas[0] = valores[mes - 1]
    medianas[1:len(valores[mes:12])+1] = valores[mes:12]
    medianas[len(valores[mes:12])+1:] = valores[0:mes]
    return medianas

def get_label_pp(fecha):
    """
    Pequeña funcion que devuelve String del mes, dependiendo de
    imes
    """
    mes = fecha.month
    smes = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago',
            'Sep', 'Oct', 'Nov', 'Dec']
    i_mes = np.empty(13, dtype=np.int64)
    meses = np.arange(0,12)
    i_mes[0] = meses[mes - 1]
    i_mes[1:len(meses[mes:12])+1] = meses[mes:12]
    i_mes[len(meses[mes:12])+1:] = meses[0:mes]
    l_mes = [smes[i] for i in i_mes]
    l_mes[0] = l_mes[0] + '\n' + str(fecha.year - 1)
    l_mes[-1] = l_mes[-1] + '\n' + str(fecha.year)
    return l_mes

def precipitacion_plot_v2(fecha, estacion, datos, cdatos, dest):
    mediana = pd.read_excel(archivo_historico, sheet_name='pp_mediana', index_col=0)
    fhist = pd.read_excel(archivo_historico, sheet_name='pp_fechas', index_col=0)
    yri = fhist.loc[estacion,'f_inicio'].strftime('%Y')
    yrf = fhist.loc[estacion,'f_fin'].strftime('%Y')
    y = reordena_medianas(mediana.loc[estacion,:].to_numpy(), fecha.month)
    l_meses = get_label_pp(fecha)
    print(l_meses)
    # Texto extra  ------------------------------------------------------
    str1 = u'Último reportado: ' + dest['u_act']
    str2 = dest['nombre'] + ', ' + dest['prov'] + '.\n' + 'Datos: ' + dest['tipo']
    # Anchos para trabajar con barras
    width = 0.9
    # -------- Comenzamos la figura ------
    sbn.set(style='ticks', palette='muted', color_codes=True,
            font_scale=0.8)
    my_dpi = 96.
    fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True,
                           sharey=False, facecolor='white', edgecolor='black',
                           figsize=(542/my_dpi, 376/my_dpi), dpi=my_dpi)

    x = np.arange(0, 13)
    # Grafico de Medianas
    label_hist = u'Mediana histórica (' + yri + '-' + yrf + ')'
    ax.plot(x, y, marker='s', ms=4, ls='-.', lw=0.5, color='firebrick',
            label=label_hist, zorder=2)
    ax.bar(x, datos, color='#0991ed', width=width, alpha=.5, edgecolor='black',
           label='Precip. acumuladas', zorder=1)
    # Texto cantidad de interpolados
    cell_text = []
    cell_text.append(['%i' % x_m for x_m in cdatos])
    the_table = ax.table(cellText=cell_text, rowLabels=[u'Días esti-\n mados'],
                         rowColours=[(9./255., 145./255., 237./255., 0.5)],
                         colLabels=l_meses, colLoc='center', cellLoc='center',
                         loc='bottom', bbox=[0, -0.3, 1, 0.275], alpha=0.5)
    the_table.scale(1,2.5)
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(8)
    # Eje X -------------------------------------------------------------
    ax.set_xlim(-0.55, 13 - 0.45)
    ax.set_xticks(x)
    ax.set_xticklabels([])
    ax.tick_params(axis='x', direction='in', bottom=False, top=False)
    ax.tick_params(axis='both', labelsize=10)
    # Eje Y -------------------------------------------------------------
    ax.yaxis.grid(True, linestyle='--', zorder=0)
    ax.set_ylabel('PP (mm)', fontsize=10)
    # Texto
    plt.gcf().text(0.67, 0.90, str1, fontsize=10)
    plt.gcf().text(0.02, 0.91, str2, fontsize=10, fontweight='bold')
    # Seteando posicion del eje -----------------------------------------
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.15,
                     box.width*1.10, box.height * (1.-0.15)])
    ax.legend(loc='best', frameon=True, edgecolor='#000000', prop={'size': 9}, framealpha=0.6)
    return fig, ax

def stat_temp_data(fecha, estacion):
    start = ((fecha - relativedelta(months=1)) - relativedelta(years=1)).replace(day=1)
    end = (fecha + relativedelta(months=1)).replace(day=15)
    aux = pd.date_range(start, end, freq='MS').to_pydatetime()
    xf = [fi.replace(day=15) for fi in aux]
    m0 = (fecha - relativedelta(months=1)).month - 1
    m1 = (fecha + relativedelta(months=1)).month - 1
    tx_mean = pd.read_excel(archivo_historico, sheet_name='tx_mean', index_col=0)
    tx_std = pd.read_excel(archivo_historico, sheet_name='tx_std', index_col=0)
    tm_mean = pd.read_excel(archivo_historico, sheet_name='tm_mean', index_col=0)
    tm_std = pd.read_excel(archivo_historico, sheet_name='tm_std', index_col=0)
    a1 = tx_mean.loc[estacion,:].to_numpy() - tx_std.loc[estacion,:].to_numpy()
    a2 = tx_mean.loc[estacion,:].to_numpy() + tx_std.loc[estacion,:].to_numpy()
    b1 = tm_mean.loc[estacion,:].to_numpy() - tm_std.loc[estacion,:].to_numpy()
    b2 = tm_mean.loc[estacion,:].to_numpy() + tm_std.loc[estacion,:].to_numpy()
    aux = np.tile(a1, 3)
    tx_inf = aux[m0:m0+15]
    aux = np.tile(a2, 3)
    tx_sup = aux[m0:m0+15]
    aux = np.tile(b1, 3)
    tm_inf = aux[m0:m0+15]
    aux = np.tile(b2, 3)
    tm_sup = aux[m0:m0+15]
    return xf, tx_inf, tx_sup, tm_inf, tm_sup

def historical_date(estacion):
    fhist = pd.read_excel(archivo_historico, sheet_name='tx_fechas', index_col=0)
    tx_yri = fhist.loc[estacion,'f_inicio'].strftime('%Y')
    tx_yrf = fhist.loc[estacion,'f_fin'].strftime('%Y')
    fhist = pd.read_excel(archivo_historico, sheet_name='tm_fechas', index_col=0)
    tm_yri = fhist.loc[estacion,'f_inicio'].strftime('%Y')
    tm_yrf = fhist.loc[estacion,'f_fin'].strftime('%Y')
    # Medias mensuales de temperatura
    lb1 = 'Rango normal de Tx (' + tx_yri + '-' + tx_yrf + ')'
    lb2 = 'Rango normal de Tm (' + tm_yri + '-' + tm_yrf + ')'
    return lb1, lb2

def temp_plot(fecha, estacion, x1, tx, x2, tm, dest):
    xf, tx_inf, tx_sup, tm_inf, tm_sup = stat_temp_data(fecha, estacion)
    lim_plot = [xf[0] - relativedelta(months=1), xf[-1] + relativedelta(months=1)]
    lb1, lb2 = historical_date(estacion)
    # Datos Interpolados
    data = ma.getdata(tx)
    mask = ma.getmask(tx)
    tx_i = ma.masked_array(data, mask=np.logical_not(mask))
    data = ma.getdata(tm)
    mask = ma.getmask(tm)
    tm_i = ma.masked_array(data, mask=np.logical_not(mask))
    # Texto extra  ------------------------------------------------------
    str1 = u'Últ. Tx Reportado: ' + dest['utx_act'] + '\n' +\
           u'Últ. Tm Reportado: ' + dest['utm_act']
    str2 = dest['nombre'] + ', ' + dest['prov'] + '.\n' + 'Datos: ' + dest['tipo']
    str3 = lim_plot[0].strftime('%Y')
    str4 = lim_plot[1].strftime('%Y')
    #####################
    # Graficos Actuales
    #####################
    sbn.set(style='ticks', palette='muted', color_codes=True,
            font_scale=0.8)
    my_dpi = 96.
    fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True,
                           sharey=False, facecolor='white',
                           figsize=(542/my_dpi, 376/my_dpi), dpi=my_dpi)
    ax.plot(x1, tx, ls='-', lw=0.7, color='firebrick', label=u'Temp. máxima (Tx)', zorder=2)
    ax.plot(x2, tm, ls='-', lw=0.7, color='#0991ed', label=u'Temp. mínima (Tm)', zorder=2)
    #ax.plot(x1, tx_i, ls='dotted', lw=0.7, color='firebrick', label='_nolegend_', zorder=2)
    #ax.plot(x2, tm_i, ls='dotted', lw=0.7, color='#0991ed', label='_nolegend_', zorder=2)
    # Linea de 0ºC y 40ºC
    ax.plot(lim_plot, [0, 0], ls='-', lw=1, color='#000000', zorder=1)
    #ax.plot(lim_plot, [40, 40], ls='-', lw=1, color='#000000' , zorder=1)
    ax.fill_between(xf, tx_inf, tx_sup, facecolor='firebrick', alpha=.2, zorder=0,
                    label=lb1)
    ax.fill_between(xf, tm_inf, tm_sup, facecolor='#0991ed', alpha=.2, zorder=0,
                    label=lb2)
    # Ejes Grafico ------------------------------------------------------
    #ax.axhline(y=0, linewidth=1, color='#000000')
    #ax.axhline(y=40, linewidth=1, color='#000000')
    #ax.axvline(linewidth=0.5)
    # Eje X -------------------------------------------------------------
    locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
    ax.set_xlim(lim_plot)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.tick_params(axis='x', labelsize=10, direction='in')
    # Eje Y -------------------------------------------------------------
    ax.yaxis.grid(True, linestyle='--', which='both')
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.set_ylabel('Temperatura (ºC)', fontsize=10)
    # Texto extra  ------------------------------------------------------
    plt.gcf().text(0.66, 0.02, str1, fontsize=9.5)
    plt.gcf().text(0.1, 0.022, str2, fontsize=9.5)
    plt.gcf().text(0.13, 0.12, str3, fontsize=9.5)  # Definido
    plt.gcf().text(0.92, 0.12, str4, fontsize=9.5)
    # Seteando posicion del eje -----------------------------------------
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width*1.10, box.height * 0.9])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.18), ncol=2,
              frameon=True, edgecolor='#000000', prop={'size': 8.5})
    return fig, ax





def precipitacion_plot(fecha, estacion, datos, cdatos,
                       freport='', nest='', prov='', tipo=''):
    mediana = pd.read_excel(archivo_historico, sheet_name='pp_mediana', index_col=0)
    fhist = pd.read_excel(archivo_historico, sheet_name='pp_fechas', index_col=0)
    yri = fhist.loc[estacion,'f_inicio'].strftime('%Y')
    yrf = fhist.loc[estacion,'f_fin'].strftime('%Y')
    y = reordena_medianas(mediana.loc[estacion,:].to_numpy(), fecha.month)
    l_meses = get_label_pp(fecha)
    # Texto extra  ------------------------------------------------------
    str1 = u'Último reportado: ' + freport
    str2 = nest + ', ' + prov + '.\n' + 'Datos: ' + tipo
    # -------- Comenzamos la figura ------
    sbn.set(style='ticks', palette='muted', color_codes=True,
            font_scale=0.8)
    my_dpi = 96.
    fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True,
                           sharey=False, facecolor='white',
                           figsize=(542/my_dpi, 376/my_dpi), dpi=my_dpi)

    x = np.arange(0, 13)
    # Grafico de Medianas
    label_hist = u'Mediana histórica (' + yri + '-' + yrf + ')'
    ax.plot(x, y, marker='s', ms=4, ls='-.', lw=0.5, color='firebrick',
            label=label_hist, zorder=2)
    ax.bar(x, datos, color='#0991ed', width=0.9, alpha=.5, edgecolor='black',
           label='Precipitaciones actuales acumuladas', zorder=1)
    # Texto cantidad de interpolados
    for xi, dato, conteo in zip(x, datos, cdatos):
        if conteo > 0 and dato > 5.:
            ax.text(xi, 0.95*dato, str(conteo), ha='center', va='top')
        elif conteo > 0 and dato <5.:
            ax.text(xi, 10, str(conteo), ha='center', va='top')
    # Eje X -------------------------------------------------------------
    ax.set_xlim([-1, 13])
    ax.set_xticks(x)
    ax.set_xticklabels(l_meses)
    ax.tick_params(axis='both', labelsize=10)
    # Eje Y -------------------------------------------------------------
    ax.yaxis.grid(True, linestyle='--', zorder=0)
    ax.set_ylabel('PP (mm)', fontsize=10)
    # Texto
    plt.gcf().text(0.67, 0.02, str1, fontsize=10)
    plt.gcf().text(0.05, 0.01, str2, fontsize=10)
    # Seteando posicion del eje -----------------------------------------
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                     box.width, box.height * 0.9])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2,
              frameon=True, edgecolor='#000000', prop={'size': 10})
    return fig, ax
