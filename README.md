[Still in progress]
# Alexa Smart Home

Imagine you could turn on and off each lamp in your home by just saying "Alex, turn on the xxx lamp". Imagin in the moring, you could lying on the bed and say "Alexa, turn on the curtain", and let the light wake you up. To me, voice controlled smart home has always been something only in the movie. But now everyone can build it with a low budget.

This project is to build a voice-controlled smart home system based on Amazon Alexa and Raspberry Pi. The Amazon Alexa provides a convenient API for voice command. The Raspberry Pi sends RF signal to RF remote outlet. 

With all the required hardware and basic software knowledge (mainly Python and Linux), this project could be finished in about 6 hours by following this tutorial. 

`See video demo:`
https://www.youtube.com/watch?v=PNNSHEmuHxk

`Data flow chart:`
<img src=https://cloud.githubusercontent.com/assets/1740687/23840867/28c6e3ae-077f-11e7-891c-3209f4bbded2.png />

# Hardware

All the hardware components you need to prepare.

## An Alexa device.
[img]
An Alexa device receives voice command from a human being, and then send it to the cloud service for voice recognition. The voice will eventually be translated to English for further processing.

Technically any Alexa supported device will do. I used an Alexa Echo Dot, because it always wait for command when stand by, which is perfect for smart home. (You could try the iphone app or the web app, which doesn't require you to buy anything, but it's not a good fit for the smart home purpose because you have to open the app every time you want to send a voice command).

## A Raspberry Pi.
[img]
A Raspberry Pi(RPI) runs an HTTP server, which listen to HTTP requests and send comand to an RF transmitter chip. (There are other components between Alexa and RPI, see Software section)

Using an RPI because it provides a development platform with linux OS and GPIO support, plus the size and price is perfect for this project. Options could be:

1. RPI 3
2. RPI zero + wifi dongle (size advantage)
3. Older RPI versions (didn't try)

## 433Mhz Rf Transmitter and Receiver chips

This kind of chip is available on Amazon or other electrical chip market.
This is the chip that I use:
[img]


## 433Mhz based remote outlet, or 433Mhz based home appliance
[img]
These are the hardware that you want to voice control.
1. For lamps and other appliance that could only turn on and off, you could connect them with RF remote outlet. I use this one which I bought from Amazon
[img]
2. If you have other home appliance that support 433Mhz RF signal, it's the same. (433Mhz radio requency is a very common standard for home devices, just to name a few, shelf speaker, remote controlled curtain, garage door remote...)


### Others

Essential hardware development tools like jump wire, bread board and Electric iron.


# Software

Unlikely to the Hardware section, here are all the required software component and knowledge, which are free, but might take a while to learn.

We are going backwards this time. Starting from the last step of the data flow to the first one.


## Send and receive 433Mhz RF signal on Raspberry Pi

### Circuit connection
In order to let the Raspberry Pi send 433Mhz RF signal, we need to connect the Raspberry PI GPIO to the RF transmitter and receiver. Connect them like this:

<img src="https://cloud.githubusercontent.com/assets/1740687/23884869/e5dc401c-0845-11e7-8cc2-91b6324c6c87.png" />

If you're using a breadboard it should look like this:

<img src="https://cloud.githubusercontent.com/assets/1740687/23885046/14687738-0847-11e7-9f48-a60bbd2f7419.png" />

### Use receiver to sniff the RF signal

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
Write down the seven digits integer numbers, they are the RF value we'll send later.

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

1. The local ip address of your Raspberry Pi, you could get it by command `ifconfig`, you could also login to your router to find this value.
2. The default port that flask uses is `5000`, you could also change the port, see [Flask doc](http://flask.pocoo.org/docs/0.12/api/)
3. The RF switch number, which you get from the previous section.
4. Check if the TCP port that flask uses is open to local ethernet. (It may behind the firewall, open that specific port on your raspberry pi first)

Assume your Raspberry Pi local IP address is `192.168.1.25`, port is 5000, RF switch number is 1332995
Now find a computer(or even smart phone) that is connected to the same wifi, open the web browser and type the following in the address line:
```
http://192.168.1.25:5000/rf?number=1332995
```
Congratuations, now you could control all your RF switches using any devices that connected to your home wifi. For this project we also need to do it outside the local router, which means that you will be able to control your RF switches anywhere in the world with Internet. This may sound not that useful, but it's necessary because in the next section, we'll build a service on Amazon Lambda, so that the http request will be from Amazon. It is not hard though, we'll be using two features that most home routers should have:
1. Address Reservation. This feature allows the router to always assign a specific IP address to a specific device (MAC address). 
2. Port forwarding. This feature allows the router to forward any request from external port to an internal ip address.

Find these two features on the manual of your router. You could also try to find them by just playing with the router app, they are very liked be under `advanced` menu.

After setup the two features above, we need to find our external IP address (The Ip address that from the ISP)，simply google "what's my ip", and the first search result should be it. Now using the same URL but change the local IP address with the external one, and you should be able to control the RF switch from external. (Try it on your smart iphone with 4G)


## Amazon Smart Home API

### Create an Amazon Oauth Profile

In this section, we'll create an Amazon Oauth Profile for later usage. Oauth is a standard protocal for third party to get access a user's account information without exposing the user's password. For example, a lot of apps uses `Facebook Login`, or `Google Login` as their registration flow, the base of which is Oauth. In this tutorial we'll use Amazon's service as our Oauth server. 



[Amazon Smart Home API](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/overviews/understanding-the-smart-home-skill-api#undefined)
[Amazon OAUTH setup](https://developer.amazon.com/blogs/post/Tx3CX1ETRZZ2NPC/Alexa-Account-Linking-5-Steps-to-Seamlessly-Link-Your-Alexa-Skill-with-Login-wit)

# Conclusion

This 