; HEADER
G0 F10000
M280 P0 S100 G0 Z10 
G28
; Acceleration
M204 T1000
; Max X jerk
M205 X1.0 
; Max Y jerk 
M205 Y1.0 

; Body

; TravelMove


; Pen Down
G4 P200 
M280 P0 S0 G0 Z0

G0 X100 Y800
G0 X0 Y700
G0 X100 Y600
G0 X0 Y500
G0 X100 Y400
G0 X0 Y300
G0 X100 Y200
G0 X0 Y100
G0 X100 Y0
G0 Y50

; Pen Up
G4 P200 
M280 P0 S100 G0 Z10





; FOOTER
G4 P200
M280 P0 S100
G0 X0
M84
M282 P0
