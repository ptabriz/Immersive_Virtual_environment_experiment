import viz
import vizinfo
import vizdlg
import vizinput
import viztask
import sys
import os
from random import shuffle
import datetime
import csv
import random
import vizshape
import vizjoy
import vizinput
import vizact
from math import ceil
import vizfx.postprocess
from vizfx.postprocess.color import GrayscaleEffect
from vizfx.postprocess.composite import BlendEffect
import collections

################################################ 
#############    Hardware setup   ##############
################################################

###Setup andinitiate Oculus Rift HMD###
import oculus
hmd = oculus.Rift()
hmd.getProfile()
hmd.setZoom(1)
if not hmd.getSensor():
	sys.exit('Oculus Rift not detected')
viz.link(hmd.getSensor(), viz.MainView)
sky = viz.addCustomNode('skydome.dlc')
viz.setMultiSample(4)
viz.go()

### Joystick operations##
dinput = viz.add('DirectInput.dle')	# Load DirectInput plug-in 
joystick = dinput.addJoystick()	# Add first available joystick
if not joystick:		# Checks for Joystick availability
    sys.exit('Failed to connect to joystick')
joystick.setDeadZone(0.2)	# Set dead zone threshold so small movements of joystick are ignored

### Get Joytick Command ####
class waitJoyButtonDown( viztask.Condition ):
    def __init__( self, joy, button ):
        self._joy = joy
        self._button = button
    def update( self ):
        return self._joy.isButtonDown(self._button)

d = viz.Data()
waitButton1 = waitJoyButtonDown(joystick,0)
waitButton2 = waitJoyButtonDown(joystick,1)

################################################ 
####### GUI ELEMENTS & Graphics setup ##########
################################################

#Grab the main window. 
window = viz.MainWindow 
#Change its background color. 
window.clearcolor(0.5,0.5,0.5)

### Setup color Theme ## 
blackTheme = viz.Theme()
blackTheme.borderColor = (.1,0.1,0.1,1)
blackTheme.backColor = (0.7,0.7,0.7,7)
blackTheme.lightBackColor = (0.6,0.6,0.6,1)
blackTheme.darkBackColor = (0.2,0.2,0.2,1)
blackTheme.highBackColor = (0.2,0.2,0.2,1)

### Fade-to-gray-efect , ! Not operationalized in this study !###
gray_effect = BlendEffect(None,GrayscaleEffect(),blend=0.0)
gray_effect.setEnabled(False)
vizfx.postprocess.addEffect(gray_effect)

def FadeToGrayTask():
    gray_effect.setBlend(1)
    gray_effect.setEnabled(True)
    yield viztask.waitCall(gray_effect.setBlend,vizact.mix(viz.BLACK,viz.WHITE,time=1.0))

#### Panels ######
canvas = viz.addGUICanvas()	# Create canvas for display UI to user
Panel = vizinfo.InfoPanel('', icon=False,parent=canvas,fontSize=18)	#Define main Panel#
Panel.alpha(.8) #set transparency
rowBottom= vizdlg.Panel(layout=vizdlg.LAYOUT_HORZ_CENTER,background=False,border=False, theme=blackTheme, spacing=30)	#Add rows to the panel#
Panel.addSeparator(.8,padding=(10,10))
Panel.addItem(rowBottom)
rowBottom.setTheme(blackTheme)
#Panel.getPanel().fontSize(22)
Panel.setTheme(blackTheme)
Panel.getPanel().font('Times New Roman')
Panel.getPanel().fontSize (12)

### SLIDER ######
Slider= rowBottom.addItem(viz.addProgressBar("0"))
maxNumber=Panel.addLabelItem('',viz.addText('Not at all ..................................................................Very high'))
maxNumber.fontSize(18)
Slider.font('calibri')
Slider.setScale(4,2.4)
Slider.message( str('%.2f'%(round(0)))[:1] )
viz.link(viz.CenterBottom,Panel,offset=(260,250,0))

##### Manages panel visibility #####
def Panelvisible(panelName,x): 
	if x==0:
		panelName.visible(viz.OFF)
	if x==1:
		panelName.visible(viz.ON)    

def showdialog():
        yield dialog.show()

################################################ 
####### User predefined variables ##############
################################################

