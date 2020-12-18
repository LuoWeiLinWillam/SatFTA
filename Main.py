# coding=utf-8
import subprocess
import time
import re
import os
import sys
import threading
import gc
import argparse
import pickle
import Queue

import config as config
import tool.Myfile as Myfile
import tool.Tool as Tool
import tool.DataAnalysis as analysis
import tool.cnfpn2dag as cnfpn2dag
import SATMCS.SATMCS as SATMCS
import Preprocess as Preprocess
import Merge as Merge

WORKSPACE 				= './'
# choose the benchmarks
BENCHMARK 				= 'test'
# set the limit time
LIMIT_TIME 				= 3600 * 1
LIMIT_MEMORY			= 1000000 * 16
IS_OUTPUT_MCS			= False
IS_OUTPUT_MODULE_MCS	= True

LIMIT_ITERATION			= 0
EXTRACT_MOD				= 0
BACKTRACK_MOD			= 1

COVER_FILE_PATH 		= WORKSPACE + 'Solver/SATMCS'
PREPROCESS_FILE_PATH	= WORKSPACE + 'Solver/Preprocess'
CASE_INPUT_FILE_PATH 	= WORKSPACE + 'example/' 
CASE_OUTPUT_FILE_PATH 	= WORKSPACE + 'example/' 
RESULT_OUTPUT_FILE_PATH = WORKSPACE + 'example/output/' 

def computeModuleSMCS(data_infor, case_name, module_name, statistics, remain_time, is_clean):
	if '-' in module_name:
		is_negative = True
	else:
		is_negative = False

	is_coherent 			= Preprocess.isCoherent(data_infor, Tool.name(module_name))
	root 					= Preprocess.getRoot(data_infor, Tool.name(module_name), is_negative)

	# case_input_file_path 	= CASE_INPUT_FILE_PATH + case_name + '/'
	# case_output_file_path 	= CASE_OUTPUT_FILE_PATH + case_name + '/'
	
	# SATMCS.initializeParameter(case_input_file_path, case_output_file_path, COVER_FILE_PATH, remain_time, LIMIT_MEMORY, EXTRACT_MOD, BACKTRACK_MOD, IS_OUTPUT_MODULE_MCS)

	result = SATMCS.SATMCS(case_name, module_name, remain_time, is_coherent, root, is_negative, statistics, is_clean)

	return result

# Algorithm	: computeSMCS(f, m0)
# ```
# q = Queue.Queue()
# q.put(m0)
# while not q.empty(): 
# 	mi = q.get()
# 	if mi is corherent:
# 		MCSs_mi = SATMCS-piup("f_mi-p.cnf")
# 	else:
# 		MCSs_mi = CoAPI("f_mi-p.cnf", "f_mi-n.cnf")
	
# 	for mcs in MCSs_mi:
# 		if exist mj in mcs:
# 			q.put(mj)
# ```
def computeSMCS(data_infor, case_name, statistics, is_clean):

	is_success = True
	MCSs = {}
	root_name = 'm0'
	remain_time = LIMIT_TIME

	q = Queue.Queue()
	q.put(root_name)

	i = 0
	while not q.empty(): 
		mi = q.get()

		if MCSs.has_key(mi):
			continue
		i = i + 1
		# print i, case_name, mi, 'solving'
		result = computeModuleSMCS(data_infor, case_name, mi, statistics, remain_time, is_clean)
		# print 'CompileCover Time:', statistics['CPU_time_CoAMCS'][mi], 'CompileAll Time:', statistics['CPU_time_AllSAT'][mi]
		# print case_name, mi, 'solved'

		if result[0] != 2:
			statistics['status'] = result[0]
			is_success = False
			break
		
		remain_time = remain_time - statistics['CPU_time_CoAMCS'][mi] - statistics['CPU_time_AllSAT'][mi]
		
		MCSs[mi] = result[1]
		# print MCSs[mi]

		for mcs in MCSs[mi]:
			for l in mcs:
				var = ''
				if l < 0:
					var = '-' + str(data_infor['module_index_var_map'][Tool.name(mi)][abs(l)])
				else:
					var = str(data_infor['module_index_var_map'][Tool.name(mi)][abs(l)])
				if 'm' in var:
					q.put(var)
	
	return [is_success, MCSs]

