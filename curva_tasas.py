# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 12:03:50 2021

@author: Investor
"""

#main_mercado.py


# Cargar las librería de python
import pandas as pd 
#import numpy as np
from datetime import datetime#, timedelta
from M import Mercados


if __name__ == "__main__":
    flujos = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/Flujos.xlsx',index_col=0) 
    operaciones = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/operaciones.xlsx',index_col=0)
    emisiones = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/emisiones.xlsx',index_col=0)
    emisores = pd.read_excel('G:/Mi unidad/MARKET DATA/BaseDatos/Emisores.xlsx')
            
    mercado=Mercado(flujos,operaciones=operaciones,calificaciones=emisores)
    
    inicio=datetime(2021,3,1)
    fin=datetime(2021,5,11)
    moneda='pyg'
    curva=mercado.curva(inicio,fin,moneda)
    
    x=curva.plot(x='duration',y='ytm',kind='scatter')
    colorn=0
    for i in curva.index.get_level_values(level='calificacion'):
        curva.loc[(i)].plot(x='duration',y='ytm',kind='scatter',ax=x,
                            color=('C'+str(colorn)))
        colorn+=1
    file_name='curva_'+str(fin.month)+str(fin.year)+'_'+moneda+'.xlsx'
    curva.to_excel(file_name)