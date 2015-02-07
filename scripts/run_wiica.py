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
  source,
	analysis_types):

  print 'Running WIICA'
  inst_results = {}
  mem_results = {}

  compile.main(directory, source)
  process_trace.main(directory, source)
  inst_results = analysis.main(directory, source, analysis_types)
  if 'memory' in analysis_types:
    mem_results = mem_analysis.main(directory, source)
  all_results = dict(inst_results.items() + mem_results.items())
  if 'register' in analysis_types:
    reg_analysis.main(directory, source)

  return all_results

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--directory', help='absolute directory of the benchmark')
  parser.add_argument('--source', help='the name of source file, e.g. fft, md, etc.')
  parser.add_argument('--analysis_types',
      choices=["opcode", "staticinst", "memory", "branch", "basicblock", "register"],
      help='Type of analysis. Separate multiple values with spaces. The '
      'supported analyses are shown.', nargs="*")
  if len(sys.argv) < 2:
    print "run_wiica.py --directory <dir> --source <source file> --analysis_types <analysis to do> "
    print "Run run_wiica.py -h to see more datails"
    sys.exit(1)
  args = parser.parse_args()
  dir = args.directory
  source = args.source
  ana = args.analysis_types

  run(dir, source, ana)

if __name__ == '__main__':
  main()

