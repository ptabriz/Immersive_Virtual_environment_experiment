import os
import vizinput
from random import shuffle
import viztask
import oculus
import vizinfo
import vizdlg
import datetime
import csv
import random
import vizshape
import vizjoy
import vizact
from math import ceil
import vizfx.postprocess
from vizfx.postprocess.color import GrayscaleEffect
from vizfx.postprocess.composite import BlendEffect
import collections

currentDIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(currentDIR,"ENV")
DATA_PATH = os.path.join(currentDIR,"DATA")
CONFIG_PATH = os.path.join(currentDIR,"config")


#print expDesign()[1]



### Get Joytick Command ####
class waitJoyButtonDown(viztask.Condition):
    def __init__( self, joy, button ):
        self._joy = joy
        self._button = button
    def update( self ):
        return self._joy.isButtonDown(self._button)


class IVE:
	''' loads configuration , experiment design , participant and stimuli management '''

	PID = "a"
	def __init__(self):

		self.hmd = oculus.Rift()
		self.link = viz.link(self.hmd.getSensor(), viz.MainView)
		self.sky = ""
		self.env = ""
		self.video = ""

		self.mainSurvey = []
		self.warmupSurvey = []
		self.config= self.readconfig()


		self.stimuli = self.config["stimuli"].strip(" ").split(",")
		self.warmup = self.config["warmup"].strip(" ").split(",")
		self.survey = self.config["survey"]
		print self.survey
		self.splitSurvey = self.config["splitSurvey"]
		self.delay = self.config["delay"]
		self.PIDdigits = int(self.config["digits"])
		# recess and message
		self.recessList = self.config["recess"].strip(" ").strip("\n").split(",")
		self.recessMessage = self.config["recessMessage"]
		# Finale and message
		self.finale = self.config["finale"]
		self.finaleMessage = self.config["finaleMessage"]

		self.group = "A"
		#self.group = self.participant()[0]
		self.designOutput = self.expDesign()


		self.stimuliList = self.designOutput[0][self.group]
		self.warmupList =  self.designOutput[1]
		self.groupNumber = len(self.designOutput[1].keys())
		#print self.groupNumber
		viz.go()


	def participant(self):

		''' Participant ID and group assignment'''

		subject = vizinput.input('Please enter the participant identification number?') #Prompt for the participant's identification number.
		participantList=open(DATA_PATH+"/"+'participant_list.txt')
		#groups = self.designOutput[0].keys()

		if not len(str(subject)) == self.PIDdigits:
			print "Invalid ID ! entered id should have one 'alphabetical' character from {0} (case sensetive) and {1} 'digits'".format(groups,self.PIDdigits-1)
			sys.exit()

		for line in participantList.readlines():

			if str(subject) == line[:self.PIDdigits]:
				print "Invalid ID ! the participant Id already exists"
				sys.exit()

		participantList=open(DATA_PATH+"/"+'participant_list.txt','a')
		participantList.write(str(subject)+"\n")
		participantList.close()
		IVE.PID = subject

		return subject

	def readconfig(self):
		configFile = os.path.join(CONFIG_PATH,"config.txt")
		configuration = open(configFile,'r')
		configDIC={}

		for index, line in enumerate(configuration.readlines()):
			if line[0].isalpha() and not line.startswith(" "):

				configDIC[line.split("=")[0]] = line.split("=")[1]
			else:
				print "WARNING: Config file line {0} contains unrecognized charachters".format(index+1)

		return configDIC


	def expDesign(self):

		''' stimuli and survey selection based on experiment design '''

		groupDIC={}
		warmupDIC={}


		if self.stimuli[0] == "True":

			stimuliList=[]

			# check stimuli type , VID , IMG , MIX and create a subset based on groups#

			for fileName in os.listdir(IMAGE_PATH) :

				if fileName.endswith("_negx.png") and fileName[0] == self.group:
					stimuliList.append(fileName[:-9]+'.png')
				elif fileName.endswith(".MP4") and fileName[0] == self.group:
					stimuliList.append(fileName)
				elif fileName.endswith(".osgb") and fileName[0] == self.group:
					stimuliList.append(fileName)

			for env in stimuliList:
				if env[0] in groupDIC.keys():
					groupDIC[env[0]].append(env)
				else:
					groupDIC[env[0]] = [env]

			# randomize stimuli #
			if "RAN" in self.stimuli[1]:
				for group in groupDIC.keys():
					shuffle(groupDIC[group])

		# check warmup stimuli type , VID , IMG , MIX #
		if "True" in self.warmup[0]:

			if "VID" in self.warmup[2]:
				warmupList = [(file) for file in os.listdir(IMAGE_PATH) if file.endswith("_.MP4") and file[0]=="W"]

			elif "IMG" in self.warmup[2]:
				warmupList = [(file[:-9]+ '.png') for file in os.listdir(IMAGE_PATH) if file.endswith("_negx.png") and file[0]=="W"]

			for env in warmupList:
				if env[0] in warmupDIC.keys():
					warmupDIC[env[0]].append(env)
				else:
					warmupDIC[env[0]] = [env]

			if "RAN" in self.warmup[1]:
					shuffle(warmupDIC["W"])

		# generate a subset of survey items based on groups #
		if "True" in self.survey:

			surveyPath = os.path.join(CONFIG_PATH,"survey.txt")
			surveyFile = open(surveyPath,'r')
			for line in surveyFile.readlines():

				if "W" in line.split(":")[0]:
					self.warmupSurvey.append(line)
				else:
					self.mainSurvey.append(line)

		if "False" not in self.splitSurvey:
			split = int(self.config["splitSurvey"])
			groupIndex = ord(self.group)-64
			if len(self.mainSurvey) % split != 0:
				print "Survey is not equally distributed"
			else:
				self.mainSurvey = self.mainSurvey [(groupIndex-1) * split:(groupIndex * split)-1]

		# randomize stimuli #
		if "True" in self.config["randomSurvey"]:
			shuffle(self.mainSurvey)

		return groupDIC,warmupDIC

	def changeScene(self,scene, remove= False):
		''' Changes IVE scenes based on type IMG , VID , 3D '''

		if scene[-4:] == ".png" :
			mode = "IMG"
		elif scene[-4:] == ".MP4" :
			mode = "VID"
		elif scene[-4:] == "osgb":
			mode = "3D"

		if remove:
			if mode == "IMG" :
				self.sky.remove()
				self.link.remove()
			if mode == "VID" :
				self.video.remove()
				self.sky.remove()
		else:

			if mode == "VID" :
				print scene
				self.video = viz.addVideo(IMAGE_PATH+"/"+scene)
				self.sky = vizshape.addSphere(radius=10000, flipFaces=True)
				self.sky.texture(self.video)
				self.sky.drawOrder(-100)
				self.video.play()
				self.sky.disable(viz.DEPTH_TEST)
				self.sky.drawOrder(-100)

			if mode == "IMG" :
				self.env = viz.addEnvironmentMap(IMAGE_PATH+"/"+scene)
				self.sky = viz.addCustomNode('skydome.dlc')
				self.sky.texture(self.env)

			if mode == "3D" :
				scene = viz.add(scene)
				navigationNode = viz.addGroup()
				self.link = viz.link(navigationNode, viz.MainView)
				self.link.preMultLinkable(self.hmd.getSensor())
				self.link.setOffset([0,1.8,0])

	def recess(n=None, message=""):

		Panel = panel().draw()[0]
		Panel.visible(viz.ON)
		Panel.alpha(1)
		Panel.setText(message)
		yield viztask.waitKeyDown('c')
		Panel.remove()

	def execute(self):
		''' runs the experiment procedure '''

		# 0. Warmup phase #
		if "True" in self.warmup:
			for index, scene in enumerate(self.warmupList[index]):
				if "True" in self.warmup[0]:
					yield self.changeScene(scene)
					# Warmup survey #
					if self.warmupSurvey:
						yield survey(scene,self.delay, self.warmupSurvey).changeQ("")
					# remove scene #
					yield self.changeScene(scene, remove=True)
			if "False" not in self.warmupMessage:
				yield self.recess("Practice stage complete, please take off the headset")

		# 1. Experimental phase #		s
		print self.stimuliList
		for index, scene in enumerate(self.stimuliList):

			yield self.changeScene(self.stimuliList[index])

			# experimental survey #
			if "True" in self.survey:
				yield survey(scene,self.delay, self.mainSurvey).changeQ("")

			else :
				yield viztask.waitKeyDown(" ")

			yield self.changeScene(scene, remove=True)

			#clear texture memory after 3 scenes#
			if index % 3 == 0 :
				viz.setOption(scene,viz.FREE_TEXTURE_MEMORY_HINT)

			# 2. recess phase
			if str(index+1) in self.recessList and index+1 != len(self.stimuliList) :
				yield self.recess(message = "Its time to get a break, please take off your headset")

		# 3. Finale phase #
		if "True" in self.finale:
			finaleFile = os.path.join(IMAGE_PATH, "Finale.osgb")
			yield self.changeScene(finaleFile)
			panel().infoPanel(self.finaleMessage)



