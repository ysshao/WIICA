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
  print '      Memory Analysis      '
  print '==========================='
  print 'Running mem_analysis.main()'
  print 'Analyzing: ' + kernel
  print ''

  BMKROOT = directory
  os.chdir(BMKROOT)
  
  BINARY=kernel + '.llvm'
  
  t_histogram = {}
  s_histogram = {}
  for i in range(21):
    value = int(math.pow(2,i))
    t_histogram[value] = 0
    s_histogram[value] = 0
  #Stride Analysis for Spatial Locality 
  spatial_locality_score = 0  # Set up output variable.
  addr_id = 0
  past_32 = []
  stride_access = 0
  #Reuse Distance for Temporal Locality
  temporal_locality_score = 0  # Set up output variable.
  last_access = {}
  mem_accesses = 0
  addr_id = 0
  mem_trace = gzip.open(BINARY + '_memtrace.gz', 'r')
  for line in mem_trace:
    addr = int(line.rstrip().split(',')[1])
    addr_id += 1
    mem_accesses += 1
    #Reuse Distance
    if addr in last_access:
      stride = addr_id - last_access[addr]
      if stride > 1048576:
        stride = 1048576
      t_histogram[int(math.pow(2,int(math.ceil(math.log(stride, 2)))))] += 1
      
    last_access[addr] = addr_id

    #Histogram of stride access
    if len(past_32) >= 32:
      stride = 1048576
      for item in past_32:
        if math.fabs(item - addr) < stride:
          stride = math.fabs(item-addr)
          print stride
      if stride != 0:
        s_histogram[int(math.pow(2,int(math.ceil(math.log(stride, 2)))))] += 1
        stride_access += 1
      del past_32[0]
    past_32.append(addr)

  mem_trace.close()
  #Distribution of Stride Accesses
  s_distribution = []
  for i in range(len(s_histogram)):
    if stride_access == 0:
        spatial_locality_score = 0
        break
    percent = s_histogram[int(math.pow(2,i))] * 1.0 / stride_access
    s_distribution.append(percent)
    spatial_locality_score += percent  * 1.0 / int(math.pow(2,i))
  print 'Spatial locality score :\t%0.4f' % (spatial_locality_score)

  #PLOT begins
  spalo = open(BINARY+'_spatial_locality','w')
  spalo.write('%0.4f\n' % (spatial_locality_score))
  spalo.close()
  #PLOT ends

  #Cumulative Distribution of Reuse Distance
  t_distribution = []
  for i in range(len(t_histogram)):
    percent = t_histogram[int(math.pow(2,i))] * 1.0 / mem_accesses
    t_distribution.append(percent)
    temporal_locality_score += percent  * 1.0  * (len(t_histogram) - i ) / len(t_histogram)
  print 'Temporal locality score:\t%0.4f' % (temporal_locality_score)
  
  #PLOT begins
  temlo = open(BINARY+'_temporal_locality','w')
  temlo.write('%0.4f\n' % (temporal_locality_score))
  temlo.close()
  #PLOT ends

  stride_output = open(BINARY + '_stride_profile', 'w')
  for i, percent in zip(range(len(s_distribution)), s_distribution):
    stride = int(math.pow(2, i))
    stride_output.write("%d,%f\n" %( stride, percent))
  stride_output.close()
  
  reuse_output = open(BINARY + '_reuse_profile', 'w')
  for i, percent in zip(range(len(t_distribution)), t_distribution):
    reuse = int(math.pow(2, i))
    reuse_output.write("%d,%f\n" %( reuse, percent))
  reuse_output.close()


  print '---------------------------'

  results = {"spatial_locality_score": spatial_locality_score,
             "temporal_locality_score": temporal_locality_score}
  return results

if __name__ == '__main__':
  directory = sys.argv[1]
  kernel = sys.argv[2]
  main(directory, kernel)
