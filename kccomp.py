#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2010 Andres Calderon, andres.calderon@emqbit.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""

from datetime import datetime
from math import ceil


class KcLibrary:
  def __init__(self, name):
    self.name = name
    self.parts = []
  
  def add_part(self, unit):
    self.parts.append(unit)

  def write(self):
    of = open(self.name,'w') 
    
    of.writelines('EESchema-LIBRARY Version 2.3  Date: ' + datetime.now().strftime("%d/%m/%Y-%H:%M:%S") + '\n\n')
    
    for p in self.parts:
      p.write(of)

class KcComponent:
  def __init__(self, part):
    self.part = part
    self.units = []
        
  def add_unit(self, unit):
    self.units.append(unit)
    
  def write(self, of):
      of.writelines('DEF ' + self.part + " U 0 40 Y Y " + str(len(self.units)) + " F N\n")
      of.writelines('F0 "U" 0 100 70 H V C C\n')
      of.writelines('F1 "' + self.part + '" 0 -100 70 H V C C\n')
      of.writelines('DRAW\n')

      for u in self.units: 
        u.write(of,self.part)

      of.writelines('ENDDRAW\n')
      of.writelines('ENDDEF\n')

class KcUnit:
  def __init__(self, id_unit):
    self.id_unit    = id_unit
    self.top_pins   = []
    self.bot_pins   = []
    self.left_pins  = []
    self.right_pins = []

  def write(self, of, part):
    ll = max(self.left_pins, key=lambda KcPin: len(KcPin.name))
    lr = max(self.right_pins, key=lambda KcPin: len(KcPin.name))
    sl = (len( ll.name + "     " + part + "     " + lr.name))/2
       
    H = max(len(self.left_pins),len(self.right_pins),10)/2*100
    W = max(len(self.top_pins)*60+len(ll.name)*40+40,len(self.bot_pins)*60+len(lr.name)*40+40,sl/2*100)
    W = int(ceil(W/100.0)*100)

    of.writelines('S ' + str(-W) + ' ' + str(-H-100) + ' ' + str(W) + ' ' + str(H+100) + ' ' + str(self.id_unit) +' 1 0 f\n')
  
    self.write_pin(of,self.left_pins, -W-300, (len(self.right_pins)/2*100),0,-100,'R')
    self.write_pin(of,self.right_pins, W+300,-(len(self.right_pins)/2*100),0, 100,'L')

    self.write_pin(of,self.top_pins,-(len(self.top_pins)/2*100), H+400,100,0,'D')
    self.write_pin(of,self.bot_pins,-(len(self.bot_pins)/2*100),-H-400,100,0,'U')
            
  def write_pin(self, of, pins, x, y, dx, dy, d):
    for signal in pins:
      of.writelines('X ' + signal.name + ' ' + signal.pin + ' ' + str(x) + ' ' + str(y) +' 300 ' + d + ' 60 60 ' + str(self.id_unit) + ' 1 ' + signal.electrical_type + ' ' + signal.pin_type + '\n')
      x = x + dx
      y = y + dy

class KcPin:
  def __init__(self, name, pin , electrical_type='P', pin_type=''):
    self.pin = pin
    self.name = name
    self.pin_type = pin_type
    self.electrical_type = electrical_type