import os
import vizinput
from random import shuffle

currentDIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(currentDIR,"ENV")
DATA_PATH = os.path.join(currentDIR,"DATA")
CONFIG_PATH = os.path.join(currentDIR,"config")


#print expDesign()[1]



	
#participant(3)

class IVE:
	
	PID = "a"
	def __init__(self):

		self.config= self.readconfig()
		print self.config
		self.stimuli = self.config["stimuli"].strip(" ").split(",")
		self.warmup = self.config["warmup"].strip(" ").split(",")
		self.delay = self.config["delay"]
		self.PIDdigits = int(self.config["digits"])

		#self.group = self.participant(self.PIDdigits)[0]
		self.group = 'A'

		self.stimuliList=self.expDesign()[0][self.group]
		self.warmupList=self.expDesign()[1]
		
		self.survey = self.config["survey"]
		print self.survey
		self.splitSurvey = self.config["splitSurvey"]
		
		self.totalGroups = len(self.expDesign()[1].keys())
		print self.totalgroups

	
	def participant(self, character):
		
		''' Participant ID and filemangement '''
		
		subject = vizinput.input('Please enter the participant identification number?') #Prompt for the participant's identification number.	
		participantList=open(DATA_PATH+"/"+'participant_list.txt')	
		groups= expDesign()[0].keys()
		if not len(str(subject)) == character:
			print "Invalid ID ! entered id should have one 'alphabetical' character from {0} (case sensetive) and {1} 'digits'".format(groups,character-1)
			sys.exit()
				
		elif str(subject)[0] not in groups:
			print "Participant ID should start with an 'alphabetical' character from {0} (case sensetive)".format(groups)
			sys.exit()
				
		for line in participantList.readlines(): 
		
			if str(subject) == line[:character]:
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

		groupDIC={}
		warmupDIC={}
		stimuliList=[]
		if self.stimuli[0] == "True":
			
			
			stimuliList=[]
			if "VID" in self.stimuli[2]:
				
				stimuliList = [(file) for file in os.listdir(IMAGE_PATH) if file.endswith("_.MP4") and file[0]==self.group]		

			elif "IMG" in self.stimuli[2]:

				stimuliList = [(file[:-9]+ '.png') for file in os.listdir(IMAGE_PATH) if file.endswith("_negx.png") and file[0]==self.group]		
		
			for env in stimuliList:			
				if env[0] in groupDIC.keys():
					groupDIC[env[0]].append(env)
				else:
					groupDIC[env[0]] = [env]
				
			if "RAN" in self.stimuli[1]:
				for group in groupDIC.keys():
					shuffle(groupDIC[group])
					
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
			
			if "True" in self.survey:
				
				surveyFile = os.path.join(CONFIG_PATH,"survey.txt")
				survey = open(configFile,'r')
					
				if "True" in self.splitSurvey:
				
					print "a"
				elif "False" in self.splitSurvey:
					print "b"
				
		return groupDIC,warmupDIC,survey
			
	def execute(self):
		for index, scene in enumerate(self.stimuliList):
			print self.stimuliList[index]
			changescene(self.stimuliList[index])
			if self.survey:
				yield runRunsurvey(self.delay)
				
			
class survey:
	survey = [
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

	def __init__(self,scene,delay):
		
		self.scene = scene
		self.delay = delay
		
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
	def onHatChange(self,e):
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
			

	def changeQ(panelTitle,breakQ=True):
		indexQuestion="delay"
		shuffle(shuffleQuestionList)
		Panelvisible(Panel,0)
		yield viztask.waitTime(self.delay)
		Panelvisible(Panel,1)
		srowBottom.visible(viz.ON)
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
				
			indexQuestion=str(index+1)
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
		if qIndex==len(qList):
			#viztask.schedule(FadeToGrayTask())
			Panelvisible(Panel,0)
			sky.visible(viz.OFF)
			yield viztask.waitTime(1)		
#participant(4)	
IVE().execution()