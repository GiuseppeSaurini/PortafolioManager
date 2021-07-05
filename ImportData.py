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
    query=query+('&isin='+isin if isin!=None else '')
    
    if(table=='instrumentos'):
        #Carga de filtros
        query=query+('&fecha_vencimiento_mt='+fecha_base)
        
        #importar los datos
        data=json.loads(requests.get(query).text)
        df=pd.json_normalize(data,sep='/')
        
        #eliminar datos None
        df=df.replace('None','')
        #definir el la columna de index
        df=df.set_index('isin')
    
    elif(table=='operaciones'):
        query=query+('&fecha_operacion_from='+fecha_base)
        #importar los datos
        data=json.loads(requests.get(query).text)
        df=pd.json_normalize(data,sep='/')
        
        #eliminar datos None
        df=df.replace('None','')
        
        for c in df.columns:
            if(c[:12]=='instrumento/'):
                df=df.rename(columns={c:c[12:]})
        
        df['fecha_operacion']=pd.to_datetime(df['fecha_operacion'])
        #definir el la columna de index
        df=df.set_index('id')
       
    elif (table=='flujos'):
        query=query+('&fecha_operacion_from='+fecha_base)
        #importar los datos
        data=json.loads(requests.get(query).text)
        df=pd.json_normalize(data,sep='/')
        
        #eliminar datos None
        df=df.replace('None','')
        
        for c in df.columns:
            if(c[:12]=='instrumento/'):
                df=df.rename(columns={c:c[12:]})
        
        df['fecha']=pd.to_datetime(df['fecha'])
        #definir el la columna de index
        df=df.set_index('id')
    
    df['fecha_colocacion']=pd.to_datetime(df['fecha_colocacion'])
    df['fecha_vencimiento']=pd.to_datetime(df['fecha_vencimiento'])
    df['valor_nominal']=pd.to_numeric(df['valor_nominal'])
    
    for row in df.itertuples():
        if(df.loc[row.Index,'simbolo_emisor']==''):    
            df.loc[row.Index,'simbolo_emisor']=row.isin[2:5]
        if(row.moneda!='pyg' or row.moneda!='usd'):
            if(row.moneda[0]=='D'):
                df.loc[row.Index,'moneda']=='usd'
            else:
                df.loc[row.Index,'moneda']=='pyg'
        
    return df

