from scipy.interpolate import interp1d
from conductor import conductor
import math
import cmath
import turtle
import numpy as np


def calculate_mev(length, power, Nc):
    standard_voltage = [33, 66 ,132, 220, 500, 765]
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
    return {'a':round(a, 2),'cl':round(cl,2),'l':round(l,2),'b':round(b,2),'c':round(c,2),'y':round(y,2),'d':round(d,2)}

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
            print(f' The conductor selected according to efficiency is\t: {selected_conductor} with efficiency: {efficiency* 100} %')
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
    return {'L': total_L, 'C': total_C, 'gmd':gmd, 'gmr': gmr}

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
    return {'VR':VR, 'A':A, 'B':B, 'C':C, 'D':D}

def calculate_efficiency(Power, voltage,length, Nc,conductor_name):
    phase_angle = 0.9
    current = (Power * 10**3) / (math.sqrt(3)*voltage*phase_angle*Nc)
    current_angle = -math.acos(phase_angle)
    current_rect = cmath.rect(current, current_angle)
    current_polar = cmath.polar(current_rect)
    R_20 = conductor[conductor_name]['resistance'] * length
    R_65 = R_20 * (1 + 0.004 * (65-20) ) 
    power_loss = (3 * current**2 * Nc * R_65) / 10**6
    efficiency = 1 - power_loss/Power
    return round(efficiency * 100, 2)


def bending_moment(mev,span, Nc, Ne, conductor_name, y, d, area, length, power):
    #print(f" Calculation for {conductor_name} conductor and span length {span}")
    y = y/100
    d = d/100
    FS = 2
    alpha = conductor[conductor_name]['alpha']

    # For T1
    t1 = conductor[conductor_name]['uts'] / FS # tension at toughest condition for power conductor
    ww = conductor[conductor_name]['wp'] * 1000 * conductor[conductor_name]['diam'] * 10 ** (-3) * (2/3)
    w1 = math.sqrt(conductor[conductor_name]['wc'] ** 2 + ww**2)
    
    #For T2
    if area == '':
        area = ((math.pi * conductor[conductor_name]['diam'] ** 2) /4) * 10 ** -6
    else:
        area = area * 10 ** -4

    k1 = ((((w1 ** 2) * ((span/1000) ** 2)) / (24 * (t1 ** 2)) )+ alpha * 27) - (t1/(conductor[conductor_name]['ym'] * 10**4 * area))
    k2 = k1 * conductor[conductor_name]['ym'] * 10**4 * area
    k3 = ((conductor[conductor_name]['wc'] ** 2 * (span/1000) ** 2) / 24) * area * conductor[conductor_name]['ym'] * 10**4
    coeffs = [1, k2, 0, -k3]
    t2 = abs([x for x in np.roots(coeffs) if x.imag == 0][0])
    
    #For T3
    k2_d = -t2 + alpha * (65-27) * area * conductor[conductor_name]['ym'] * 10 ** 4 + ((w1 ** 2 * (span/1000) ** 2) / (24 * t2 ** 2) * area * conductor[conductor_name]['ym'] *10**4)
    coeffs = [1, k2_d, 0 , -k3]
    t3 = abs([x for x in np.roots(coeffs) if x.imag == 0][0])

    Dmax = ((conductor[conductor_name]['wc'] * (span * 0.5/1000)**2) / (2 * t3)) * 1000

    ###############################

    hg = ((mev * 1.1 - 33)/33 + 17) * 0.3048
    h1 = hg + Dmax
    if Nc == 1:
        h2 = h1 + y/2
        h3 = h2 + y/2
        Ht = h3 + d
    else:
        
        h2 = h1 + y
        h3 = h2 + y
        Ht = h3 + d

    # selection of earth wire
    #For GUINEA
    # print(conductor_name, Ht, Dmax,)
    uts = 6664
    T1ew = uts/2

    dcrew = 14.6/1000

    #Bending moment calculation

    Fwp = (2/3) * (conductor[conductor_name]['diam']/1000) * span
    
    Fwp = Fwp * conductor[conductor_name]['wp']
    
    Fwe = (2/3) * dcrew * span
    Fwe = Fwe * conductor[conductor_name]['wp']
    
    BMPw = Fwp * Nc * (h1 + h2 + h3)
    BMEw = Fwe * Ne * Ht
    BMPt = 2 * t1 *( math.sin(math.radians(1)) * 0.8 + math.sin(math.radians(15/2)) * 0.15 + math.sin(math.radians(15))*0.05) * Nc * (h1+h2+h3)
    BMPe = 2 * T1ew * ( math.sin(math.radians(1)) * 0.8 + math.sin(math.radians(15/2)) * 0.15 + math.sin(math.radians(15))*0.05)  * Nc * Ht
    TBM = BMPw + BMEw + BMPt + BMPe
    tower_weight = 0.000631 * Ht * math.sqrt(TBM * FS) 
    No_tower = round(((length * 10 ** 3) / span) + 1)
    Cost_per_tower = 150000 * tower_weight
    Cost_per_length = 150000 * tower_weight * (No_tower / length)
    return {
        'Nc': Nc,
        'span': span,
        't1': round(t1,2),
        't2': round(t2,2),
        't3': round(t3,2),
        'h1': round(h1,2),
        'h2': round(h2,2),
        'h3': round(h3,2),
        'Ne': Ne,
        'T1ew': round(T1ew,2),
        'BMPw': round(BMPw),
        'BMEw': round(BMEw,2),
        'BMPt': round(BMPt,2),
        'BMPe': round(BMPe,2),
        'TBM': round(TBM,2),
        'conductor': conductor_name,
        'k1': k1,
        'k2': k2,
        'k3': k3,
        'weight': round(tower_weight,4),
        'num_tower': math.ceil(No_tower),
        'cpt': round(Cost_per_tower,4),
        'cpl': round(Cost_per_length,4),
        'length': length,
        'power': power,
        'mev': mev
    }

