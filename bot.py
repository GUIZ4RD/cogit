from random import randint
from time import sleep, gmtime, strftime
from functions import *
from settings import *
from emojis import Emojis
import pickle
import schedule
from threading import Thread
import string
import unirest
from flask import Flask, request
from pymessenger.bot import Bot
from pymessenger import Element
import requests
import json


VERSION = 0.2

VAR_TYPE = {'IS-STRING':'toString','IS-INT':'toInt','IS-FLOAT':'toFloat'}

users_context={}

brain = None
chat_id = 0

ALGORITHMS_LOAD = {'probabilistic': 'loadProba', 'standard': 'loadStandard'}
ALGORITHMS_MATCH = {'probabilistic': 'matchProba', 'standard': 'matchStandard'}


@app.route("/", methods = ['GET', 'POST'])
def incoming():

    """Handle incoming messages from users"""

    # Just for facebook validation
    if request.method == 'GET':
        if (request.args.get("hub.verify_token") == VERIFY_TOKEN):
                return request.args.get("hub.challenge")
    #--------------------------


    # Incoming message from users
    if request.method == 'POST':
        output = request.json

    event = output['entry'][0]['messaging']
    for x in event:
        if (x.get('message') and x['message'].get('text')):
            message = x['message']['text'].lower()
            recipient_id = x['sender']['id']
        elif (x.get('postback') and x['postback'].get('payload')):
            message = x['postback']['payload'].lower()
            recipient_id = x['sender']['id']

        think(recipient_id ,message)



def think(chat_id, text):

    """Function used to compute the answer based on user message and current chat's context

        Parameters
        ----------
        chat_id: unique identifier for an user
        text: the corpus of the user's message
    """

    if(UNDER_MAINTENANCE and DEV_ID!=chat_id):
      bot.send_text_message(chat_id,UNDER_MAINTENANCE_MSG)
      return

    text = text.encode('ascii', 'ignore').decode('ascii')

    global brain
    global conn

    #Retrieve current context
    context=getChatContext(chat_id)

    if(DEBUG):
        Log.d("INCOMING",str(chat_id)+": "+text+" ["+context+"]")

    # Get responses for context
    my_var = None
    response = brain[context]

    # If the text is a "base" message (I.E: Hello, How are you ?), ignore the current context
    if(text in brain['base']):
      response = brain['base'][text]


    else:

      input_type = isInput(response)

      if(input_type is not None):
        response=response[input_type]
        my_var = getInput(text,input_type)
        if(my_var==-1):
              response = response['result']['error']

      else:
        try:
          response2 = response
          response = globals()[str(ALGORITHMS_MATCH[ALGORITHM])](response, text)
          if(response==None):
            response = globals()[str(ALGORITHMS_MATCH[ALGORITHM])](brain['base'], text)
            if(response==None):
              if(haveField(response2,'default')):
                response = response2['default']
              else:
                response = brain['base']['default']
        except Exception, e:
          print e

    # If the request contains an action execute it and select the correct result
    if(haveAction(response)):
      if(haveField(response,"parameter")):
        if(response['parameter']==True):
          my_var=text
      if(my_var is None):
          if(haveId(response)):
            result=globals()[str(response['action'])](chat_id)
          else:
            result=globals()[str(response['action'])]()
      else:
          if(haveId(response)):
            result=globals()[str(response['action'])](chat_id,my_var)
          else:
            result=globals()[str(response['action'])](my_var)

      if(isinstance(result,dict) and response['action']!='setAlertHour' and response['action']!='setWakeupHour' and response['action']!='setBreakfast' and response['action']!='setLunch' and response['action']!='setDinner' and response['action']!='setMorningSnack' and response['action']!='setAfternoonSnack' and response['action']!='setNightSnack'):
        response=response['result']['ARRAY']
        response['text']=replacePlaceholder(response['template'],result)
      elif(haveResult(response)):
        if(response['action']=='setAlertHour' or response['action']=='setWakeupHour' or response['action']=='setBreakfast' or response['action']=='setLunch' or response['action']=='setDinner' or response['action']=='setMorningSnack' or response['action']=='setAfternoonSnack' or response['action']=='setNightSnack'):
          if(result!="error"):
            setAlert(result['chat_id'],result)
            result="ok"
        response=response['result'][result]
      else:
        response['text']=replacePlaceholder(response['template'],result)

    # Store new context for user
    if(newContext(response)):
      setChatContext(chat_id, response['context'])

    keyboard=None
    # If output contain button, add it to the response

    if(haveField(response, "choose")):
      keyboard = getInlineKeyboard(response['choose'],chat_id)
    elif(haveField(response, "buttons")):
      keyboard = getInlineKeyboard(response['buttons'],chat_id)

    response=response.copy()
    response['text'] = replaceInfos(response['text'],chat_id)

    # Send response to user client
    if(haveField(response, "template")):
        text = replacePlaceholder(response["template"], result)
        if(haveField(response, "choose")):
          keyboard = getInlineKeyboard(response['choose'],chat_id)
          raw = sendButtons(chat_id,text,keyboard)
          content=bot.send_raw(raw)
        else:
          content=bot.send_text_message(chat_id,text) #ADD HTML PARSING

    elif(keyboard != None):
      if(haveField(response, "choose")):
        raw = sendButtons(chat_id,response['text'],keyboard)
        content=bot.send_raw(raw)
      elif(haveField(response, "buttons")):
        response['text'].lower()
        if(response['text'].lower()=="Great, keep pushing ! Do you want to share your result ?".lower() or response['text'].lower()=="You're getting stronger ;) do you want to share your result ?".lower() or response['text'].lower()=="Okay, i'll take note of this for your next workout, do you want to share your result ?".lower()):
          bot.send_image_url(chat_id,IMG_SHARE_URL.replace("$ID",chat_id))
        content=bot.send_button_message(chat_id, response['text'], keyboard)
    else:
      content=bot.send_text_message(chat_id,response['text']) #ADD HTML PARSING



