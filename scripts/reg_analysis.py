#!/usr/bin/env python 
import os
import sys
import operator
import gzip
import math
import numpy as np
from collections import defaultdict

import stride_plot
import reuse_plot

def main(directory, kernel):
  
  print ''
  print '==========================='
  print '     Register Analysis     '
  print '==========================='
  print 'Running reg_analysis.main()'
  print 'Analyzing: ' + kernel
  print ''
  

  BMKROOT = directory
  os.chdir(BMKROOT)
  BINARY=kernel + '.llvm'
  trace = open(BINARY + '_fulltrace', 'r')
  inst = -1

#for degree
  read_count = 0
  write_count = 0
#for dependency distance
  write_register = {}
  read_register = {}
  hist = []  		#dependence distance (registers are used multiple times)
  last_hist = []	#lifetime of registers (only count the last access of the register)
  n_register = []
  for i in range(10000):
    hist.append(0)
    last_hist.append(0)

  for line in trace:
    if len(line.split(",")) < 2:
	continue
    if line[0] == '0':
      func = line.split(',')[2]
      bbid = line.split(',')[3]
 
      inst += 1
      if inst == 0:
        n_register.append(0)
      else:
        n_register.append(n_register[inst-1])

    #read
    if line[0] <> '0' and line[0] <> 'r':
      if line.split(',')[3] == "1": #is register
	if line.split(',')[4].strip('\n').isdigit():
	  reg_name = func + bbid + line.split(',')[4].strip('\n')
	else:
	  reg_name = line.split(',')[4].strip('\n')
	if not reg_name in write_register:
          index = inst 
        else:
          read_count += 1
	  read_register[reg_name] = inst
	  index = inst - write_register[reg_name]
	if index < 10000:
	  hist[index] += 1

    #write    
    if line[0] == 'r' and line.split(',')[3] == "1":
      write_count += 1
      if line.split(',')[4].strip('\n').isdigit():
        reg = func + bbid + line.split(',')[4].strip('\n')
      else:
        reg = line.split(',')[4].strip('\n')
      if reg in write_register:
	if reg in read_register:
	  index = read_register[reg] - write_register[reg]
	if index < 10000 and index > 0:
          last_hist[index] += 1
        if reg in read_register:
	  sta = read_register[reg]
          for i in range(inst - sta):
            n_register[i+sta+1] -= 1
	else:
	  sta = write_register[reg]
	  for i in range(inst - sta + 1):
	    n_register[i+sta] -= 1

      write_register[reg] = inst
      n_register[inst] += 1 

  for r in write_register:
    if r in read_register:
      index = read_register[r] - write_register[r]
      if index < 10000 and index > 0:
        last_hist[index] += 1

  for r in read_register:
    index = inst - read_register[r]
    sta = read_register[r]
    for i in range(index):
	if n_register[i+sta+1] > 0:
	  n_register[i+sta+1] -= 1
    if write_register[r] > read_register[r]:
	index = inst - write_register[r]
        sta = write_register[r]
        for i in range(index+1):
	  if n_register[i+sta] > 0:
            n_register[i+sta] -= 1

  trace.close()

  print read_count
  print write_count
  #PLOT begins
  degree = open(BINARY+'_reg_degree','w')
  degree.write('%0.4f\n' % (float(read_count)/float(write_count)))
  degree.close()
  #PLOT ends

  #print hist   
  #PLOT begins
  distr = open(BINARY+'_reg_distribution','w')
  for i in hist:
    distr.write('%d\n' % (i))
  distr.close()
  #PLOT ends

  #print last_hist   
  #PLOT begins
  distr = open(BINARY+'_reg_lifetime','w')
  for i in last_hist:
    distr.write('%d\n' % (i))
  distr.close()
  #PLOT ends

#  print n_register   
  #PLOT begins
  distr = open(BINARY+'_reg_number','w')
  for i in n_register:
    distr.write('%d\n' % (i))
  distr.close()
  #PLOT ends

  print max(n_register)   
  #PLOT begins
  distr = open(BINARY+'_reg_maxn','w')
  distr.write('%d\n' % (max(n_register)))
  distr.close()
  #PLOT ends
  print '---------------------------'


if __name__ == '__main__':
  directory = sys.argv[1]
  kernel = sys.argv[2]

  main(directory, kernel)
