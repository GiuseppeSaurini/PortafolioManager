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

st.title('Valoración de Bono')

#Definision de instrumentos

fecha=datetime.today()
fecha_str=str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)

emisiones = importData(table='instrumentos',fecha_base=fecha_str)
emisiones['fecha_vencimiento']=pd.to_datetime(emisiones['fecha_vencimiento'])
emisiones=emisiones[~(emisiones['fecha_vencimiento'].isna())]


#Select section
isin = st.sidebar.selectbox(
                    "Selecciona el bono que esta buscando",
                    emisiones.index.values
                    )

flujos=importData(isin,'flujos').sort_values(by='fecha')

bono=Mercado(flujos).getBond(isin) 

#Infomacion del instrumento seleccionado
st.write('Datos del instrumento seleccionado')
st.table(bono.info)

#Datos de cotizacion del Bono
fecha_cotizacion=st.sidebar.date_input('Selecciones la fecha de valoracion:',
                                       value=date.today())

fecha_cotizacion=pd.to_datetime(fecha_cotizacion)

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

    valorActualNeto=(price)/100*bono.info['ValorNominal']

    rendimiento=bono.rendimiento(fecha_cotizacion,
                                valorActualNeto)

elif(metodo_cotizacion=='Precio Clean'):
    price= st.sidebar.text_input('Precio Clean:',value='100.00')
    price=pd.to_numeric(price)
    
    dias_Corridos=bono.diasCorridos(fecha_cotizacion)
    
    interesCorrido=bono.info['TasaCupon']/365*dias_Corridos*100
    
    valor_clean=(price+interesCorrido)/100*bono.info['ValorNominal']
    
    rendimiento=bono.rendimiento(fecha_cotizacion,
                                 valor_clean)

elif(metodo_cotizacion=='Precio Base'):
    price_base= st.sidebar.text_input('Precio Base:',value='100.00')
    price_base=pd.to_numeric(price_base)
    dias_Corridos=bono.diasCorridos(fecha_cotizacion)
    nueva_fecha_cotizacion=fecha_cotizacion-timedelta(days=dias_Corridos)
    valor_base=price_base/100*bono.info['ValorNominal']
    rendimiento=bono.rendimiento(nueva_fecha_cotizacion,valor_base)
    

elif(metodo_cotizacion=='Rendimimiento(TIR)'):
    price=st.sidebar.text_input('Rendimimiento',value='0.100')
    price=pd.to_numeric(price)
    rendimiento=price



st.write('Datos valoración')
st.table(bono.datosValor(rendimiento,fecha_cotizacion))


