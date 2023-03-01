import argparse 
from helper import *

parser = argparse.ArgumentParser(description="Design of transmission system")
parser.add_argument('-l', '--length', type=int, metavar='', required=True, help='Length of the transmission line')
parser.add_argument('-p', '--power', type=int, metavar='',required=True, help='Power transmitted')
args = parser.parse_args()

full_data = {
    '1':{'Zc':400},
    '2':{'Zc':200},
    'power': args.power,
    'length': args.length
}

data = {}


for Nc in range(1,3):
	Nc = str(Nc)
	full_data[Nc]['mev'] = calculate_mev(args.length, args.power, int(Nc))
	full_data[Nc]['mf_limit'] = float(technical_requirements(args.length))
	full_data[Nc]['SIL'] = (full_data[Nc]['mev'] ** 2) / full_data[Nc]['Zc']
	mf_calc = round(args.power/full_data[Nc]['SIL'],3)
	mf_margin = full_data[Nc]['mf_limit'] - mf_calc
	full_data[Nc]['mf_calc'] = mf_calc 
	
	if mf_margin < 0:
		full_data[Nc]['mf_margin'] = 1000
	else:
		full_data[Nc]['mf_margin'] = mf_margin 

mf_margin_1 = full_data['1']['mf_margin']
mf_margin_2 = full_data['2']['mf_margin']

if mf_margin_1 < mf_margin_2:
	print_data(data = full_data['1'], power = args.power, length = args.length)
	print(' Hence, Choosing a single circuit line.\n')
	data = full_data['1']
	clearance = calculate_clearance(data, 1)
	calculate_disc(full_data['1']['mev'])
	not_selected = []
	selected_conductor = ''
	for key in conductor:
		conductor_data = conductor_selection(full_data['power'], full_data['1']['mev'],full_data['length'], 1, not_selected)
		if conductor_data['selected_conductor'] == None:
			print(' No conductor was fit for the line, bundling should be done')
			break
		LC = calculate_LC(clearance, conductor_data['selected_conductor'], full_data['length'], 1)	
		VR = calculate_VR(LC['L'], LC['C'], conductor_data['R_65'], full_data['1'], full_data['power'], 1,full_data['length'])['VR']
		if  VR < 12:
			#print(f" The conductor rejected are {', '.join(not_selected)}")
			selected_conductor = conductor_data['selected_conductor']
			print(f" The conductor selected is\t\t\t\t: {conductor_data['selected_conductor']}")
			print(f" The voltage regulation is\t\t\t\t: {VR} %")
			break
		else:
			not_selected.append(conductor_data['selected_conductor'])
	
	#print the tower
	#print_the_tower(clearance)
	print('='*80)
	for x in conductor:
		LC = calculate_LC(clearance, x, full_data['length'], 1)
		R_65 = conductor[x]['resistance']* full_data['length'] * (1 + 0.004 * (65-20) ) 
		VR = calculate_VR(LC['L'], LC['C'], R_65, full_data['1'],full_data['power'],1, full_data['length'])['VR']
		efficiency = calculate_efficiency(full_data['power'], full_data['1']['mev'], full_data['length'], 1, x)
		print(f" {x}")
		print(f"\tefficiency \t\t\t: {efficiency} %")
		conductor[x]['VR'] = VR
		print(f'\tVR \t\t\t\t: {VR} %')
	print('='*80)
	tension=[]
	for con in conductor:
		for x in [250,275,300,325,400]:
			tension.append(bending_moment(full_data['1']['mev'], x, 1, 1, con,  clearance['y'],clearance['d'],conductor[con]['area'], full_data['length'], full_data['power']))
	print_tension(tension)
	print_economic_data(tension)
	final_op(clearance, "morculla", full_data['length'], 1, full_data['power'], full_data['1'])


	
else:
	print_data(data = full_data['2'], power = args.power, length = args.length)
	print(' Hence, Choosing a double circuit line.\n')
	data = full_data['2']
	clearance = calculate_clearance(data, 2)
	calculate_disc(full_data['2']['mev'])
	not_selected = []
	selected_conductor = ''
	print('_'*100)
	for key in conductor:
		conductor_data = conductor_selection(full_data['power'], full_data['2']['mev'],full_data['length'], 2, not_selected)
		if conductor_data['selected_conductor'] == None:
			print(' No conductor was fit for the line, bundling should be done')
			break
		LC = calculate_LC(clearance, conductor_data['selected_conductor'], full_data['length'], 2)	
		VR = calculate_VR(LC['L'], LC['C'], conductor_data['R_65'], full_data['2'], full_data['power'], 2, full_data['length'])['VR']
		if  VR < 12:
			#print(f" The conductor rejected are {', '.join(not_selected)}")
			selected_conductor = conductor_data['selected_conductor']
			print(f" The conductor selected is\t\t\t\t: {conductor_data['selected_conductor']}")
			print(f" The voltage regulation is\t\t\t\t: {VR} %")
			break
		else:
			not_selected.append(conductor_data['selected_conductor'])
	print('_'*100)
	for x in conductor:
		LC = calculate_LC(clearance, x, full_data['length'], 2)
		R_65 = conductor[x]['resistance']* full_data['length'] * (1 + 0.004 * (65-20) ) 
		VR = calculate_VR(LC['L'], LC['C'], R_65, full_data['2'],full_data['power'],2, full_data['length'])['VR']
		print(f' For {x} : {VR}')
		conductor[x]['VR'] = VR
	tension = []
	for con in conductor:
		for x in [250,275,300,325,400]:
			tension.append(bending_moment(full_data['2']['mev'], x, 2, 2, con, clearance['y'],clearance['d'],conductor[con]['area'], full_data['length'], full_data['power']))
	print_tension(tension)	
	print_economic_data(tension)
	final_op(clearance, "morculla", full_data['length'], 2, full_data['power'], full_data['2'], full_data['2']['mev'])

