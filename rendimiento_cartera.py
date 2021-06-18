# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 12:01:35 2021

@author: Investor
"""
#main_portafolio.py


# Cargar las librería de python
import pandas as pd 
#import numpy as np
from datetime import datetime, timedelta
from Portafolio import Portafolio
from Mercados import Mercado


if __name__ == "__main__":
   # Leer csv con datos y cargar en el dataframe data
   # Leer csv con datos y cargar en el dataframe data
    flujos = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/Flujos.xlsx',index_col=0) 
    #operaciones=pd.read_csv('G:\Mi unidad\MARKET DATA\BaseDatos\operaciones.csv',index_col=0,sep=',')
          
    mercado=Mercado(flujos=flujos)
    
    cliente=Portafolio()
    cliente.operacion('compra',mercado,'PYCON01F6605',datetime(2017,2,22),1062849,2)
    cliente.operacion('compra',mercado,'PYATM03F6452',datetime(2017,2,22),1075315,4)
    cliente.operacion('compra',mercado,'PYINN03F5295',datetime(2017,2,22),1036266,4)
    cliente.operacion('compra',mercado,'PYINN01F5271',datetime(2017,10,13),1038734,4)
    cliente.operacion('compra',mercado,'PYELE01F3737',datetime(2018,6,5),1046284,2)
    cliente.operacion('compra',mercado,'PYINN04F5633',datetime(2019,2,13),1020658,2)
    cliente.operacion('compra',mercado,'PYATM01F8823',datetime(2019,9,26),1032673,20)
    cliente.operacion('compra',mercado,'PYATM02F8830',datetime(2019,12,19),1024114,9)
    
    
    
    
