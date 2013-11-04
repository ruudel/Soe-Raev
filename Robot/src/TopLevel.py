# -*- coding: utf-8 -*-
import serial


#===============================================================================
# GLOBAALSED ASJAD
#===============================================================================

seadmed = []

global parem
global vasak
global coil

global pallMin
global pallMax
global kollaneMin
global kollaneMax
global sinineMin
global kollaneMax

global tume
global hele

global sihik

#===============================================================================
# VÄRVIDE INITSIALISEERIMINE
#===============================================================================

pallMin = [0,215,140]
pallMax = [15,255,195]

kollaneMin = [25,160,110]
kollaneMax = [35,200,160]

sinineMin = [80,150,60]
sinineMax = [140,300,130]

mustMin = [95,35,0]
mustMax = [135,180,55]

#===============================================================================
# LEIAB SEADMED
#===============================================================================

for i in range(10):
    try:
        s=serial.Serial('/dev/ttyACM'+str(i),timeout=1,parity=serial.PARITY_NONE,baudrate=115200)
        s.write("?\n")
        idstr=s.readline()
        if (idstr=='<id:1>\n'):
            parem=s
            seadmed.append(parem)
        elif (idstr=='<id:2>\n'):
            vasak=s
            seadmed.append(vasak)
        else:
            coil=s
            seadmed.append(coil)
    except serial.SerialException:
        pass
if len(seadmed)<2:
    print('Mingi seade on puudu!')

#===============================================================================
# KONTROLLIB KAS ON PALL HAMBUS
#===============================================================================

while(1):
    
    #===========================================================================
    # PINGIB COILI KOGU AEG, ET SEE OLEKS ALATI VALMIS
    #===========================================================================    
    coil.write('c')
    coil.write('p')
    
    parem.write('gb\n')
    if parem.readline() == '<b:1>\n':
        
        #=======================================================================
        # KUI ON PALL, SIIS KONTROLLIB KUMB VÄRAV ON
        #=======================================================================
        coil.write('p') 
        
        parem.write('go\n')
        v=parem.readline()
        
        if v=='<0mine>\n':
            hele = sinineMax
            tume = sinineMin
            
        else:
            hele = kollaneMax
            tume = kollaneMin
            
        #=======================================================================
        # JA OTSI SEE ÜLES
        #=======================================================================
        
        if sihik > 0:
            coil.write('p') 
            if sihik < 70:
                parem.write('-sd10')
            elif sihik > 110:
                vasak.saada('sd10')
            else:
                coil.write('k10000')
        
        #=======================================================================
        # EI NÄE VÄRAVAT
        #=======================================================================
        
        else:
            parem.write('-sd10')
            vasak.prite('sd10')    
                    
    #===========================================================================
    # KUI PALLI POLE HAMBUS, SIIS AJA PALLI TAGA
    #===========================================================================
        
    else:
        hele = pallMax
        tume = pallMin
        
        parem.write('sd10')
        vasak.prite('-sd10')
