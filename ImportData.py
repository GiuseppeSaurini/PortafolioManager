# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 16:03:23 2021

@author: Investor
"""

#ImportData.py

# Cargar las librería de python data analysis
import pandas as pd 
#import numpy as np
#from datetime import datetime, timedelta
#import os
import requests
import json


def importData(isin=None,table='instrumentos',fecha_base=''):
    #API Datawharehousing url y contraseña
    url_DWH='https://data.marketdata.com.py/api/v1/'
    key='?api_key=Tp1u3Wb0y2X31w4ZMjcRxAldlpHjC8hy'
    
    #Definir que tabla se busca
    query=url_DWH+table+key
    
    #Carga de filtros
    query=query+('&isin='+isin if isin!=None else '') 
    query=query+('&fecha_vencimiento_mt='+fecha_base)
   
    #importar los datos
    data=json.loads(requests.get(query).text)
    df=pd.json_normalize(data,sep='/')
    
    #ajustes de datos
    df=df.replace('None','')
    for c in df.columns:
        if(c[:12]=='instrumento/'):
            df=df.rename(columns={c:c[12:]})
    df['fecha_colocacion']=pd.to_datetime(df['fecha_colocacion'])
    df['fecha_vencimiento']=pd.to_datetime(df['fecha_vencimiento'])
    df['valor_nominal']=pd.to_numeric(df['valor_nominal'])
    
    if(table=='operaciones'):
        df['fecha_operacion']=pd.to_datetime(df['fecha_operacion'])
    elif (table=='flujos'):
        df['fecha']=pd.to_datetime(df['fecha'])
    
    for row in df.itertuples():
        df.loc[row.Index,'simbolo_emisor']=row.isin[2:5]
    
    #definir el la columna de index
    if(table=='instrumentos'):
        df=df.set_index('isin')
    else:
        df=df.set_index('id')
        
    return df

