#!/usr/bin/env python 
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import gzip
import math
import sys

color_code = ['#FFA540', '#3BA3D0']
marker_code = ['o', 's']

def main(directory, kernel, algorithm):
  
  print 'Plotting stride pattern...'

  BMKROOT = directory
  os.chdir(BMKROOT)
  
  BINARY=kernel  + '.'+ algorithm + '.cil'
  
  stride_file = open(BINARY + '_stride_profile', 'r')
  s_distribution = []
  for line in stride_file:
    if len(s_distribution) == 0:
      s_distribution.append(float(line.split(',')[1]))
    else:
      prev = s_distribution[-1]
      s_distribution.append(float(line.split(',')[1]) + prev)
  ind = np.arange(len(s_distribution))
  
  fig = plt.figure()
  fig.subplots_adjust(wspace=.5, bottom=.2, left=.12, top=.98, right=.99, hspace=.2)
  currentplot = fig.add_subplot(1, 1, 1)
  currentplot.plot(ind, s_distribution, color=color_code[0], \
    marker=marker_code[0], label=kernel, linewidth=2, markersize=8)
  currentplot.set_ylim([0,1])
  currentplot.set_xlim([0,16])
  currentplot.set_ylabel('Percentage of Mem Ops')
  currentplot.set_xlabel('Stride (in Bytes)')
  tick = np.arange(16)
  labels = []
  for item in tick:
    labels.append(str(int(math.pow(2,item))))
  currentplot.set_xticks(tick)
  currentplot.set_xticklabels(labels, rotation=90)
  leg = currentplot.legend(loc='lower right', fancybox=True, ncol=1)
  leg.get_frame().set_alpha(0.5)
  plt.grid(True)
  file_name = kernel + '_spatial_locality.pdf'
  plt.savefig(file_name)


if __name__ == '__main__':
  kernel = sys.argv[1]
  main(kernel)
