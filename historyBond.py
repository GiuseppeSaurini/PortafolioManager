# -*- coding: utf-8 -*-
"""
Created on Fri May  7 11:32:00 2021

@author: Investor
"""


# Cargar las librería de python
import pandas as pd 
from datetime import datetime#, timedelta
from Mercados import Mercado
from ImportData import importData
#import icecream as ic


if __name__ == "__main__":
    # flujos = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/Flujos.xlsx',index_col=0) 
    # operaciones = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/operaciones.xlsx',index_col=0)
    # emisiones = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/emisiones.xlsx',index_col=0)
    # emisores = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/Emisores.xlsx')
    isin_bono='PYATM01F8823'
    api_operaciones=importData(isin_bono,'operaciones')
    api_flujos=importData(isin_bono,'flujos')
        
    mercado=Mercado(api_flujos,api_operaciones)
      
    bono_history=mercado.history_pClean(isin_bono)
    
    
    bono_history.plot(x='date',y='precio_clean')
    
    
    
    