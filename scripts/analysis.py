#!/usr/bin/env python 
import os
import sys
import operator
import gzip
import math
import numpy as np
from collections import defaultdict


import LLVM_IR

def main (directory, kernel, analyses):

  print ''
  print '========================'
  print '  Instruction analysis  '
  print '========================'
  print 'Running analysis.main()'
  print 'Analyzing: ' + str(analyses)
  print ''
  
  BMKROOT = directory
  os.chdir(BMKROOT)
  
  opcode_ana_flag = 0
  staticinst_ana_flag = 0
  mem_ana_flag = 0
  branch_ana_flag = 0
  bblock_ana_flag = 0
  
  # Set up all the output variables.
  branch_entropy = 0
  mem_entropy = 0

  for ana in analyses:
    if ana == 'opcode':
      opcode_ana_flag = 1
    elif ana == 'staticinst':
      staticinst_ana_flag = 1
    elif ana == 'memory':
      mem_ana_flag = 1
    elif ana == 'branch':
      branch_ana_flag = 1
    elif ana == 'basicblock':
      bblock_ana_flag = 1
    elif ana == 'register':
      reg = 1
    else:
      print "Unknown analysis type!"
      sys.exit(0)

  BINARY=kernel +'.llvm'
  
  total_inst_count = 0
  
  if opcode_ana_flag == 1:
    opcode_counts = np.zeros(60)

  if staticinst_ana_flag == 1:
    static_inst = {}
  
  if mem_ana_flag == 1:
    mem_trace_file = gzip.open(BINARY + '_memtrace.gz', 'w')
    addr_counter = {}
    addr_size = {}
    mem_accesses = 0

  if branch_ana_flag == 1:
    branch_stream = defaultdict(list)
  
  if bblock_ana_flag == 1:
    basic_blocks_size = {}
    basic_blocks_count = {}
    last_basic_block = 'a.1'
  
  dump_file = open(BINARY + '_fulltrace', 'r')
  br_branch_flag = 0
  swi_branch_flag = 0
  mem_flag = 0
  for line in dump_file:
    if len(line.split(',')) < 2:
	continue
    if line.split(',')[0] == '0' :
      method = line.split(',')[2]
      bblockid = line.split(',')[3]
      position = line.split(',')[4]
      opcode = int(line.split(',')[-1])
      opcode_name = LLVM_IR.IR_name[line.rstrip().split(',')[-1]]
      static_id = method+ '.' + position + '.' + opcode_name
      total_inst_count +=1
      
      #opcode
      if opcode_ana_flag == 1:
        opcode_counts[opcode]+=1
      #static inst
      if staticinst_ana_flag == 1:
        if static_id in static_inst:
          static_inst[static_id] +=1
        else:
          static_inst[static_id] =1
      #mem
      if mem_ana_flag == 1:
        mem_flag = 0
        if opcode_name in LLVM_IR.IR_MEMORY:
        #if opcode == 36 or opcode == 37:
          mem_flag = 1
          base_address = 0
          offset = 0
          mem_trace_file.write(static_id + ",")

      #basic block
      if bblock_ana_flag == 1:
        #FIXME
        if opcode_name in LLVM_IR.IR_BRANCH or  \
           opcode_name in LLVM_IR.IR_COMPUTE or  \
           opcode_name in LLVM_IR.IR_MEMORY :

          bblock_identifier = method + '.' + bblockid
          if bblock_identifier in  basic_blocks_size:
            basic_blocks_size[bblock_identifier] += 1
          else:
            basic_blocks_size[bblock_identifier] = 1
          if bblock_identifier != last_basic_block:
            last_basic_block = bblock_identifier
            if bblock_identifier in  basic_blocks_count:
              basic_blocks_count[bblock_identifier] += 1
            else:
              basic_blocks_count[bblock_identifier] = 1

      #branch
    if branch_ana_flag == 1:
      if line[0] == '0' and opcode_name == 'Br':
	pos_branch_flag = 1
      elif opcode_name == 'Br' and pos_branch_flag == 1:
        if line[0] == '2':
          br_branch_flag = 1
          target1 = line.split(',')[4].strip('\n')
	  br_static_id = static_id
          pos_branch_flag = 0
        elif line[0]  == '3':
          target2 = line.split(',')[4].strip('\n')
      elif line[0] == '0' and opcode_name == 'Select':
	sel_branch_flag = 1
      elif opcode_name == 'Select' and sel_branch_flag == 1:
	if line[0] == '1':
	  taken = int(line.split(',')[2].strip('\n'))
	  branch_stream[static_id].append(taken)
          sel_branch_flag = 0
      elif line[0]=='0' and opcode_name == 'Switch':
	pos_swi_branch_flag =1
	swi_label = {}
	swi_static_id = static_id
      elif opcode_name == 'Switch' and pos_swi_branch_flag == 1:	
	swi_branch_flag =1
	if int(line.split(',')[0])%2 == 0:
	  swi_label[line.split(',')[4].strip('\n')] = int(line.split(',')[0])/2
	  
      if line[0] == '0' and br_branch_flag == 1:
        curr_block = line.split(',')[3].strip('\n')
        assert(curr_block == target1 or curr_block == target2)
        if curr_block == target1:
          taken = 1
        elif curr_block == target2:
          taken = 0
        #print static_id, taken
        branch_stream[br_static_id].append(taken)
        br_branch_flag = 0
    
      if line[0] == '0' and swi_branch_flag == 1:     
	curr_block = line.split(',')[3]
	assert(curr_block in swi_label)
	taken = swi_label[curr_block]
	branch_stream[swi_static_id].append(taken)
        swi_branch_flag = 0
	pos_swi_branch_flag = 0 

    if mem_ana_flag == 1:
      if mem_flag == 1:
	if opcode_name == 'Load' and line[0] == '1':
          addr = int(line.strip().split(',')[2])
	  mem_trace_file.write(str(addr) + ",")
	  mem_accesses += 1   
	  if addr in addr_counter:
	    addr_counter[addr]+=1
	  else:
	    addr_counter[addr] = 1
	elif opcode_name == 'Store' and line[0] == '2':
	  addr = int(line.strip().split(',')[2])	
	  store_size = int(line.strip().split(',')[1])  
          mem_trace_file.write(str(addr) + ",")
          mem_accesses += 1   
          if addr in addr_counter:
            addr_counter[addr]+=1
          else:
            addr_counter[addr] = 1
          addr_size[addr] = store_size
          mem_trace_file.write(str(store_size) + "\n")
        elif opcode_name == 'Load' and line[0] == 'r':
	  size = int(line.rstrip().split(',')[1]) 
	  addr_size[addr] = size
          mem_trace_file.write(str(size) + "\n")
