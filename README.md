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



## Flask server on Raspbery Pi

## Amazon Smart Home API
[Amazon Smart Home API](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/overviews/understanding-the-smart-home-skill-api#undefined)
[Amazon OAUTH setup](https://developer.amazon.com/blogs/post/Tx3CX1ETRZZ2NPC/Alexa-Account-Linking-5-Steps-to-Seamlessly-Link-Your-Alexa-Skill-with-Login-wit)

# Conclusion

This 