class survey:

	### Joystick operations##
	dinput = viz.add('DirectInput.dle')	# Load DirectInput plug-in
	joystick = dinput.addJoystick()	# Add first available joystick
	if not joystick:		# Checks for Joystick availability
		sys.exit('Failed to connect to joystick')
	joystick.setDeadZone(0.2)	# Set dead zone threshold so small movements of joystick are ignored

	d = viz.Data()
	waitButton1 = waitJoyButtonDown(joystick,0)
	waitButton2 = waitJoyButtonDown(joystick,1)

	def __init__(self, scene=None, delay=None, survey=None):

		self.survey = survey
		self.scene = scene
		self.delay = delay

		panelElements = panel().draw(panel=True, slider=True)
		self.Panel = panelElements[0]
		self.rowBottom = panelElements[1]
		self.Slider = panelElements[2]
		self.scaleText = ""
		self.Slider.visible(viz.ON)
		##### Manages panel visibility #####

	def showdialog():
			yield dialog.show()

	def showdialog():
			yield dialog.show()

#### Save participants rating #####
	def saveRate(qIndex,sceneIndex,question):

		pos=Slider.get()
		print "Question"+str(question+1)+ '\t'+ str(rate)
		if sceneIndex=="U_0_control.png" or sceneIndex=="2_med.png":
			sceneName=sceneIndex
			print "Nots"
		else:
			sceneName=env_map_namelist[sceneIndex][:7]
		pos_slider=str(subject) + '\t' + groupID.upper() +'\t'+ sceneName+ '\t' + str(question+1)+'\t'+str(int(rate))+ '\n'
		participant_data.write(pos_slider)
		group_data.write(pos_slider)

	#### define slider move on hat change event###
	def onHatChange(self,e):
		pos = self.Slider.get()
		if int(e.value) == 90:
			pos = pos+.090909
			self.Slider.set(pos)
		elif int(e.value)== 270:
			pos = pos-.090909
			self.Slider.set(pos)
	#Update rating update#
		if pos < .07:
			self.Slider.message("")
		else:
			if pos > 0.93:
				rate=11
				self.Slider.message( "10" )
			else:
				rate=ceil(abs(pos*10))
				self.Slider.message(str(rate-1)[:1])
			return rate

	#### slider question update###
	def changeMessage(self,item,scale,breakQ=True):
		self.Panel.removeItem(self.scaleText)
		self.scaleText = self.Panel.addLabelItem('',viz.addText(scale))
		self.scaleText.fontSize(18)

		if breakQ:
			breakLimit = 10
			if len(item)> breakLimit:
				t = item.split()
				ttrunk1=t[:breakLimit]
				ttrunk2=t[breakLimit:]
				j=" ".join(ttrunk1)
				k=" ".join(ttrunk2)
				Question=self.Panel.setText("   "+j+"\n"+"   "+k)
		else:
			Question=self.Panel.setText("   "+a+"\n"+"                          .                      ")


	def changeQ(self,panelTitle,breakQ=True):
		#print self.survey
		indexQuestion="warmup"
		shuffle(self.survey)
		self.Panel.visible(viz.OFF)
		yield viztask.waitTime(int(self.delay))
		self.Panel.visible(viz.ON)
		self.rowBottom.visible(viz.ON)
		#self.maxNumber.visible(viz.ON)

		for counter, items in enumerate(self.survey) :

			self.Panel.setTitle(panelTitle)
			viz.callback(self.dinput.HAT_EVENT, self.onHatChange)
			question = items.split(":")[1]
			index = items.split(":")[0]
			scale = items.split(":")[2]

			self.changeMessage(question, scale, breakQ)

			#track.setEnabled(viz.OFF)
			yield viztask.waitAny([self.waitButton1],self.d)
			if self.d.condition is self.waitButton1:
					yield viztask.waitTime(.2)
					pos = self.Slider.get()
					if round(abs(pos/.1),1) > 0:
						#saveRate(qIndex,sceneIndex,index)
						self.Slider.set(0)
						self.Slider.message( "" )
						yield viztask.waitTime(.2)
					else:
						#Panel.setTitle("MINIMUM SELECTION IS (0)")
						yield viztask.waitTime(3)
			if counter > len(self.survey):
				break
		self.Panel.visible(viz.OFF)
		yield viztask.waitTime(1)


