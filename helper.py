from scipy.interpolate import interp1d
from conductor import conductor
import math
import cmath


def calculate_mev(length, power, Nc):
    standard_voltage = [33, 132, 220, 500, 765]
    mev = 5.5 * ( (length/1.6) + (power*1000)/(150*Nc*0.9)   )**0.5
    standard_voltage.append(mev)
    standard_voltage.sort()
    index =standard_voltage.index(mev)
    if index ==0:
        return standard_voltage[1]
    elif index == (len(standard_voltage)-1):
        return standard_voltage[-2]
    else:
        diff_1 = abs(mev - standard_voltage[index-1])
        diff_2 = abs(mev - standard_voltage[index+1])

        if diff_1 < diff_2:
            return standard_voltage[index-1]
        else:
            return standard_voltage[index+1]

def technical_requirements(length):
    x = length
    km = [80, 160]
    mf_limit = [2.75, 2.25]

    interpolate_for = length

    mf_interpolate = interp1d(km, mf_limit, fill_value='extrapolate')

    return(mf_interpolate(x))

def print_data(data, power, length):
    print(' Line length \t\t\t: {} km'.format(length))
    print(' Power to be transmitted \t: {} MW'.format(power))
    print(' Impedance of transmission line : {} ohm'.format(data['Zc']))
    print(' Most Economical Voltage \t: {} KV'.format(data['mev']))
    print(' mf limit \t\t\t: {}'.format(data['mf_limit']))
    print(' SIL\t\t\t\t: {} MW'.format(data['SIL']))
    print(' mf calc \t\t\t: {}\n'.format(data['mf_calc']))

def calculate_clearance(data, Nc):
    voltage = data['mev']
    max_voltage = round((voltage / math.sqrt(3)) * 1.1 * math.sqrt(2), 3)
    min_ground_clearance = (((voltage - 33) / 33) + 17) # ft
    a = 1 * max_voltage + 20 # minimum air clearance 
    cl = 2 * a # cross-arm length 
    l = a * math.sqrt(2) # insulator string length
    b = 2 * a # width of the tower
    c = cl + b + cl # horizontal separation between conductors
    y_deno = 1 - ( ((l+a)/cl) ** 2 ) * (0.3)**2 
    y = (l + a) / math.sqrt(y_deno) # vertical spacing between conductor
    
    if Nc == 1:
      d = math.sqrt(3) * ( b/2 + cl ) # height of earth wire from topmost conductor
    else: 
      d = cl/math.tan(math.pi/6)

    print(f' Minimum air clearance [a]\t\t\t\t: {a} cm')
    print(f' Cross-arm length [cl]\t\t\t\t\t: {cl} cm')
    print(f' Insulator string length [l]\t\t\t\t: {round(l,3)} cm')
    print(f' Width of the tower [b]\t\t\t\t\t: {b} cm')
    print(f' Horizontal separation between conductor [c]\t\t: {c} cm')
    print(f' Vertical spacing between conductors [y]\t\t: {round(y,3)} cm')
    print(f' Height of earth wire from top most conductor [d]\t: {round(d,3)} cm')
    return {'y':y, 'c':c}

def calculate_disc(MEV):
  NAC = 1.1
  FS = 1.2
  FWR = 1.15
  EF = 0.8
  SSR = 2.8
  SIR = 1.2

  system_voltage = {
      '33': {
          'max_voltage':123,
          'one_min_dry': 215,
          'one_min_wet': 185,
          'impulse': 450
      },
      '132': {
          'max_voltage':145,
          'one_min_dry': 265,
          'one_min_wet': 230,
          'impulse': 550
      },
      '220': {
          'max_voltage':245,
          'one_min_dry': 435,
          'one_min_wet': 395,
          'impulse': 900
      },
      '400': {
          'max_voltage':420,
          'one_min_dry': 760,
          'one_min_wet': 680,
          'impulse': 1550
      },
  }
  no_of_discs = []
  one_min_dry = [80,115,215,270,325,380,435,486,535,585,635,685,730,775,820,865]
  one_min_wet = [50,90,130,170,210,250,290,330,370,410,450,485,510,585,590,620]
  impulse = [50,225,335,440,525,610,695,780,860,945,1025,1105,1185,1265,1345,1425] 


  voltage = system_voltage[str(MEV)]
  a = voltage['one_min_dry'] * NAC * FS * FWR # 1-min dry equivalent withstand test
  b = voltage['one_min_wet'] * NAC * FS * FWR # 1-min wet equivalent withstand test
  c = voltage['max_voltage'] * EF *  math.sqrt(2) * NAC * FS * FWR # temporary o/v withstand test
  d = voltage['impulse'] * NAC * FS * FWR # impulse withstand test
  max_voltage = (MEV / math.sqrt(3)) * 1.1 * math.sqrt(2) * SSR 
  e = max_voltage * SIR * NAC * FS * FWR 
  
  no_of_discs.append(choose_no_of_discs(one_min_dry, a))
  no_of_discs.append(choose_no_of_discs(one_min_wet, b))
  no_of_discs.append(choose_no_of_discs(one_min_wet, c))
  no_of_discs.append(choose_no_of_discs(impulse, d))
  no_of_discs.append(choose_no_of_discs(impulse, e))

  print(' Total number of insulator disc\t\t\t\t: {}'.format(max(no_of_discs)))

  

def choose_no_of_discs(table, ov):
    for x in range(len(table)):
        if table[x] < ov:
            pass
        else:
            noi = x+1
            return noi

  
