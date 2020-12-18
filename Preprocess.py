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
import signal
import json

LIMIT_TIME = 3600

def showDataInfor(data_infor):
	print '*********************** Overview ***********************'
	print 'simplify_time:',data_infor['simplify_time']
	print 'module_time:',data_infor['module_time']
	print 'origin_basic_event_num:',data_infor['origin_basic_event_num']
	print 'origin_gate_evnet_num:',data_infor['origin_gate_evnet_num']
	print 'basic_event_num:',data_infor['basic_event_num']
	print 'gate_event_num:',data_infor['gate_event_num']
	print 'modules_num:',data_infor['modules_num']
	print 'modularized:',data_infor['modularized']
	
	print '*********************** Detail ***********************'
	for m in data_infor['coherent_map']:
		print '***********************', m, '***********************'
		print 'coherent_map:',data_infor['coherent_map'][m]
		print 'root_map:',data_infor['root_map'][m]
		print 'module_var_index_map:',data_infor['module_var_index_map'][m]
		print 'module_index_var_map:',data_infor['module_index_var_map'][m]
	
def initStatistics(infor, statistics):
	statistics['status'] = 2
	statistics['num_all_MCSs'] = 0
	statistics['all_CPU_time'] = 0.0
	statistics['all_CPU_time_CoAMCS'] = 0.0
	statistics['all_CPU_time_AllSAT'] = 0.0
	statistics['all_memory'] = 0
	statistics['all_memory_CoAMCS'] = 0
	statistics['all_memory_AllSAT'] = 0
	statistics['all_num_API'] = 0
	statistics['all_ave_size_API'] = 0.0
	statistics['all_times_SAT'] = 0

	statistics['origin_basic_event_num'] = infor['origin_basic_event_num']
	statistics['origin_gate_evnet_num'] = infor['origin_gate_evnet_num']
	statistics['basic_event_num'] = infor['basic_event_num']
	statistics['gate_event_num'] = infor['gate_event_num']
	statistics['modules_num'] = infor['modules_num']
	statistics['simplify_time'] = infor['simplify_time']
	statistics['module_time'] = infor['module_time']
	is_coherent = True
	for m in infor['coherent_map']:
		if not infor['coherent_map'][m]:
			is_coherent = False
			break
	statistics['is_coherent'] = is_coherent

	CPU_time_CoAMCS = {}
	memory_CoAMCS = {}
	CPU_time_AllSAT = {}
	memory_AllSAT = {}
	num_API = {}
	num_PI = {}
	times_SAT = {}
	ave_size_API = {}

	for m in infor['coherent_map']:
		CPU_time_CoAMCS[m] = 0.0
		memory_CoAMCS[m] = 0
		CPU_time_AllSAT[m] = 0.0
		memory_AllSAT[m] = 0
		num_API[m] = 0
		num_PI[m] = 0
		times_SAT[m] = 0
		ave_size_API[m] = 0.0
	
	statistics['CPU_time_CoAMCS'] = CPU_time_CoAMCS
	statistics['memory_CoAMCS'] = memory_CoAMCS
	statistics['CPU_time_AllSAT'] = CPU_time_AllSAT
	statistics['memory_AllSAT'] = memory_AllSAT
	statistics['num_API'] = num_API
	statistics['num_PI'] = num_PI
	statistics['times_SAT'] = times_SAT
	statistics['ave_size_API'] = ave_size_API

def getPickle(OUTPUT_DIR, FILE_NAME):

	raw = open(OUTPUT_DIR + FILE_NAME + "/package")
	result = ""
	for line in raw:
		result += line
	obj = json.loads(result)
	for key, value in obj["module_index_var_map"].items():
		n = {}
		for k, v in value.items():
			n[int(k)] = v
		obj["module_index_var_map"][key] = n
	data_file = open(OUTPUT_DIR + FILE_NAME + "/pickle_data", "wb")
	pickle.dump(obj, data_file, 2)

def preprocess(PREPROCESS_FILE_PATH, INPUT_DIR, OUTPUT_DIR, SAME_GATE, ONE_CHILD, SAME_TREE, NORMAL_PROCESS, LCC_PROCESS, SIMPLE_OUTPUT, FILE_NAME):
	command = PREPROCESS_FILE_PATH + ' -INPUT_DIR=' + INPUT_DIR + ' -OUTPUT_DIR=' + OUTPUT_DIR
	if SAME_GATE:
		command = command + ' -SAME_GATE=true'
	else:
		command = command + ' -SAME_GATE=false'
	if ONE_CHILD:
		command = command + ' -ONE_CHILD=true'
	else:
		command = command + ' -ONE_CHILD=false'
	if SAME_TREE:
		command = command + ' -SAME_TREE=true'
	else:
		command = command + ' -SAME_TREE=false'
	if NORMAL_PROCESS:
		command = command + ' -NORMAL_PROCESS=true'
	else:
		command = command + ' -NORMAL_PROCESS=false'
	if LCC_PROCESS:
		command = command + ' -LCC_PROCESS=true'
	else:
		command = command + ' -LCC_PROCESS=false'
	if SIMPLE_OUTPUT:
		command = command + ' -SIMPLE_OUTPUT=true'
	else:
		command = command + ' -SIMPLE_OUTPUT=false'
	command = command + ' -FILE_NAME=' + FILE_NAME + '.dag'

	# print command
	
	gc.collect()
	p = subprocess.Popen(command, preexec_fn = os.setsid, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	begin_time = time.time()
	is_err = False
	while p.poll() == None:
		now_time = time.time()
		if (now_time - begin_time) > LIMIT_TIME :
			print 'Time out'
			is_err = True
			# print 'kill: '+str(p.pid)
			os.killpg( p.pid, signal.SIGTERM)
			break
		else:
			time.sleep(1)
	
	if is_err:
		return 1
	else:
		getPickle(OUTPUT_DIR, FILE_NAME)
		return 0
	
def readInfor(CASE_INPUT_FILE_PATH, case_name, statistics):
	infor_path = CASE_INPUT_FILE_PATH + case_name + '/' + 'pickle_data'
	data_file = open(infor_path, "rb")
	infor = pickle.load(data_file)

	initStatistics(infor, statistics)
		
	return infor

def isCoherent(data_infor, module_name):
	
	return data_infor['coherent_map'][module_name]

def getRoot(data_infor, module_name, is_negative):
	
	if is_negative:
		return 0 - data_infor['root_map'][module_name]
	else:
		return data_infor['root_map'][module_name]