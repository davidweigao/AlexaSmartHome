# Alexa Smart Home

Imagine you could turn on and off each lamp in your home by just saying "Alex, turn on the xxx lamp". Imagine in the moring, you could be lying on the bed and say "Alexa, turn on the curtain", and let the light wake you up. For me, voice controlled smart home has always been something only in the movie. But now everyone can build it with a low budget.

This project is to build a voice-controlled smart home system based on Amazon Alexa and Raspberry Pi. The Amazon Alexa provides a convenient API for voice command. The Raspberry Pi sends RF signal to RF remote outlet. 

With all the required hardware and basic software knowledge (mainly Python and Linux), this project could be finished in about 6 hours by following this tutorial. 

`See video demo:`
https://www.youtube.com/watch?v=PNNSHEmuHxk

`Data flow chart:`
<img src=https://cloud.githubusercontent.com/assets/1740687/23840867/28c6e3ae-077f-11e7-891c-3209f4bbded2.png />

This is the final version of the Raspberry Pi Zero + RF transmitter + wifi dongle, however during development, a Raspberry Pi 3+ and breadboard will be used.
![img_0501](https://cloud.githubusercontent.com/assets/1740687/24025427/a8a03a1c-0a90-11e7-9e01-5bc20e9053f3.JPG)

# Hardware

All the hardware components.

## An Alexa device

![image](https://cloud.githubusercontent.com/assets/1740687/24025171/4173a136-0a8f-11e7-8fa8-ac7b61d4c94b.png)

An Alexa device receives voice command from a human being, and then send it to the cloud service for voice recognition. The voice will eventually be translated to English for further processing.

Technically any Alexa supported device will do. I used an Alexa Echo Dot, because it always wait for command when stand by, which is perfect for smart home. (You could try the iphone app or the web app, which doesn't require you to buy anything, but it's not a good fit for the smart home purpose because you have to open the app every time you want to send a voice command).

## A Raspberry Pi

![image](https://cloud.githubusercontent.com/assets/1740687/24025184/60159086-0a8f-11e7-9b30-57bb74ef0c21.png)

A Raspberry Pi(RPI) runs an HTTP server, which listen to HTTP requests and send comand to an RF transmitter chip. (There are other components between Alexa and RPI, see Software section)

Using an RPI because it provides a development platform with linux OS and GPIO support, plus the size and price is perfect for this project. Options could be:

1. RPI 3 (easy for development prototype)
2. RPI zero + wifi dongle (size advantage)
3. Older RPI versions (didn't try)

## 433Mhz Rf Transmitter and Receiver chips

![image](https://cloud.githubusercontent.com/assets/1740687/24025204/785f8930-0a8f-11e7-9f4c-93b9a714108d.png)

This kind of chip is available on Amazon or other electrical chip market.


## 433Mhz based remote outlet, or 433Mhz based home appliance
These are the hardware that you want to voice control.

1. For lamps and other appliance that could only turn on and off, you could connect them with RF remote outlet. I use this one which I bought from Amazon
![ras](https://cloud.githubusercontent.com/assets/1740687/24025394/75692776-0a90-11e7-973b-491d4766ff17.jpg)

2. If you have other home appliance that support 433Mhz RF signal, theoritically they could also be controlled. However this tutorial will only focus on RF switch control. (433Mhz radio requency is a common standard for home devices, just to name a few, bookshelf speaker, remote controlled curtain, garage door remote...)


### Others

Essential hardware development tools like jump wire, bread board and Electric iron.


# Implementation

This section includes are all the required software components, starting from the last step of the data flow to the first one. (see the data flow diagram above)


## Send and receive 433Mhz RF signal on Raspberry Pi

### Circuit connection
In order to let the Raspberry Pi send 433Mhz RF signal, we need to connect the Raspberry PI GPIO to the RF transmitter and receiver. Connect them like this:

<img src="https://cloud.githubusercontent.com/assets/1740687/23884869/e5dc401c-0845-11e7-8cc2-91b6324c6c87.png" />

If you're using a breadboard it should look like this:

<img src="https://cloud.githubusercontent.com/assets/1740687/23885046/14687738-0847-11e7-9f48-a60bbd2f7419.png" />

### Use the receiver to sniff the RF signal

After connect the chips correctly, we'll use the RF receiver chip to sniff the RF signal, it's an integer value that we'll send using the transmitter later.


Firstly, download the ``pi_switch` library using `pip`

```
pip install pi_switch
```

You could also checkout [the source code of this library](https://github.com/lexruee/pi-switch-python) to know more about how to use it.

After successfully install the library, create a python file named `receive_rf.py`, with the code:
```python
from pi_switch import RCSwitchReceiver

receiver = RCSwitchReceiver()
receiver.enableReceive(2)
while True:
    if receiver.available():
        received_value = receiver.getReceivedValue()
        if received_value: print(received_value)
        receiver.resetAvailable()
```
Then run the code with root permission:
```
sudo python receive_rf.py
```
While running the command, press the buttons on the RF remote controller, and you should see some numbers in the terminal:
```
1334531
1332995
1332995
1333004
1333004
```
Write down those seven digits integer numbers, they are the RF number that corresponding to each button you clicked on the RF remote, we'll send them using the transmitter chip later.

### Use transmitter to send the RF signal

Create a python file, name it `send_rf.py`, and put the following code in it:
```python
from pi_switch import RCSwitchSender

num = 1334531 #Change this to the value that you get in the previous section.
sender = RCSwitchSender()
sender.enableTransmit(0)
sender.setPulseLength(189)
sender.sendDecimal(num, 24)
```

run the code with command:
```
sudo python send_rf.py
```
It should send the specified RF signal, and the corresponding receiver should be able to receive it. If you're using a RF remote outlet to control a lamp, you've already been able to control the light with raspberry pi! Yeah!

The next section will be about control the light with HTTP request.



## HTTP server on Raspbery Pi

The next step is to build an http server on the Raspberry pi so that you could control the RF switch over internet. [Flask](http://flask.pocoo.org/) is the framework we'll use in this project because of its lightweighted and easy to use.

Firstly, install Flask using pip
```
pip install flask
```

Now create a file named "rf_server.py", with the code:

```python
from flask import Flask
from flask import request
from pi_switch import RCSwitchSender

app = Flask(__name__)
sender = RCSwitchSender()
sender.enableTransmit(0)  # use WiringPi pin 0
sender.setPulseLength(189)

@app.route("/rf", methods=['GET'])
def rf():
    n = request.args.get('number')
    number_list = n.split(',')
    for number in number_list:
        sender.sendDecimal(int(number), 24)
    return ""

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
```

Before we test on a web browser, there are something need to be done first:

1. The local **IP address** of your Raspberry Pi, you could get it by command `ifconfig`, you could also login to your router to find this value.
2. The default **TCP/IP Port** that flask uses is `5000`, you could also change the port, see [Flask doc](http://flask.pocoo.org/docs/0.12/api/)
3. The **RF switch numbers**, which you get from the previous section.
4. Check if the TCP port that flask uses is open to local ethernet. (It may behind the **firewall**, open that specific port on your raspberry pi first)

Assume your Raspberry Pi local IP address is `192.168.1.25`, port is 5000, RF switch number is 1332995
Now find a computer(or even smart phone) that is connected to the **same wifi**, open the web browser and type the following in the address line:
```
http://192.168.1.25:5000/rf?number=1332995
```
Congratuations, now you could control all your RF switches using any devices that connected to your home wifi. For this project we also need to do it outside the local router, which means that you will be able to control your RF switches anywhere in the world with Internet. This may sound not that useful, but it's necessary because in the next section, we'll build a service on Amazon Lambda, so the http request will be from Amazon. It is not hard though, we'll be using two features that most home routers should have:

1. Address Reservation. This feature allows the router to always assign a specific IP address to a specific device (MAC address). 

2. Port forwarding. This feature allows the router to forward any request from external port to an internal ip address.

Find these two features on the manual of your router. You could also try to find them by just playing with the router app, they are very liked to be under `advanced` menu.

Here is the screenshot form my router config:
Address Reservation:
![netgear router r6300 1](https://cloud.githubusercontent.com/assets/1740687/24027074/574d0324-0a9b-11e7-9ede-fc4dd41b255f.png)
Port forwarding:
![netgear router r6300](https://cloud.githubusercontent.com/assets/1740687/24027076/5ce18102-0a9b-11e7-8b83-df6e0bab3a93.png)

After setup the two features above, we need to find our external IP address (The Ip address that from the ISP)，simply google "what's my ip", and the first search result should be it. Now using the same URL but change the local IP address with the external one, and you should be able to control the RF switch from external. (Try it on your smart iphone with 4G)


## Amazon Smart Home API

### Create an Amazon Oauth Profile

In this section, we'll create an Amazon Oauth Profile for later usage. [Oauth](https://en.wikipedia.org/wiki/OAuth) is a standard protocal for third party to get access a user's account information without exposing the user's password. For example, a lot of apps uses `Facebook Login`, or `Google Login` as their registration flow, the base of which is Oauth. In this tutorial we'll use Amazon's service as our Oauth server. 

1. Login to [Amazon Developer Console](https://developer.amazon.com/lwa/sp/overview.html) and create a new Profile like this:
![oauth1](https://cloud.githubusercontent.com/assets/1740687/23980105/13da204e-09d4-11e7-8e3d-e6f64ae50f45.png)

2. Type in some demo text into the required field (not important for personal use), and click save:
![oauth2](https://cloud.githubusercontent.com/assets/1740687/23980117/2b4dbefc-09d4-11e7-980d-d2d37424eb54.png)

3. Copy this two values into somewhere for future use
![oauth3](https://cloud.githubusercontent.com/assets/1740687/23980137/5a7cd302-09d4-11e7-9343-6eb179a97064.png)


### Create an Amazon Lambda Function

[Amazon Lambda](https://aws.amazon.com/lambda/) is a AWS service that provides a lightweighted serverless box for running stateless functions. This is perfect for this project since it's easy to configure and free of charge. 

In this section, we'll create an empty Lambda function and configure it later.

1. Login to Amazon Lambda and click `New function`, then select `Blank Function`:
![lambda1](https://cloud.githubusercontent.com/assets/1740687/23980357/8954ee5c-09d5-11e7-8fee-a3e3379cecea.png)

2. Just click `next`
![lambda2](https://cloud.githubusercontent.com/assets/1740687/23980278/2baf3c58-09d5-11e7-978f-aa4b9708c940.png)

3. On this page, do the following and click `Next`
![lambda3](https://cloud.githubusercontent.com/assets/1740687/23980386/a94a23d0-09d5-11e7-83c0-07f2a802caa3.png)

4. On this page, leave everything default and click `Create Function`:
![lambda4](https://cloud.githubusercontent.com/assets/1740687/23980403/b5f2ddac-09d5-11e7-80c6-e03d877831a5.png)

5. You've just created an empty function, the page will take you to the function for coding and configuration. We'll leave everything empty and come back later, but **copy the `ARN` somewhere for the next section.**
![lambda6](https://cloud.githubusercontent.com/assets/1740687/23980442/db2ff8d4-09d5-11e7-9441-7160bb9eb90f.png)


### Create an Amazon Smart Home Skill

The last step is to create an `Amazon Smart Home Skill` using their API. This is like an App for the Alexa platform. 

1. Login to [Amazon Developer Console](https://developer.amazon.com/edw/home.html#/) and goes to the `Alexa`, click `Get Started` on `Alexa Skills Kit`
![smarthome0](https://cloud.githubusercontent.com/assets/1740687/23980641/4e59df90-09d7-11e7-9120-3fd6966f067e.png)

2. In the Alexa Skill list page, click `Add a New Skill` on the upper left corner
![smarthome0 5](https://cloud.githubusercontent.com/assets/1740687/23980650/62f25fae-09d7-11e7-9037-df66bdb71848.png)

3. On the Skill information configuration page, select `Smart Home Skill API` and create a Name. The name will be your skill name show up in your Alexa Mobile App later.
![smarthome2](https://cloud.githubusercontent.com/assets/1740687/23980675/922b28aa-09d7-11e7-8945-fe75013aaa64.png)

4. On the Interaction Model page, just click Next since we're using the Home Skill API
![smarthome1](https://cloud.githubusercontent.com/assets/1740687/23980664/7e06d752-09d7-11e7-9ef4-a4282e05111d.png)

5. On the configuration page, do the following, use the three values that we created from previous section:
![smarthome5](https://cloud.githubusercontent.com/assets/1740687/23980719/e7b2f0f0-09d7-11e7-8360-0eaadcee8fbd.png)


6. On this page, check `Show this skill in the Alexa App`, since we're not going to publish this App, this enabled the developer mode and be used without publishing if you're using the same Amazon account on your Alexa.
![smarthome4](https://cloud.githubusercontent.com/assets/1740687/23980712/d531dd7e-09d7-11e7-8204-760382cc99e7.png)

After finish the above steps, just click save and skip the publishing and privacy configuration, and go back to the skills list, the created skill will be there. Then do the following two things:

1. Click into the created skill, and copy the Skill `ID`, which should be under the Skill Name, it should start with `amzn1.ask.skill` followed by a long UUID.

2. Go to your iOS/Android Alexa App -> Skills -> My Skills, you should find the created skill in the list. Click the skill and then click `Enabled`, then it will take you to an Amazon login page. Login with your Amazon account (To get the Oauth token)(The Amazon account of the Alexa Echo should be the same as the Amazon Developer account)

### Configure the Amazon Lambda Function

In previous section we created an empty Lambda Function. Now let's configure it. 

First we need to create a trigger for the Lambda function.

1. Go back to the Lambda page, click into the function we created
2. go to tab `Triggers`, and click add triggers:
![lambda2-1](https://cloud.githubusercontent.com/assets/1740687/23981175/fa65bc16-09da-11e7-8a23-1a6ee05bbd25.png)
3. add a Amazon Smart Home trigger, the `Application Id` is the skill ID we created in the last section.
![lambda2-2](https://cloud.githubusercontent.com/assets/1740687/23981198/1bb9cf10-09db-11e7-83f8-be3b924ec9d0.png)

Click `submit`, and the trigger will be created. 

Now let's import the code `lambda_app.py` into the "code" section, add add the environement variables below. The env variables are your external ip address and the RF numbers of the RF switches. See previous sections to know how to get them.

![lambdacode](https://cloud.githubusercontent.com/assets/1740687/24024923/6d212b3e-0a8d-11e7-9c9d-65c62ac66f40.png)

Click save, and everything should just work now. You need to read the python code to change the name of the light/lamp in your room, change them accordingly, and try say "Alexa, turn on the [lamp name]" to Alexa Echo.

### Reference

1. [Blog about controlling RF switches with Raspberry Pi](https://www.samkear.com/hardware/control-power-outlets-wirelessly-raspberry-pi)
2. [Amazon Smart Home API](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/overviews/understanding-the-smart-home-skill-api#undefined)
3. [Amazon OAUTH setup](https://developer.amazon.com/blogs/post/Tx3CX1ETRZZ2NPC/Alexa-Account-Linking-5-Steps-to-Seamlessly-Link-Your-Alexa-Skill-with-Login-wit)

# Conclusion

This tutorial only described the simple flow of building the system, to know more and deeper about how each part works requires a lot more reading on the specific object. I hope whoever read this and does the project could enjoy the voice controlled smart home and maybe try build something more on top of it.
