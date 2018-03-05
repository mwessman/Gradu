from math import cos, sin
import datetime
import os.path

inputFilePath = "./201802281445p.txt"

#If this is false, the output will be in .3D format
outputInXYZ = False

outputFilePath = "./xyz/"
if(not outputInXYZ):
	outputFilePath = "./3d_new/"
file = open(inputFilePath, "r") 
time = 0

lctr = 0

#Each line of raw data is one lidar measurement
for line in file:
	#Parse the timestamp into a filename
	s1 = line[1:-2].split(':')
	tt = int(100.0*float(s1[0]))
	sect = tt / 100

        lctr += 1
	#every second entry is appended to old file since the measurements are done in pairs (upper half and lower half). This means that while the data is received 10 times in a second, there is only 5 measurements
	if(lctr % 2 == 0): 
 		time = datetime.datetime.fromtimestamp(sect).strftime('%Y%m%d%H%M%S') + str(tt - 100*sect)	
	entry_data = s1[1].split(';')
	name = outputFilePath + "lp_" + str(time)

	if(outputInXYZ):
		name += ".3d"
	else:
		name += ".txt"

	if(os.path.isfile(name)):
		out = open(name, "a")
	else:
		out = open(name, "w")

	#Parse each point of raw data
	for point in entry_data[0:-1]:
		#interpret the raw data
		pointc = point.split('|')
		dist = float(pointc[0])
		hangle = float(pointc[1])
		vangle = float(pointc[2])
		echow = pointc[3]
	
		#convert angular position into xyz position
		diag = dist * cos(vangle)
		x = diag * cos(hangle)
		y = diag * sin(hangle)
		z = dist * -sin(vangle)

		#Write a line of XYZ format data
		if(outputInXYZ):
			outstr = str(x)
			outstr += " "
			outstr += str(y)
			outstr += " "
			outstr += str(z)
			outstr += " O:"
		#else write output in 3D format
		else:
			
			outstr = str(x)
			outstr += " "
			outstr += str(y)
			outstr += " "
			outstr += str(z)		
			outstr += " 0:"
		outstr += '\n'
		out.write(outstr)
	out.close()
file.close()

