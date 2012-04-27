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

import re
import sys
import getopt
from kccomp import *

def usage(appname):
    print "usage : " + appname + " --pkg-file=inputfile.pkg --output-file=output.lib"

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:o:', ['pkg-file=', 'output-file='])
  except getopt.GetoptError:
    usage(sys.argv[0])
    sys.exit(2)
     
  inputfile=None
  outputfile=None
  for o, a in opts:
    if o in ("-p", "--pkg-file"):
      inputfile = a
    elif o in ("-o", "--output-file"):
      outputfile = a
  
  if inputfile==None:
    usage(sys.argv[0])
    sys.exit(2)
  
  part = inputfile.split('.')[0]
  if outputfile==None:
    outputfile = part+'.lib'
   
  f = open(inputfile,'r') 

  pl = re.compile('^(pin|pkgpin)')
  pins = []

  for line in f.read().split('\n'): 
    if pl.search(line):
      tags = re.split('\s+',line)
#                  pin or  function  pin     vref    vcco 
#                  pkgpin  name      name    bank    bank 
      pins.append((tags[0],tags[5],  tags[2],tags[3],tags[4]))   
    
  f.close()
  
  m = {}
  for i in xrange(len(pins)):
    if not m.has_key(pins[i][4]):
      m[pins[i][4]] = []
    m[pins[i][4]].append(i)

  xl = KcLibrary (outputfile)

  comp = KcComponent(part);

  xl.add_part(comp)

  subpart=1
  for id_bank in m:
    un = KcUnit(subpart)
    comp.add_unit(un)
    subpart=subpart+1
  
    signals = []
    for signal in m[id_bank]:
      if re.search("VCC",pins[signal][1]):
        un.top_pins.append(KcPin(pins[signal][1],pins[signal][2]))
      else:
        if re.search("GND",pins[signal][1]):
          un.bot_pins.append(KcPin(pins[signal][1],pins[signal][2]))
        else:
          signals.append(KcPin(pins[signal][1],pins[signal][2]))
          
    #signals=sorted(signals,  key=lambda KcPin: KcPin.name)

    #for signal in signals:
      #if(signal.name=="NC"):
        #signal.pin_type = 'N'
      
    sp=len(signals)/2
    for signal in signals[0:sp]:
      un.left_pins.append(signal)
      
    for signal in signals[sp:]:
      un.right_pins.append(signal)
      
    xl.write()

#end-main

if __name__ == "__main__":
    main()
