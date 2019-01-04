# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import plotRadarPolares as plotRad2
import maskFunction as mk
import os
import sys
reload(plotRad2)
reload(mk)




def createCircularMask(height, width, center=None, radius=None):
    '''
        Funcion para hacer una máscara circular a una matriz
        height: altura de la matriz en pixeles
        width: ancho de la matriz en pixeles
        center: el default es None y la funcion lo calcula pero se puede especificar el pixel donde está el centro
        radius: el default es None y la funcion lo calcula automaticamente pero se puede especificar el radio en pixeles
    '''
    if center is None:
        center = [int(width / 2), int(height / 2)]
    if radius is None:
        radius = min(center[0], center[1], width - center[0], height - center[1])
        print radius
    Y, X = np.ogrid[:height, :width]
    distFromCenter = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
    mask = distFromCenter <= radius
    return mask


def find_nearest(array, value1):
    idx1 = (np.abs(array - value1)).argmin()
    return idx1

def mask_sector(angle_range, shape, cx, cy):
    mask= np.ones(shape)
    alto, ancho = shape 
    radio =  alto / 2.
        
    x, y = np.ogrid[:shape[0], :shape[1]]
    
    tmin,tmax = np.deg2rad(angle_range)
    # ensure stop angle > start angle
    if tmax < tmin:
            tmax += 2*np.pi
    # convert cartesian --> polar coordinates
    r2 = (x-cx)*(x-cx) + (y-cy)*(y-cy)
    theta = np.arctan2(x-cx,y-cy) - tmin
    # wrap angles between 0 and 2*pi
    theta %= (2*np.pi)
    # circular mask
    circmask = r2 <= radio*radio
    # angular mask
    anglemask = theta <= (tmax-tmin)
    mask_aux = circmask*anglemask
    mask[mask_aux] = np.nan
    return mask 




# ===================================================================================== #
pathMatriz = '/home/jmvalenciap/Documents/Radar/DictMaxRef/'
pathAlturas = '/home/jmvalenciap/Documents/Radar/'

latInf, lonInf, latSup, lonSup = 5.97, -75.734, 6.53, -75.22  #zoom
# latInf, lonInf, latSup, lonSup = 5.27, -76.45, 7.10, -74.62
# latInf, lonInf, latSup, lonSup = 4., -77.8, 8.4, -73.3


# latInf, lonInf, latSup, lonSup = 4.95, -76.75, 7.4, -74.29

swept = '010'
varPolar = 'Normalizada'
nameToSave = 'ReflectividadMaximaNormalizada' + swept + '_prueba.png'

pathSave = '/home/jmvalenciap/Documents/Radar/DictMaxRef/Figuras/'
#pathSal = 'jmvalenciap@siata.gov.co:/var/www/jmvalenciap/Radar/Ver_graficas_temporales/'
# ====================================================================================== #

if swept == '005':
	lons = np.linspace(-78.116, -72.932, 1728)
	lats = np.linspace(3.604, 8.788, 1728)
else:
	lons = np.load('/home/jmvalenciap/Documents/Radar/lon.npz').items()[0][1]
	lats = np.load('/home/jmvalenciap/Documents/Radar/lat.npz').items()[0][1]

heights = np.load(pathAlturas + 'matrizAlturas' + str(float('005') / 10.) + '.npz').items()[0][1]

coordes = {'latitude': lats, 'longitude': lons}

matriz = np.load(pathMatriz + 'matrizNumeroOcurrencias' + swept + '.npz').items()[0][1]

if swept == '005':
	lat_ubicacion_radar = 6.190881
	lon_ubicacion_radar = -75.528625
	cx = find_nearest(lats, lat_ubicacion_radar)
	cy = find_nearest(lons, lon_ubicacion_radar) 
	angle_range = (153.0, 158.0)
	maskMontain = mask_sector(angle_range, matriz.shape, float(cx), float(cy))
	matriz *= maskMontain


####----- mask with shapefile
maskedMatrix = mk.add_shape_coord_from_data_array(matriz, '/home/jmvalenciap/Documents/Shapes/prueba/juanma.shp', coordes)
mask = maskedMatrix.where(maskedMatrix==0, other=np.nan)
matriz[np.isnan(mask.values)] = np.nan


if swept == '005':
	indBorrar = np.where(matriz == np.nanmax(matriz))
	matriz[indBorrar] = np.nan

# ####----- mask circular
circMask = createCircularMask(matriz.shape[0], matriz.shape[1], radius=710)
matriz[circMask == 0] = np.nan


matriz /= np.nanmax(matriz)

matriz[heights > 8] = np.nan

plotRad2.plot(matriz, lats, lons, latInf, lonInf, latSup, lonSup, 'frecuencia normalizada de reflectividades > 40 dBZ', 0, 1, 'NWSRef', 'Barrido de ' + str(int(swept)/10.) + '$^\circ$', pathSave + nameToSave)

np.savez_compressed(pathMatriz + 'matrizNumeroOcurrenciasNormalizadaEnmascarada' + swept + '.npz', matriz)

# plotRad2.plotOnlyColorBar(matriz, lats, lons, latInf, lonInf, latSup, lonSup, 'Frecuencia normalizada de reflectividades > 40 dBZ', 0, 1, 'NWSRef', 'Barrido de ' + str(int(swept)/10.) + '$^\circ$', pathSave + nameToSave)