def computeSMCSNoOutput(data_infor, case_name, statistics, is_clean):

	is_success = True
	MCSs = {}
	root_name = 'm0'
	remain_time = LIMIT_TIME

	q = Queue.Queue()
	for item in range(0, statistics['modules_num']):
		q.put('m' + str(item))

	i = 0
	while not q.empty(): 
		mi = q.get()

		if MCSs.has_key(mi):
			continue
		i = i + 1
		# print i, case_name, mi, 'solving'
		result = computeModuleSMCS(data_infor, case_name, mi, statistics, remain_time, is_clean)
		# print 'CompileCover Time:', statistics['CPU_time_CoAMCS'][mi], 'CompileAll Time:', statistics['CPU_time_AllSAT'][mi]
		# print case_name, mi, 'solved'

		if result[0] != 2:
			statistics['status'] = result[0]
			is_success = False
			break
		
		remain_time = remain_time - statistics['CPU_time_CoAMCS'][mi]
		
		MCSs[mi] = result[1]
		# print MCSs[mi]
	
	return [is_success, MCSs]

def computeStatistics(statistics):
	if statistics['status'] == 2:
		compile_cover_times = []
		compile_cover_memorys = []
		compile_all_times = []
		compile_all_memorys = []
		for m in statistics['CPU_time_CoAMCS']:
			compile_cover_times.append(statistics['CPU_time_CoAMCS'][m])
		for m in statistics['memory_CoAMCS']:
			compile_cover_memorys.append(statistics['memory_CoAMCS'][m])
		for m in statistics['CPU_time_AllSAT']:
			compile_all_times.append(statistics['CPU_time_AllSAT'][m])
		for m in statistics['memory_AllSAT']:
			compile_all_memorys.append(statistics['memory_AllSAT'][m])
		statistics['all_CPU_time_CoAMCS'] = sum(compile_cover_times)
		statistics['all_CPU_time_AllSAT'] = sum(compile_all_times)
		statistics['all_CPU_time'] = statistics['all_CPU_time_CoAMCS'] + statistics['all_CPU_time_AllSAT']
		statistics['all_memory_CoAMCS'] = max(compile_cover_memorys)
		statistics['all_memory_AllSAT'] = max(compile_all_memorys)
		statistics['all_memory'] = max(statistics['all_memory_CoAMCS'], statistics['all_memory_AllSAT'])

		num_APIs = []
		size_APIs = []
		times_SATs = []
		for m in statistics['num_API']:
			num_APIs.append(statistics['num_API'][m])
		for m in statistics['times_SAT']:
			times_SATs.append(statistics['times_SAT'][m])
		for m in statistics['ave_size_API']:
			size_APIs.append(statistics['ave_size_API'][m] * statistics['num_API'][m])
		statistics['all_num_API'] = sum(num_APIs)
		if statistics['all_num_API'] == 0:
			statistics['all_ave_size_API'] = 0.0
		else:
			statistics['all_ave_size_API'] = float(sum(size_APIs)) / float(statistics['all_num_API'])
		statistics['all_times_SAT'] = sum(times_SATs)
		
	elif statistics['status'] == 0:
		statistics['all_CPU_time_CoAMCS'] = 0.0
		statistics['all_CPU_time_AllSAT'] = 0.0
		statistics['all_CPU_time'] = 0.0

		statistics['all_memory_CoAMCS'] = LIMIT_MEMORY
		statistics['all_memory_AllSAT'] = LIMIT_MEMORY
		statistics['all_memory'] = LIMIT_MEMORY
	elif statistics['status'] == 1:
		statistics['all_CPU_time_CoAMCS'] = LIMIT_TIME
		statistics['all_CPU_time_AllSAT'] = LIMIT_TIME
		statistics['all_CPU_time'] = LIMIT_TIME

		statistics['all_memory_CoAMCS'] = 0
		statistics['all_memory_AllSAT'] = 0
		statistics['all_memory'] = 0

	