#	mode : group assignment method : based on framing or permeability 
#	delay: wait time( per second) before on-screen questions prompted for each scene # 
#	breaklimit: Split questions based on the assigned integer that represents the maximum line lenght in words#
#	DATAPATH: Location of experment saved data
#	IMAGE_PATH: Location of the cube images 
#	groupfileList: list of environments assigned to the experimental group
#	natureList: list on Natural Envs assigned to the group
#	urbanList: list of Urban envs assigned to the group
#	env_map_namelist: final List of envs shown to the group
#	mainQOrig: list of the survey questions 
rounds=4
scenePerRound=7 
delay= 1
#breakLimit=10  # Split question lines based on assigned value#
#IMAGE_PATH = os.path.join(os.getcwd(),"ENV")
#DATA_PATH= os.path.join(os.getcwd(),"DATA")
currentDIR=os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(currentDIR,"ENV")
DATA_PATH= os.path.join(currentDIR,"DATA")
#IMAGE_PATH = os.path.join("D:/PRTexperiment","ENV")
#DATA_PATH= os.path.join("D:/PRTexperiment","DATA")
groupfileList=[]
natureList=[]
urbanList=[]
env_map_namelist = []

mainQOrig= [
'I like this environment',
'Everything I see in this environment goes well together',
"How natural do you percieve this enviornment?", 
"I would be able to rest and recover my ability to focus in this environment",

"How complex you perceive this enviornment?",
"Spending time here gives me a good break from my day-to-day routine",
"I feel safe to spend time alone in this place during day",
"I would be able to rest and recover my ability to focus in this environment.",

"There is much to explore and discover in this environment ",
"How easy would it be to move within or through this environment?",
"How well can you see all parts of this environment without having your view blocked or interfered with?",
"I would be able to rest and recover my ability to focus in this environment ",
]

surveyScale={

'I like this environment': 								   						'Strongly disagree..................................................Strongly agree',
'Everything I see in this environment goes well together': 						'Strongly disagree..................................................Strongly agree',
"How natural do you percieve this enviornment?":            					'Not at all ..................................................................Very natural',
"I would be able to rest and recover my ability to focus in this environment":	'Strongly disagree..................................................Strongly agree',


"How complex you perceive this enviornment?":            					    'Not at all ..................................................................Very complex',
"Spending time here gives me a good break from my day-to-day routine":  		'Strongly disagree...................................................Strongly agree',
"I feel safe to spend time alone in this place during day":						'Strongly disagree...................................................Strongly agree',
"I would be able to rest and recover my ability to focus in this environment.":	'Strongly disagree...................................................Strongly agree',

"There is much to explore and discover in this environment ":					'Strongly disagree...................................................Strongly agree',
"How easy would it be to move within or through this environment?": 		    'Not at all........................................................................ Very easy',
"How well can you see all parts of this environment without having your view blocked or interfered with?":
																				'Not at all........................................................................ Very well',
"I would be able to rest and recover my ability to focus in this environment ":	'Strongly disagree...................................................Strongly agree',
} 

IntroQ= ['How strong was your sense of presence in this environment?',
		 'How strong was your sense of  "actualy being" in this environment?',
		 'How realistic did the environment appear to you?' ]

sceneRotation=[]
indexScene="demo"
indexQuestion="0"

################################################ 
####### Participant ID and filemangement #######
################################################

###Create/open data files###
subject = vizinput.input('Please enter the participant identification number?') #Prompt for the participant's identification number.
participant_data = open(DATA_PATH+"/"+"Individual_data"+'/'+str(subject)+'.txt','a') 
group_data = open(DATA_PATH+"/"+'group_.txt','a') 
participantList=open(DATA_PATH+"/"+'participant_list.txt')
#open a data file and to fill it with tracking data#
tracking_data = open(DATA_PATH+"/"+"Tracking"+"/"+'tracking'+str(subject)+'.txt', 'a')

###Check for Existing and Correct ID format and add it to the participants list###
for line in participantList.readlines(): 
	if str(subject) ==line[:4]:
		print "Invalid ID ! the participant Id already exists"
		sys.exit()
if not len(str(subject))==4:
		print "Invalid ID ! entered id should have exactly one character and 3 digits"
		sys.exit()
elif str(subject)[0]!="a" and str(subject)[0]!="b" and str(subject)[0]!="c":
		print "Participant ID should start with a or b or c"
		sys.exit()

participantList=open(DATA_PATH+"/"+'participant_list.txt','a')
participantList.write(str(subject)+"\n")
participantList.close() 



################################################ 
####### STIMULI Orders, GROUP ASSIGNMENT #######
################################################

### Assign questions to groups based on Particpant identifiers"
groupID= subject[0]
if groupID=="a":
	Qselect= mainQOrig[0:4]
elif groupID=="b":
	Qselect= mainQOrig[4:8]
elif groupID=="c":
	Qselect= mainQOrig[8:12]
	
###Define orders based on participant ID###

# generate file list based on order#
fileList = os.listdir(IMAGE_PATH)

