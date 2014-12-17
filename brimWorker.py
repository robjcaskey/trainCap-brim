#!/usr/bin/env python
from dccpi import *
import time
import sys
import select

print "Lets get this show on the road!"

def kbHasData():
        dr,dw,de = select.select([sys.stdin], [], [], 0)
        return dr <> []
def kbGetData():
	return sys.stdin.readline()

class FakeDCCControllerThread:
	def __init__(self, dcc_controller):
		self.dcc_controller = dcc_controller
		self.dcc_encoder = dcc_controller.dcc_encoder
		self.idle_count = 0
	def join(self):
		self.tick()
	def tick(self):
		try:
			self.idle_count = 0
			state = self.dcc_controller.state
			if state is 'idle':
				self.dcc_encoder.send_idle(1)
				self.idle_count += 1
				if self.idle_count >= 250:
					# Resending the payload causes some
					# flickering in the lights, but we have
					# to in case the loco didn't get it
					self.dcc_controller.state = 'newpayload'
			elif state is 'startup':
				self.dcc_encoder.tracks_power_on()
				self.dcc_encoder.send_reset(2)
				self.dcc_controller.state = 'newpayload'
			elif state is 'shutdown':
				self.dcc_encoder.send_stop(2)
				self.dcc_encoder.send_reset(2)
				self.dcc_encoder.tracks_power_off()
				return
			elif state is 'newpayload':
				self.dcc_encoder.send_payload(2)
				self.dcc_controller.state = 'idle'
				self.idle_count = 0
			else:
				sys.stderr.write("Unknown state %s!" % state)
				self.dcc_controller.state = 'shutdown'
			time.sleep(0.015)
		except:
			self.dcc_encoder.tracks_power_off()
			m = "An exception ocurred! Please stop the controller!"
			sys.stderr.write(m)
			raise

e = DCCRPiEncoder(pin_a=3,pin_b=2,pin_break=0,packet_separation=15)
c = DCCController(e)           # Create the DCC controller with the RPi encoder
l1 = DCCLocomotive("DCC6", 3)  # Create locos (see DCCLocomotive class)
c.register(l1)        # Register locos on the controller
#c.start()            # Start controller. Remove brake signal
c._thread = FakeDCCControllerThread(c)
c.state = 'startup'
c._thread.tick()

l1.reverse()                  # Change direction bit
x = 0
total_ticks = 0 
current_speed = 0
last_time = time.time()
#while True:
quitting = False
while not quitting:
	c._thread.tick()
	if kbHasData():
		cmd = kbGetData().strip()
		exec(cmd)	
	if time.time() - last_time > 10:
		total_ticks += 1
		current_speed += 1
		print 'changing speed to %s' % current_speed
		last_time = time.time()
	#l1.speed = current_speed                 # Change speed
	if False:
		if total_ticks % 2:
			l1.fl = True
			l1.f1 = True
			l1.f2 = True
			l1.f3 = True
			l1.f4 = True
		else:
			l1.fl = False
			l1.f1 = False
			l1.f2 = False
			l1.f3 = False
			l1.f4 = False
c.stop()