def showResult(case_name, statistics, all_MCSs):

	if IS_OUTPUT_MCS:
		MCSs_output_file = RESULT_OUTPUT_FILE_PATH + case_name + '.mcs'

		f = file(MCSs_output_file, 'w+')
		for mcs in all_MCSs:
			output_mcs = ''
			for l in mcs:
				output_mcs = output_mcs + l + ' '
			output_mcs = output_mcs + '\n'
			f.writelines(output_mcs)
		f.close()

	statistics_output_file = RESULT_OUTPUT_FILE_PATH + case_name + '.res'
	computeStatistics(statistics)

	f = file(statistics_output_file, 'w+')
	PIn_size_info = 'The number of MCSs\t: ' + str(statistics['num_all_MCSs']) + '\n'
	f.writelines(PIn_size_info)

	mem_info = 'Total memory usage (kb)\t\t: ' + str(statistics['all_memory']) + '\n'
	f.writelines(mem_info)
	time_info = 'Total time usage (s)\t\t: ' + str(statistics['all_CPU_time']) + '\n'
	f.writelines(time_info)

	info = 'Number of MCS\t\t: ' + str(statistics['all_num_API']) + '\n'
	f.writelines(info)
	info = 'Average of the size of MCS\t\t: ' + str(statistics['all_ave_size_API']) + '\n'
	f.writelines(info)
	info = 'Number of call SAT\t\t: ' + str(statistics['all_times_SAT']) + '\n'
	f.writelines(info)

	info = 'Original number of basic event\t\t: ' + str(statistics['origin_basic_event_num']) + '\n'
	f.writelines(info)
	info = 'Original number of gate event\t\t: ' + str(statistics['origin_gate_evnet_num']) + '\n'
	f.writelines(info)
	info = 'Number of basic event\t\t: ' + str(statistics['basic_event_num']) + '\n'
	f.writelines(info)
	info = 'Number of gate event\t\t: ' + str(statistics['gate_event_num']) + '\n'
	f.writelines(info)
	info = 'Number of modules\t\t: ' + str(statistics['modules_num']) + '\n'
	f.writelines(info)
	info = 'Coherent\t\t: ' + str(statistics['is_coherent']) + '\n'
	f.writelines(info)
	info = 'Module time usage (kb)\t\t: ' + str(statistics['module_time']) + '\n'
	f.writelines(info)
	info = 'Simplify time usage (s)\t\t: ' + str(statistics['simplify_time']) + '\n'
	f.writelines(info)

	f.close()

	
def SatMCS(case_name):
	is_clean 		= True
	statistics 		= {}
	all_MCSs 		= []
	INPUT_DIR       = CASE_INPUT_FILE_PATH + case_name + '/'
	OUTPUT_DIR      = CASE_OUTPUT_FILE_PATH

	# Preprocess
	st = Preprocess.preprocess(PREPROCESS_FILE_PATH, INPUT_DIR, OUTPUT_DIR, config.SAME_GATE, config.ONE_CHILD, config.SAME_TREE, config.NORMAL_PROCESS, config.LCC_PROCESS, config.SIMPLE_OUTPUT, case_name)
	if st == 1:
		print 'Preprocess time out!'
		return
	data_infor = Preprocess.readInfor(CASE_INPUT_FILE_PATH, case_name, statistics)
	# Preprocess.showDataInfor(data_infor)

	# Computing
	case_input_file_path 	= CASE_INPUT_FILE_PATH + case_name + '/'
	case_output_file_path 	= CASE_OUTPUT_FILE_PATH + case_name + '/'
	
	SATMCS.initializeParameter(case_input_file_path, case_output_file_path, COVER_FILE_PATH, LIMIT_MEMORY, EXTRACT_MOD, BACKTRACK_MOD, IS_OUTPUT_MODULE_MCS)

	if IS_OUTPUT_MODULE_MCS:
		result = computeSMCS(data_infor, case_name, statistics, is_clean)
	else:
		result = computeSMCSNoOutput(data_infor, case_name, statistics, is_clean)

	if result[0] == True:
		statistics['num_all_MCSs'] = Merge.getNumMCSs(data_infor, 'm0', result[1])
		if IS_OUTPUT_MCS:
			all_module_MCSs = {}
			history = ['m0']
			all_MCSs = Merge.mergeMCSs(data_infor, 'm0', result[1], all_module_MCSs, history)
			print 'get all MCSs of m0'
	
	showResult(case_name, statistics, all_MCSs)
	return [statistics['modules_num'], statistics['simplify_time'] + statistics['module_time'],statistics['num_all_MCSs'], statistics['all_CPU_time'], statistics['all_memory']]
	
def SatMCSs():

	unsolve_case = ["cea9601", "das9701", "edf9206", "nus9601"]

	pathDir =  os.listdir(CASE_INPUT_FILE_PATH)
	case_names = []
	for allDir in pathDir:
		case_name = allDir
		case_names.append(case_name)

	case_names = set(case_names)
		  # break
	  # print case_names
	i = 0
	for case_name in case_names:

		if case_name in unsolve_case:
			continue

		i = i + 1
		print i,'th ' + case_name+' solving...' + '['+time.strftime('%Y-%m-%d %H:%M:%S')+']'
		result = SatMCS(case_name)
		clean(case_name)
		print '|#Module:', result[0], '|Pre Time:', result[1], '|#MCSs:', result[2], ' |Time:', result[3], ' |Memory:', result[4]
		print case_name + ' solved' + '['+time.strftime('%Y-%m-%d %H:%M:%S')+']'

