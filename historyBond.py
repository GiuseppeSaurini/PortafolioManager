# -*- coding: utf-8 -*-
"""
Created on Fri May  7 11:32:00 2021

@author: Investor
"""


# Cargar las librería de python
import pandas as pd 
from datetime import datetime#, timedelta
from Mercados import Mercado


if __name__ == "__main__":
    flujos = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/Flujos.xlsx',index_col=0) 
    operaciones = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/operaciones.xlsx',index_col=0)
    emisiones = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/emisiones.xlsx',index_col=0)
    emisores = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/Emisores.xlsx')
            
    mercado=Mercado(flujos,operaciones=operaciones)
      
    bono_history=mercado.history(input('Ingreses el codigo del Bono:'))
    
    bono_history.plot(x='date',y='ytm')
    
    
    
    
    