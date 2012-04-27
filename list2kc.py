#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2012 Andrew 'Necromant' Andrianov, contact@ncrmnt.org
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
import os
import getopt
from kccomp import *

def usage(appname):
    print("A small utility to generate eeschema files from a text-like description")
    print "usage : " + appname + " --pkg-file=inputfile.pkg --output-file=output.lib"
    print("(c) Andrew 'Necromant' Andrianov, based on xil2kc by Andres Calderon")

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
  
  part = os.path.basename(outputfile).split('.')[0]
  if outputfile==None:
    outputfile = part+'.lib'
    
  xl = KcLibrary (outputfile)
  comp = KcComponent(part);
  print("part is " + part);
  

  f = open(inputfile,'r') 
  pl = re.compile('\[\d+:\d+\]')
  rule = re.compile('@[A-z]+')
  pins = []
  rules = []
  for line in f.read().split('\n'):
    line = line.strip()
    if pl.search(line):
      tags = re.findall('\d+',line)
      print("Reading section: "+line)
      start = int(tags[0])
      end = int(tags[1])
      if start>end:
        ddir=-1
      else:
        ddir=1
      pos=int(start)
    elif (len(line)!=0) and (line[0]=='~'):
       subparts = re.findall('\d+',line)[0]
       print("Will create " + subparts + " subpart(s)")
       un = []
       for i in range(1,int(subparts)+1):
          print(i);
          unit = KcUnit(i)
          un.append(unit)
          comp.add_unit(unit)
    elif (len(line)!=0) and (line[0]==':'):
       tags = line.split(":")
       if tags[2] == "top":
         trg = un[int(tags[3])].top_pins
       elif tags[2] == "bot":
         trg = un[int(tags[3])].bot_pins
       elif tags[2] == "left":
         trg = un[int(tags[3])].left_pins
       elif tags[2] == "right":
         trg = un[int(tags[3])].right_pins
       else:
          print("Invalid pin orient: " + tags[2])
          exit()
       print("Loaded rule for: " + tags[1]);
       rules.append((tags[1],trg))
    elif len(line)!=0:  
        print("---| pin "+str(pos)+" is "+line)
        if ((ddir==1) and (pos>end)):
         print("OOPS:Section ["+str(start)+":"+str(end)+"] has extra lines, check that")
         exit()
	      
        if ((ddir==1) and (pos>end)):
         print("OOPS:Section ["+str(start)+":"+str(end)+"] has extra lines, check that")
         exit()
        #TODO: Sorting rules from file
        pos=str(pos)
        for p in rules:
           #print(p)
           if re.search(p[0],line):
             p[1].append(KcPin(line,pos))
             break
        pos=int(pos)
        pos+=ddir
    
  xl.add_part(comp)     
  f.close()
  xl.write()
  print("All done, have a nice day");
  exit()    
    

#end-main

if __name__ == "__main__":
    main()
