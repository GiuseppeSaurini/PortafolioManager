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
#Fecha predeterminada
fecha=datetime.today()
fecha_str=str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)

#Importar los instrumentos de MarketData
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

st.table(valoracion)

volumen_Cotizacion=price/100*bono.info['ValorNominal']*cantidad

volumen_Cotizacion