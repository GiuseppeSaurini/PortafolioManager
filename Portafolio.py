# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 11:12:33 2020

@author: Investor
"""
# Cargar las librería de python
import pandas as pd 
import numpy as np
from datetime import datetime, timedelta
from scipy.optimize import fsolve
from Mercados import Mercado,Bono


#Funcion del Net Present Value a una tasa de descuento
def npv(irr, cfs, dias,va=0):  
    #irr es el tasa al que se descuenta el flujo futuro
    #cfs son los valores del flujo a descontar
    #dias se refiere a los dias de descuento de cada valor del flujo
    
    return np.sum(cfs/(1+ irr)**(dias/365))-va

#Funcion que define la tasa en la que NPV es 0
def irr(cashFlow,time,va):
    return np.asscalar(fsolve(npv,0, args=(cashFlow,time,va)))

#Define la ecuacion logaritmica (valores a y b) tomando en cuenta los ejes x,y
def logfunc(list_x,list_y):
    return np.polyfit(np.log(list_x),list_y,1)


class Portafolio:
    def __init__(self,denominacion='',stock=[]):
        #bono identificacion
        self.name=denominacion
        self.operaciones=pd.DataFrame(columns=['operacion','isin',
                                              'fecha','valorUnitario',
                                              'cantidad','ValorOperacion',
                                               'TirOperacion'])
       
    def operacion(self,tipo_op,mercado,isin,fechaOp,valorUnitario,cantidad):
        
        tirOp=mercado.getBond(isin).rendimiento(fechaOp,valorUnitario)

        self.operaciones=self.operaciones.append({'operacion':tipo_op,
                                                        'isin':isin,
                                                     'fecha':fechaOp,
                                                     'valorUnitario':valorUnitario,
                                                     'cantidad':cantidad,
                                                     'TirOperacion':tirOp,
                                                      'ValorOperacion':valorUnitario*cantidad,
                                                      'bono':mercado.getBond(isin)
                                                     },ignore_index=True)
    def stockPortafolio(self,fechaValor):
        #Definir columnas df
        stock=pd.DataFrame(columns=['isin','cantidad','tirOp','ValorBono'])
        wordsCompra=['compra','Compra','COMPRA']
        wordsVenta=['venta','Venta','VENTA']
        #En base a las operaciones definir el stock disponible a la fecha requerida
        for i in self.operaciones[self.operaciones.fecha<=fechaValor].index:
            #Operaciones de compra se suman
            if(self.operaciones.loc[i,'operacion'] in wordsCompra):
                
                stock=stock.append({'isin':self.operaciones.loc[i,'isin'],
                                   'cantidad':self.operaciones.loc[i,'cantidad'],
                                   'tirOp':self.operaciones.loc[i,'TirOperacion'],
                                   'bono':self.operaciones.loc[i,'bono']
                                   },
                                  ignore_index=True)
            
            #Operaciones de venta se restan a cantidad de cada stock
            elif(self.operaciones.loc[i,'operacion'] in wordsVenta):
                qventa=self.operaciones.loc[i,'cantidad']
                
                for item in stock[stock['isin']==self.operaciones.loc[i,'isin']].itertuples():    
                    if(item.cantidad>qventa):
                        stock.loc[item.Index,'cantidad']-=qventa
                        qventa=0
                    elif(item.cantidad<=qventa):
                        qventa-=stock.loc[item.Index,'cantidad']
                        stock=stock.drop(index=item.Index)
                    else:
                        pass
                                
            else:
                print('No hay disponibilidad de %s en: ',self.operaciones.loc[i,'isin'])
        for i in stock.itertuples():
            #Valoracion de Bonos
            stock.loc[i.Index,'ValorBono']=i.bono.valorActual(i.tirOp,fechaValor)*i.cantidad
        
        return stock    
                        
    def valorPortafolio(self,fechaValor):
        npv=0
        for item in self.stockPortafolio(fechaValor).itertuples():
            npv+=item.ValorBono*item.cantidad
        return npv
    
    def flujoPortafolio(self,fecha_inicial,fecha_final):
        
        if(fecha_inicial<self.operaciones['fecha'].min()):
            fecha_inicial=self.operaciones['fecha'].min()
        fechadesde=fecha_inicial
        fechahasta=fecha_final
        
        wordsCompra=['compra','Compra','COMPRA']
        wordsVenta=['venta','Venta','VENTA']

        #Creacion del Dataframe
        flujoPort=pd.DataFrame(columns=['fecha','isin','concepto','pago'])

        #Carga de los bonos en stock a la fecha de inicio y sus flujos
        for item in self.stockPortafolio(fechadesde).itertuples():
            flujoPort=flujoPort.append({'fecha':fechadesde,
                                        'isin':item.isin,
                                        'concepto':'valor inicial',
                                       'pago':-item.ValorBono
                                       }
                                       ,ignore_index=True)
            for f in mercado.getBond(item.isin).flujoVigente(fechadesde,fechahasta).itertuples():
                flujoPort=flujoPort.append({'fecha':f.fecha,
                                            'isin':item.isin,
                                            'concepto':'interes',
                                            'pago':f.int*item.cantidad}
                                           ,ignore_index=True)
                
                flujoPort=flujoPort.append({'fecha':f.fecha,
                                            'isin':item.isin,
                                            'concepto':'capital',
                                            'pago':f.amort*item.cantidad}
                                           ,ignore_index=True)

        #Cargar las operaciones de compra y de venta durante el periodo y sus flujos
        for item in self.operaciones[(self.operaciones['fecha']>fechadesde)&(self.operaciones['fecha']<fechahasta)].itertuples():
            if(item.operacion in wordsCompra):
                #Cargar la operacion de compra del bono agregando en negativo valor de la operacion
                flujoPort=flujoPort.append({'fecha':item.fecha,
                                            'isin':item.isin,
                                            'concepto':'compra',
                                           'pago':-item.ValorOperacion}
                                           ,ignore_index=True)
                #cargar los flujos del bono comprado, por su cantidad, hasta fecha estipulada final
                for f in mercado.getBond(item.isin).flujoVigente(item.fecha,fechahasta).itertuples():
                    flujoPort=flujoPort.append({'fecha':f.fecha,
                                                'isin':item.isin,
                                                'concepto':'interes',
                                                'pago':f.int*item.cantidad}
                                               ,ignore_index=True)
                    flujoPort=flujoPort.append({'fecha':f.fecha,
                                                'isin':item.isin,
                                                'concepto':'capital',
                                                'pago':f.amort*item.cantidad}
                                               ,ignore_index=True)
            #Cargar operaciones de venta
            elif(item.operacion in wordsVenta):
                #Sumar al flujo el valor de la operacion
                flujoPort=flujoPort.append({'fecha':item.fecha,
                                            'isin':item.isin,
                                            'concepto':'venta',
                                           'pago':item.ValorOperacion}
                                           ,ignore_index=True)
                #Restar los flujos restante del bono por la cantidad vendida
                for f in mercado.getBond(item.isin).flujoVigente(item.fecha,fechahasta).itertuples():
                    flujoPort=flujoPort.append({'fecha':f.fecha,
                                                'isin':item.isin,
                                                'concepto':'interes',
                                                'pago':-f.int*item.cantidad}
                                               ,ignore_index=True)
                    flujoPort=flujoPort.append({'fecha':f.fecha,
                                                'isin':item.isin,
                                                'concepto':'capital',
                                                'pago':-f.amort*item.cantidad}
                                               ,ignore_index=True)
        #Agragar valor final de cada bono final
        for item in self.stockPortafolio(fechahasta).itertuples():
            flujoPort=flujoPort.append({'fecha':fechahasta,
                                        'isin':item.isin,
                                        'concepto':'valor final',
                                       'pago':item.ValorBono}
                                       ,ignore_index=True)
            
        #Devolver el DataFrame ordenado por fecha
        return flujoPort.sort_values(by='fecha')

    def historyValue(self,fecha_inicial,fecha_final,frequency='D'):
        
        #Condicionar que si la fecha requerida es menor a la primera operacion, este sea la fecha inicial 
        if(fecha_inicial<self.operaciones['fecha'].min()):
            fecha_inicial=self.operaciones['fecha'].min()
        
        #Carga de flujo del protafolio
        f=self.flujoPortafolio(fecha_inicial,fecha_final)
        
        #Establecer las fechas de valoracion
        dates=pd.Series(pd.date_range(fecha_inicial,fecha_final,freq=frequency).values)
        if(f[~(f['fecha'].isin(dates))].shape[0]>0):
            d=pd.Series(f[~(f['fecha'].isin(dates))].pivot_table(index='fecha').index)
            dates=dates.append(d,ignore_index=True)
        
        hist=pd.DataFrame(index=dates.sort_values().values)
        
        #Valoracion inicial de portafolio
        startValue=self.valorPortafolio(fecha_inicial)
        valorAcumulado=1
        fecha=fecha_inicial
        word=['valor inicial','valor final']
        
        for row in hist.itertuples():
            hist.loc[row.Index,'valorPrtafolio']=self.valorPortafolio(row.Index)
            hist.loc[row.Index,'flujo']=(f[~(f['concepto'].isin(word))&(f['fecha']==row.Index)]['pago'].sum())
            #hist.loc[row.Index,'flujo']=-(f[~(f['concepto'].isin(word))&(f['fecha']<=row.Index)&(f['fecha']>fecha)]['pago'].sum())
            #hist.loc[row.Index,'dias']=((row.Index-fecha_inicial)/timedelta(days=1))
            hist.loc[row.Index,'growth']=(hist.loc[row.Index,'valorPrtafolio']+hist.loc[row.Index,'flujo'])/startValue-1
            #hist.loc[row.Index,'timeWeightedRetunr']=(hist.loc[row.Index,'growth']**(365/hist.loc[row.Index,'dias']))-1
            #hist.loc[row.Index,'anualRetunr']=(hist.loc[row.Index,'growth']-1)*(365/hist.loc[row.Index,'dias'])
            hist.loc[row.Index,'growthValue']=valorAcumulado*(1+hist.loc[row.Index,'growth'])
            valorAcumulado=hist.loc[row.Index,'growthValue']
            startValue=hist.loc[row.Index,'valorPrtafolio']
            #fecha=row.Index
        return hist
    

