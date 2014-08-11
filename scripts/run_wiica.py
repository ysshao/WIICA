#!/usr/bin/env python 
import os
import sys
import os.path
import subprocess
import argparse


import compile
import analysis
import mem_analysis
import reg_analysis
import process_trace
def run(directory,
	kernel,
        source,
	arguments,
	analysis_types):

  print 'Running WIICA'
  inst_results = {}
  mem_results = {}

  if arguments[0] == 'non':
    arguments = []

  compile.main(directory, kernel, source, arguments)
  process_trace.main(directory, kernel)
  inst_results = analysis.main(directory, kernel, analysis_types)
  if 'memory' in analysis_types:
    mem_results = mem_analysis.main(directory, kernel)
  all_results = dict(inst_results.items() + mem_results.items())
  if 'register' in analysis_types:
    reg_analysis.main(directory, kernel)

  return all_results

def main():
  print "run_wiica"
  parser = argparse.ArgumentParser()
  parser.add_argument('--directory', help='absolute directory of the benchmark')
  parser.add_argument('--kernel', help='benchmark to analyze. If the benchmark is one of the algorithms of the kernel, use kernel.algorithm instead')
  parser.add_argument('--source', help='the name of source file, e.g. fft, md, etc.')
  parser.add_argument('--arguments', help='the list of arguments to run the program', nargs="*")
  parser.add_argument('--analysis_types', 
      choices=["opcode", "staticinst", "memory", "branch", "basicblock", "register"],
      help='Type of analysis. Separate multiple values with spaces. The '
      'supported analyses are shown.', nargs="*")
  if len(sys.argv) < 2:
    print "run_wiica.py --directory <dir> --kernel <kernel> --source <source file> --arguments <args> --analysis_types <analysis to do> "
    print "Run run_wiica.py -h to see more datails"
    sys.exit(1)
  args = parser.parse_args()
  dir = args.directory
  kernel = args.kernel
  source = args.source
  arguments = args.arguments
  ana = args.analysis_types
  
  run(dir, kernel, source, arguments, ana)

if __name__ == '__main__':
  main()
  