for file in fileList:
	im=file.split(".")[0]
	imCut=im[2:]
	if file.endswith('_negx.png'):
		env_map_namelist.append(file[:-9]+ '.png')	
shuffle(env_map_namelist)
print env_map_namelist

################################################ 
####### Survey Slider     ######################
################################################

#### Save participants rating #####
def saveRate(qIndex,sceneIndex,question):

	pos=Slider.get()
	print "Question"+str(question+1)+ '\t'+ str(rate)
	if sceneIndex=="U_0_control.png" or sceneIndex=="2_med.png":
		sceneName=sceneIndex
		print "Nots"
	else:
		sceneName=env_map_namelist[sceneIndex][:7]
	pos_slider=str(subject) + '\t' +groupID.upper() +'\t'+ sceneName+ '\t' + str(question+1)+'\t'+str(int(rate))+ '\n'
	participant_data.write(pos_slider)
	group_data.write(pos_slider)


#### define slider move on hat change event###
def onHatChange(e):
	pos = Slider.get()
	if int(e.value)==90:
		pos=pos+.090909
		Slider.set(pos)
	elif int(e.value)==270:
		pos=pos-.090909
		Slider.set(pos)
#Update rating update#
	if pos<.07:
		Slider.message("")
	else:
		if pos>0.93:
			rate=11
			Slider.message( "10" )
		else:
			rate=ceil(abs(pos*10))
			Slider.message(str(rate-1)[:1])
		return rate
		global rate
		
#### slider question update###		
def changeMessage(a,breakQ=True):
	global maxNumber
	if a not in IntroQ:
		Panel.removeItem(maxNumber)	
		maxNumber= Panel.addLabelItem('',viz.addText(surveyScale[a]))
	#maxNumber= Panel.addLabelItem(' Strongly disagree.............................................................................Strongly agree',viz.addText(''))
	maxNumber.fontSize(18)

	if breakQ:
		if len(a)> breakLimit:
			t= a.split()
			ttrunk1=t[:breakLimit]
			ttrunk2=t[breakLimit:]
			j=" ".join(ttrunk1)
			k=" ".join(ttrunk2)
			Question=Panel.setText("   "+j+"\n"+"   "+k) 
	else:
		Question=Panel.setText("   "+a+"\n"+"                          .                      ")

################################################ 
####### Headtracking    ########################
################################################

