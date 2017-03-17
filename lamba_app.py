import urllib2
import os
import json

# Class to define a home device that to be controlled by Alexa. eg. Lamp
class AlexaHomeApp:
    def __init__(self, applianceId, name, id):
        self.applianceId = applianceId
        self.manufacturerName = 'weigao'
        self.modelName = 'model 01'
        self.version = '0.1'
        self.friendlyDescription = 'descriptionThatIsShownToCustomer'
        self.friendlyName = name
        self.isReachable = True
        self.actions = ["turnOn", "turnOff"]
        self.additionalApplianceDetails = {'id':id}

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

# The function that Lambad will call to handle any events.
def lambda_handler(event, context):
    eventname = event['header']['namespace']
    if eventname == 'Alexa.ConnectedHome.Discovery':
        return handleDiscovery()
    elif eventname == 'Alexa.ConnectedHome.Control':
        return handleControl(event) 

bigLightOnly = AlexaHomeApp("only1", "light only", "light1")
smallLightOnly = AlexaHomeApp("only2", "small only", "light2")
deskLightOnly = AlexaHomeApp("only3", "desk only", "light3")
windowLightOnly = AlexaHomeApp("only4", "window only", "light4")
bigLight = AlexaHomeApp("light1", "light", "light1")
smallLight = AlexaHomeApp("light2", "small light", "light2")
deskLight = AlexaHomeApp("light3", "desk light", "light3")
windowLight = AlexaHomeApp("light4", "window light", "light4")
allLights = AlexaHomeApp("light1234", "all the lights", "light1234")

base_url = os.environ['BASE_URL']
RF1_ON = os.environ['RF1_ON']
RF1_OFF = os.environ['RF1_OFF']
RF2_ON = os.environ['RF2_ON']
RF2_OFF = os.environ['RF2_OFF']
RF3_ON = os.environ['RF3_ON']
RF3_OFF = os.environ['RF3_OFF']
RF4_ON = os.environ['RF4_ON']
RF4_OFF = os.environ['RF4_OFF']
RF_ON = "on"
RF_OFF = "off"

LIGHT1 = {RF_ON: RF1_ON, RF_OFF: RF1_OFF}
LIGHT2 = {RF_ON: RF2_ON, RF_OFF: RF2_OFF}
LIGHT3 = {RF_ON: RF3_ON, RF_OFF: RF3_OFF}
LIGHT4 = {RF_ON: RF4_ON, RF_OFF: RF4_OFF}
RF_MAP = {"light1": LIGHT1,
          "light2": LIGHT2,
          "light3": LIGHT3,
          "light4": LIGHT4, }

# This function return all the devices in a JSON body.
# see document in https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#discovery-messages
def handleDiscovery():
    header = {
        "namespace": "Alexa.ConnectedHome.Discovery",
        "name": "DiscoverAppliancesResponse",
        "payloadVersion": "2"
    }

    payload = {"discoveredAppliances": 
        [
            bigLight.__dict__,
            smallLight.__dict__,
            windowLight.__dict__,
            deskLight.__dict__,
            allLights.__dict__, 
            bigLightOnly.__dict__, 
            smallLightOnly.__dict__, 
            windowLightOnly.__dict__, 
            deskLightOnly.__dict__
        ]
    }

    response = {
        'header': header,
        'payload': payload
    }
    return response

# This is the function to handle the event request. The event will be generated when you talk to Alexa Echo with a valid request.
# See https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#onoff-messages
def handleControl(event):
    on = RF_ON
    name = "TurnOnConfirmation"

    event_name = event['header']['name']
    if event_name == 'TurnOnRequest':
        on = RF_ON
        name = "TurnOnConfirmation"
    elif event_name == 'TurnOffRequest':
        on = RF_OFF
        name = "TurnOffConfirmation"

    applianceId = event['payload']['appliance']['applianceId']
    if applianceId == allLights.applianceId:
        rf_list = map(lambda m: m[on], RF_MAP.values())
        send_request_batch(rf_list)
    elif applianceId.startswith('only'):
        rf_list = map(lambda m: m[RF_OFF], RF_MAP.values())
        light_id = event['payload']['appliance']['additionalApplianceDetails']['id']
        rf_list.remove(RF_MAP[light_id][RF_OFF])
        rf_list.append(RF_MAP[light_id][RF_ON])
        send_request_batch(rf_list)
    else:
        send_request(applianceId, on)

    header = {
        "namespace": "Alexa.ConnectedHome.Control",
        "name": name,
        "payloadVersion": "2",
    }
    return {
        'header': header,
        'payload': {}
    }

# Send the HTTP request to Raspberry Pi server
def send_request(id, on):
    url = base_url + "/rf?frequency=" + RF_MAP[id][on]
    urllib2.urlopen(url)

# Since our Raspberry Pi server support batch, this is the command for sending multiple RF transmitter request in one Http Request.
def send_request_batch(frequency_list):
    url = base_url + "/rf?frequency=" + ','.join(frequency_list)
    urllib2.urlopen(url)