# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 16:03:23 2021

@author: Investor
"""

#ImportData.py

# Cargar las librería de python data analysis
import pandas as pd 
import numpy as np
from datetime import datetime, timedelta
import os
import requests
import json


def importData(isin=None,table='instrumentos',fechaVnc_base=None):
    #API Datawharehousing url y contraseña
    url_DWH='https://data.marketdata.com.py/api/v1/'
    key='?api_key=Tp1u3Wb0y2X31w4ZMjcRxAldlpHjC8hy'
    
    #Definir que tabla se busca
    query=url_DWH+table+key
    
    #Carga de filtros
    query=query+('&isin='+isin if isin!=None else '') 
    query=query+('&fecha_vencimiento_mt='+fechaVnc_base if fechaVnc_base!=None else '')
   
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
    
    
    for row in df.itertuples():
        df.loc[row.Index,'simbolo_emisor']=row.isin[2:5]
    
    #definir el la columna de index
    if(table=='instrumentos'):
        df=df.set_index('isin')
    else:
        df=df.set_index('id')
        
    return df

if __name__ == "__main__":
    #Importacion de instrumentos
    bonos=importData()
    bonos.to_excel('G:/Mi unidad/MARKET DATA/BaseDatos/emisiones.xlsx')
    
    #(0) Inicio de carga de datos 
    flujos=importData(table='flujos')
    
    #Renombrar columnas o extraer nombre de agrupacion
    flujos['fecha']=pd.to_datetime(flujos['fecha'])
    
    #Definir los bonos
    flujos=flujos[flujos['isin'].isin(bonos.index)]
    
    #Filtrado de flujos incompletos
    for i in flujos.pivot_table(index='isin').index:
        if(flujos[flujos['isin']==i]['amortizacion'].sum()!=1000000
           and flujos[flujos['isin']==i]['amortizacion'].sum()!=1000):
            flujos=flujos.drop(flujos[flujos['isin']==i].index)
    
    #Generar un archivo excel con los datos
    flujos.to_excel('G:/Mi unidad/MARKET DATA/BaseDatos/flujos.xlsx')    
    
    operaciones=importData(table='operaciones')
    operaciones=operaciones[operaciones['isin'].isin(flujos.pivot_table(index='isin').index)]
    operaciones=operaciones[(operaciones['isin'].isin(flujos.pivot_table(index='isin').index))&
                           (~operaciones['ytm'].isna())&
                           (operaciones['ytm']>0)]
    
    operaciones.to_excel('G:/Mi unidad/MARKET DATA/BaseDatos/operaciones.xlsx')
    


