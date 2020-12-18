# coding=utf-8
import subprocess
import time
import re
import os
import sys
import threading
import gc
import argparse

import compile_prime
import cdnf
import tool.Tool as Tool

WORKSPACE 				= './'
# set the limit time
LIMIT_TIME 				= 3600 * 1
LIMIT_MEMORY			= 1000000 * 16

EXTRACT_MOD				= 0
BACKTRACK_MOD			= 0
IS_OUTPUT				= 1

COVER_FILE_PATH 		= ''
CASE_INPUT_FILE_PATH 	= ''
CASE_OUTPUT_FILE_PATH 	= ''

var_index_map 			= {}
index_var_map 			= {}
var_index_dual_rail_map = {}
index_var_dual_rail_map = {}
dag 					= {}
cover_PI 				= []
all_PI 					= []
num_all_PI 				= 0

SATMCS_time 			= 0.0
SATMCS_memory 			= 0
DPLL_time				= 0.0
Extract_time			= 0.0
Backtrack_time			= 0.0
num_API					= 0
times_SAT				= 0
ave_size_API			= 0.0
first_shrink_size 		= 0
second_shrink_size 		= 0
other_shrink_size 		= 0
ave_first_shrink 		= 0.0
ave_second_shrink 		= 0.0
ave_other_shrink 		= 0.0
times_fix_point			= 0
ave_blocker_ignore		= 0.0

ASSMT_time 				= 0.0
ASSMT_memory 			= 0

pi 						= []
min 					= []
fact 					= []
dr 						= []

is_time_out_cover		= False
is_time_out_all			= False
is_memory_out_cover		= False
is_memory_out_all		= False

def clear():
	global var_index_map
	var_index_map = {}
	global index_var_map
	index_var_map = {}
	global var_index_dual_rail_map
	var_index_dual_rail_map = {}
	global index_var_dual_rail_map
	index_var_dual_rail_map = {}
	global dag
	dag = {}
	global cover_PI
	cover_PI = []
	global all_PI
	all_PI = []
	global num_all_PI
	num_all_PI = 0
	global SATMCS_time
	SATMCS_time = 0.0
	global SATMCS_memory
	SATMCS_memory = 0
	global DPLL_time
	DPLL_time = 0.0
	global Extract_time
	Extract_time = 0.0
	global Backtrack_time
	Backtrack_time = 0.0
	global num_API
	num_API = 0
	global times_SAT
	times_SAT = 0
	global ave_size_API
	ave_size_API = 0.0
	global first_shrink_size
	first_shrink_size = 0
	global second_shrink_size
	second_shrink_size = 0
	global other_shrink_size
	other_shrink_size = 0
	global ave_first_shrink
	ave_first_shrink = 0.0
	global ave_second_shrink
	ave_second_shrink = 0.0
	global ave_other_shrink
	ave_other_shrink = 0.0
	global times_fix_point
	times_fix_point = 0
	global ave_blocker_ignore
	ave_blocker_ignore = 0.0
	global ASSMT_time
	ASSMT_time = 0.0
	global ASSMT_memory
	ASSMT_memory = 0
	global pi
	pi = []
	global min
	min = []
	global fact
	fact = []
	global dr
	dr = []
	global is_time_out_cover
	is_time_out_cover = False
	global is_time_out_all
	is_time_out_all	= False
	global is_memory_out_cover
	is_memory_out_cover = False
	global is_memory_out_all
	is_memory_out_all = False

def clean(file_name):

	cnf_path = CASE_INPUT_FILE_PATH + file_name + '.cnf'
	ana_path = CASE_INPUT_FILE_PATH + file_name + '.ana'
	cpi_path = CASE_INPUT_FILE_PATH + file_name + '.cpi'
	out_path = CASE_INPUT_FILE_PATH + file_name + '.out'
	
	if os.path.isfile(cnf_path):
		os.remove(cnf_path)
	if os.path.isfile(ana_path):
		os.remove(ana_path)
	if os.path.isfile(cpi_path):
		os.remove(cpi_path)
	if os.path.isfile(out_path):
		os.remove(out_path)

def get_info(file_name):
	num_ori_var = 0
	open_file_path = CASE_INPUT_FILE_PATH + file_name + '-p.cnf'
	f = open(open_file_path, 'r')

	for line in f:
		if 'c n orig vars' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_ori_var = int(words[0])
			break

	global var_index_map
	global index_var_map
	for i in range(1, num_ori_var + 1):
		var = 'e' + str(i)
		index = i
		var_index_map[var] = index
		index_var_map[index] = var