#bending_moment(132,250, 2, 2, 'zebra', 358,479,4.845)



def print_tension(data):
    print('_'*100)
    print(" SN\tSpan(m)\tt1(kg)\tt2(kg)\tt3(kg)\t\th1(m)\th2(m)\th3(m)\tT1ew(kg)\tBMPw(kg-m)\tBMEwkg-m)\tBMPtkg-m)\tBMPekg-m)\tTBMkg-m)")
    prev = data[0]['conductor']
    print(f"Conductor {data[0]['conductor']}")
    for i in range(len(data)):
        if i != 0:
            prev = data[i-1]["conductor"]
        if( prev != data[i]["conductor"]):
            print(f"Conductor {data[i]['conductor']}")
        t = data[i]
        print(" {:<3}\t{}\t{:<7}\t{:<7}\t{:<10}\t{:<7}\t{:<7}\t{:<7}\t{:<7}\t\t{:<7}\t\t{:<10}\t{:<10}\t{:<10}\t{:<7}\t".format(i, t['span'], t['t1'], t['t2'], t['t3'], 
        t['h1'], t['h2'], t['h3'], t['T1ew'], t['BMPw'], t['BMEw'],t['BMPt'], t['BMPe'],t['TBM']))

def print_economic_data(data):
    print('_'*100)
    print(" SN\tSpan(m)\tweight(tonnes)\tTowers\tCost per Tower\tCost/length\tESpan\tMin cost\tCapitalCost\tConductorcost\tPowerloss\tEloss\t\tAnnual cost per km\t")
    prev = data[0]['conductor']
    print(f"COnductor {data[0]['conductor']}")
    conductor_name = data[0]['conductor']
    for i in range(len(data)):
        if i != 0:
            prev = data[i-1]["conductor"]
        if( prev != data[i]["conductor"]):
            print(f"Conductor {data[i]['conductor']}")
        t = data[i]
        conductor_name = t['conductor']
        min_cost = []
        for x in data:
            if x['conductor'] == conductor_name:
                min_cost.append({'span':x['span'], 'cpl':x['cpl']})
        
        span_eco = min_cost[0]['span']
        cpl = min_cost[0]['cpl']
        
        for x in min_cost:
            if(x['cpl'] < cpl):
                cpl = x['cpl']
                span_eco = x['span']
            else:
                continue
        conductor[conductor_name]['span'] = span_eco
        conductor[conductor_name]['cpl'] = cpl

        min_cost = []


        c_al = 20105
        c_steel = 150000
        wt_al = conductor[conductor_name]['wa']
        wt_steel = conductor[conductor_name]['ws']
        LF = 0.5
        LLF = 0.2 * LF + 0.8 * LF ** 2
        PU_cost = 7.5
        n = 25 
        rate = 0.1
        Annuity_factor = (rate * (1+rate) ** n) / ((1+rate)**n - 1)
        power_conductor_cost = (c_al * wt_al + c_steel * wt_steel) * data[i]['Nc'] * 3
        Capital_cost = power_conductor_cost + conductor[conductor_name]['cpl']
        # print(conductor_name, Capital_cost, Annuity_factor, power_conductor_cost)
        Annual_cost = Annuity_factor * Capital_cost
        R_65 = conductor[conductor_name]['resistance']  * (1 + 0.004 * (65-20) ) 

        phase_angle = 0.9
        I = (data[i]['power'] * 10**3) / (math.sqrt(3)*data[i]['mev']*phase_angle*data[i]['Nc'])


        Power_loss = round(3 * I**2 * R_65 * data[i]['Nc'],3)
        
        Energy_loss_cost = Power_loss * LLF * 365 * 24 * 10 ** -3 * PU_cost
        #print(conductor_name, power_conductor_cost)
        TAC = round(Energy_loss_cost + Annual_cost,2)


        print(" {:<3}\t{}\t{:<10}\t{:<7}\t{:<10}\t{:<10}\t{}\t{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}".format(i, t['span'], t['weight'], t['num_tower'], t['cpt'], t['cpl'],conductor[conductor_name]['span'],conductor[conductor_name]['cpl'],round(Capital_cost,2),round(power_conductor_cost,2),round(Power_loss,2), round(Energy_loss_cost,2) ,TAC))

