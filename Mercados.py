# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 12:08:17 2021

@author: Investor
"""

#Mercados.py

# Cargar las librería de python
import pandas as pd 
import numpy as np
from datetime import timedelta
from scipy.optimize import fsolve
import icecream as ic



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


class Bono:
    
    def __init__(self,isin,flujo):
        #identificacion del bono
        self.isin=isin
        
        #flujo de pago
        self.flujo=flujo.loc[:,['fecha','interes','amortizacion']]
        #Ordenar por fecha
        self.flujo=self.flujo.sort_values(by='fecha')
        
        #Informacion del Bono
        df=pd.DataFrame(data={'isin':self.isin,
                                'simbolo':self.isin[2:5],
                                'Emisor':flujo['emisor'].values[0],
                                'Tipo_Instrumento':flujo['tipo_instrumento'].values[0],
                                'Moneda':flujo['moneda'].values[0],
                                'Fecha_Emision':flujo['fecha_colocacion'].values[0],
                                'Fecha_Vencimiento':self.flujo['fecha'].max(),
                                'ValorNominal':self.flujo['amortizacion'].sum(),
                                'TasaCupon':flujo['tasa_interes'].values[0]
                                },
                           index=[0])
        self.info=df.loc[0]
        
    def flujoVigente(self,fecha):
        #determinar el flujo a cobrar
        df=self.flujo[(self.flujo['fecha']>fecha)]
        
        #calcular pago total de los flujos 
        df.loc[:,'pago']=df.loc[:,'interes']+df.loc[:,'amortizacion']
        #calcular dias a cobrar de cada flujo
        df.loc[:,'dias']=((df.loc[:,'fecha']-fecha)/timedelta(days=1)).astype(int)
        
        return df
        
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
        
    def datosValor(self,irr,fechaValor):
        #Valoracion segun rendimiento
        valorActualNeto=self.valorActual(irr,fechaValor)
        #flujo de pago futuro desde fechaValor
        flujo=self.flujoVigente(fechaValor).sort_values(by='fecha')
        #Valor nominal unitario
        valorNominal=self.info['ValorNominal']
        #Tasa cupon
        tasaCupon=self.info['TasaCupon']
        
        #Periodo de vencimiento o maduracion del instrumento
        maduracion=int((self.info['Fecha_Vencimiento']-fechaValor)/timedelta(days=1))
        
        #Dias desde el ultimo pago cupon
        dias_desde_ultimoCupon=round(flujo.iloc[0].at['interes']*365/(tasaCupon*valorNominal),0)
        
        dias_corridos=dias_desde_ultimoCupon-flujo.iloc[0].at['dias']
        
        interes_corrido=tasaCupon/365*dias_corridos*valorNominal
        
        interes_devengado_ultimoCupon=((1+irr)**(dias_corridos/365)-1)*valorActualNeto
        #Tasa nominal
        tasa_nominal=(flujo['pago'].sum()/valorActualNeto-1)*(365/maduracion)
        #Duration de la operacion
        duration=sum(flujo['pago']/(1+irr)**(flujo['dias']/365)*flujo['dias'])/valorActualNeto
        
        #Precios
        pdirty=valorActualNeto/valorNominal*100
        pclean=(valorActualNeto-interes_corrido)/valorNominal*100
        pCupon=(valorActualNeto-interes_devengado_ultimoCupon)/valorNominal*100
        
            
        datos={'Rendimiento':irr,
               'TasaNominal':tasa_nominal,
               'PrecioDirty':pdirty,
               'PrecioClean':pclean,
               'PrecioUltimoCupon':pCupon,
               'InteresCorrido':interes_corrido/valorNominal*100,
                'Duration':duration/365,
               'Maduracion':maduracion/365}
        
        
        return pd.DataFrame(data=datos,index=[0]).loc[0]
    
class Mercado:
    def __init__(self,flujos,operaciones=None,calificaciones=None):
        
        #Cargar los instrumentos con la condicion que tenga flujo
        self.instrumentos=pd.DataFrame(index=flujos.pivot_table(index='isin').index)
        
        for i in self.instrumentos.index:
            self.instrumentos.loc[i,'bono']=Bono(i,flujos[flujos['isin']==i])
        print("Instumentos cargados")
        
        #Operaciones del mercado
        if(type(operaciones)==type(pd.DataFrame())):
            self.operaciones=operaciones
            self.operaciones['fecha_operacion']=pd.to_datetime(self.operaciones['fecha_operacion'])
            print('Operaciones cargadas')
            #Cargar las calificaciones de cada emisor
            if(type(calificaciones)==type(pd.DataFrame())):
                self.calificaciones=calificaciones
                #recorido por todas las operaciones
                for row in self.operaciones.itertuples():
                    if(calificaciones[calificaciones['SIMBOLO']==row.simbolo_emisor].shape[0]>0): 
                        cali=calificaciones[calificaciones['SIMBOLO']==row.simbolo_emisor].iloc[0].at['Calificacion_letras']
                        self.operaciones.loc[row.Index,'calificacion']=cali
                    else:
                        self.operaciones.loc[row.Index,'calificacion']=np.nan
                print("Calificaciones cargadas")
            else:
                self.calificaciones=None
        else:
            pass
                
    def getBond(self,isin):
        if(isin in self.instrumentos.index):
            return self.instrumentos.loc[isin,'bono']
        else:
            print('No se encuentra disponible el bono: ', isin)
            return None
        
    def listOfBond(self):
        lbono=pd.DataFrame()
        for bono in self.instrumentos.index:
            lbono=lbono.append(self.getBond(bono).info)
        return lbono
    
    def curva(self,fecha_curva,fecha_rango,moneda):
        if(type(self.calificaciones)==type(pd.DataFrame())):
            #filtrar las operaciones en base a parametros
            operaciones=self.operaciones[(self.operaciones['fecha_operacion']>=fecha_rango)&
                                (self.operaciones['fecha_operacion']<=fecha_curva)&
                                (self.operaciones['moneda']==moneda)]
            
            for row in operaciones.itertuples():
                operaciones.loc[row.Index,'duration']=self.getBond(row.isin).datosValor(row.ytm,fecha_curva)['Duration']
            
            curva=operaciones.pivot_table(index=['calificacion','emisor','isin'],values=['ytm','duration'],aggfunc=np.mean)
            return curva
        else:
            print('No se puede ejecutar esta funcion al no tener cargadas las calificaciones de los instrumentos')
            return None     
        
    def history(self,bono):
        
        #Ultima fecha de operaciones cargadas
        fecha_maxima=self.operaciones['fecha_operacion'].max()

        #Captar las operaciones historicas del bono
        historia_operaciones=self.operaciones[self.operaciones['isin']==bono]

        #Determinar fecha inicio de datos
        fecha_inicio_operaciones=historia_operaciones['fecha_operacion'].min()

        #Cargar los dias segun rango de fechas de f_inicio hasta f_final
        historia = pd.DataFrame({'date':pd.date_range(start=fecha_inicio_operaciones, 
                                                         end=fecha_maxima
                                                        ,freq='d')})

        #Cargar rendimiento historico
        for row in historia.itertuples():
            y=historia_operaciones[historia_operaciones['numero_operacion']==historia_operaciones[historia_operaciones['fecha_operacion']<=row.date]['numero_operacion'].max()].iloc[0].at['ytm']
            print (row.date)
            datos=self.getBond(bono).datosValor(y,row.date)
    
            historia.loc[row.Index,'ytm']=datos['Rendimiento']
            historia.loc[row.Index,'PrecioDirty']=datos['PrecioDirty']
            historia.loc[row.Index,'PrecioClean']=datos['PrecioClean']
            historia.loc[row.Index,'PrecioUltimoCupon']=datos['PrecioUltimoCupon']
            historia.loc[row.Index,'cantidad']=historia_operaciones[historia_operaciones['fecha_operacion']==row.date]['cantidad'].sum()
            
        return historia
    
    def history_pClean(self,bono_isin):
            #definir el bono
            bono=self.getBond(bono_isin)
            #Captar las operaciones historicas del bono
            historia_operaciones=self.operaciones[self.operaciones['isin']==bono_isin].sort_values(by=['fecha_operacion','numero_operacion'])
            #crear listado de fechas
            fechas_operaciones=pd.to_datetime(historia_operaciones['fecha_operacion'].values)
            
            fechas_flujos=pd.to_datetime(bono.flujo['fecha'].values)

            #Determinar fecha inicio de datos
            fecha_inicio_operaciones=fechas_operaciones.min()
            #Ultima fecha de operaciones cargadas
            fecha_maxima=self.operaciones['fecha_operacion'].max()
            #Cargar los dias segun rango de fechas de f_inicio hasta f_final
            historia = pd.DataFrame({'date':pd.date_range(start=fecha_inicio_operaciones, 
                                                             end=fecha_maxima
                                                            ,freq='d')})

            #primera operacion
            ultima_operacion=historia_operaciones[historia_operaciones['fecha_operacion']==fecha_inicio_operaciones].iloc[-1]

            #Datos de valoracion de la primera operacion
            datos=bono.datosValor(ultima_operacion['ytm'],fecha_inicio_operaciones)
            #Carga del primer dato
            historia.loc[0,'precio_clean']=datos['PrecioUltimoCupon']
            
            for row in historia.loc[1:].itertuples():

                if(row.date in fechas_operaciones):
                    ultima_operacion=historia_operaciones[historia_operaciones['fecha_operacion']==row.date].iloc[-1]
                    datos=bono.datosValor(ultima_operacion['ytm'],row.date)

                    fechas_operaciones=fechas_operaciones[~(fechas_operaciones==row.date)]

                elif(row.date in fechas_flujos):
                    datos=bono.datosValor(ultima_operacion['ytm'],row.date)

                historia.loc[row.Index,'precio_clean']=datos.at['PrecioUltimoCupon']
                

            return historia