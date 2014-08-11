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
  obj = source + '.llvm'
  opt_obj = source + '-opt.llvm'
  
  exe = source + '-instrumented'
  source += '.c'

  args = ''
  for arg in arguments:  
    args += arg + ' '
  
  os.system('clang -g -O1 -S -fno-slp-vectorize -fno-vectorize -fno-unroll-loops -fno-inline -emit-llvm -o ' + obj + ' '  + source)
  os.system('opt -S -load=' + os.getenv('TRACER_HOME') + '/full-trace/full_trace.so -fulltrace ' + obj + ' -o ' + opt_obj)
  os.system('llvm-link -o full.llvm ' + opt_obj + ' '+ os.getenv('TRACER_HOME') +'/profile-func/trace_logger.llvm')
  os.system('llc -O1 -filetype=obj -o full.o full.llvm')
  os.system('gcc -o ' + exe + ' full.o -lm')

  print './'+ exe + ' ' + args
  os.system('./'+ exe + ' ' + args)
  os.system('mv dynamic_trace '+ kernel+'.llvm'+'_fulltrace')

if __name__ == '__main__':
  directory = sys.argv[1]
  kernel = sys.argv[2]
  source = sys.argv[3]
  print directory, kernel, source
  main(directory, kernel, ource)
