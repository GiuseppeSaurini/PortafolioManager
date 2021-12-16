# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 15:21:10 2021

@author: DELL_Giuseppe
"""


#webApp.py

import streamlit as st
import pandas as pd
import requests
import json
from Mercados import Bono
from ImportData import *
from datetime import datetime,timedelta,date
import numpy as np

st.set_page_config(
    page_title='Cotizacion_Bonos',
    page_icon='chart_with_upwards_trend',
    layout='wide',
    initial_sidebar_state='auto',
    #menu_items=None
    )

st.title('Valoración de Bono')

#Definision de instrumentos
#Fecha predeterminada
fecha=datetime.today()
fecha_str=str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)

#Importar los instrumentos de MarketData
emisiones = get_instrumentos(fecha_base=fecha_str)
emisiones['fecha_vencimiento']=pd.to_datetime(emisiones['fecha_vencimiento'])
emisiones=emisiones[~(emisiones['fecha_vencimiento'].isna())]

#Select section
isin = st.sidebar.selectbox(
                    "Selecciona el bono que esta buscando",
                    emisiones.index.values
                    )

#importar flujo del instrumento seleccionado
bono=Bono(isin,importData(isin,table='flujos').sort_values(by='fecha'))


#Datos de cotizacion del Bono
fecha_cotizacion=st.sidebar.date_input('Selecciones la fecha de valoracion:',
                                       value=date.today())


fecha_cotizacion=pd.to_datetime(fecha_cotizacion)

#Seleccion de metodo de valoracion del Bono 
metodo_cotizacion=st.sidebar.selectbox(
                                    "Selecciona metodo de cotizacion",
                                        ['Precio Dirty',
                                        'Precio Clean',
                                        'Precio Base',
                                        'Rendimimiento(TIR)']
                                    )

if(metodo_cotizacion=='Precio Dirty'):
    price= st.sidebar.text_input('Precio Dirty:',value='100.00')
    price=pd.to_numeric(price)

    valor=(price)/100*bono.info['ValorNominal']

    rendimiento=bono.rendimiento(fecha_cotizacion,valor)

elif(metodo_cotizacion=='Precio Clean'):
    price= st.sidebar.text_input('Precio Clean:',value='100.00')
    price=pd.to_numeric(price)
    
    dias_Corridos=bono.diasCorridos(fecha_cotizacion)
    
    interesCorrido=bono.info['TasaCupon']/365*dias_Corridos*100
    
    valor=(price+interesCorrido)/100*bono.info['ValorNominal']
    
    rendimiento=bono.rendimiento(fecha_cotizacion,valor)

elif(metodo_cotizacion=='Precio Base'):
    price_base= st.sidebar.text_input('Precio Base:',value='100.00')
    price_base=pd.to_numeric(price_base)
    dias_Corridos=bono.diasCorridos(fecha_cotizacion)
    nueva_fecha_cotizacion=fecha_cotizacion-timedelta(days=dias_Corridos)
    valor=price_base/100*bono.info['ValorNominal']
    
    rendimiento=bono.rendimiento(nueva_fecha_cotizacion,valor)

elif(metodo_cotizacion=='Rendimimiento(TIR)'):
    price=st.sidebar.text_input('Rendimimiento',value='0.100')
    price=pd.to_numeric(price)
    rendimiento=price
    
    price=bono.valorActual(rendimiento,fecha_cotizacion)/bono.info['ValorNominal']*100

#Igresa la cantidad de Bonos a ser Cotizados
cantidad= st.sidebar.number_input('Cantidad a cotizar',value=0)

#Tabla de Valoracion del Bono
st.write('Datos valoración')
valoracion=bono.datosValor(rendimiento,fecha_cotizacion)

col1, col2, col3, col4 = st.columns(4)


# 'simbolo':self.isin[2:5],
# 'Emisor':flujo['emisor/nombre'].values[0],
# 'Tipo_Instrumento':flujo['tipo_instrumento'].values[0],
# 'Moneda':flujo['moneda'].values[0],
# 'Fecha_Emision':flujo['fecha_colocacion'].values[0],
# 'Fecha_Vencimiento':self.flujo['fecha'].max(),
# 'ValorNominal':self.flujo['amortizacion'].sum(),
# 'TasaCupon':flujo['tasa_interes'].values[0]

col1.metric('Emisor',bono.info['Emisor'])
col2.metric('Instrumento',bono.info['Tipo_Instrumento'])
col3.metric('Moneda',bono.info['Moneda'])
col4.metric('Tasa Cupon',str(np.around(bono.info['TasaCupon']*100,2))+'%')


col5, col6, col7, col8 = st.columns(4)

col5.metric('Rendimiento',str(np.around(valoracion['Rendimiento']*100,2))+'%')
col6.metric('Precio Dirty',str(np.around(valoracion['PrecioDirty'],4)))
col7.metric('Precio Clean',str(np.around(valoracion['PrecioClean'],4)))
col8.metric('Precio Base',str(np.around(valoracion['PrecioUltimoCupon'],4)))


volumen_Cotizacion=price/100*bono.info['ValorNominal']*cantidad

st.metric('Volumen Cotizado',np.around(volumen_Cotizacion,0))