class panel:

	## Setup color Theme ##
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


	def __init__(self):

		self.canvas = viz.addGUICanvas()	# Create canvas for display UI to user

	def draw(self, panel = True, slider = True):

		if panel:
					#### Panels ######

			self.Panel = vizinfo.InfoPanel('', icon=False,parent=self.canvas,fontSize=18)	#Define main Panel#
			self.Panel.alpha(.8) #set transparency
			self.rowBottom= vizdlg.Panel(layout=vizdlg.LAYOUT_HORZ_CENTER, background=False, border=False, theme=self.blackTheme, spacing=30)	#Add rows to the panel#
			self.Panel.addSeparator(.8,padding=(10, 10))
			self.Panel.addItem(self.rowBottom)
			self.rowBottom.setTheme(self.blackTheme)
			self.Panel.getPanel().fontSize(22)
			self.Panel.setTheme(self.blackTheme)
			self.Panel.getPanel().font('Times New Roman')
			self.Panel.getPanel().fontSize(12)

		if slider:
						### SLIDER ######
			self.Slider= self.rowBottom.addItem(viz.addProgressBar("0"))
			self.Slider.font('calibri')
			self.Slider.setScale(4,2.4)
			self.Slider.message( str('%.2f'%(round(0)))[:1] )
			viz.link(viz.CenterBottom,self.Panel,offset=(260, 250, 0))
			self.Slider.visible(viz.OFF)
			return self.Panel, self.rowBottom, self.Slider
		else:
			return self.Panel, self.rowBottom

	def infoPanel(self,message):
			Panel2 = vizinfo.InfoPanel(message,parent=self.canvas,align=viz.ALIGN_CENTER,fontSize=22,icon=False,title="Finished")
			Panel2.alpha(.8)

#participant(4)
#viztask.schedule(IVE().execute())
viztask.schedule(IVE().execute())
#print survey().canvas
