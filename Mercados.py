# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 12:08:17 2021

@author: Giuseppe
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
def irr(cfs, dias, va=0):
    #cfs es el flujo a descontar
    #dias se refiere a cantidad de dias a descontar cada flujo
    #va se refiere al valor actual o valor de la inversion

    tasa=fsolve(npv,0, args=(cfs, dias,va))
    return tasa.item()

#Define la ecuacion logaritmica (valores a y b) tomando en cuenta los ejes x,y
def logfunc(list_x,list_y):
    # calculate the best fit line for data points in the list
    # input: two lists (list_x and list_y) containing data points
    # output: coefficients (a, b) of the line equation: y = a*log(x) + b

    return np.polyfit(np.log(list_x),list_y,1)


class Bono:  
    def __init__(self,isin,flujo):
        #identificacion del bono
        self.isin=isin
        
        #flujo de pago
        self.flujo=flujo.loc[:,['fecha','interes','amortizacion']]
        #Ordenar por fecha
        self.flujo=self.flujo.sort_values(by='fecha')
        #calcular el flujo de pago sin discriminar el proposito 
        self.flujo['pago']=self.flujo['interes']+self.flujo['amortizacion']
        
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
        #Periodo de vencimiento o maduracion del instrumento
        if(self.info['Fecha_Vencimiento']==flujo['fecha'].max()):
            pass
        else:
            self.info['Fecha_Vencimiento']=flujo['fecha'].max()
      
    def flujoVigente(self,fechaValor,fecha_fin=''):
        #determinar el flujo a cobrar
        df=self.flujo[(self.flujo['fecha']>fechaValor)]
        
        #calcular dias a cobrar de cada flujo
        df['dias']=((df['fecha']-fechaValor)/np.timedelta64(1, 'D')).astype(int)
        df['pago']=df['interes']+df['amortizacion']
        
        if(fecha_fin==''):
            return df
        else:
            return df[df.fecha<=fecha_fin]
        
    #Devuelve los dias transcurridos que genera el interes a ser pagado
    def dias_transcurridos_por_intereses(self,valor_nominal,valor_interes,tasa_interes):
        dias_transcurridos=valor_interes/valor_nominal*(365/tasa_interes)
        
        return np.around(dias_transcurridos)
        
    def fecha_ultimo_pago(self,fechaValor):
        #Definir si se pago cupon antes de la fechaValor
        if(pd.notna(self.flujo[self.flujo['fecha']<fechaValor]['fecha'].max())):
            
            return self.flujo[self.flujo['fecha']<fechaValor]['fecha'].max()
         
        elif(pd.notna(self.info['Fecha_Emision'])):
            
            #Descartar que la fechaValor no sea antes que la emision
            if(fechaValor<self.info['Fecha_Emision']):
                print('Error: La fecha ',fechaValor,' es previo a la fecha de emision')
                return np.nan
            else:
                return self.info['Fecha_Emision']
        
        elif(pd.notna(self.flujo[self.flujo['fecha']>fechaValor]['fecha'].min())):
            
            flujo=self.flujoVigente(fechaValor)
            
            dias=self.dias_transcurridos_por_intereses(flujo['amortizacion'].sum(),
                                                  flujo['interes'].iloc[0],
                                                  self.info['TasaCupon'])
            fecha=flujo['fecha'].iloc[0]-timedelta(dias)
            return fecha
            
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
    
    def interesCorrido(self,fechaValor):
        dias_corridos=self.diasCorridos(fechaValor)
        valorNominal=self.valorNominalUnitario(fechaValor)
        tasaCupon=self.info['TasaCupon']
        interes_corrido=tasaCupon/365*dias_corridos*valorNominal
        return interes_corrido
    
    def maduracion_dias(self,fechaValor):
        fecha_vencimiento=self.info['Fecha_Vencimiento']
        maduracion=int((fecha_vencimiento-fechaValor)/timedelta(days=1))
        return maduracion
    
    def tasaNominal_de_tir(self,irr,periodicidad):
        tasa_nominal=round(((1+irr)**(1/periodicidad)-1)*periodicidad,6)
        return tasa_nominal
    
    def tir_de_tasaNominal(self,tasa_nominal,periodicidad):
        irr=round((1+tasa_nominal/periodicidad)**periodicidad-1,6)
        return irr
    
    def tasaNominal_directa(self,fechaValor,valorActual):
        flujo=self.flujoVigente(fechaValor)
        maduracion=self.maduracion_dias(fechaValor)
        tasa_nominal_directa=(flujo['pago'].sum()/valorActual-1)*(365/maduracion)
        return tasa_nominal_directa
    
    def rendimiento(self,fechaValor,valorActual):
        #Definir el flujo residual
        flujo=self.flujoVigente(fechaValor)
        
        return irr(flujo.pago,flujo.dias,valorActual)
    
    def valorActual(self,irr,fechaValor):
        flujo=self.flujoVigente(fechaValor)
        try:
            value=npv(irr,flujo['pago'],flujo['dias'])
            return value
        except:
            print('ERROR')
            print(self.isin,flujo['dias'])
            
    def duration(self,irr,fechaValor):
        #definir flujo
        flujo=self.flujoVigente(fechaValor)
        #calcular las variables
        valor_tiempo_ponderado=npv(irr,flujo['pago']*flujo['dias'],flujo['dias'])
        valor_actual = self.valorActual(irr,fechaValor)
        #calcular duration
        duration = valor_tiempo_ponderado/valor_actual
        #devolver calculo
        return duration
    
    def periodicidad_pago_interes(self):
        try: 
            plazo_anos=(self.info.Fecha_Vencimiento-self.info.Fecha_Emision).days/365
            cantidad_cupones=self.flujo.interes.count()
            return round(cantidad_cupones/plazo_anos)
        except:
            print('Error: Fecha_Emision esta vacio')
            return np.nan
    
    def valorNominalUnitario(self,fechaValor=''):
        if(fechaValor==''):
            return self.flujo.amortizacion.sum()
        else:
            return self.flujoVigente(fechaValor).amortizacion.sum()
        
    def valor_por_precioClean(self,fechaValor,precio):
        valorNominal=self.valorNominalUnitario(fechaValor)
        precioDirty=precio+round(self.interesCorrido(fechaValor)/valorNominal*100,4)
        
        valorActual=precioDirty/100.00*valorNominal
        
        irr=self.rendimiento(fechaValor,valorActual)
        
        return self.datosValor(irr, fechaValor)
    
    def valor_por_precioDirty(self,fechaValor,precioDirty):
        valorNominal=self.valorNominalUnitario(fechaValor)
        
        valorActual=precioDirty/100.00*valorNominal
        
        irr=self.rendimiento(fechaValor,valorActual)
        
        return self.datosValor(irr, fechaValor)
    
        
    def valor_por_tasaNominal(self,fechaValor,tasa_nominal,periodicidad):
        irr=self.tir_de_tasaNominal(tasa_nominal,periodicidad)
        return self.datosValor(irr, fechaValor)
    
    def datosValor(self,irr,fechaValor):
        #Valoracion segun rendimiento
        valorActualNeto=self.valorActual(irr,fechaValor)

        #Valor nominal unitario
        valorNominal=self.valorNominalUnitario(fechaValor)
              
        #Tasa cupon
        tasaCupon=self.info['TasaCupon']
        #Dias corridos desde pago ultimo cupon        
        dias_corridos=self.diasCorridos(fechaValor)
        
        #Dias desde el ultimo pago cupon
        if(tasaCupon>0):
            interes_corrido=self.interesCorrido(fechaValor)
        else:
            interes_corrido=0

        #Maduracion y Duration Mcauly del instrumento
        maduracion=self.maduracion_dias(fechaValor)
        duration=self.duration(irr,fechaValor)
        
        periodicidad=self.periodicidad_pago_interes()
        
        #Tasa nominal en base a la TIR tomando la periodicidad de pago de interes
        tasa_nominal_tir=self.tasaNominal_de_tir(irr,periodicidad)
        
        #Precios
        pdirty=round(valorActualNeto/valorNominal*100,4)
        pclean=round((valorActualNeto-interes_corrido)/valorNominal*100,4)
        pBase=round((valorActualNeto/((1+irr)**(dias_corridos/365)))/valorNominal*100,4)
        
        #Carga de datos  
        datos={'tasa_efectiva':irr,
               'tasa_nominal':tasa_nominal_tir,
               'precio_dirty':pdirty,
               'precio_clean':pclean,
               'precio_base':pBase,
               'interes_corrido':round(interes_corrido/valorNominal*100,4),
               'duration':round(duration/365,2),
               'maduracion':round(maduracion/365,2)}
        
        #Transformar a Serie
        return pd.DataFrame(data=datos,index=[0]).loc[0]
    