class headTrack(viz.EventClass):
	global IMAGE_PATH
	global IMAGE_SIZE 
	global FILE_PATH
	global DATA_PATH
	global track
	IMAGE_SIZE = 1024
	FILE_PATH = os.getcwd()
	
	def __init__(self):
		self.delay=3
		viz.EventClass.__init__(self)
		self.cube = vizshape.addCube(size=1024,splitFaces=True)
		self.cube.disable(viz.RENDERING)
		self.current = 0
		self.valid_pid = 0
		self.savedb_all = []
		#self.__button_press_cnt = 1
		self.save_dbase = []  

	def getPickInfo(self):
		"""Returns selected cube environment's cube face and coordinates.
		(e.g. [[front][x,y,z]]"""
		info = viz.pick(info=True)
		picked = {}
		picked = {'face':info.name, 'x':info.point[0], 'y':info.point[1], 'z':info.point[2]}
		return picked
	
	def setCoordinatesData(self):
		self.coor_data = {} # All data to store
		# Cube coordinates
		pos_info = self.getPickInfo() 
		# World coordinates
		line_pass = viz.MainWindow.screenToWorld(viz.mouse.getPosition())
		pos = vizmat.MoveAlongVector(line_pass.begin,line_pass.dir,512) 
		question = 2
		face = pos_info['face']
		x = pos_info['x'] # cube coordinate
		y = pos_info['y'] # cube coordinate
		z = pos_info['z'] # cube coordinate
		time_stamp = datetime.datetime.now()
		
		pic_index_XY = self.convertXY(face,x,y,z)
		imx = pic_index_XY[0] # image coordinate - top left to be [0,0]
		imy = pic_index_XY[1] # image coordinate - top left to be [0,0]
		imyf = self.flipPicIndexY(pic_index_XY[1]) # image coordinate - bottom left to be [0,0]
		
		world_x = pos[0] # world coordinate
		world_y = pos[1] # world coordinate
		world_z = pos[2] # world coordinate
		
	
		coor_data = [face,imx,imy,imyf]
		return coor_data
		
	#___________________________________________________________________
	# Code below is converting the cube environment coordinates to 
	# 2D image pixel coordinates (imx, imy) and 'imyf' is flipping 
	# minimum and maximum values of imy.
	#___________________________________________________________________
	
	#*********************************************************************
	# Convert cube environment coordinates (center is [0,0])to 2D image 
	# pixel coordinates. For 2D image pixel coordinates, left top corner 
	# should be [0,0].
	# ********************************************************************
	 
	def holizontalNormal(self, cubeX_coor):  # face: front, left, top and bottom
		if cubeX_coor < 0 or cubeX_coor > 0:
			pic_index_X = IMAGE_SIZE/2 + cubeX_coor
		elif cubeX_coor == 0:
			pic_index_X = IMAGE_SIZE/2
		else:
			print "[holizontalNormal] - Check coordinates."
		return pic_index_X

	def holizontalOpposit(self, cubeX_coor): # face: right and back
		if cubeX_coor < 0 or cubeX_coor > 0:
			pic_index_X = IMAGE_SIZE/2 - cubeX_coor
		elif cubeX_coor == 0:
			pic_index_X = IMAGE_SIZE/2 
		else:
			print "[holizontalOppositCheck] - coordinates."
		return pic_index_X
	
	def verticalNormal(self, cubeY_coor):	# All faces
		if cubeY_coor < 0 or cubeY_coor > 0:
			pic_index_Y = IMAGE_SIZE/2 - cubeY_coor
		elif cubeY_coor == 0:
			pic_index_Y = IMAGE_SIZE/2 
		else:
			print "[verticalNormal] - Check coordinates."
		return pic_index_Y
	
	
	#*********************************************************
	# flip value 'imy': eg imy = 0 -> imyf = image size (1024)
	#*********************************************************
	def flipPicIndexY(self, pic_index_Y):
		fliped_Y = IMAGE_SIZE - pic_index_Y
		return fliped_Y
		
	#***********************************************************************
	# Fix 2D image coordinates for Holizontal Strip image.
	# [face order: front | right | back |left |top | bottom] 
	# Front face left top [0,0],		Bottom face right top [1024,0]
	# Front face left bottom [0,1024],	Bottom face right bottom [1024,1024]
	#************************************************************************
	def convertXY(self,cube_face, cubeX_coor, cubeY_coor, cubeZ_coor):
		if cube_face == 'front':
			pic_index_X = self.holizontalNormal(cubeX_coor)
			pic_index_Y = self.verticalNormal(cubeY_coor)
			
		elif cube_face == 'right':
			pic_index_X = self.holizontalOpposit(cubeZ_coor) + IMAGE_SIZE
			pic_index_Y = self.verticalNormal(cubeY_coor)
			
		elif cube_face == 'back':
			pic_index_X = self.holizontalOpposit(cubeX_coor) + IMAGE_SIZE * 2
			pic_index_Y = self.verticalNormal(cubeY_coor)
			
		elif cube_face == 'left':
			pic_index_X = self.holizontalNormal(cubeZ_coor) + IMAGE_SIZE * 3
			pic_index_Y = self.verticalNormal(cubeY_coor)
			
		elif cube_face == 'top':
			pic_index_X = self.holizontalNormal(cubeX_coor) + IMAGE_SIZE * 4
			pic_index_Y = self.verticalNormal(cubeZ_coor)
			
		elif cube_face == 'bottom':
			pic_index_X = self.holizontalNormal(cubeX_coor) + IMAGE_SIZE * 5
			pic_index_Y = self.verticalNormal(cubeZ_coor)
			
		else:
			print "Error: [convertXY]"
		
		converted_XY = [pic_index_X, pic_index_Y]
		
		return converted_XY

	def makeMarkers(self):
		datai = self.setCoordinatesData()
		data2 = self.setCoordinatesData()
		data2 = indexScene+ "\t"+ indexQuestion+'\t'+ str(datai[0]) + '\t' + str(datai[1]) + '\t' + str(datai[2]) + "\t" + str(datai[3])+'\n'
		tracking_data.write(data2)

################################################ 
####### Scene operation   ######################
################################################

def StartDemo(env,wait):
	a=env
	sky.visible(viz.ON)
	env = viz.addEnvironmentMap(IMAGE_PATH+'/'+env)
	sky.texture(env)
	Panelvisible(Panel,0)
	yield viztask.waitTime(4)
	sky.visible(viz.OFF)
	yield changeQ(a,IntroQ,0,"",breakQ=True)
	if wait:
		Panelvisible(Panel,1)
		Panel.setText("Warmup stage complete! Please take off your headset ") 
		rowBottom.visible(viz.OFF)
		maxNumber.visible(viz.OFF)
		yield viztask.waitKeyDown('c')
		#yield viztask.waitAny([waitButton2],d)
		#if d.condition is waitButton2:
		Panelvisible(Panel,0)
		rowBottom.visible(viz.OFF)
		sky.visible(viz.OFF)