def sendButtons(recipient_id, text, keyboard):
    raw = ({
                "recipient":{
                    "id":recipient_id
                },
                "message":{
                "text":text,
                "quick_replies":[]
                }})

    for button in keyboard:
        raw["message"]["quick_replies"].append({
                        "content_type":"text",
                        "title":button['title'],
                        "payload":button['payload']
                    })
    return raw



def sendButtons(recipient_id, text, keyboard):
    raw = ({
                "recipient":{
                    "id":recipient_id
                },
                "message":{
                "text":text,
                "quick_replies":[]
                }})

    for button in keyboard:
        raw["message"]["quick_replies"].append({
                        "content_type":"text",
                        "title":button['title'],
                        "payload":button['payload']
                    })

    return raw


def getInlineKeyboard(buttons,id):
  keyboard = []
  for line in buttons:
    for text in line:
      button = {}
      if(text.lower()=='yeah, share'):
        button['title'] = text
        button['type'] = 'web_url'
        user_share = SHARE_URL.replace("$ID",str(id))
        button['url'] = user_share
      else:
        button['title'] = text
        button['type'] = 'postback'
        button['payload'] = text
      keyboard.append(button)
  return keyboard


def containsUrl(text):
  pos = text.find("http")
  return pos


def replacePlaceholder(text, parms):
  plcs = getParameters(text)
  for plc in plcs:
      text=text.replace("$"+plc.upper(), str(parms[plc.lower()]))
  return text

def replaceInfos(text, id):
  infos = ['index','first_name','last_name','id','fitness','lang','sex','age','workout']
  user=users.get(id)
  if(user==None):
    initUser(id)
    user=users.get(id)
  plc_start = text.find("*")
  sub_text = text
  counter = 0
  while plc_start != -1:
    if(counter==10):
      return
    counter+=1
    sub_text = sub_text[plc_start+1:]
    plc_end = sub_text.find(" ")
    if(plc_end==-1):
      plc = sub_text
    else:
      plc = sub_text[:plc_end].replace(" ","").replace(",","").replace(".","")
    plc_start = sub_text.find("*")

    for i in range(0,len(infos)):
      if(infos[i]==plc.lower()):
        text=text.replace("*"+plc.upper(), str(user[i]))
  return text