#	elif opcode_name == 'Store' and line[0] == '1':
#	  store_size = int(line.rstrip().split(',')[1])

  dump_file.close()
  if mem_ana_flag == 1:
    mem_trace_file.close()
  
  #opcode output:
  if opcode_ana_flag == 1:
    opcode_output = open(BINARY + '_opcode_profile', 'w')
    compute_op = 0
    mem_op = 0
    branch_op = 0
    print "Instruction counts"
    print "------------------"
    for op,  count in zip(range(len(opcode_counts)), opcode_counts):
      opcode_output.write("%d," % (count))
      if count != 0:
        name = LLVM_IR.IR_name[str(op)]
        print "%s:  %d" % (name, int(count))
        
        if name in LLVM_IR.IR_COMPUTE:
          compute_op += count
        elif name in LLVM_IR.IR_MEMORY:
          mem_op += count
        elif name in LLVM_IR.IR_COND_BRANCH or name in LLVM_IR.IR_UNCOND_BRANCH:
          branch_op += count
        #else:
        #  print name
    print 'Total compute instructions: %d' % compute_op
    print 'Total memory instructions: %d' % mem_op
    print 'Total branch instructions: %d' % branch_op
    # print '======Compute:Memory:Branch:%d:%d:%d' %(compute_op, mem_op, branch_op)


    opcode_output.write("\n")
    opcode_output.close()
  
  #static instruction
  if staticinst_ana_flag == 1:
    staticinst_output = open(BINARY + '_staticinst_profile', 'w')
    for w in sorted(static_inst.iteritems(), key=operator.itemgetter(1), reverse=True):
      key = w[0]
      value = str(w[1])
      staticinst_output.write(key + ',' + value + "\n")
    staticinst_output.close()

  #memory
  if mem_ana_flag == 1:
    total_bits = 0
    for addr, size in addr_size.iteritems():
      total_bits += size
    print '--------------------------'
    print '    Entropy analysis      '
    print '--------------------------'
    print 'Memory footprint: %d bytes' % (total_bits / 8)

    #PLOT begins
    footprint = open(BINARY+'_footprint','w')
    footprint.write('%d\n' % (total_bits / 8))
    footprint.close()
    #PLOT ends

    for w in sorted(addr_counter.iteritems(), key=operator.itemgetter(1), reverse=True):
      key = w[0]
      value = int(w[1])
      prob = value * 1.0 / mem_accesses
      mem_entropy = mem_entropy - prob * math.log(prob, 2)
    print 'Memory Entropy: %0.2f bits' % (mem_entropy)

    #PLOT begins
    mementro = open(BINARY+'_mem_entropy','w')
    mementro.write('%0.2f\n' % (mem_entropy))
    mementro.close()
    #PLOT ends

    #local entropy
    print ""
    print "Local memory address entropy"
    print "LSBs skipped\tEntropy (bits)"
    print "------------------------------"
    for i in range(10):
      nskip = i+1
      skip_value = math.pow(2, nskip)
      local_addr_counter = {}
      for key, value in addr_counter.iteritems():
        local_addr = int(int(key) / skip_value)
        if local_addr in local_addr_counter:
          local_addr_counter[local_addr] += int(value)
        else:
          local_addr_counter[local_addr] = int(value)

      local_entropy = 0
      for key, value in local_addr_counter.iteritems():
        prob = value * 1.0 / mem_accesses
        local_entropy = local_entropy - prob * math.log(prob, 2)
      local_addr_counter.clear()
      print "%d\t\t%0.2f" % (nskip, local_entropy)

  #branch
  if branch_ana_flag == 1:
    branch_pattern = {}
    pattern_count = 0
    for key, value in branch_stream.iteritems():
      print key, value
      for i in range(len(value) - 15):
        curr_pattern = ""
        for j in range(16):
          curr_pattern +=str(value[i+j])
        pattern_count += 1
        if branch_pattern.has_key(curr_pattern):
          branch_pattern[curr_pattern] += 1
        else:
          branch_pattern[curr_pattern] = 1

    #print branch_pattern
    for w in sorted(branch_pattern.iteritems(), key=operator.itemgetter(1), reverse=True):
      pattern = w[0]
      count = int(w[1])
      p_pattern = count * 1.0 / pattern_count
      branch_entropy = branch_entropy - p_pattern * math.log(p_pattern, 2)
    
    print "Branch entropy: %0.2f" % (branch_entropy)
     
    #PLOT begins
    mementro = open(BINARY+'_branch_entropy','w')
    mementro.write('%0.2f\n' % (branch_entropy))
    mementro.close()
    #PLOT ends

    branch_stream.clear()
    branch_pattern.clear()
  #basic block
  if bblock_ana_flag == 1:
    basicblock_output = open(BINARY + '_basicblock_profile', 'w')
    for key, count in basic_blocks_count.iteritems():
      size = basic_blocks_size[key]
      basicblock_output.write('%s,%d,%d,%d\n' %(key, size, count, size * 1.0 / count))
    basicblock_output.close()
  
  results = {"branch_entropy": branch_entropy,
             "mem_entropy": mem_entropy}
  return results

if __name__ == '__main__':
  kernel = sys.argv[1]
  analysis_to_do = sys.argv[2]
  main(kernel, analysis_to_do)
