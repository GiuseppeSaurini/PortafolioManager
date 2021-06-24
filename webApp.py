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
from Mercados import Mercado,importData
from datetime import datetime,date


#Definision de instrumentos
emisiones = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/emisiones.xlsx')
emisiones['fecha_vencimiento']=pd.to_datetime(emisiones['fecha_vencimiento'])
emisiones=emisiones[~(emisiones['fecha_vencimiento'].isna())]
emisiones=emisiones[emisiones['fecha_vencimiento']>datetime.today()]

isin = st.selectbox(
                    "Selecciona el bono que esta buscando",
                    emisiones.loc[:,'isin'].values
                    
                    )


mercado=Mercado(importData(isin,'flujos'),
                operaciones=importData(isin,'operaciones'))  
bono=mercado.getBond(isin) 

st.table(bono.info)

price= st.number_input('Valoriza el bono:',value=100)
rendimiento=bono.rendimiento(datetime.today(),bono.info['ValorNominal'])
st.table(rendimiento)


