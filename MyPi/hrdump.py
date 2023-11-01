import max30102

m = max30102.MAX30102()

red, ir = m.read_sequential(100)

bpm, valid_bpm, spo2, valid_spo2 = hrcalc.calc_hr_and_spo2(ir_data, red_data)
printstr = ""
if valid_bpm:
    printstr += "BPM: {0}".format(bpm)
else:
    printstr += "BPM: invalid"

if valid_spo2:
    printstr += "SpO2: {0}".format(spo2)
else:
    printstr += "SpO2: invalid"

m.shutdown()
