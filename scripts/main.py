from orvibo.s20 import S20, discover

hosts = discover() # Discover devices on your local network.
s20 = S20("192.168.10.250") # Use a discovered host, or supply a known host.
print(s20.on) # Current state (True = ON, False = OFF).
#s20.on = True # Turn it on.
#s20.on = False # Turn it off.

