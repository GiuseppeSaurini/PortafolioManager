# -*- coding: utf-8 -*-
"""
Created on Fri May  7 11:32:00 2021

@author: Giuseppe
"""


# Cargar las librería de python
import pandas as pd 
from datetime import datetime#, timedelta
from Mercados import Mercado
from MarketData import MarketDataAPI as md
#import icecream as ic



if __name__ == "__main__":
    
    isin_bono='PYMUV01F8148'
    #api_operaciones=importData(isin_bono,'operaciones')
    api_flujos=md.importData(isin_bono,'flujos')
    api_insturmento=md.importData(isin_bono)
        
    #mercado=Mercado(api_flujos,api_operaciones)
    mercado=Mercado(api_flujos)
    bono=mercado.getBond(isin_bono)
      
    #bono_history=mercado.history_pClean(isin_bono)
    
    
    #bono_history.plot(x='date',y='precio_clean')
    
    valor=bono.datosValor(0.060,datetime(2021,10,29))
    
    
    