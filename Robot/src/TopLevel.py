import Seadmed
import Silmad

#===============================================================================
# GLOBAALSED ASJAD
#===============================================================================

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

#===============================================================================
# LEIAB SEADMED
#===============================================================================

Seadmed

#===============================================================================
# KONTROLLIB KAS ON PALL HAMBUS
#===============================================================================

while(1):
    parem.write('gb\n')
    if parem.readline() == '<b:1>\n':
        
        #=======================================================================
        # KUI ON PALL, SIIS KONTROLLIB KUMB VÄRAV ON
        #=======================================================================
        
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
            if sihik < 70:
                parem.write('-sd10')
            elif sihik > 110:
                vasak.saada('sd10')
            else:
                coil.write('k10000')        
                    
    #===========================================================================
    # KUI PALLI POLE HAMBUS, SIIS AJA PALLI TAGA
    #===========================================================================
        
    else:
        hele = pallMax
        tume = pallMin

#===============================================================================
# NÄGEMISLOOGIKA
#===============================================================================

Silmad