def cleanAll():
	pathDir =  os.listdir(CASE_INPUT_FILE_PATH)
	case_names = []
	for allDir in pathDir:
		case_name = allDir
		case_names.append(case_name)

	case_names = set(case_names)
	for case_name in case_names:
		ignore_file = [case_name + '.dag']
		file_path = CASE_OUTPUT_FILE_PATH + case_name + '/'
		Myfile.clean_file(file_path, ignore_file)

def clean(case_name):
	ignore_file = [case_name + '.dag']
	file_path = CASE_OUTPUT_FILE_PATH + case_name + '/'
	Myfile.clean_file(file_path, ignore_file)

def cnf2dag():
	pathDir = os.listdir(CASE_INPUT_FILE_PATH)
	case_names = []
	for allDir in pathDir:
		case_name = allDir
		case_names.append(case_name)

	case_names = set(case_names)
	for case_name in case_names:
		cnfpn2dag.cnf2dag(CASE_INPUT_FILE_PATH, case_name)

def dataSatMCS():
	pathDir =  os.listdir(CASE_INPUT_FILE_PATH)
	case_names = []
	for allDir in pathDir:
		case_name = allDir
		case_names.append(case_name)

	case_names = set(case_names)

	excel_file_name = 'data_SatMCS.xls'
	excel_file_path = WORKSPACE
	analysis.write_data(case_names, RESULT_OUTPUT_FILE_PATH, excel_file_name, excel_file_path, LIMIT_TIME, LIMIT_MEMORY)


def parser():

	parser = argparse.ArgumentParser()
	parser.add_argument("-bm", type = str, default = 'test', help = "set the benchmark (default = test)")
	parser.add_argument("-tl", type = int, default = 3600 * 1, help = "set the time limit (s) (default = 3600)")
	parser.add_argument("-omcs", type = int, choices = [0, 1], default = 0, help = "set whether to output MCSs (0: False; 1: True) (default = 0)")
	parser.add_argument("-ommcs", type = int, choices = [0, 1], default = 1, help = "set whether to output module MCSs (0: False; 1: True) (default = 1)")
	parser.add_argument("-ex", type = int, choices = [0, 1, 2], default = 0, help = "set extracting method (0: LPG; 1: linear; 2: QX) (default = 0)")
	parser.add_argument("-bt", type = int, choices = [0, 1], default = 1, help = "set the backtrack mode (0: backtrack; 1: backjump) (default = 1)")

	args = parser.parse_args()

	global BENCHMARK
	BENCHMARK = args.bm + '/'
	global LIMIT_TIME
	LIMIT_TIME = args.tl
	global IS_OUTPUT_MCS
	if args.omcs == 0:
		IS_OUTPUT_MCS = False
	else:
		IS_OUTPUT_MCS = True
	global IS_OUTPUT_MODULE_MCS
	if args.ommcs == 0:
		IS_OUTPUT_MODULE_MCS = False
	else:
		IS_OUTPUT_MODULE_MCS = True
	global EXTRACT_MOD
	EXTRACT_MOD = args.ex
	global BACKTRACK_MOD
	BACKTRACK_MOD = args.bt

	global CASE_INPUT_FILE_PATH
	CASE_INPUT_FILE_PATH = CASE_INPUT_FILE_PATH + BENCHMARK
	global CASE_OUTPUT_FILE_PATH
	CASE_OUTPUT_FILE_PATH = CASE_OUTPUT_FILE_PATH + BENCHMARK
	global RESULT_OUTPUT_FILE_PATH
	RESULT_OUTPUT_FILE_PATH = RESULT_OUTPUT_FILE_PATH + BENCHMARK

	# new result path
	if not os.path.exists(RESULT_OUTPUT_FILE_PATH):
		os.mkdir(RESULT_OUTPUT_FILE_PATH)

def printStatus():
	print 'BENCHMARK \t\t\t\t=', BENCHMARK
	print 'LIMIT_TIME \t\t\t\t=', LIMIT_TIME
	print 'IS_OUTPUT_MCS \t\t\t\t=', IS_OUTPUT_MCS
	print 'IS_OUTPUT_MODULE_MCS \t\t\t\t=', IS_OUTPUT_MODULE_MCS
	print 'EXTRACT_MOD \t\t\t=', EXTRACT_MOD
	print 'BACKTRACK_MOD \t\t\t=', BACKTRACK_MOD

if __name__ == "__main__":
	
	parser()
	print '******************** STATUS ********************'
	printStatus()

	print '******************** SOLVE ********************'
	# SatMCS('motor2')
	SatMCSs()
	dataSatMCS()

	# cnf2dag()
	# cleanAll()
	print '********************  END  ********************'