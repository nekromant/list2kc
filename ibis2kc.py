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
from operator import  attrgetter
from kccomp import *

def pin_cmp(X,Y):
  r = re.compile('([A-Z|a-z]+)?([0-9]+)?([\x20-\x7E]+)?')
  
  mo = r.match(X.name)
  mi = r.match(Y.name)
  
  if mo.group(2) and mi.group(2):
    return cmp((mo.group(1),int(mo.group(2)),mo.group(3)),(mi.group(1),int(mi.group(2)),mi.group(3)))
  else:
    return cmp((mo.group(1),mo.group(2),mo.group(3)),(mi.group(1),mi.group(2),mi.group(3)))
  

def usage(appname):
    print "usage : " + appname + " --ibis-file=inputfile.pkg --output-file=output.lib --vcc-prefix=prefix --gnd-prefix=prefix"

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:v:g:', ['ibis-file=', 'output-file=','vcc-prefix=', 'gnd-prefix='])
  except getopt.GetoptError:
    usage(sys.argv[0])
    sys.exit(2)
    
  inputfile=None
  outputfile=None
  vcc_prefix="VCC"
  gnd_prefix="GND"
  
  for o, a in opts:
    if o in ("-i", "--ibis-file"):
      inputfile = a
    elif o in ("-o", "--output-file"):
      outputfile = a
    elif o in ("-v", "--vcc-prefix"):
      vcc_prefix = a
    elif o in ("-g", "--gnd-prefix"):
      gnd_prefix = a
    
  if inputfile==None:
    usage(sys.argv[0])
    sys.exit(2)
    
  if outputfile==None:
    outputfile = inputfile.split('.')[0] + '.lib'

  f = open(inputfile,'r') 

  raw_data = f.read()

  regexp = re.compile('\[Component\]([\x20-\x7E]*?)[\r\n|\n][\x20-\x7E\n\r]*?\[Pin\].+[\r\n|\n]?([\x20-\x7E\n\r^\|]*?)[\r\n|\n]?\[')
  
  matches = [m.groups() for m in regexp.finditer(raw_data)]
  
  xl = KcLibrary (outputfile)

  for m in matches:
    part = m[0].strip()
    print '  Importing: ' + part
    
    comp = KcComponent(part);
    xl.add_part(comp)

    pins = []

    for line in m[1].split('\n'): 
        tags = re.split('\s+',line.strip())
        if len(tags[0]) and (len(tags)>1) and  (tags[0][0]!="|"):
          pins.append(KcPin(tags[1],tags[0]))
    
    un = KcUnit(1)
    comp.add_unit(un)
    
    pins=sorted(pins,  cmp=pin_cmp)

    signals = []
    for p in pins:
      if re.search(vcc_prefix,p.name):
        un.top_pins.append(p)
      elif re.search(gnd_prefix,p.name):
        un.bot_pins.append(p)
      else:
        signals.append(p)
    
    for p in signals:
     if (p.name.find('#')>0):
       p.pin_type = 'I'
       p.electrical_type = 'I'
       
    sp=len(signals)/2
    for p in signals[0:sp]:
      un.left_pins.append(p)
        
    for p in signals[sp:]:
      un.right_pins.append(p)
    
  xl.write()

#end-main

if __name__ == "__main__":
    main()