def final_op(clearance, conductor_name, length, Nc, power, full_data,mev):
    diam = conductor[conductor_name]['diam']
    R_20 = conductor[conductor_name]['resistance'] 
    R_65 = R_20 * (1 + 0.004 * (65-20) ) * length
    LC = calculate_LC(clearance, conductor_name, 1, Nc)
    ABCD = calculate_VR(LC['L'], LC['C'], R_65, full_data, power, Nc, length)
    efficiency = calculate_efficiency(power, mev,length, Nc,conductor_name)
    # print(LC)


def print_the_tower(obj):

    a = obj['a'] * 0.5
    cl = obj['cl'] * 0.5
    l = obj['l'] * 0.5
    b = obj['b'] * 0.5
    c = obj['c'] * 0.5
    y = obj['y'] * 0.5
    d = obj['d'] * 0.5
    scr = turtle.Turtle()
    scr.width(2)
    # beginning point
    scr.hideturtle()
    scr.penup()
    scr.goto(0,350)
    scr.showturtle()
    scr.pendown()

    #earth wire
    scr.forward(200)
    scr.backward(400)
    scr.color('blue')
    scr.write('Earthwire', move=False, align="left")
    scr.color('black')
    scr.forward(200)
    #earth wire done

    #tower width (b)
    scr.forward(b/2)
    scr.right(90)

    scr.penup()
    scr.forward(d-l-100)
    scr.pendown()
    scr.forward(y+d-(d-l-100))
    scr.right(90)
    scr.forward(b)
    scr.color('blue')
    scr.write(f'Width of the tower = {b*2} cm')
    scr.color('black')
    scr.right(90)
    scr.forward(y+d-(d-l-100))
    scr.penup()
    scr.forward(d-l-100)
    scr.pendown()

    scr.right(90)

    scr.forward(b)
    scr.right(90)
    scr.penup()
    scr.forward(d-l)
    scr.pendown()
    scr.left(90)
    scr.forward(cl/2)
    scr.color('blue')
    scr.write(f'cl = {cl*2} cm')
    scr.color('black')
    scr.forward(cl/2)
    scr.right(90)
    scr.forward(l)
    scr.color('blue')
    scr.write(f'   l={l*2} cm')
    scr.color('black')
    scr.penup()
    scr.left(90)
    scr.forward(40)
    scr.pendown()
    scr.right(90)
    scr.color("green")
    scr.forward(200/2)
    scr.color("blue")
    scr.write(f"  y = {y*2} cm")
    scr.color("green") # 100-l+100+l
    scr.forward(200/2)
    scr.backward(200)
    scr.left(90)
    scr.penup()
    scr.backward(40)
    scr.color('black')
    scr.setheading(270)
    scr.heading()
    scr.penup()
    scr.left(90)
    scr.forward(80)
    scr.pendown()
    scr.color('green')
    scr.left(90)
    scr.forward((d)/2)
    scr.color('blue')
    scr.write(f'  d={d*2} cm')
    scr.color('green')
    scr.forward((d)/2)
    scr.backward(d)
    scr.penup()
    scr.setheading(180)
    scr.heading()
    scr.forward(80)
    scr.pendown()
    scr.setheading(270)
    scr.heading()
    scr.color("black")
    scr.backward(l)
    scr.setheading(270)
    scr.heading()
    scr.right(45)
    scr.forward(l)
    scr.penup()
    scr.left(45)
    scr.forward(20)
    scr.pendown()
    scr.right(90)
    scr.color('green')
    scr.forward(a)
    scr.color("blue")
    scr.write(f" a={a*2}cm")
    scr.color('green')
    scr.backward(a)
    scr.setheading(270)
    scr.heading()
    scr.penup()
    scr.backward(20)
    scr.pendown()
    scr.right(45)
    scr.color('black')
    scr.backward(l)
    scr.setheading(0)
    scr.heading()
    scr.left(180-math.degrees(math.asin(100/math.sqrt(100**2 + cl ** 2))))
    scr.forward(math.sqrt(100**2 + cl ** 2))
    scr.setheading(180)
    scr.heading()

    scr.forward(b)
    scr.left(90)
    scr.forward(200)
    scr.right(90)
    scr.forward(cl)
    scr.left(90)
    scr.forward(l)
    scr.backward(l)
    scr.setheading(180)
    scr.heading()
    scr.right(180-math.degrees(math.asin(100/math.sqrt(100**2 + cl ** 2))))
    scr.forward(math.sqrt(100**2 + cl ** 2))
    scr.setheading(0)
    scr.heading()
    scr.forward(b)
    scr.right(90)
    scr.forward(200)
    scr.left(90)
    scr.forward(cl)
    scr.right(90)
    scr.forward(l)
    scr.backward(l)
    scr.setheading(0)
    scr.heading()
    scr.left(180-math.degrees(math.asin(100/math.sqrt(100**2 + cl ** 2))))
    scr.forward(math.sqrt(100**2 + cl ** 2))
    scr.setheading(270)
    scr.heading()
    scr.forward(100)
    scr.setheading(180)
    scr.heading()

    scr.forward(b)
    scr.setheading(0)
    scr.heading()
    scr.left(math.degrees(math.asin(100 / math.sqrt(b**2 + 100 **2) )))
    scr.forward(math.sqrt(b**2 + 100 **2) )
    scr.setheading(180)
    scr.heading()
    scr.forward(b)
    scr.setheading(0)
    scr.heading()
    scr.left(math.degrees(math.asin(100 / math.sqrt(b**2 + 100 **2) )))
    scr.forward(math.sqrt(b**2 + 100 **2) )
    scr.setheading(180)
    scr.heading()
    scr.forward(b)
    scr.setheading(0)
    scr.heading()
    scr.left(math.degrees(math.asin(100 / math.sqrt(b**2 + 100 **2) )))
    scr.forward(math.sqrt(b**2 + 100 **2) )
    scr.setheading(180)
    scr.heading()
    scr.forward(b)

    scr.setheading(270)
    scr.heading()
    scr.left(math.degrees(math.asin(b / math.sqrt(b**2 + 100 **2) )))
    scr.forward(math.sqrt(b**2 + 100 **2) )
    scr.setheading(180)
    scr.forward(b)

    scr.setheading(270)
    scr.heading()
    scr.left(math.degrees(math.asin(b / math.sqrt(b**2 + 100 **2) )))
    scr.forward(math.sqrt(b**2 + 100 **2) )
    scr.setheading(180)
    scr.forward(b)

    scr.setheading(270)
    scr.heading()
    scr.left(math.degrees(math.asin(b / math.sqrt(b**2 + 100 **2) )))
    scr.forward(math.sqrt(b**2 + 100 **2) )
    scr.setheading(180)
    scr.forward(b)
    scr.setheading(90)
    scr.heading()
    scr.forward(200)
    scr.penup()
    scr.forward(d-l)
    scr.pendown()
    scr.right(90)
    scr.forward(b/2)
    scr.right(90+math.degrees(math.asin((b/2)/math.sqrt((b/2)**2 + (d-l-100)**2   ))))
    scr.forward(math.sqrt((b/2)**2 + (d-l-100)**2 ))
    scr.backward(math.sqrt((b/2)**2 + (d-l-100)**2 ))
    scr.setheading(270)
    scr.heading()
    scr.left(math.degrees(math.asin((b/2)/math.sqrt((b/2)**2 + (d-l-100)**2   ))))
    scr.forward(math.sqrt((b/2)**2 + (d-l-100)**2 ))

    #foot

    scr.setheading(270)
    scr.heading()
    scr.forward(y+d-(d-l-100))
    scr.left(20)
    scr.forward(200)
    scr.backward(200)
    scr.setheading(180)
    scr.heading()
    scr.forward(b)
    scr.setheading(270)
    scr.heading()
    scr.right(20)
    scr.forward(200)
    scr.backward(200)

    scr.setheading(270)
    scr.heading()
    scr.penup()
    scr.forward(50)
    scr.pendown()
    scr.color("green")
    scr.right(90)
    scr.forward(cl)
    scr.color('blue')
    scr.write(f' c={c*2} cm')
    scr.color('green')
    scr.backward(3*cl)


    turtle.done()

        

