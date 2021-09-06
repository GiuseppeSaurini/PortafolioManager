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
from ImportData import importData


if __name__ == "__main__":
   #Descarga de instumentos
    #api_flujos=importData(table='flujos')
   
   #Carga de instumentos
    #mercado=Mercado(api_flujos)
    
   #Apertura de portafolio
    cliente=Portafolio()
    
   #Carga de operaciones ejemplo
    #operacion(tipoOP,mercado,isin,fechaOP,precioOP,cantidad)
    cliente.operacion('compra',Mercado(importData('PYCON01F6605',table='flujos')),'PYCON01F6605',datetime(2017,2,22),1062849,2)
    
    #cliente.operacion('compra',mercado,'PYATM03F6452',datetime(2017,2,22),1075315,4)
    #cliente.operacion('compra',mercado,'PYINN03F5295',datetime(2017,2,22),1036266,4)
    #cliente.operacion('compra',mercado,'PYINN01F5271',datetime(2017,10,13),1038734,4)
    #cliente.operacion('compra',mercado,'PYELE01F3737',datetime(2018,6,5),1046284,2)
    cliente.operacion('compra',Mercado(importData('PYINN04F5633',table='flujos')),'PYINN04F5633',datetime(2019,2,13),1020658,2)
    #cliente.operacion('compra',mercado,'PYATM01F8823',datetime(2019,9,26),1032673,20)
    #cliente.operacion('compra',mercado,'PYATM02F8830',datetime(2019,12,19),1024114,9)

   #Rango de fecha    
    fecha_inicio=datetime(2017,1,1)
    fecha_fin=datetime(2020,12,14)
    
   #Valor historico de portafolio
    hist=cliente.historyValue(fecha_inicio,fecha_fin,frequency='M')
   
   #Generar el excel
    writer=pd.ExcelWriter('Portafolio_test.xlsx')
    
   #Carga de Valor historico
    hist.to_excel(writer,sheet_name='historyValue')
    
   #Carga de flujo de efectivo
    cliente.flujoPortafolio(fecha_inicio,fecha_fin).to_excel(writer,sheet_name='flujo')
    
   #Carga de detalle y valoracion del portafolio
    cliente.stockPortafolio(fecha_fin).to_excel(writer,sheet_name='Cartera')
    
   #Cerrar
    writer.save()
   
    