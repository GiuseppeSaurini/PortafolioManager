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
        self.operaciones=pd.DataFrame()
       
    def operacion(self,tipo_op,instrumento,fechaOp,valorUnitario,cantidad):
        
        tirOp=instrumento.rendimiento(fechaOp,valorUnitario)
        self.operaciones=self.operaciones.append({'operacion':tipo_op,
                                                 'isin':instrumento.isin,
                                                 'fecha':fechaOp,
                                                 'valorUnitario':valorUnitario,
                                                 'cantidad':cantidad,
                                                 'TirOperacion':tirOp,
                                                 'ValorOperacion':valorUnitario*cantidad,
                                                 'bono':instrumento
                                                 },ignore_index=True)
                             
        
    def stockPortafolio(self,fechaValor):
        #Definir columnas df
        stock=pd.DataFrame(columns=['isin','cantidad','tirOp','Valor'])
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
            npv+=item.ValorBono
        return npv
    
    def flujoPortafolio(self,fecha_inicial,fecha_final):
        #Cambiar fecha_inicio en caso de que la sea antes de la primera operacion
        if(fecha_inicial<self.operaciones['fecha'].min()):
            fecha_inicial=self.operaciones['fecha'].min()
        
        
        fecha_final=fecha_final
        
        #Opciones de instruccion de operacion
        wordsCompra=['compra','Compra','COMPRA']
        wordsVenta=['venta','Venta','VENTA']

        #Creacion del Dataframe
        flujo_portafolio=pd.DataFrame(columns=['fecha','isin','concepto','pago'])

        #Carga de los bonos en stock a la fecha de inicio y sus flujos
        for item in self.stockPortafolio(fecha_inicial).itertuples():
            flujo_portafolio=flujo_portafolio.append({'fecha':fecha_inicial,
                                        'isin':item.isin,
                                        'concepto':'valor inicial',
                                       'pago':-item.ValorBono
                                       }
                                       ,ignore_index=True)
            
            for f in item.bono.flujoVigente(fecha_inicial,fecha_final).itertuples():
                flujo_portafolio=flujo_portafolio.append({'fecha':f.fecha,
                                            'isin':item.isin,
                                            'concepto':'interes',
                                            'pago':f.interes*item.cantidad}
                                           ,ignore_index=True)
                if(f.amortizacion>0):
                    flujo_portafolio=flujo_portafolio.append({'fecha':f.fecha,
                                                'isin':item.isin,
                                                'concepto':'capital',
                                                'pago':f.amortizacion*item.cantidad}
                                               ,ignore_index=True)
                else:
                    pass

        #Cargar las operaciones de compra y de venta durante el periodo y sus flujos
        for item in self.operaciones[(self.operaciones['fecha']>fecha_inicial)&(self.operaciones['fecha']<fecha_final)].itertuples():
            if(item.operacion in wordsCompra):
                input_output=-1
            #Cargar operaciones de venta
            elif(item.operacion in wordsVenta):
                input_output=1    
            else:
                print('Error: no existe el concepto: ',item.operacion)
                pass
            
            #Sumar al flujo el valor de la operacion
            flujo_portafolio=flujo_portafolio.append({'fecha':item.fecha,
                                        'isin':item.isin,
                                        'concepto':item.operacion,
                                       'pago':item.ValorOperacion*input_output}
                                       ,ignore_index=True)
            #Restar los flujos restante del bono por la cantidad vendida
            for f in item.bono.flujoVigente(item.fecha,fecha_final).itertuples():
                flujo_portafolio=flujo_portafolio.append({'fecha':f.fecha,
                                            'isin':item.isin,
                                            'concepto':'interes',
                                            'pago':f.interes*item.cantidad*input_output*-1}
                                           ,ignore_index=True)
                if(f.amortizacion>0):
                    flujo_portafolio=flujo_portafolio.append({'fecha':f.fecha,
                                                'isin':item.isin,
                                                'concepto':'capital',
                                                'pago':f.amortizacion*item.cantidad*input_output*-1}
                                               ,ignore_index=True)
        #Agragar valor final de cada bono final
        for item in self.stockPortafolio(fecha_final).itertuples():
            flujo_portafolio=flujo_portafolio.append({'fecha':fecha_final,
                                        'isin':item.isin,
                                        'concepto':'valor final',
                                       'pago':item.ValorBono}
                                       ,ignore_index=True)
            
        #Devolver el DataFrame ordenado por fecha
        return flujo_portafolio.sort_values(by='fecha')

    def historyValue(self,fecha_inicial,fecha_final,frequency='D'):
        
        #Condicionar que si la fecha requerida es menor a la primera operacion, este sea la fecha inicial 
        if(fecha_inicial<self.operaciones['fecha'].min()):
            fecha_inicial=self.operaciones['fecha'].min()
        
        
        #Carga de flujo del protafolio
        flujo=self.flujoPortafolio(fecha_inicial,fecha_final)
        
        
        #Establecer las fechas de valoracion historica
        history=pd.DataFrame({'fecha':pd.date_range(fecha_inicial,fecha_final,freq=frequency).values})
        
        #Determinar las fehcas del flujo de pago
        fecha_flujo=pd.DataFrame({'fecha':flujo[~(flujo['fecha'].isin(history.fecha))]['fecha'].unique()})
        #Cargar todas las fechas
        history=history.append(fecha_flujo,ignore_index=True)
        #Ordenar fechas    
        history=history.sort_values(by='fecha')
        
        #Determinar valor inicial
        valor_portafolio_anterior=self.valorPortafolio(fecha_inicial)
        valorAcumulado=1
        #fecha=fecha_inicial
        word=['valor inicial','valor final']
        
        for row in history.itertuples():
            valor_portafolio=self.valorPortafolio(row.fecha)
            if(valor_portafolio>0):
                #Valor inicial del portafolio
                history.loc[row.Index,'valorPrtafolio']=valor_portafolio
                            
                history.loc[row.Index,'flujo']=(flujo[~(flujo['concepto'].isin(word))&(flujo['fecha']==row.fecha)]['pago'].sum())
                
                history.loc[row.Index,'growth']=(history.loc[row.Index,'valorPrtafolio']+history.loc[row.Index,'flujo'])/valor_portafolio_anterior-1
                
                history.loc[row.Index,'growthValue']=valorAcumulado*(1+history.loc[row.Index,'growth'])
                
                valorAcumulado=history.loc[row.Index,'growthValue']
                
                valor_portafolio_anterior=valor_portafolio
            else:
                return history
        return history
    

