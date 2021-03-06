# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 16:03:23 2021

@author: Giuseppe
"""

#ImportData.py

# Cargar las librería de python data analysis
import pandas as pd 
import numpy as np
from datetime import datetime, timedelta
import os
import requests
import json

class MarketDataAPI():
    
    def get_instrumentos(isin='',fecha_base=''):
        #API Datawharehousing url y contraseña
        url_DWH='https://data.marketdata.com.py/api/v1/'
        key='?api_key='+os.environ.get('MD_API_KEY')
        
        #Definir que tabla se busca
        query=url_DWH+'instrumentos/list'+key
        
        #Filtrar por isin    
        query=query+'&isin='+isin
        
        #Carga de filtros fecha
        query=query+('&fecha_vencimiento_mt='+fecha_base)
        
        #importar los datos
        data=json.loads(requests.get(query).text)
        df=pd.json_normalize(data,sep='/')
        
        #eliminar datos None
        df=df.replace('None','')
        #definir el la columna de index
        df=df.set_index('isin')
        
        df['fecha_colocacion']=pd.to_datetime(df['fecha_colocacion'])
        df['fecha_vencimiento']=pd.to_datetime(df['fecha_vencimiento'])
        df['valor_nominal']=pd.to_numeric(df['valor_nominal'])
        
        #transformar a valor numerico [monto_serie,
        
        return df
        
    def importData(isin='',table='instrumentos/list',fecha_base=''):
        #API Datawharehousing url y contraseña
        
        url_DWH='https://data.marketdata.com.py/api/v1/'
        key='?api_key='+os.environ.get('MD_API_KEY')
        
        #Definir que tabla se busca
        query=url_DWH+table+key
        
        #Filtrar por isin    
        query=query+'&isin='+isin
        
        #Carga de filtros fecha
        query=query+('&fecha_vencimiento_mt='+fecha_base)
        if(table=='operaciones'):
            query=query+('&fecha_operacion_from='+fecha_base)    
        
        #importar los datos
        data=json.loads(requests.get(query).text)
        df=pd.json_normalize(data,sep='/')
        
        #eliminar datos None
        df=df.replace('None','')
          
        #Desglosar instrumento
        for c in df.columns:
            if(c[:12]=='instrumento/'):
                df=df.rename(columns={c:c[12:]})
        #Desglose simbolo_emisor
        for c in df.columns:
            if(c[:15]=='simbolo_emisor/'):
                df=df.rename(columns={c:c[15:]})
              
        #Ajustes condicionales
        if(table=='instrumentos/list'):
            #definir el la columna de index
            df=df.set_index('isin')
            
        elif(table=='operaciones'):
            df['fecha_operacion']=pd.to_datetime(df['fecha_operacion'])
            
           
        elif (table=='flujos'):
            df['fecha']=pd.to_datetime(df['fecha'])
     
        
        df['fecha_colocacion']=pd.to_datetime(df['fecha_colocacion'])
        df['fecha_vencimiento']=pd.to_datetime(df['fecha_vencimiento'])
        df['valor_nominal']=pd.to_numeric(df['valor_nominal'])
        
        for row in df.itertuples():
            # if(table!='instrumentos'):
            #     if(df.loc[row.Index,'simbolo_emisor']==''):    
            #         df.loc[row.Index,'simbolo_emisor']=row.isin[2:5]
                    
            if(row.moneda!='pyg' or row.moneda!='usd'):
                try:
                    if(row.moneda[0]==''):
                        df.loc[row.Index,'moneda']=='usd'
                    else:
                        df.loc[row.Index,'moneda']=='pyg'
                except:
                    pass
                
            
        return df
    
    def get_value(isin,rendimiento,fechaValor,cantidad=1):
        #API Datawharehousing url y contraseña
        url_DWH='https://data.marketdata.com.py/api/v1/'
        key='?api_key='+os.environ.get('MD_API_KEY')
        
        #Definir que tabla se busca
        query=url_DWH+'cotizador'+key
        
        #Filtrar por isin    
        query=query+'&isin='+isin
        
        #Carga de fecha valoracion
        query=query+('&fecha_valoracion='+fechaValor)
        #Cargar metodo
        query=query+('&metodo_cotizacion=rendimiento')
        #Cargar rendimieneto
        query=query+('&rendimiento='+str(rendimiento))
        
        query=query+('&cantidad='+str(cantidad))
        
        #importar los datos
        data=json.loads(requests.get(query).text)
        df=pd.json_normalize(data,sep='/')
        
        #eliminar datos None
        df=df.replace('None','')  
        
        return df
    
    def get_operaciones(isin='',fecha_base='2021-1-1'):
        #API Datawharehousing url y contraseña
        
        url_DWH='https://data.marketdata.com.py/api/v1/'
        key='?api_key='+os.environ.get('MD_API_KEY')
        
        #Definir que tabla se busca
        query=url_DWH+'operasiones'+key
        
        #Filtrar por isin    
        query=query+'&isin='+isin
        
        query=query+'&fecha_operacion_from='+fecha_base
        
        #importar los datos
        data=json.loads(requests.get(query).text)
        df=pd.json_normalize(data,sep='/')
        
        #eliminar datos None
        df=df.replace('None','')
        
        return df
    
    def get_flujos(isin=''):
        #API Datawharehousing url y contraseña
        
        url_DWH='https://data.marketdata.com.py/api/v1/'
        key='?api_key='+os.environ.get('MD_API_KEY')
        
        #Definir que tabla se busca
        query=url_DWH+'flujos'+key
        
        #Filtrar por isin    
        query=query+'&isin='+isin    
        
        #importar los datos
        data=json.loads(requests.get(query).text)
        df=pd.json_normalize(data,sep='/')
        
        #eliminar datos None
        df=df.replace('None','')
        
        #simplificar columnas instrumento
        for c in df.columns:
            if(c[:12]=='instrumento/'):
                df=df.rename(columns={c:c[12:]})
        #Desglose simbolo_emisor
        for c in df.columns:
            if(c[:15]=='simbolo_emisor/'):
                df=df.rename(columns={c:c[15:]})
        
        df['fecha']=pd.to_datetime(df['fecha'])
        df['fecha_colocacion']=pd.to_datetime(df['fecha_colocacion'])
        df['fecha_vencimiento']=pd.to_datetime(df['fecha_vencimiento'])
        df['valor_nominal']=pd.to_numeric(df['valor_nominal'])
        
        return df