def haveField(response, field):
  if field in response:
    return True
  else:
    return False

def haveId(response):
  if 'id' in response:
    return True
  return False

def haveResult(response):
  if 'result' in response:
    return True
  return False

def haveAction(response):
  if 'action' in response:
    return True
  return False


def newContext(response):
  if 'context' in response:
    return True
  return False

def isInput(response):
  global VAR_TYPE
  for var in VAR_TYPE:
    if var in response:
      return var
  return None

def getInput(text,type):
   global VAR_TYPE
   try:
      return globals()[VAR_TYPE[type]](text)
   except Exception, e:
      print e
      return -1

def getParameters(string):
    loc=string.find("$")
    offset=0
    par=[]
    while(loc!=-1):
        offset+=loc+1
        string=string[loc+1:]
        loc=string.find("$")

        c = string[0]
        s = ""
        i = 0
        while(c.isupper()):
            s+=c
            i+=1
            if(i>=len(string)):
                break
            c=string[i]
        par.append(s)
    return par


### CONVERTERS AND VALIDATORS ###

def toInt(var):
  return [int(s) for s in var.split() if s.isdigit()][0]

def toFloat(var):
   return float(var)

def toString(var):
   return str(var)

def setChatContext(chat_id, context):
  global users_context
  try:
    users_context[chat_id]=context
    with open(BASE_PATH+'users_context.pkl', 'wb') as output:
      pickle.dump(users_context, output, pickle.HIGHEST_PROTOCOL)

  except Exception, e:
    print e

def getChatContext(chat_id):
  try:
    with open(BASE_PATH+'users_context.pkl', 'rb') as input:
      users_context = pickle.load(input)
    return users_context[chat_id]
  except Exception, e:
    print e
    return "base"

#--------------------------------


## MATCHING ALGORITHMS ##

def matchStandard(response, text):

    """Standard matching, it select a response that contains
        exactly the user message

        Parameters
        ----------
        response: the text corpora where search
        text: the user's message
    """

  return response[text]


def matchProbab(response, text):

    """Perform a probabilistic matching between user message and text corpora
        using a modified implementation of TF/IDF,
        it select the text with lower cost (better affinity),
        if nothing is found or the cost is less than the threshold
        it will return the standard response

        Parameters
        ----------
        response: the text corpora where search
        text: the user's message
    """

	best_match = {"text":"","cost":1000.0}
	processed_text = preprocess(text).split(" ")
	for pattern in response:
		if(len(pattern)>0):
			words_list = pattern.lower().split(" ")
			diff = float(len(list(set(words_list) - set(processed_text))))/float(len(words_list))
			if(diff<best_match['cost']):
				best_match['cost']=diff
				best_match['text']=pattern

    if(DEBUG):
	       Log.d("Best pattern: "+best_match['text']+" ["+str(best_match['cost'])+"]")
	if(best_match['score']<=PROBA_THRESHOLD):
		return response[best_match['text']]
	return None

#----------------------------


# TEXT CORPORA LOADING ALGORITHMS #

def loadProba():

  """
    Build a TF/IDF with text corpora
  """"

  import glob
  import json

  global brain

  sentences_counter=0
  context_counter=1

  files=glob.glob("var/www/html/thecoach/app/corpora/*.json")
  files.remove("var/www/html/thecoach/app/corpora/brain.json")

  with open("var/www/html/thecoach/app/corpora/brain.json") as file:
    tmp_brain = json.load(file)

  for file in files:
    with open(file) as jfile:
      my_json_2 = json.load(jfile)

    for key in my_json_2:
      if(key=="base"):
        sentences_counter+=len(my_json_2[key])
        tmp_brain[key].update(my_json_2[key])
      else:
        sentences_counter+=len(my_json_2[key])
        tmp_brain[key]=my_json_2[key]
        context_counter+=1

  brain = {}

  for key in tmp_brain:
    brain[key]={}
    for pattern in tmp_brain[key]:
      try:
        brain[key][preprocess(pattern)] = tmp_brain[key][pattern]
      except Exception, e:
        print e
        print "KEY: "+key
        print tmp_brain[key]
  print "Total context in brain: "+str(context_counter)
  print "Total sentences in brain: "+str(sentences_counter)


