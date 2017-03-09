from flask import Flask
from flask import request
from pi_switch import RCSwitchSender

app = Flask(__name__)
sender = RCSwitchSender()
sender.enableTransmit(0)  # use WiringPi pin 0
sender.setPulseLength(189)

@app.route("/rf", methods=['GET'])
def rf():
    f = request.args.get('frequency')
    frequency_list = f.split(',')
    for frequency in frequency_list:
        sender.sendDecimal(int(frequency), 24)
    return ""

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)