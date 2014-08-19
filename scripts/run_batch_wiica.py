#!/usr/bin/env python 
import argparse
import ast
import matplotlib
matplotlib.use("Agg")  # No xterm
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

import run_wiica

# Set of all kernels
all_kernels = {
  'aes' : 'gf_alog,gf_log,gf_mulinv,rj_sbox,rj_xtime,aes_subBytes,aes_addRoundKey,aes_addRoundKey_cpy,aes_shiftRows,aes_mixColumns,aes_expandEncKey,aes256_encrypt_ecb',
#  'backprop' :
#    'bpnn_layerforward,bpnn_layerforward_hidden,bpnn_output_error,bpnn_hidden_error,bpnn_adjust_weights,bpnn_adjust_weights_hidden,bpnn_train_kernel',
  'bfs-bulk' : 'bfs',
  'bfs-queue' : 'bfs',
  'des' : 'deskey,usekey,cookey,cpkey,scrunch,unscrun,desfunc,des_enc',
  'kmp' : 'CPF,kmp',
  'fft-simple' : 'fft',
#  'fft-transpose' : 'twiddles8,loadx,loady,fft1D_512',
  'gemm-blocked': 'bbgemm',
  'gemm-simple' : 'gemm',
  'md-knn':'md_kernel',
#  'md-grid': 'md',
  'nw' : 'needwun',
#  'sha' : 'SHA1_Transform,SHA1_Update,SHA1_Final',
  'sort-merge' : 'merge,mergesort',
  'sort-radix' : 'local_scan,sum_scan,last_step_scan,init,hist,update,ss_sort',
  'spmv-crs' : 'spmv',
  'spmv-ellpack' : 'ellpack',
  'stencil-simple' : 'stencil',
  'stencil-stencil3d' : 'stencil3d',
  'viterbi' : 'viterbi',
}

# Name of the C file that contains the main code.
main_kernel_c = {
  'aes' : 'aes',
#  'backprop' : 'back',
  'bfs-bulk' : 'bulk',
  'bfs-queue' : 'queue',
  'des' : 'des',
  'kmp' : 'kmp',
  'fft-simple' : 'fft',
#  'fft-transpose' : 'fft',
  'gemm-blocked': 'bbgemm',
  'gemm-simple' : 'gemm',
  'md-knn': 'md',
#  'md-grid': 'md',
  'nw' : 'needwun',
#  'sha' : 'sha',
  'sort-merge' : 'merge',
  'sort-radix' : 'radix',
  'spmv-crs' : 'crs',
  'spmv-ellpack' : 'ellpack',
  'stencil-simple' : 'stencil',
  'stencil-stencil3d' : 'stencil3d',
  'viterbi' : 'viterbi',
}

# Types of analysis results that can be plotted.
allowed_analyses = ["memory", "branch"]

def plot_results(full_results):
  ''' Plots bar charts for instruction and memory analysis results.
 
  Args:
    full_results: A dict keyed by kernel name. Each value is a dict whose key
      is the name of the analysis result (spatial_locality_score, etc.).
  '''
  figure_num = 1
  bar_width = 0.5
  colors = "rbgyk"
  color_idx = 0
  for result_type, result_names in full_results.iteritems():
    fig = plt.figure(figure_num)
    ax = fig.add_subplot(111)
    bar_centers = np.arange(len(result_names))
    keys = []
    values = []
    for key, val in result_names.iteritems():
      keys.append(key)
      values.append(val)
    ax.bar(bar_centers, values, bar_width,
           color=colors[color_idx], label=result_type)
    color_idx = color_idx + 1
    ax.set_ylabel(result_type)
    ax.set_xticks(bar_centers + bar_width/2)
    ax.set_xticklabels(keys)
    ax.legend(loc=0)
    plt.savefig("/home/vagrant/%s.pdf" % result_type)
    figure_num = figure_num + 1
  
def main():

  parser = argparse.ArgumentParser()
  parser.add_argument("kernels", 
      help="Comma-separated list of kernels to analyze. Type anything here to "
      "trigger an invalid kernel error and see the list of valid kernels.")
  parser.add_argument("machsuite_dir",
      help="Directory where MachSuite is located.")
  parser.add_argument('enable',
      help='Type of analysis. Separate multiple values with commas. The '
      'supported analyses are opcode, staticinst, memory, branch, basicblock.')

  
  args = parser.parse_args();
  args.kernels = args.kernels.split(",")
  # Check if all kernels are valid, and exit if not.
  for kernel in args.kernels:
    if kernel=='all':
      args.kernels = main_kernel_c.iterkeys()
      break
    if not kernel in all_kernels:
      print "%s is not a valid kernel." % kernel
      print ""
      print "Valid kernels are:"
      print [kernel for kernel in all_kernels.iterkeys()]
      sys.exit(1)
  
  # Results dict, keyed by kernel name.
  full_results = {} 

  # Change the BENCH_HOME environment variable that is used throughput these
  # scripts. Not elegant, but will work for now.
  old_bench_home = os.getenv("BENCH_HOME") 
  os.environ["BENCH_HOME"] = args.machsuite_dir
  BENCH_HOME = args.machsuite_dir+'/'
  harness_file = "%s/common/harness.c" % args.machsuite_dir
  analysis_types = args.enable.split(",")
 
  for kernel in args.kernels:
    directory = os.environ["BENCH_HOME"] + '/'
    # Some kernels have multiple algorithms implemented, and they are named like
    # [kernel]-[algorithm]. We need to separate these two parameters in this
    # case, as the file directory structure is [kernel]/[algorithm].
    if not (kernel.find('-') == -1):
      directory += kernel.split('-')[0] +'/'+ kernel.split('-')[1]
      kernel_pri = kernel.split('-')[0]
      algorithm = kernel.split('-')[1] 
      source = main_kernel_c[kernel]
      
      # compile_script_kernel is kind of a hack to get this batch script to work
      # with compile.py without changing the primary function signature (since
      # it's used everywhere).
    else:
      directory += kernel
      kernel_pri = kernel
      algorithm = ''
      source = main_kernel_c[kernel]

    for ana in analysis_types:
      if ana == 'all':
        analysis_types = ["opcode", "staticinst", "memory", "branch", "basicblock", "register"]
	break
   
    kernel_pri += '.'+algorithm
    arg = ['input.data', 'check.data']
    test = BENCH_HOME+'common/harness.c'
    print ""
    print "###########################"
    print "     %s" % kernel
    print "###########################"
    analysis_results = run_wiica.run(
        directory,
	kernel_pri,
	source,
	arg,
	test,
	analysis_types)
    for result_type in analysis_results.iterkeys():
      if not result_type in full_results:
        full_results[result_type] = {}
      full_results[result_type][kernel] = analysis_results[result_type]
  #plt.close('all')
  #plot_results(full_results)
  #os.environ["BENCH_HOME"] = old_bench_home
  #print "Plots have bene saved to /home/vagrant."

if __name__ == "__main__":
  main()
