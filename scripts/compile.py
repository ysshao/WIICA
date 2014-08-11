#!/usr/bin/env python 
import os
import sys
import operator
import gzip
import math

kernels = {
'bb_gemm' : 'bb_gemm',
'fft' : 'fft1D_512,step1,step2,step3,step4,step5,step6,step7,step8,step9,step10,step11',
'md' : 'md,md_kernel',
'pp_scan' : 'pp_scan,local_scan,sum_scan,last_step_scan',
'reduction' : 'reduction',
'ss_sort' : 'ss_sort,init,hist,local_scan,sum_scan,last_step_scan,update',
'stencil' : 'stencil',
'triad' : 'triad',
}

def main (directory, kernel, source, arguments):
 

  print "-- LLVM Compilation --" 
  
  os.chdir(directory)
  obj = source + '.llvm'
  opt_obj = source + '-opt.llvm'
  
  exe = source + '-instrumented'
  source += '.c'

  args = ''
  for arg in arguments:  
    args += arg + ' '
  
  os.environ['WORKLOAD']=kernels[source]
  
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
