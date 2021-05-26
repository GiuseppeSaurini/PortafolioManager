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
        
        df=self.flujo[(self.flujo['fecha']>fecha)]
        
        df['pago']=df['interes']+df['amortizacion']
        df['dias']=((self.flujo['fecha']-fecha)/timedelta(days=1)).astype(int)
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
        flujo=self.flujoVigente(fechaValor)
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
    
    def curva(self,finicio,ffin,moneda):
        if(type(self.calificaciones)==type(pd.DataFrame())):
            #filtrar las operaciones en base a parametros
            op=self.operaciones[(self.operaciones['fecha_operacion']>=finicio)&
                                (self.operaciones['fecha_operacion']<=ffin)&
                                (self.operaciones['moneda']==moneda)]
            
            for row in op.itertuples():
                op.loc[row.Index,'duration']=self.getBond(row.isin).datosValor(row.ytm,ffin)['Duration']
            
            curva=op.pivot_table(index=['calificacion','emisor','isin'],values=['ytm','duration'],aggfunc=np.mean)
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
            datos=self.getBond(bono).datosValor(y,row.date)
    
            historia.loc[row.Index,'ytm']=datos['Rendimiento']
            historia.loc[row.Index,'PrecioDirty']=datos['PrecioDirty']
            historia.loc[row.Index,'PrecioClean']=datos['PrecioClean']
            historia.loc[row.Index,'PrecioUltimoCupon']=datos['PrecioUltimoCupon']
            historia.loc[row.Index,'cantidad']=historia_operaciones[historia_operaciones['fecha_operacion']==row.date]['cantidad'].sum()
            
        return historia
    
    def history_pClean(self,bono):
        
        #Captar las operaciones historicas del bono
        historia_operaciones=self.operaciones[self.operaciones['isin']==bono].sort_values(by=['fecha_operacion','numero_operacion'])
        #Ordenar por fecha y operacione
        historia_operaciones=historia_operaciones.sort_values(by=['fecha_operacion','numero_operacion'])
        
        #Ultima fecha de operaciones cargadas
        fecha_maxima=self.operaciones['fecha_operacion'].max()

        #Determinar fecha inicio de datos
        fecha_inicio_operaciones=historia_operaciones['fecha_operacion'].min()

        #Cargar los dias segun rango de fechas de f_inicio hasta f_final
        historia = pd.DataFrame({'date':pd.date_range(start=fecha_inicio_operaciones, 
                                                         end=fecha_maxima
                                                        ,freq='d')})
        #Cargar precio historico
        ultima_operacion=historia_operaciones[historia_operaciones['fecha_operacion']==fecha_inicio_operaciones].iloc[-1]
        datos=self.getBond(bono).datosValor(ultima_operacion['ytm'],fecha_inicio_operaciones)
        
        for row in historia.itertuples():
            if(row.date in historia_operaciones[historia_operaciones['fecha_operacion']>=ultima_operacion['fecha_operacion']]['fecha_operacion'].values):
                ultima_operacion=historia_operaciones[historia_operaciones['fecha_operacion']==row.date].iloc[-1]
                datos=self.getBond(bono).datosValor(ultima_operacion['ytm'],row.date)
                                
            elif(row.date in self.getBond(bono).flujo['fecha'].values):
                datos=self.getBond(bono).datosValor(ultima_operacion['ytm'],row.date)

            historia.loc[row.Index,'precio_clean']=datos['PrecioUltimoCupon']              
            
        return historia