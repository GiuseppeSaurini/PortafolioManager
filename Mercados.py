# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 12:08:17 2021

@author: Investor
"""

#Mercados.py

# Cargar las librería de python
import pandas as pd 
import numpy as np
from datetime import timedelta,datetime,date
from scipy.optimize import fsolve



#Funcion Net Present Value a una tasa de descuento
def npv(irr, cfs, dias,va=0):
    #Definicio de variables
    
    #irr es el tasa al que se descuenta el flujo futuro
    #cfs es el flujo a descontar
    #dias se refiere a cantidad de dias a descontar cada flujo
    #va se refiere al valor actual o valor de la inversion
    '''
    El Valor Actual (va) es opcional ya que en algunas ocaciones este valor
    no se tiene, ya que es el valor que se desea hayar
    '''

    #Funcion de descuento
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
                                'Emisor':flujo['emisor/nombre'].values[0],
                                'Tipo_Instrumento':flujo['tipo_instrumento'].values[0],
                                'Moneda':flujo['moneda'].values[0],
                                'Fecha_Emision':flujo['fecha_colocacion'].values[0],
                                'Fecha_Vencimiento':self.flujo['fecha'].max(),
                                'ValorNominal':self.flujo['amortizacion'].sum(),
                                'TasaCupon':flujo['tasa_interes'].values[0]
                                },
                           index=[0])
        #Traformar a Serie
        self.info=df.loc[0]
    
      
    def flujoVigente(self,fechaValor,fecha_fin=''):
        #determinar el flujo a cobrar
        df=self.flujo[(self.flujo['fecha']>fechaValor)]
        
        #calcular el flujo de pago sin discriminar el proposito 
        df.loc[:,'pago']=df.loc[:,'interes']+df.loc[:,'amortizacion']
        #calcular dias a cobrar de cada flujo
        df.loc[:,'dias']=((df.loc[:,'fecha']-fechaValor)/timedelta(days=1)).astype(int)
        
        
        if(fecha_fin==''):
            return df
        else:
            return df[df.fecha<=fecha_fin]
    
    def fecha_ultimo_pago(self,fechaValor):
        #Definir si se pago cupon antes de la fechaValor
        if(pd.notna(self.flujo[self.flujo['fecha']<=fechaValor]['fecha'].max())):
            
            return self.flujo[self.flujo['fecha']<=fechaValor]['fecha'].max()
         
        elif(pd.notna(self.info['Fecha_Emision'])):
            
            #Descartar que la fechaValor no sea antes que la emision
            if(fechaValor<self.info['Fecha_Emision']):
                print('La fecha ',fechaValor,' es previo a la fecha de emision')
                return np.nan
            else:
                return self.info['Fecha_Emision']
        else:
            print('Error: Fecha_Emision esta vacio')
            return np.nan
             
            
    def diasCorridos(self,fechaValor):
        
        if(pd.notna(self.fecha_ultimo_pago(fechaValor))):
            
            fechaUltimoCupon=self.fecha_ultimo_pago(fechaValor)
            
            diasCorridos=int((fechaValor-fechaUltimoCupon)/timedelta(days=1))
                
            return diasCorridos
        else:
            return np.nan
    
    def rendimiento(self,fechaValor,valorActual):
        #Definir el flujo residual
        flujo=self.flujoVigente(fechaValor)
        
        return irr(flujo['pago'],flujo['dias'],valorActual)
    
    def valorActual(self,irr,fechaValor):
        flujo=self.flujoVigente(fechaValor)
        try:
            value=npv(irr,flujo['pago'],flujo['dias'])
            return value
        except:
            print('ERROR')
            print(self.isin,flujo['dias'])
            
         
    def datosValor(self,irr,fechaValor):
        #Valoracion segun rendimiento
        valorActualNeto=self.valorActual(irr,fechaValor)
        #flujo de pago futuro desde fechaValor
        flujo=self.flujoVigente(fechaValor)
        
        #Valor nominal unitario
        if(self.info['ValorNominal']==0):
            valorNominal=(1000000 if self.info['Moneda']=='pyg' else 1000)
        else:
            valorNominal=self.info['ValorNominal']
            
        #Tasa cupon
        tasaCupon=self.info['TasaCupon']
        
        #Periodo de vencimiento o maduracion del instrumento
        maduracion=int((self.info['Fecha_Vencimiento']-fechaValor)/timedelta(days=1))
        
        #Dias desde el ultimo pago cupon
        if(tasaCupon>0):
            dias_corridos=self.diasCorridos(fechaValor)
            interes_corrido=tasaCupon/365*dias_corridos*valorNominal
        else:
            interes_corrido=0
            
        #Tasa nominal
        tasa_nominal=(flujo['pago'].sum()/valorActualNeto-1)*(365/maduracion)

        #Duration de la operacion
        duration=sum(flujo['pago']/(1+irr)**(flujo['dias']/365)*flujo['dias'])/valorActualNeto
        
        #Precios
        pdirty=valorActualNeto/valorNominal*100
        pclean=(valorActualNeto-interes_corrido)/valorNominal*100
        pBase=(valorActualNeto/((1+irr)**(dias_corridos/365)))/valorNominal*100
        
            
        datos={'Rendimiento':irr,
               'TasaNominal':tasa_nominal,
               'PrecioDirty':pdirty,
               'PrecioClean':pclean,
               'PrecioUltimoCupon':pBase,
               'InteresCorrido':interes_corrido/valorNominal*100,
               'Duration':duration/365,
               'Maduracion':maduracion/365}
        
        #Transformar a Serie
        return pd.DataFrame(data=datos,index=[0]).loc[0]
    
class CDA(Bono):
    def __init__(self,serie,flujo,emisor='',tipo_instrumento='',moneda='',
                 fecha_colocacion='',tasa_interes=''):
        #identificacion del bono
        self.serie=serie
        
        #flujo de pago
        self.flujo=flujo.loc[:,['fecha','interes','amortizacion']]
        #Ordenar por fecha
        self.flujo=self.flujo.sort_values(by='fecha')
        
        #Informacion del Bono
        df=pd.DataFrame(data={'serie':serie,
                                'simbolo':'',
                                'Emisor':emisor,
                                'Tipo_Instrumento':tipo_instrumento,
                                'Moneda':moneda,
                                'Fecha_Emision':fecha_colocacion,
                                'Fecha_Vencimiento':self.flujo['fecha'].max(),
                                'ValorNominal':self.flujo['amortizacion'].sum(),
                                'TasaCupon':tasa_interes
                                },
                           index=[0])
        #Traformar a Serie
        self.info=df.loc[0]
    
class Mercado:
    def __init__(self,flujos,operaciones=None,calificaciones=''):
        
        #Cargar los instrumentos con la condicion que tenga flujo
        self.instrumentos=pd.DataFrame(index=flujos.pivot_table(index='isin').index)
        
        for i in self.instrumentos.index:
            self.instrumentos.loc[i,'bono']=Bono(i,flujos[flujos['isin']==i])
        print("Instumentos cargados")
        
        #Operaciones del mercado
        if(type(operaciones)==type(pd.DataFrame())):
            self.operaciones=operaciones
            
            self.operaciones=self.operaciones.rename(columns={'emisor/calificacion':'calificacion'})
            
            #Carga de calificacion simple
            for row in self.operaciones.itertuples():
                calif=str(row.calificacion).replace('py','')
                calif=calif.replace('+','')
                calif=calif.replace('-','')
                self.operaciones.loc[row.Index,'calif_simple']=calif
            
            print('Operaciones cargadas')
        
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
        #filtrar las operaciones en base a parametros
        operaciones=self.operaciones[(self.operaciones['moneda']==moneda)&
                                     (self.operaciones['ytm']>0)&
                                     (self.operaciones['fecha_operacion']>=fecha_curva)&
                                     (self.operaciones['fecha_operacion']<=fecha_rango)]
        
        #Asignacion de variables
        agrupacion=['calif_simple','emisor','isin']
        columns_values=['ytm']
        
        #Generar reporte
        curva = operaciones.pivot_table(index=agrupacion,
                                        values=columns_values)
        
        #Devolver reporte
        return curva
        
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