def conductor_selection(Power, voltage,length, Nc, skip_conductor=[]):
    phase_angle = 0.9
    current = (Power * 10**3) / (math.sqrt(3)*voltage*phase_angle*Nc)
    current_angle = -math.acos(phase_angle)
    current_rect = cmath.rect(current, current_angle)
    current_polar = cmath.polar(current_rect)
    selected_conductor = select_conductor(current,skip_conductor) 
    if selected_conductor == '':
        return {'selected_conductor': None}
    for i in range(100):
        R_20 = conductor[selected_conductor]['resistance'] * length
        R_65 = R_20 * (1 + 0.004 * (65-20) ) 
        power_loss = (3 * current**2 * Nc * R_65) / 10**6
        efficiency = 1 - power_loss/Power
        if efficiency > 0.94:
            print(f' The conductor selected according to efficiency is\t: {selected_conductor}')
            return {'selected_conductor':selected_conductor, 'R_65': R_65}
            break
        else:
            skip_conductor.append(selected_conductor)
            selected_conductor = select_conductor(current,skip_conductor)
            if selected_conductor == '':
                return {'selected_conductor': None}

def select_conductor(ampacity,skip_conductor=[]):
    selected = ''
    prev_difference = 1000
    for key in conductor:
        if key not in skip_conductor:
            difference = conductor[key]['current'] - ampacity
            if difference > 0 and difference < prev_difference:
                selected = key
                prev_difference = difference
            else:
                pass
        else:
            pass 
    return selected 


def GMR(y, c, Nc, radius):
    if Nc == 2:
        '''
        FOR GMR
            a       c'
                        |y
            b       b'
                        |y
            c       a'
            ____c____
        
        GMR = root(Daa Daa' Da'a Da'a')
            = root(r' Daa' Da'a r')

        '''
        Da_a = 0.768 * radius * ( 10 ** - 3 )
        Da_ad = math.sqrt( (2*y) ** 2 + c**2) * ( 10 ** - 2 )

        Db_b = Da_a
        Db_bd = c * 10 ** -2
        Db = (Db_b ** 2 * Db_bd ** 2) ** (1/4)
        Da = (Da_a ** 2 * Da_ad ** 2) ** (1/4)
        
        Dc = Da 
        
        GMR_L = (Da * Db * Dc) ** (1/3)

        Da_a = radius * (10 ** -3 )
        Da_ad = Da_ad
        Db_b = Da_a
        Db_bd = Db_bd
        Db = (Db_b ** 2 * Db_bd ** 2) ** (1/4)
        Da = (Da_a ** 2 * Da_ad ** 2) ** (1/4)
        Dc = Da

        GMR_C = (Da * Db * Dc ) ** (1/3)
        return {'GMR_L': GMR_L , 'GMR_C': GMR_C}
    else:
        GMR_L = 0.768 * radius * (10 ** -3 )
        GMR_C = radius * ( 10 ** -3)
        return {'GMR_L': GMR_L , 'GMR_C':GMR_C} 
        
def GMD(y, c, Nc, radius):
    if Nc == 2:
        Da_b = y 
        Da_bd = math.sqrt(y**2 + c ** 2)
        Dad_b = Da_bd
        Dbd_ad = Da_b 
        Dab = ( (Da_b * Da_bd * Dad_b * Dbd_ad) ** (1/4) ) * (10 ** -2)
        Dbc = Dab 

        Da_c = 2*y
        Da_cd = c
        Dad_c = c 
        Dad_cd = 2*y 
        Dac = ( (Da_c * Da_cd * Dad_c * Dad_cd) ** (1/4)) * (10 ** -2)
        GMD = (Dab * Dbc * Dac) ** (1/3)
        return {'GMD' : GMD}
    else:
        Da_b = math.sqrt((y/2)**2 + c**2)
        Db_c = Da_b
        Da_c = y
        GMD = ( Da_b * Db_c * Da_c ) ** (1/3)
        return {'GMD': GMD * (10 ** -2)}  
                 
def calculate_LC(clearance, conductor_name, length, Nc):
    gmr = GMR(clearance['y'], clearance['c'], Nc, conductor[conductor_name]['diam']/2)
    gmd = GMD(clearance['y'], clearance['c'], Nc, conductor[conductor_name]['diam']/2)
    L = 2 * (10 ** -7) * math.log(gmd['GMD']/gmr['GMR_L']) * 1000
    C = (2 * math.pi * 8.854 * (10 ** -12) * 1000) / math.log(gmd['GMD']/gmr['GMR_C'])
    total_L = L * length
    total_C = C * length
    return {'L': total_L, 'C': total_C}

def calculate_VR(L, C, R, full_data, power, Nc, length):
    Xl = 2 * math.pi * 50 * L 
    Xc = 2 * math.pi * 50 * C
    Z = complex(R, Xl)
    Y = complex(0, Xc)
    
    # ABCD parameters
    if length > 80:
        A = 1 + (Y * Z) / 2
        D = A 
        B = Z 
        C = Y * (1 + (Y * Z)/4)
    else:
        A=D=1
        B = Z
        C = 0
    
    # Voltage regulation

    Ir = (power * 10**3) / (math.sqrt(3) * full_data['mev'] * 0.9 * Nc)
    Ir_ang = -math.acos(0.9)
    Ir_rect = cmath.rect(Ir, Ir_ang)
    Vs_fl = (A * (full_data['mev'] * 1000 / math.sqrt(3)) + Ir_rect * B) * 10 ** -3
    Vr_fl = full_data['mev'] / math.sqrt(3)
    VR = (abs(Vs_fl)/abs(A) - Vr_fl)/Vr_fl
    VR = VR * 100
    return round(VR,3)


    

