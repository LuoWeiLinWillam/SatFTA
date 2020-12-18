#coding=utf-8
import sys,re,os,time,xlrd,xlwt
from xlutils.copy import copy
import shutil

def get_item(input_file_path):
	num_original_event	= 0
	num_original_gate	= 0
	num_event			= 0
	num_gate 			= 0
	num_module			= 0
	num_MCS				= 0
	total_time    		= 0.0
	total_memory  		= 0
	simplify_time    	= 0.0
	module_time    		= 0.0
	cover_time   		= 0.0
	cover_memory 		= 0
	all_time    		= 0.0
	all_memory  		= 0
	num_AMCS			= 0
	ave_size_AMCS		= 0.0
	num_call_SAT		= 0
	is_coheren			= ''

	for line in open(input_file_path):
		if 'Original number of basic event' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_original_event = int(words[0])
		elif 'Original number of gate event' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_original_gate = int(words[0])
		elif 'Number of basic event' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_event = int(words[0])
		elif 'Number of gate event' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_gate = int(words[0])
		elif 'Number of modules' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_module = int(words[0])
		elif 'The number of MCSs' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_MCS = int(words[0])
		elif 'Total time usage (s)' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			total_time = float(words[0])
		elif 'Total memory usage (kb)' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			total_memory = int(words[0])
		elif 'Simplify time usage' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			simplify_time = float(words[0])
		elif 'Module time usage' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			module_time = float(words[0])
		elif 'CompileCover time usage (s)' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			cover_time = float(words[0])
		elif 'CompileCover memory usage (kb)' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			cover_memory = int(words[0])
		elif 'CompileAll time usage (s)' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			all_time = float(words[0])
		elif 'CompileAll memory usage (kb)' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			all_memory = int(words[0])
		elif 'Number of AMCS' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_AMCS = int(words[0])
		elif 'Average of the size of AMCS' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			ave_size_AMCS = float(words[0])
		elif 'Number of call SAT' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_call_SAT = int(words[0])
		elif 'Coherent' in line:
			if 'True' in line:
				is_coheren = 'Coherent'
			else:
				is_coheren = 'Non-coherent'
		else:
			continue

	item = []
	item.append(num_original_event)
	item.append(num_original_gate)
	item.append(num_event)
	item.append(num_gate)
	item.append(num_module)
	item.append(num_MCS)
	item.append(total_time)
	item.append(total_memory)
	item.append(simplify_time)
	item.append(module_time)
	item.append(cover_time)
	item.append(cover_memory)
	item.append(all_time)
	item.append(all_memory)
	item.append(num_AMCS)
	item.append(ave_size_AMCS)
	item.append(num_call_SAT)
	item.append(is_coheren)

	return item

def write_data(file_names, result_output_file_path, excel_file_name, excel_file_path, limit_time, limit_memory):
	source_dir = excel_file_path + excel_file_name
	target_dir = result_output_file_path + excel_file_name
	shutil.copy(source_dir, target_dir)

	datar = xlrd.open_workbook(target_dir)
	dataw = copy(datar)
	table = dataw.get_sheet(0)
	nrows = datar.sheets()[0].nrows

	for file_name in file_names:
		input_file_path = result_output_file_path + file_name + '.res'
		if os.path.isfile(input_file_path):
			item = get_item(input_file_path)
		else:
			item = []

		table.write(nrows, 0, file_name)
		if len(item) == 0:
			table.write(nrows, 1, limit_memory)
			table.write(nrows, 4, limit_time)
		
		for i in range(len(item)):
			table.write(nrows, i + 1, item[i])

		dataw.save(target_dir)
		nrows = nrows + 1