def pncnf2outMCS(file_name, is_coherent, root, is_negative):

	if is_negative:
		positive_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-n.cnf'
		negative_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-p.cnf'
	else:
		positive_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-p.cnf'
		negative_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-n.cnf'

	output_file_path_ana = CASE_INPUT_FILE_PATH + file_name + '.ana'
	output_file_path_cpi = CASE_INPUT_FILE_PATH + file_name + '.cpi'

	# for MCS, only UP or UCE or QX
	st = compile_prime.compile_cover_NPCNF(COVER_FILE_PATH, LIMIT_TIME, root, positive_input_file_path, negative_input_file_path, output_file_path_ana, output_file_path_cpi, is_coherent, EXTRACT_MOD, BACKTRACK_MOD)

	if st == 2:
		result = []
		result = compile_prime.read_all_MCS(output_file_path_cpi)
		global all_PI
		all_PI = result[0]
		global SATMCS_memory
		SATMCS_memory = result[2]
		global SATMCS_time
		SATMCS_time = result[3]
	
	return st

def pncnf2outMPC(file_name, is_coherent, root, is_negative):

	if is_negative:
		positive_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-n.cnf'
		negative_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-p.cnf'
	else:
		positive_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-p.cnf'
		negative_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-n.cnf'

	output_file_path_ana = CASE_INPUT_FILE_PATH + file_name + '.ana'
	output_file_path_cpi = CASE_INPUT_FILE_PATH + file_name + '.cpi'

	# for MPC, only PC
	st = compile_prime.compile_cover_NPCNF(COVER_FILE_PATH, LIMIT_TIME, IS_OUTPUT_MODULE_MCS, TASK, is_coherent, root, False, False, False, False, False, IS_MPCPC_OPEN, positive_input_file_path, negative_input_file_path, output_file_path_ana, output_file_path_cpi, LIMIT_ITERATION, BACKTRACK_MOD)

	if st == 2:
		result = []
		result = compile_prime.read_all_MCS(output_file_path_cpi)
		global all_PI
		all_PI = result[0]
		global SATMCS_memory
		SATMCS_memory = result[2]
		global SATMCS_time
		SATMCS_time = result[3]
	
	return st

def pncnf2cpi(file_name, is_coherent, root, is_negative):

	if is_negative:
		positive_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-p.cnf'
		negative_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-n.cnf'
	else:
		positive_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-n.cnf'
		negative_input_file_path = CASE_INPUT_FILE_PATH + file_name + '-p.cnf'

	output_file_path_ana = CASE_INPUT_FILE_PATH + file_name + '.ana'
	output_file_path_cpi = CASE_INPUT_FILE_PATH + file_name + '.cpi'	
	
	# for non-coherent fault tree in task 2, PC can't use
	st = compile_prime.compile_cover_NPCNF(COVER_FILE_PATH, LIMIT_TIME, True, TASK, is_coherent, root, IS_PIUCA_OPEN, IS_PIZM_OPEN, IS_PIUP_OPEN, IS_PIUCE_OPEN, IS_PIUQX_OPEN, False, positive_input_file_path, negative_input_file_path, output_file_path_ana, output_file_path_cpi, LIMIT_ITERATION, 0)

	if st == 2:
		result = []
		result = compile_prime.read_cover_PI(output_file_path_ana, output_file_path_cpi)
		global cover_PI
		cover_PI = result[0]
		global SATMCS_memory
		SATMCS_memory = result[1]
		global SATMCS_time
		SATMCS_time = result[2]
		global DPLL_time
		DPLL_time = result[3]
		global Extract_time
		Extract_time = result[4]
		global Backtrack_time
		Backtrack_time = result[5]
		global num_API
		num_API = result[6]
		global times_SAT
		times_SAT = result[7]
		global ave_size_API
		ave_size_API = result[8]
		global first_shrink_size
		first_shrink_size = result[9]
		global second_shrink_size
		second_shrink_size = result[10]
		global other_shrink_size
		other_shrink_size = result[11]
		global ave_first_shrink
		ave_first_shrink = result[12]
		global ave_second_shrink
		ave_second_shrink = result[13]
		global ave_other_shrink
		ave_other_shrink = result[14]
		global times_fix_point
		times_fix_point = result[15]
		global ave_blocker_ignore
		ave_blocker_ignore = result[16]
	
	return st

