# Bogons
Bogons IPv4 for NSX-T

This Bogons script interacts with NSX-T to create a security Group called 'Bogons' and populates it with a list of Bogons IPv4 subnets for denying traffic to a destination.

It will then create a Gateway Firewall Policy and apply that policy to your Tier0 Gateway Logical Routers, dropping any traffic originating from a Bogons subnet 
