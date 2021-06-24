# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 15:21:10 2021

@author: DELL
"""


#webApp.py

import streamlit as st
import pandas as pd
import requests
import json
from Mercados import Mercado
from ImportData import importData
from datetime import datetime,timedelta,date


#Definision de instrumentos
emisiones = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/emisiones.xlsx')
emisiones['fecha_vencimiento']=pd.to_datetime(emisiones['fecha_vencimiento'])
emisiones=emisiones[~(emisiones['fecha_vencimiento'].isna())]
emisiones=emisiones[emisiones['fecha_vencimiento']>datetime.today()]

#Select section
isin = st.sidebar.selectbox(
                    "Selecciona el bono que esta buscando",
                    emisiones.loc[:,'isin'].values
                    )
flujos=importData(isin,'flujos').sort_values(by='fecha')

bono=Mercado(flujos).getBond(isin) 

fecha_cotizacion=st.sidebar.date_input('Selecciones la fecha de valoracion:')
fecha_cotizacion=pd.to_datetime(date.today())

price= st.sidebar.number_input('Precio Dirty:',value=100)

rendimiento=bono.rendimiento(fecha_cotizacion,
                             (price)/100*bono.info['ValorNominal'])

st.title('Caotizador de Instrumentos Bursatiles')

st.write('Datos del instrumento seleccionado')
st.table(bono.info)

st.write('Datos valoración')
st.table(bono.datosValor(rendimiento,fecha_cotizacion))


