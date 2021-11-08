import time
import math
import DraftVecUtils
import matplotlib.pyplot as plt
import numpy as np

APP=App.getDocument("fourbar")
GUI=Gui.getDocument("fourbar")
ROTATIONS=2

def obj_label(label):
	return APP.getObjectsByLabel(label)[0];

def get_edge_vector(edge):
	return edge.EndPoint.sub(edge.StartPoint)

def get_edge_midpoint(edge):
	return edge.EndPoint.add(edge.StartPoint).multiply(0.5)

def get_ccwangle(v1,v2,always_positive=False): #counter clockwise
	angle=DraftVecUtils.angle(v1,v2)
	if always_positive and angle<0:
		return angle+2*math.pi
	return angle

def set_mechanism(sktch,sprdsheet):
	i=1
	for j in sktch:
		j.toggleActive(j.getIndexByName("TmpConstraint"))
	while sprdsheet.get('A'+str(i))!="End":
		for j in sktch:
			j.setDatum( j.getIndexByName(sprdsheet.get('A'+str(i))) , App.Units.Quantity(sprdsheet.get('B'+str(i))) )
		i=i+1
	for j in sktch:
		j.toggleActive(j.getIndexByName("TmpConstraint"))
	return

def show_animation(revs,sktch,sprdsheet):
	GUI.setEdit(sktch.ViewObject)
	angle=0
	revolutions=0
	while True:
		time.sleep(0.001)
		angle+=5
		sktch.setDatum(sktch.getIndexByName("InputAngle"),App.Units.Quantity(str(angle)+" deg"))
		Gui.updateGui()
		if angle == 360:
			angle=0
			revolutions+=1
			print(str(revolutions)+" revolution/s completed")
			if revolutions==revs:
				break
	sktch.setDatum(sktch.getIndexByName("InputAngle"),App.Units.Quantity('0 deg'))
	APP.recompute()
	GUI.resetEdit()
	Gui.updateGui()
	return


