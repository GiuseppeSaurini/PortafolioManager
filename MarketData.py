# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 16:03:23 2021

@author: Giuseppe
"""

#ImportData.py

# Cargar las librería de python data analysis
import pandas as pd 
#import numpy as np
#from datetime import datetime, timedelta
import os
import requests
import json

MD_API_KEY=os.environ.get('MD_API_KEY')

class MarketDataAPI:
    
    def get_instrumento(isin='',fecha_base=''):
        #API Datawharehousing url y contraseña
        url_DWH='https://data.marketdata.com.py/api/v1/'
        key='?api_key='+MD_API_KEY
        
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
        
        
        return df    
       
    def get_value(isin,rendimiento,fechaValor,cantidad=1):
        #API Datawharehousing url y contraseña
        url_DWH='https://data.marketdata.com.py/api/v1/'
        key='?api_key='+MD_API_KEY
        
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
        key='?api_key='+MD_API_KEY
        
        #Definir que tabla se busca
        query=url_DWH+'operaciones'+key
        
        #Filtrar por isin    
        query=query+'&isin='+isin
        
        #Carga de filtros fecha
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
                  
        df['fecha_operacion']=pd.to_datetime(df['fecha_operacion'])
        
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
    
    def get_flujo(isin=''):
        #API Datawharehousing url y contraseña
        
        url_DWH='https://data.marketdata.com.py/api/v1/'
        key='?api_key='+MD_API_KEY
        
        #Definir que tabla se busca
        query=url_DWH+'flujos'+key
        
        #Filtrar por isin    
        query=query+'&isin='+isin    
        
        #importar los datos
        data=json.loads(requests.get(query).text)
        df=pd.json_normalize(data,sep='/')
        
        #eliminar datos None
        df=df.replace('None','')

        #definir el la columna de index
        df=df.set_index('id')
        
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
    
    def get_flujos_from_list(self,list_isin):
        """
        Funcion para importar varios flujos de un
        listado de instrumentos solo agregando el 
        codigo isin a la lista.
        El resultado es un DataFrmae con los datos 
        del los flujos de instrumentos seleccionados.
        En el caso que no tengan flujo se imprime el isin
        
        """
        """
        Este metodo es un instance method por lo que 
        para utilizar la funcion primero se debe activar 
        a la clase:
        md=MarketDataAPI()
        md.get_flujos_from_list(list_isin)
        """
        flujos=pd.DataFrame()
        for isin in list_isin:
            try:
                flujo_bono=MarketDataAPI.get_flujo(isin)  
                flujos=pd.concat([flujos,flujo_bono])
            except:
                print('no tiene flujo',isin)
        return flujos