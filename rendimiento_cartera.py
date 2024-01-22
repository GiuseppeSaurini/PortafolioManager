# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 12:01:35 2021

@author: Investor
"""
#main_portafolio.py


# Cargar las librería de python
import pandas as pd 
#import numpy as np
from datetime import datetime#, timedelta
from Portafolio import Portafolio
from Mercados import Bono,CDA
from MarketData import MarketDataAPI as md
#from icecream import ic


if __name__ == "__main__":
   
   #Apertura de portafolio
    cliente=Portafolio()
    
    #Lectura de datos
        #Obtencion de los flujos de CDA
    flujos_cda=pd.read_excel('dato_portafolio.xlsx',sheet_name='flujos')
        #Datos de operaciones para creacion de cartera
    cartera_pyg=pd.read_excel('dato_portafolio.xlsx',sheet_name='cartera_pyg')
    
   #Carga de operaciones
    for row in cartera_pyg.itertuples():
        print(row.serie)
        if(row.instrumento=='CDA'):
        
            cda=CDA(flujos_cda[flujos_cda['serie']==row.serie],row.tasa_cupon,
                   row.serie,row.emisor,row.instrumento)
            cliente.operacion(row.tipo_operacion,
                              cda,
                              row.fecha_operacion,
                              row.valor_unitario,
                              row.cantidad)
        else:
            bono=Bono(row.serie,md.get_flujo(row.serie))
            cliente.operacion(row.tipo_operacion,
                              bono,
                              row.fecha_operacion,
                              row.valor_unitario,
                              row.cantidad)
    print('loading operation finish\n')       
   
   #Rango de fecha    
    fecha_inicio=datetime(2023,1,1)
    fecha_fin=datetime(2023,12,31)
    
   #Valor historico de portafolio
    historyValue=cliente.historyValue(fecha_inicio,fecha_fin,frequency='M')
   #Carga de flujo de efectivo
    flujoPortafolio=cliente.flujoPortafolio(fecha_inicio,fecha_fin)
   #Carga de detalle y valoracion del portafolio al cierre
    carteraFinal=cliente.stockPortafolio(fecha_fin)
   
   #Generar el excel
    writer=pd.ExcelWriter('Portafolio_test.xlsx')
    
    #Cargar al excel
    historyValue.to_excel(writer,sheet_name='historyValue')
    
    flujoPortafolio.to_excel(writer,sheet_name='flujo')
    
    carteraFinal.to_excel(writer,sheet_name='Cartera')
    
   #Cerrar
    writer.save()
    writer.close()
   
    