def calculate_dimensions(steps,sprdsheet,configD,velD,accD,sprdsheet_input):
	sprdsheet.clear('B4:Z5000')
	angle=0
	step=360/steps	

	configD.setDatum(configD.getIndexByName("InputAngle"),App.Units.Quantity('0 deg'))	
	velD.setDatum(velD.getIndexByName("InputVelocity"),App.Units.Quantity(sprdsheet_input.get("E1")))
	accD.setDatum(accD.getIndexByName("InputAcceleration"),App.Units.Quantity(sprdsheet_input.get("E2")))
	APP.recompute()
	bars=configD.Geometry
	lCrank=bars[0].length()
	lCoupler=bars[1].length()
	lFollower=bars[2].length()
	while angle<360:
		APP.recompute()
		bars=configD.Geometry
		vels=velD.Geometry
		accs=accD.Geometry

		coupler_angle=math.degrees(get_ccwangle(get_edge_vector(bars[3]).multiply(-1),get_edge_vector(bars[1]),True))
		follower_angle=math.degrees(get_ccwangle(get_edge_vector(bars[3]),get_edge_vector(bars[2]),True))
		transmission_angle=math.degrees(get_ccwangle(get_edge_vector(bars[1]),get_edge_vector(bars[2]).multiply(-1),True))
		sprdsheet.set('B'+str(int(4+angle/step)),"= "+str(angle)+" deg")
		sprdsheet.set('C'+str(int(4+angle/step)),"= "+str(coupler_angle)+" deg")
		sprdsheet.set('D'+str(int(4+angle/step)),"= "+str(follower_angle)+" deg")
		sprdsheet.set('E'+str(int(4+angle/step)),"= "+str(transmission_angle)+" deg")
		sprdsheet.set('G'+str(int(4+angle/step)),"= "+str(bars[0].EndPoint.x)+" mm")
		sprdsheet.set('H'+str(int(4+angle/step)),"= "+str(bars[0].EndPoint.y)+" mm")
		sprdsheet.set('I'+str(int(4+angle/step)),"= "+str(bars[2].StartPoint.x)+" mm")
		sprdsheet.set('J'+str(int(4+angle/step)),"= "+str(bars[2].StartPoint.y)+" mm")

		vCrank=vels[0].length()
		vCoupler=vels[1].length()
		vFollower=vels[2].length()
		sprdsheet.set('L'+str(int(4+angle/step)),"= "+str(vCoupler)+" mm/s")
		sprdsheet.set('M'+str(int(4+angle/step)),"= "+str(vFollower)+" mm/s")
		dirVC = 1 if get_ccwangle(get_edge_vector(bars[1]),get_edge_vector(vels[1]))>0 else -1
		dirVF = 1 if get_ccwangle(get_edge_vector(bars[2]),get_edge_vector(vels[2]))>0 else -1
		sprdsheet.set('N'+str(int(4+angle/step)),"= "+str(dirVC * vCoupler / lCoupler)+" rad/s")
		sprdsheet.set('O'+str(int(4+angle/step)),"= "+str(dirVF * vFollower / lFollower)+" rad/s")
		
		accD.setDatum(accD.getIndexByName("RadialCrank"),App.Units.Quantity(str(vCrank * vCrank / lCrank)+" mm"))
		accD.setDatum(accD.getIndexByName("RadialCoupler"),App.Units.Quantity(str(vCoupler * vCoupler / lCoupler)+" mm"))
		accD.setDatum(accD.getIndexByName("RadialFollower"),App.Units.Quantity(str(vFollower * vFollower / lFollower)+" mm"))
		print("RadialCrank",vCrank * vCrank / lCrank)
		print("RadialCoupler",vCoupler * vCoupler / lCoupler)
		print("RadialFollower",vFollower * vFollower / lFollower)
		APP.recompute()

		accs=accD.Geometry
		sprdsheet.set('Q'+str(int(4+angle/step)),"= "+str(math.sqrt(accs[0].length()**2 + accs[1].length()**2))+" mm/s^2")
		sprdsheet.set('R'+str(int(4+angle/step)),"= "+str(math.sqrt(accs[2].length()**2 + accs[3].length()**2))+" mm/s^2")
		sprdsheet.set('S'+str(int(4+angle/step)),"= "+str(math.sqrt(accs[4].length()**2 + accs[5].length()**2))+" mm/s^2")
		dirAC = 1 if get_ccwangle(get_edge_vector(bars[1]),get_edge_vector(accs[2]))>0 else -1
		dirAF = 1 if get_ccwangle(get_edge_vector(bars[2]),get_edge_vector(accs[4]))>0 else -1
		sprdsheet.set('T'+str(int(4+angle/step)),"= "+str(dirAC * accs[2].length() / lCoupler)+" rad/s^2")
		sprdsheet.set('U'+str(int(4+angle/step)),"= "+str(dirAF * accs[4].length() / lFollower)+" rad/s^2")
		angle+=step

		configD.setDatum(configD.getIndexByName("InputAngle"),App.Units.Quantity(str(angle)+' deg'))
		
	configD.setDatum(configD.getIndexByName("InputAngle"),App.Units.Quantity('0 deg'))
	APP.recompute()
	print("Spreadsheet updated.")
	return

