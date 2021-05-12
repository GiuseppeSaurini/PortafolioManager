# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 11:12:33 2020

@author: Investor
"""

#Portafolio.py

# Cargar las librería de python
import pandas as pd 
import numpy as np
from datetime import datetime, timedelta
from scipy.optimize import fsolve

"""
#Funcion del Net Present Value a una tasa de descuento
def npv(irr, cfs, dias,va=0):  
    #irr es el tasa al que se descuenta el flujo futuro
    #cfs son los valores del flujo a descontar
    #dias se refiere a los dias de descuento de cada valor del flujo
    
    return np.sum(cfs/(1+ irr)**(dias/365))-va

#Funcion que define la tasa en la que NPV es 0
def irr(cashFlow,time,va):
    return np.asscalar(fsolve(npv,0, args=(cashFlow,time,va)))

#Definicion del Bono, funciones y atributos
class Bono:
    def __init__(self,isin,cf):
        #identificacion del bono
        self.isin=isin
        
        #flujo de pago
        self.flujo=pd.DataFrame(cf[cf.ISIN==isin].loc[:,['Fecha','Interes','Amortizacion']])
        
        #Definir fecha terminacion Bono
        self.fechaVenc=self.flujo.max().values[0]
        
        #datos generales del bono
        self.info=pd.DataFrame(cf[cf.ISIN==isin].drop_duplicates(subset='ISIN').loc[:,
                                                                            ['ISIN',
                                                                            'Fecha.Emision.Serie',
                                                                            'Emisora',
                                                                            'Tasa.Interes',
                                                                            'TipoInstrumento',
                                                                            'valor nominal']])
        self.info['Simbolo']=self.isin[2:5]
        self.info['FechaVenc']=self.flujo['Fecha'].max() 
        self.info=self.info.iloc[0]
        

    def flujoVigente(self,fecha,fechafin=0):
        if(fechafin==0):
            fechafin=self.fechaVenc 
        return pd.DataFrame({'fecha':self.flujo[(self.flujo['Fecha']>fecha)&(self.flujo['Fecha']<=fechafin)]['Fecha'],
                           'dias':((self.flujo[(self.flujo['Fecha']>fecha)&(self.flujo['Fecha']<=fechafin)]['Fecha']-fecha)/timedelta(days=1)).astype(int),
                           'int':self.flujo[(self.flujo['Fecha']>fecha)&(self.flujo['Fecha']<=fechafin)]['Interes'],
                            'amort':self.flujo[(self.flujo['Fecha']>fecha)&(self.flujo['Fecha']<=fechafin)]['Amortizacion'],
                            'pago':self.flujo[(self.flujo['Fecha']>fecha)&(self.flujo['Fecha']<=fechafin)]['Interes']+self.flujo[(self.flujo['Fecha']>fecha)&(self.flujo['Fecha']<=fechafin)]['Amortizacion']
                          })

    def rendimiento(self,fechaValor,valorActual):
        flujo=self.flujoVigente(fechaValor)
        return irr(flujo['pago'],flujo['dias'],valorActual)
    
    def valorActual(self,irr,fechaValor):
        flujo=self.flujoVigente(fechaValor)
        try:
            value=npv(irr,flujo['pago'],flujo['dias'])
            return value
        except:
            print(self.isin,flujo['dias'])
"""