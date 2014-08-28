#!/usr/bin/env python 
import os
import sys
import operator
import gzip
import math


def main (directory, kernel, source, arguments):
 
  print ''
  print '==========================='
  print '     LLVM Compilation      '
  print '==========================='
  print 'Running compile.main()'
  print 'Compiling: ' + kernel
  print ''
  
  os.chdir(directory)
  obj = {}
  opt_obj = {}
  for s in source:
    name = s.split('/')[-1].split('.')[0]
    obj[s] = name + '.llvm'
    opt_obj[s] = name + '-opt.llvm'
    print obj[s]
    print opt_obj[s]
    
  exe = kernel.split('.')[-1] + '-instrumented'
  
  args = ''
  for arg in arguments:  
    args += arg + ' '
  
  for s in source:
    os.system('clang -g -O3 -S -fno-slp-vectorize -fno-vectorize -fno-unroll-loops -fno-inline -emit-llvm -o ' + obj[s] + ' '  + s)
    os.system('opt -S -load=' + os.getenv('TRACER_HOME') + '/full-trace/full_trace.so -fulltrace ' + obj[s] + ' -o ' + opt_obj[s])

  link = 'llvm-link -o full.llvm '
  for s in source:
    link += opt_obj[s] + ' '
  link += os.getenv('TRACER_HOME') +'/profile-func/trace_logger.llvm'

  print link
  os.system(link)

  os.system('llc -O3 -filetype=obj -o full.o full.llvm')
  os.system('gcc -o ' + exe + ' full.o -lm')

  print './'+ exe + ' ' + args
  os.system('./'+ exe + ' ' + args)
  os.system('mv dynamic_trace '+ kernel+'.llvm'+'_fulltrace')

if __name__ == '__main__':
  directory = sys.argv[1]
  kernel = sys.argv[2]
  source = sys.argv[3]
  arguments = sys.argv[4]
  test_file = sys.argv[4]
  print directory, kernel, source, arguments, test_file
  main(directory, kernel, source, arguments, test_file)