def show_plots(sprdsheet):
	for i in sprdsheet:
		inputA=[]
		couplerA=[]
		followerA=[]
		transmissionA=[]
		couplerVwrtcrank=[]
		followerV=[]
		couplerAccwrtcrank=[]
		followerAcc=[]
		row=4
		while i.getContents('B'+str(row))!="":
			inputA.append(float(i.get('B'+str(row)).toStr().split()[0]))
			inputA.append(360+inputA[len(inputA)-1])
			couplerA.append(float(i.get('C'+str(row)).toStr().split()[0]))
			followerA.append(float(i.get('D'+str(row)).toStr().split()[0]))
			transmissionA.append(float(i.get('E'+str(row)).toStr().split()[0]))
			couplerVwrtcrank.append(float(i.get('N'+str(row)).toStr().split()[0]))
			followerV.append(float(i.get('O'+str(row)).toStr().split()[0]))
			couplerAccwrtcrank.append(float(i.get('S'+str(row)).toStr().split()[0]))
			followerAcc.append(float(i.get('T'+str(row)).toStr().split()[0]))
			row=row+1

		inputA.sort()
		couplerA.extend(couplerA)
		followerA.extend(followerA)
		transmissionA.extend(transmissionA)
		couplerVwrtcrank.extend(couplerVwrtcrank)
		followerV.extend(followerV)
		couplerAccwrtcrank.extend(couplerAccwrtcrank)
		followerAcc.extend(followerAcc)


		fig, axs = plt.subplots(3, sharex=True, sharey=True)
		if i.Label.find("C1") != -1:
			fig.suptitle("Configuration 1")
		if i.Label.find("C2") != -1:
			fig.suptitle("Configuration 2")
		axs[2].set_xlabel('Input angle')
		axs[0].set_ylabel('Coupler angle')
		axs[0].set_aspect(1)
		axs[1].set_ylabel('Follower angle')
		axs[1].set_aspect(1)
		axs[2].set_ylabel('Transmission angle')
		axs[2].set_aspect(1)
		axs[0].plot(np.array(inputA),np.array(couplerA),color = (1,0,0))
		axs[1].plot(np.array(inputA),np.array(followerA),color = (0,1,0))
		axs[2].plot(np.array(inputA),np.array(transmissionA),color = (0,0,1))
		
		fig.show()
		
		fig, axs = plt.subplots(2, sharex=True, sharey=True)
		if i.Label.find("C1") != -1:
			fig.suptitle("Configuration 1")
		if i.Label.find("C2") != -1:
			fig.suptitle("Configuration 2")
		axs[1].set_xlabel('Input angle')
		axs[0].set_ylabel('Coupler angular velocity')
		axs[1].set_ylabel('Follower angular velocity')
		
		axs[0].plot(np.array(inputA),np.array(couplerVwrtcrank),color = (1,1,0))
		axs[1].plot(np.array(inputA),np.array(followerV),color = (0,1,1))
		
		fig.show()
		
		fig, axs = plt.subplots(2, sharex=True, sharey=True)
		if i.Label.find("C1") != -1:
			fig.suptitle("Configuration 1")
		if i.Label.find("C2") != -1:
			fig.suptitle("Configuration 2")
		axs[1].set_xlabel('Input angle')
		axs[0].set_ylabel('Coupler angular acceleration')
		axs[1].set_ylabel('Follower angular acceleration')
		
		axs[0].plot(np.array(inputA),np.array(couplerAccwrtcrank),color = (1,0.5,0.5))
		axs[1].plot(np.array(inputA),np.array(followerAcc),color = (0.5,0.5,1))
		
		fig.show()
		
	return

print("Started...")

def debug(sktchs):
	for i in sktchs:
		if not i.FullyConstrained:
			raise RuntimeError(i.Label+" is not fully constrained.")
	return

debug([obj_label("Sketch_C1"),obj_label("Sketch_C2")])
set_mechanism([obj_label("Sketch_C2"),obj_label("Sketch_C1")],obj_label("Spreadsheet_InputParameters"))
show_animation(ROTATIONS,obj_label("Sketch_C2"),obj_label("Spreadsheet_InputParameters"))
show_animation(ROTATIONS,obj_label("Sketch_C1"),obj_label("Spreadsheet_InputParameters"))
calculate_dimensions(36,obj_label("Spreadsheet_C1"),obj_label("Sketch_C1"),obj_label("Sketch_V1"),obj_label("Sketch_A1"),obj_label("Spreadsheet_InputParameters"))
calculate_dimensions(36,obj_label("Spreadsheet_C2"),obj_label("Sketch_C2"),obj_label("Sketch_V2"),obj_label("Sketch_A2"),obj_label("Spreadsheet_InputParameters"))
show_plots([obj_label("Spreadsheet_C1"),obj_label("Spreadsheet_C2")])


# exec(open("/home/user/Documents/FreeCAD/Macro/rotate_4bar.FCMacro").read())