def loadStandard():
  import glob
  import json

  global brain

  sentences_counter=0
  context_counter=1

  files=glob.glob("var/www/html/thecoach/app/corpora/*.json")
  files.remove("var/www/html/thecoach/app/corpora/brain.json")

  with open("var/www/html/thecoach/app/corpora/brain.json") as file:
    brain = json.load(file)

  for file in files:
    with open(file) as jfile:
      my_json_2 = json.load(jfile)

    for key in my_json_2:
      if(key=="base"):
        sentences_counter+=len(my_json_2[key])
        brain[key].update(my_json_2[key])
      else:
        sentences_counter+=len(my_json_2[key])
        brain[key]=my_json_2[key]
        context_counter+=1

  print "Total context in brain: "+str(context_counter)
  print "Total sentences in brain: "+str(sentences_counter)

#----------------------------



def setAlert(id,time):
	print "set-alert for "+str(id)
	print time
	hour = time['hour']
	days = time['days'].strip().split(',')
	print days

	for day in days:
            if(day=='1'):
                print schedule.every().monday.at(hour).do(job,id)
            elif(day=='2'):
                print schedule.every().tuesday.at(hour).do(job,id)
            elif(day=='3'):
                print schedule.every().wednesday.at(hour).do(job,id)
            elif(day=='4'):
                print schedule.every().thursday.at(hour).do(job,id)
            elif(day=='5'):
                print schedule.every().friday.at(hour).do(job,id)
            elif(day=='6'):
                print schedule.every().saturday.at(hour).do(job,id)
            elif(day=='7'):
                print schedule.every().sunday.at(hour).do(job,id)


def job(id):
	alerts = PermanentStorage()
	alerts.create(name='alerts', fields={'chat_id':'VARCHAR(20)', 'days':'VARCHAR(30)', 'hour':'VARCHAR(30)','local_hour':'VARCHAR(30)'})
	if(alerts.contains(id)):
		alert = alerts.get(id,'hour')
		print alert
		ctime=strftime("%H:%M", gmtime())
		print ctime
		if(alert[0]==ctime):
			try:
				response = brain["sheduled"]["workout-alert"]
				setChatContext(id, response['context'])
				keyboard = getInlineKeyboard(response['choose'],chat_id)
				raw = sendButtons(id,response['text'],keyboard)
				bot.send_raw(raw)

			except Exception, e:
				print e
				print "Unable to send notification to user "+str(id)+": Bot was blocked by user"
		else:
			return schedule.CancelJob
	else:
		return schedule.CancelJob


def run_schedule():
    print "SETUP SCHEDULE"
    while 1:
        schedule.run_pending()
        sleep(1)


def preprocess(sentence):
    """Preprocess the sentenes,
        convert to lowercase and remove punctuation
    """

  if "-" in sentence or "/" in sentence:
    return sentence
  sentence = str(sentence)
  sentence = sentence.lower()
  sentence = sentence.translate(None, string.punctuation)
  return sentence



app = Flask(__name__)
bot = Bot(MESSENGER_TOKEN)

print "Initializing..."
globals()[str(ALGORITHMS_LOAD[ALGORITHM])]()

# Load alerts from alertDB and set them up for each user
alerts_db = PermanentStorage()
alerts_db.create(name='alerts', fields={'chat_id':'VARCHAR(20)', 'days':'VARCHAR(30)', 'hour':'VARCHAR(30)','local_hour':'VARCHAR(30)'})
alerts = alerts_db.getAll()
print alerts

print "Setting alerts..."
for alert in alerts:
  id=int(alert[1])
  time={'hour':alert[2],'days':alert[3]}
  setAlert(id,time)


t = Thread(target=run_schedule)
t.start()

emojis = Emojis()
if __name__ == "__main__":
    app.run(port=PORT, debug=DEBUG)
