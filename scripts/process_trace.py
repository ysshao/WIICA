#!/usr/bin/env python
import os
import sys
import operator
import gzip
import math
import numpy as np
from collections import defaultdict


import LLVM_IR

def main (directory, source):

  print ''
  print '========================'
  print ' Processing LLVM Traces '
  print '========================'
  print 'Running process_trace.main()'
  print ''

  BMKROOT = directory
  os.chdir(BMKROOT)
  BINARY=source + '.llvm'
  dump_file = open(BINARY + '_fulltrace', 'r')
  process_file = open(BINARY + '_fulltrace_afterprocess', 'w')
  call_flag = 0
  store_args_flag = 0
  bitcast_flag = 0
  for line in dump_file:
    if len(line.split(',')) < 2:
      continue

    if line.split(',')[0] == '0':

      if call_flag == 1 and store_args_flag == 0:
         for l in call_lines:
           process_file.write(l+'\n')
      instnumber = line.split(',')[1]
      method = line.split(',')[2]
      bblockid = line.split(',')[3]
      position = line.split(',')[4]
      opcode = int(line.split(',')[-2])
      opcode_name = LLVM_IR.IR_name[line.rstrip().split(',')[-2]]
      last = line.split(',')[-1]
      arguments = []
      call_lines = []
      call_flag = 0
      store_args_flag = 0
      c = 0

      if opcode_name == 'Call':
        call_flag = 1

    if opcode_name == 'BitCast' and line[0] == '1':
        size = int(line.split(',')[1].strip('\n'))
        bitcast_flag = 1

    if opcode_name == 'BitCast' and line[0] == 'r':
        reg = line.split(',')[4].strip('\n')

    if opcode_name <> 'Call':
      process_file.write(line)

    if store_args_flag == 1:
      c = c+1
      arguments.append(line)

    if c==5: # start to process the traces

      itr_num = (int(arguments[-3].split(',')[2].strip('\n'))*8)/int(arguments[-2].split(',')[1])
      address = int(arguments[-1].split(',')[2].strip('\n'))

      if bitcast_flag == 0:
        print "Size = " + str(size) + '\n'
        size = int(arguments[-1].split(',')[1])

      for i in range(1,itr_num):
        process_file.write("0,"+instnumber+","+method+","+bblockid+","+position+","+"28,"
+last+ "\n")
        process_file.write("2," + str(size) + "," + str(address) + ',1,' + reg+"\n")
        process_file.write("1," + str(size) +","+arguments[-2].split(',')[2].strip('\n')+",0\n")
        address = address + size/8
      bitcast_flag = 0

    if call_flag == 1:
      call_lines.append(line.strip('\n'))
      if  len(line.split(',')) > 4:
        if "llvm.memset" in line.split(',')[4]:
          store_args_flag = 1

    if opcode_name <> "Call" and opcode_name <> "BitCast":
        bitcast_flag = 0

  os.system("mv "+BINARY + '_fulltrace_afterprocess '+BINARY+'_fulltrace')
  dump_file.close()
  process_file.close()

if __name__ == '__main__':
  directory = sys.argv[1]
  source = sys.argv[2]
  main(directory, source)