class CDA(Bono):
    
    def __init__(self,flujo,tasa_interes,serie='',emisor='',tipo_instrumento=''
                 ,moneda='',fecha_colocacion=''):
        #identificacion del bono
        self.isin=serie
        
        #flujo de pago
        self.flujo=flujo.loc[:,['fecha','interes','amortizacion']]
        #Ordenar por fecha
        self.flujo=self.flujo.sort_values(by='fecha')
        #calcular el flujo de pago sin discriminar el proposito 
        self.flujo['pago']=self.flujo['interes']+self.flujo['amortizacion']
        
        #determinar fecha colocacion/emision
        if(fecha_colocacion==''):
            self.fecha_ultimo_pago(flujo.iloc[0,0])
        else:
            pass
        #Informacion del Bono
        df=pd.DataFrame(data={'serie':serie,
                                'isin':'',
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
    def __init__(self,flujos,operaciones=None,calificaciones='',isin=''):
        
        #Cargar los instrumentos con la condicion que tenga flujo
        self.instrumentos=pd.DataFrame(index=flujos.pivot_table(index='isin').index)
        
        for i in self.instrumentos.index:
            self.instrumentos.loc[i,'bono']=Bono(i,flujos[flujos['isin']==i])
        print("Instumentos cargados")
        
        #Operaciones del mercado
        if(type(operaciones)==type(pd.DataFrame())):
            self.operaciones=operaciones
            
        #     self.operaciones=self.operaciones.rename(columns={'emisor/calificacion':'calificacion'})
            
        #     #Carga de calificacion simple
        #     for row in self.operaciones.itertuples():
        #         calif=str(row.calificacion).replace('py','')
        #         calif=calif.replace('+','')
        #         calif=calif.replace('-','')
        #         self.operaciones.loc[row.Index,'calif_simple']=calif
            
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
                                     (self.operaciones['fecha_operacion']<=fecha_curva)&
                                     (self.operaciones['fecha_operacion']>=fecha_rango)]
        
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
    
    def history_pClean(self,bono_isin,frecuencia='d'):
            #definir el bono
            bono=self.getBond(bono_isin)
            #Captar las operaciones historicas del bono
            historia_operaciones=self.operaciones[self.operaciones['isin']==bono_isin].sort_values(by=['fecha_operacion','numero_operacion'])
            
            #Definir fechas principales
                #Fecha de la operaciones
            fechas_operaciones=pd.to_datetime(historia_operaciones['fecha_operacion'].values)
                #Fecha de flujo de pagos
            fechas_flujos=pd.to_datetime(bono.flujo['fecha'].values)

            #Determinar fecha inicio de datos
            fecha_inicio_operaciones=fechas_operaciones.min()
            
            #Ultima fecha de operaciones cargadas
            fecha_maxima=self.operaciones['fecha_operacion'].max()
            #Cargar los dias segun rango de fechas de fecha_inicio hasta fecha_final
            historia = pd.DataFrame({'date':pd.date_range(start=fecha_inicio_operaciones, 
                                                             end=fecha_maxima
                                                            ,freq=frecuencia)})

            #primera operacion
            ultima_operacion=historia_operaciones[historia_operaciones['fecha_operacion']==fecha_inicio_operaciones].iloc[-1]
            
            #Datos de valoracion de la primera operacion
            datos=bono.valor_por_precioDirty(ultima_operacion.fecha_operacion,ultima_operacion.precio)
            #Carga del primer dato
            historia.loc[0,'precio_clean']=datos['precio_clean']
            
            for row in historia.loc[1:].itertuples():

                if(row.date in fechas_operaciones):
                    ultima_operacion=historia_operaciones[historia_operaciones['fecha_operacion']==row.date].iloc[-1]
                    datos=bono.valor_por_precioDirty(ultima_operacion.fecha_operacion,ultima_operacion.precio)

                    fechas_operaciones=fechas_operaciones[~(fechas_operaciones==row.date)]

                elif(row.date in fechas_flujos):
                    datos=bono.datosValor(ultima_operacion['ytm'],row.date)

                historia.loc[row.Index,'precio_clean']=datos.at['precio_clean']
                

            return historia