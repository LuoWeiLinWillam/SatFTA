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

import tool.Tool as Tool

def getNumMCSs(data_infor, module_name, MCSs_map):
	num_module_MCSs = 0
	MCSs = MCSs_map[module_name]
	for mcs in MCSs:
		new_MCS_num = 1
		for l in mcs:
			l_index = abs(l)
			l_var = data_infor['module_index_var_map'][Tool.name(module_name)][l_index]
			if l < 0:
				l_var = '-' + l_var

			if 'm' in l_var:
				new_MCS_num_temp = getNumMCSs(data_infor, l_var, MCSs_map)
				if new_MCS_num_temp != 0:
					new_MCS_num = new_MCS_num * getNumMCSs(data_infor, l_var, MCSs_map)
					
		num_module_MCSs = num_module_MCSs + new_MCS_num

	return num_module_MCSs

def extendMCSs(p_MCSs, m_MCSs):
	new_p_MCSs = []
	if len(p_MCSs) == 0:
		for item in m_MCSs:
			new_p_MCSs.append(item)
	elif len(m_MCSs) == 0:
		for item in p_MCSs:
			new_p_MCSs.append(item)
	else:
		for item_1 in p_MCSs:
			for item_2 in m_MCSs:
				item_1_temp = item_1 + item_2
				new_p_MCSs.append(item_1_temp)
	
	return new_p_MCSs

def mergeMCSs(data_infor, module_name, MCSs_map, module_all_MCSs, hesitory):
	num_MCS = 0
	# print '***************** begin', module_name, '*****************'
	all_MCSs = []
	MCSs = MCSs_map[module_name]
	for mcs in MCSs:
		MCSs_cluster = []
		for l in mcs:
			l_index = abs(l)
			l_var = data_infor['module_index_var_map'][Tool.name(module_name)][l_index]
			if l < 0:
				l_var = '-' + l_var

			if 'm' in l_var:
				if module_all_MCSs.has_key(l_var):
					module_MCSs = module_all_MCSs[l_var]
					# print 'have obtained all MCSs of', l_var
				else:
					if l_var in hesitory:
						# print 'there is a roop'
						sys.exit()
					else:
						hesitory.append(l_var)

					module_MCSs = mergeMCSs(data_infor, l_var, MCSs_map, module_all_MCSs, hesitory)
					# print '***************** continue', module_name, '*****************'
					module_all_MCSs[l_var] = module_MCSs
					# print 'get all MCSs of', l_var
					hesitory.remove(l_var)
					# print module_all_MCSs
			else:
				module_MCSs = [[l_var]]

			MCSs_cluster = extendMCSs(MCSs_cluster, module_MCSs)

		# if module_name is 'm0':
		# 	for item in MCSs_cluster:
		# 		num_MCS = num_MCS + 1
		# 		print num_MCS, item

		all_MCSs = all_MCSs + MCSs_cluster

	# print '***************** end', module_name, '*****************'
	return all_MCSs