def finalDemo():
	sky.remove()
	Panel.remove()
	piazza = viz.add('gallery.osgb')
	Panel2 = vizinfo.InfoPanel("You may now take off the headset, Thank you for your participation",parent=canvas,align=viz.ALIGN_CENTER,fontSize=22,icon=False,title="Finished")
	Panel2.alpha(.8)
	navigationNode = viz.addGroup()
	viewLink = viz.link(navigationNode, viz.MainView)
	viewLink.preMultLinkable(hmd.getSensor())
	viewLink.setOffset([0,1.8,0])
	viz.link(viz.CenterBottom,Panel2,offset=(400,230,0))

def Changescene(i):
	env = viz.addEnvironmentMap(IMAGE_PATH+'/'+env_map_namelist[i])
	sky.visible(viz.ON)
	sky.texture(env)
	viz.setOption('viz.hint',viz.FREE_TEXTURE_MEMORY_HINT)
	global sky
	
def Sky(toggle):
	if toggle == 1:
		sky = viz.addCustomNode('skydome.dlc')
		global sky
	if toggle == 0:
		sky.remove()

def changeQ(sceneIndex,qList,delayTime,panelTitle,breakQ=True):
	indexQuestion="delay"
	global indexQuestion
	if sceneIndex=="U_0_control.png"  or sceneIndex=="2_med.png":
		condition="demo"
		indexscene=sceneIndex
		shuffleQuestionList=list(IntroQ)
		shuffle(shuffleQuestionList)
	else: 
		condition="scene"
		indexScene=env_map_namelist[sceneIndex]
		shuffleQuestionList=list(qList)
		shuffle(shuffleQuestionList)
	
	global indexScene
	Panelvisible(Panel,0)
	yield viztask.waitTime(delayTime)
	Panelvisible(Panel,1)
	rowBottom.visible(viz.ON)
	maxNumber.visible(viz.ON)

	qIndex=0
	while qIndex<len(qList):
		Panel.setTitle(panelTitle)
		viz.callback(dinput.HAT_EVENT, onHatChange)
		question=shuffleQuestionList[qIndex]
		changeMessage(shuffleQuestionList[qIndex],breakQ)
		
		if condition=="scene":
			index=mainQOrig.index(question)
		if condition=="demo":
			index=IntroQ.index(question)
			
		indexQuestion = str(index+1)
		global indexQuestion
		#track.setEnabled(viz.OFF)
		yield viztask.waitAny([waitButton1],d)
		if d.condition is waitButton1:
				yield viztask.waitTime(.2)
				pos = Slider.get()
				if round(abs(pos/.1),1) > 0:
					saveRate(qIndex,sceneIndex,index)
					Slider.set(0)
					Slider.message( "" )
					qIndex=qIndex+1
				else:
					yield viztask.waitTime(.2)
					#Panel.setTitle("MINIMUM SELECTION IS (0)")
					yield viztask.waitTime(3)
	if qIndex == len(qList):
		#viztask.schedule(FadeToGrayTask())
		Panelvisible(Panel,0)
		sky.visible(viz.OFF)
		yield viztask.waitTime(1)
		

def recess():
	Panelvisible(Panel,1)
	Panel.setText("Stage 1 complete, please take off the headset") 
	rowBottom.visible(viz.OFF)
	maxNumber.visible(viz.OFF)
	yield viztask.waitKeyDown('c')

################################################ 
####### Execution         ######################
################################################

def exc():
	
	if int(subject[2:])%2 == 0:
		demo1="U_0_control.png"
		demo2="2_med.png"
	else:
		demo2="U_0_control.png"
		demo1="2_med.png"
	breakLimit=8
	global breakLimit
	yield StartDemo(demo1,False)
	yield StartDemo(demo2,True)
	
	breakLimit=10
	global breakLimit
	index=0

	track.setEnabled(viz.ON)
	
	for i in range (0,rounds):

		for sceneIndex in range (i*scenePerRound,((i+1)*scenePerRound)):

			print "now loading scene" + str(sceneIndex+1)
			Sky(1)
			Changescene(sceneIndex)
			yield changeQ(sceneIndex,Qselect,delay,"")
			Sky(0)
			if sceneIndex+1== len(env_map_namelist):
				track.setEnabled(viz.OFF)
				tracking_data.close()
				participant_data.close()
				group_data.close()
				finalDemo()
				sys.exit()	
				
		yield recess()
		
track=vizact.ontimer(.25, headTrack().makeMarkers)
viztask.schedule(exc())
