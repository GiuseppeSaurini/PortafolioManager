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

fecha=datetime.today()
fecha_str=str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)

emisiones = importData(table='instrumentos',fecha_base=fecha_str)
emisiones['fecha_vencimiento']=pd.to_datetime(emisiones['fecha_vencimiento'])
emisiones=emisiones[~(emisiones['fecha_vencimiento'].isna())]

#emisiones=emisiones[emisiones['fecha_vencimiento']>datetime.today()]


#Select section
isin = st.sidebar.selectbox(
                    "Selecciona el bono que esta buscando",
                    emisiones.index.values
                    )

flujos=importData(isin,'flujos').sort_values(by='fecha')

bono=Mercado(flujos).getBond(isin) 

fecha_cotizacion=st.sidebar.date_input('Selecciones la fecha de valoracion:',
                                       value=date.today())

fecha_cotizacion=pd.to_datetime(fecha_cotizacion)

cotizacion=st.sidebar.selectbox(
                                    "Selecciona metodo de cotizacion",
                                        ['Precio Dirty',
                                        'Precio Clean',
                                        'Rendimimiento']
                                    )

if(cotizacion=='Precio Dirty'):
    price= st.sidebar.text_input('Precio Dirty:',value='100.00')
    price=pd.to_numeric(price)
    rendimiento=bono.rendimiento(fecha_cotizacion,
                                (price)/100*bono.info['ValorNominal'])

elif(cotizacion=='Precio Clean'):
    price= st.sidebar.text_input('Precio Clean:',value='100.00')
    price=pd.to_numeric(price)
    
    dias_Corridos=bono.diasCorridos(fecha_cotizacion)
    
    interesCorrido=bono.info['TasaCupon']/365*dias_Corridos*100
    
    price_clean=(price+interesCorrido)/100*bono.info['ValorNominal']
    
    
    rendimiento=bono.rendimiento(fecha_cotizacion,
                                 price_clean)

elif(cotizacion=='Rendimimiento'):
    price=st.sidebar.text_input('Rendimimiento',value='0.100')
    price=pd.to_numeric(price)
    rendimiento=price

st.title('Valoración de Bono')

st.write('Datos del instrumento seleccionado')
st.table(bono.info)

st.write('Datos valoración')
st.table(bono.datosValor(rendimiento,fecha_cotizacion))