def cpi2cnf(file_name):

	input_file_path = CASE_INPUT_FILE_PATH + file_name + '.cpi'
	output_file_path = CASE_OUTPUT_FILE_PATH + file_name + '.cnf'
	
	result = []
	result = cdnf.get_dual_rail(var_index_map)
	global var_index_dual_rail_map
	var_index_dual_rail_map = result[0]
	global index_var_dual_rail_map
	index_var_dual_rail_map = result[1]

	# print var_index_dual_rail_map
	# print index_var_dual_rail_map

	result = []
	global cover_PI
	result = cdnf.get_cdnf(file_name, cover_PI, index_var_dual_rail_map)
	cover_PI = []
	global pi
	pi = result[0]
	global min
	min = result[1]
	global fact
	fact = result[2]
	global dr
	dr = result[3]

	cdnf.output_cnf(output_file_path, var_index_dual_rail_map, pi, min, dr, fact)


def cdnf2out(file_name, is_coherent, is_negative):

	input_file_path = CASE_INPUT_FILE_PATH + file_name + '.cnf'
	output_file_path = CASE_OUTPUT_FILE_PATH + file_name + '.out'

	st = compile_prime.compile_all_NPCNF(ALL_FILE_PATH, LIMIT_TIME - SATMCS_time, input_file_path, output_file_path, is_negative, str(BACKTRACK_MOD))

	global is_memory_out_all
	is_memory_out_all = compile_prime.decode(output_file_path)

	result= []
	result = compile_prime.read_all_PI(output_file_path, TASK, is_coherent)
	global all_PI
	all_PI = result[0]
	global num_all_PI
	num_all_PI = result[1]
	global ASSMT_memory
	ASSMT_memory = result[2]
	global ASSMT_time
	ASSMT_time = result[3]
	
	return st

def readDetailResult(file_name, module_name, statistics):
	output_file_path_ana = CASE_INPUT_FILE_PATH + file_name + '.ana'

	f = open(output_file_path_ana, 'r')
	for line in f:
		line = line.strip('\n')
		
		if 'The number of API' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			statistics['num_API'][module_name] = int(words[0])
		elif 'The times of call SAT' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			statistics['times_SAT'][module_name] = int(words[0])
		elif 'The average size of API' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			statistics['ave_size_API'][module_name] = float(words[0])
	f.close()

def computeMCS(file_name, module_name, is_coherent, root, is_negative, statistics, output):
	st = pncnf2outMCS(file_name, is_coherent, root, is_negative)
	output.append(st)
	if st == 0:
		statistics['CPU_time_CoAMCS'][module_name] = 0.0
		statistics['memory_CoAMCS'][module_name] = LIMIT_MEMORY
	elif st == 1:
		statistics['CPU_time_CoAMCS'][module_name] = LIMIT_TIME
		statistics['memory_CoAMCS'][module_name] = 0
	else:
		output.append(all_PI)
		statistics['CPU_time_CoAMCS'][module_name] = SATMCS_time
		statistics['memory_CoAMCS'][module_name] = SATMCS_memory
		statistics['num_PI'][module_name] = len(all_PI)
		readDetailResult(file_name, module_name, statistics)

	statistics['CPU_time_AllSAT'][module_name] = 0.0
	statistics['memory_AllSAT'][module_name] = 0

# return 0(memory out); 1(time out); 2(successful) 
def SATMCS(case_name, module_name, limit_time, is_coherent, root, is_negative, statistics, is_clean):
	
	output = []
	
	clear()
	global LIMIT_TIME
	LIMIT_TIME = limit_time
	file_name = case_name + '_' + Tool.name(module_name)
	get_info(file_name)
	computeMCS(file_name, module_name, is_coherent, root, is_negative, statistics, output)

	if is_clean:
		clean(file_name)
		
	return output

def initializeParameter(case_input_file_path, case_output_file_path, CompileCover, limit_memory, extract_mod, backtrack_mod, is_output):

	global LIMIT_MEMORY
	LIMIT_MEMORY = limit_memory
	global EXTRACT_MOD
	EXTRACT_MOD = extract_mod
	global BACKTRACK_MOD
	BACKTRACK_MOD = backtrack_mod
	global IS_OUTPUT
	IS_OUTPUT = is_output

	global COVER_FILE_PATH
	COVER_FILE_PATH = CompileCover

	global CASE_INPUT_FILE_PATH
	CASE_INPUT_FILE_PATH = case_input_file_path
	global CASE_OUTPUT_FILE_PATH
	CASE_OUTPUT_FILE_PATH = case_output_file_path
