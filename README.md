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

# Connection and prototype

# Software

Unlikely to the Hardware section, here are all the required software component and knowledge, which are free, but might take a while to learn.


## Send 433Mhz RF signal on Raspberry Pi

## Flask server on Raspbery Pi

## Amazon Smart Home API
[Amazon Smart Home API](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/overviews/understanding-the-smart-home-skill-api#undefined)
[Amazon OAUTH setup](https://developer.amazon.com/blogs/post/Tx3CX1ETRZZ2NPC/Alexa-Account-Linking-5-Steps-to-Seamlessly-Link-Your-Alexa-Skill-with-Login-wit)

# Conclusion

This 