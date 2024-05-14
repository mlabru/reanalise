###########################################################################################################################
# Este script obtem variáveis meteorológicas nas latitudes e longitudes de aeroportos, utilizando dados de reanálise ERA5 #
###########################################################################################################################

function reanalise (args)

latit = subwrd(args,1)
longi = subwrd(args,2)
aero = subwrd(args,3)
anomes = subwrd(args,4)

fm1 = '%6.1f'

'reinit'

# Single levels
'sdfopen 'anomes'_single_levels.nc'

# Pressure levels 
'sdfopen 'anomes'_pressure_levels_1000.nc' 
'sdfopen 'anomes'_pressure_levels_850.nc' 


tt = 1

'set t last'
'q dims'
res = sublin(result,5)
ultimo_tt = substr(res,41,3)


while (tt <= ultimo_tt)  

'set t ' tt

'q dims'
res  = sublin(result,5)
hdmy = substr(res,23,12)
h = substr(hdmy,1,3)  
d = substr(hdmy,4,2)
m = substr(hdmy,6,3)  
y = substr(hdmy,9,4) 

if(m='JAN');mesc=01;endif
if(m='FEB');mesc=02;endif
if(m='MAR');mesc=03;endif
if(m='APR');mesc=04;endif
if(m='MAY');mesc=05;endif
if(m='JUN');mesc=06;endif
if(m='JUL');mesc=07;endif
if(m='AUG');mesc=08;endif
if(m='SEP');mesc=09;endif
if(m='OCT');mesc=10;endif
if(m='NOV');mesc=11;endif
if(m='DEC');mesc=12;endif 

'set lat ' latit
'set lon ' longi

#############################################
# MONTA O NOME E O CABEÇALHO DO ARQUIVO .csv
#############################################

if (h = 00Z)
#saida = aero.i'_'d mesc y'.txt'
saida = anomes'/'aero'_'d mesc y'.csv'
cab = ICAO';'data';'hora';'prec';'dirv';'magv';'rajv';'qfe';'qnh';'temp';'td';'tbu';'cnuv';'abnv';'umir';'visi

rc = write(saida,cab)
endif

##########################################################
# OBTÊM AS VARIÁVEIS DE FORMA HORÁRIA PARA CADA AERÓDROMO
##########################################################

# precipitação total, em mm
'd tp*1000'
wrd = subwrd(result,4)
tp = math_format(fm1,wrd)


# direção do vento, em graus
'define v = ((1/0.0175432) * atan2(u10,v10)) + 180'
'd v'              
wrd = subwrd(result,4)
v = math_nint(wrd)


# magnitude do vento, em m/s
'define mgm = mag(u10,v10)'
'd mgm'
wrd = subwrd(result,4)
mgm = math_nint(wrd)


# magnitude do vento, em kt (nós)
'define mg = mag(u10,v10)'
'd mg*1.94'
wrd = subwrd(result,4)
mg = math_nint(wrd)


# rajada de vento, em kt (nós)
'd i10fg*1.94'
wrd = subwrd(result,4)
i10fg = math_nint(wrd)


# pressão a superfície, em hPa (qfe)
'define p = sp/100'
'd p'
wrd = subwrd(result,4)
p = math_format(fm1,wrd)


# pressão ao nível médio do mar, em hPa (qnh)
'define pnm = msl/100'
'd pnm'
wrd = subwrd(result,4)
pnm = math_format(fm1,wrd)


# temperatura à 2m, em graus Celsius
'define t = t2m-273.15'
'd t'
t2 = subwrd(result,4)
t = math_format(fm1,t2)


# cobertura de nuvem, de 1 a 8
'd tcc*8'
wrd = subwrd(result,4)
tcc = math_nint(wrd)

######################################################
# umidade relativa, em %                                   
'd r.2'
umi2= subwrd(result,4)
umi = math_nint(umi2)


# altura da base da nuvem, em decâmetros
'd cbh/10'
wrd = subwrd(result,4)
abn = math_nint(wrd)

if (wrd = -999000000.00)
abn = 'NULL'
endif


# temperatura do ponto de orvalho, em graus Celsius
'define tpo = d2m-273.15'
'd tpo'
wrd = subwrd(result,4)
tpo = math_format(fm1,wrd)


# temperatura do bulbo úmido, em graus Celsius
pass1 = math_pow (umi2 + 8.313659,0.5)
pass2 = math_atan2 (0.151977*pass1,1)
pass3 = math_atan2 (t2 + umi2,1)
pass4 = math_atan2 (umi2-1.676331,1)
pass5 = math_pow (umi2,1.5)
pass6 = (0.00391838*pass5)
pass7 = math_atan2 (0.023101*umi2,1)
BULBUMI = (t2*pass2+pass3-pass4+pass6*pass7-4.686035)
buu = substr(BULBUMI,1,5)
tbum = math_format(fm1,buu)


# temperatura do em 850hPa, em graus Celsius
'define t850 = t.3-273.15'
'd t850'
wrd = subwrd(result,4)
t850 = math_format(fm1,wrd)


# visibilidade Wantuch - 850 hpa até a superfície, em decâmetros
# vento em metros por segundo e temperaturas em graus Celsius
'define wind = sqrt(pow(u.3,2)+pow(v.3,2))'
'define FH = 2*abs(t-t850)+2*(t-tpo)+2*mgm'
'define vis = -1.33+0.45*FH'
'define visb = (vis*1000)'
'd visb/10'
wrd = subwrd(result,4)
bat = math_nint(wrd)

###########################################################
# ESCREVE OS DADOS EM ARQUIVO .txt
###########################################################
cab = aero';'d mesc y';'h';'tp';'v';'mg';'i10fg';'p';'pnm';'t';'tpo';'tbum';'tcc';'abn';'umi';'bat 
src  = write(saida,cab)

###########################################################

tt = tt + 1
endwhile
