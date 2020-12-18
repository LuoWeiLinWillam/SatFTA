# coding=utf-8
import subprocess
import time
import re
import os
import sys
import threading
import signal
import gc

# return 0(memory out); 1(time out); 2(successful) 
def compile_cover_NPCNF(project_file_path, limit_time, root, positive_input_file_path, negative_input_file_path, output_file_path_ana, output_file_path_cpi, is_coherent, EXTRACT_MOD, BACKTRACK_MOD):

	command = '/usr/bin/time -v' + ' ' + project_file_path + ' ' + positive_input_file_path + ' ' + negative_input_file_path + ' -inpopi -omcs'
	command = command + ' -ex=' + str(EXTRACT_MOD)
	command = command + ' -tl=' + str(limit_time)
	command = command + ' -of=' + output_file_path_ana
	if is_coherent:
		command = command + ' -co'
	command = command + ' -r=' + str(root)
	command = command + ' -bt=' + str(BACKTRACK_MOD)
	command = command + ' > ' + output_file_path_cpi
	# print command
	
	gc.collect()
	p = subprocess.Popen(command, preexec_fn = os.setsid, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	begin_time = time.time()
	is_err = False
	while p.poll() == None:
		now_time = time.time()
		if (now_time - begin_time) > limit_time :
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
		statistics = p.stderr.readlines()

		user_time = 0.0
		system_time = 0.0
		memory = 0

		for line in statistics:
			if 'User time (seconds)' in line:
				pattern='[0-9]+.[0-9]+'
				words = re.findall(pattern,line)
				if len(words) == 0:
					pattern='[0-9]+'
					words = re.findall(pattern,line)
				words = filter(lambda x: x!='',words)
				user_time = float(words[0])
			if 'System time (seconds)' in line:
				pattern='[0-9]+.[0-9]+'
				words = re.findall(pattern,line)
				if len(words) == 0:
					pattern='[0-9]+'
					words = re.findall(pattern,line)
				words = filter(lambda x: x!='',words)
				system_time = float(words[0])
			if 'Maximum resident set size' in line:
				pattern = '[0-9]+'
				words = re.findall(pattern,line)
				words = filter(lambda x: x!='',words)
				memory = int(words[0])

		time_info = 't ' + str(user_time + system_time) + '\n'
		mem_info = 'b ' + str(memory) + '\n'
		
		output = []
		f = open(output_file_path_cpi, 'r')
		for line in f:
			output.append(line)
		f.close()

		# memory out
		if len(output) == 0:
			print 'Memory out'
			return 0

		# memory out
		if not os.path.exists(output_file_path_ana):
			print 'Memory out'
			return 0
		
		f = file(output_file_path_cpi, 'w+')
		
		f.writelines(mem_info)
		f.writelines(time_info)
		f.writelines(output)
		f.close()
		return 2

def read_cover_PI(output_file_path_ana, output_file_path_cpi):
	cover_PI = []
	memory = 0
	time = 0.0
	DPLL_time = 0.0
	extract_time = 0.0
	backtrack_time = 0.0
	num_API = 0
	times_SAT = 0
	ave_API = 0.0
	first_shrink_size = 0
	second_shrink_size = 0
	other_shrink_size = 0
	ave_first_shrink = 0.0
	ave_second_shrink = 0.0
	ave_other_shrink = 0.0
	times_fix_point = 0
	ave_blocker_ignore = 0.0

	output = []

	f = open(output_file_path_cpi, 'r')

	for line in f:
		line = line.strip('\n')
		words = line.split(' ')
		if line[0] == 'b':
			memory = int(words[1])
		elif line[0] == 't':
			time = float(words[1])
		elif line[0] == 'm':
			continue
		elif line[0] == 's':
			continue
		else:
			clause = []
			for word in words:
				lit = int(word)
				if lit != 0:
					if lit % 2 == 0:
						lit = lit + 1
					else:
						lit = lit - 1
					clause.append(lit)
			cover_PI.append(clause)
	
	f.close()

	output.append(cover_PI)
	output.append(memory)
	output.append(time)

	f = open(output_file_path_ana, 'r')
	for line in f:
		line = line.strip('\n')
		if 'DPLL time' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			DPLL_time = float(words[0])
		elif 'Extract time' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			extract_time = float(words[0])
		elif 'Backtrack time' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			backtrack_time = float(words[0])
		elif 'The number of API' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			num_API = int(words[0])
		elif 'The times of call SAT' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			times_SAT = int(words[0])
		elif 'The average size of API' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			ave_API = float(words[0])
		elif 'The first shrink size' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			first_shrink_size = int(words[0])
		elif 'The second shrink size' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			second_shrink_size = int(words[0])
		elif 'The other shrink size' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			other_shrink_size = int(words[0])
		elif 'The average first shrink rate' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			ave_first_shrink = float(words[0])
		elif 'The average second shrink rate' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			ave_second_shrink = float(words[0])
		elif 'The average other shrink rate' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			ave_other_shrink = float(words[0])
		elif 'The times of getting fix point' in line:
			pattern = '[0-9]+'
			words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			times_fix_point = int(words[0])
		elif 'The average times of blocker ignore' in line:
			pattern='[0-9]+.[0-9]+'
			words = re.findall(pattern,line)
			if len(words) == 0:
				pattern='[0-9]+'
				words = re.findall(pattern,line)
			words = filter(lambda x: x!='',words)
			ave_blocker_ignore = float(words[0])
	f.close()

	output.append(DPLL_time)
	output.append(extract_time)
	output.append(backtrack_time)
	output.append(num_API)
	output.append(times_SAT)
	output.append(ave_API)
	output.append(first_shrink_size)
	output.append(second_shrink_size)
	output.append(other_shrink_size)
	output.append(ave_first_shrink)
	output.append(ave_second_shrink)
	output.append(ave_other_shrink)
	output.append(times_fix_point)
	output.append(ave_blocker_ignore)

	return output

def compile_all_NPCNF(project_file_path, limit_time, input_file_path, output_file_path, is_negative, backtrack_mod):
	
	command = '/usr/bin/time -v' + ' ' + project_file_path + ' -inpopi -bt=' + backtrack_mod + ' ' + input_file_path + ' > ' + output_file_path
	# print command

	gc.collect()
	p = subprocess.Popen(command, preexec_fn = os.setsid, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	begin_time = time.time()
	is_err = False
	while p.poll() == None:
		now_time = time.time()
		if (now_time-begin_time) > limit_time :
			print 'Time out'
			is_err = True
			# print 'kill: '+str(p.pid)
			os.killpg( p.pid, signal.SIGTERM)
			break
		else:
			time.sleep(1)

	if is_err:
		return False
	else:
		statistics = p.stderr.readlines()

		user_time = 0.0
		system_time = 0.0
		memory = 0

		for line in statistics:
			if 'User time (seconds)' in line:
				pattern='[0-9]+.[0-9]+'
				words = re.findall(pattern,line)
				if len(words) == 0:
					pattern='[0-9]+'
					words = re.findall(pattern,line)
				words = filter(lambda x: x!='',words)
				user_time = float(words[0])
			if 'System time (seconds)' in line:
				pattern='[0-9]+.[0-9]+'
				words = re.findall(pattern,line)
				if len(words) == 0:
					pattern='[0-9]+'
					words = re.findall(pattern,line)
				words = filter(lambda x: x!='',words)
				system_time = float(words[0])
			if 'Maximum resident set size' in line:
				pattern = '[0-9]+'
				words = re.findall(pattern,line)
				words = filter(lambda x: x!='',words)
				memory = int(words[0])

		time_info = 't ' + str(user_time + system_time) + '\n'
		mem_info = 'b ' + str(memory) + '\n'
		
		output = []
		f = open(output_file_path, 'r')
		for line in f:
			output.append(line)
		f.close()
		
		f = file(output_file_path, 'w+')
		
		f.writelines(mem_info)
		f.writelines(time_info)
		f.writelines(output)
		f.close()
		return True

def decode(input_file_path):
	is_error = True
	output = []
	f = open(input_file_path, 'r')
	for line in f:
		if line[0] == '0':
			is_error = False
		elif line[0] == 'b':
			output.append(line)
		elif line[0] == 't':
			output.append(line)
		else:
			# decode
			words = line.split(' ')
			line = ''
			for lit in words:
				if lit[0] is not '0':
					lit = int(lit)
					lit = lit / 2
					sign = lit % 2
					index = 0
					if sign == 1:
						index = (lit + 1) / 2
					else:
						index = lit / 2
					if sign == 1:
						lit = 0 - index
					else:
						lit = index

					line = line + str(lit) + ' '
			line = line + '0\n'
			output.append(line)
	f.close()
		
	f = file(input_file_path, 'w+')
	f.writelines(output)
	f.close()
	return is_error

def read_all_PI(input_file_path, task, is_coherent):
	all_PI = []
	num_all_temp = 0
	num_all = 0
	memory = 0
	time = 0.0

	output = []

	f = open(input_file_path, 'r')

	if (not is_coherent) and task == 2:
		for line in f:
			line = line.strip('\n')
			words = line.split(' ')
			if line[0] == 'b':
				memory = int(words[1])
			elif line[0] == 't':
				time = float(words[1])
			elif line[0] == 'm':
				continue
			elif line[0] == 's':
				continue
			elif line[0] == 'n':
				num_all = int(words[1])
			else:
				num_all_temp = num_all_temp + 1
				term = []
				for word in words:
					lit = int(word)
					if lit != 0:
						term.append(lit)
				all_PI.append(term)

	else:
		for line in f:
			line = line.strip('\n')
			words = line.split(' ')
			if line[0] == 'b':
				memory = int(words[1])
			elif line[0] == 't':
				time = float(words[1])
			elif line[0] == 'm':
				continue
			elif line[0] == 's':
				continue
			else:
				term = []
				for word in words:
					lit = int(word)
					if lit != 0:
						index = lit / 2
						sign = lit % 2
						if sign == 1:
							lit = 0 - index
						else:
							lit = index
						term.append(lit)
				all_PI.append(term)

	f.close()

	output.append(all_PI)
	if num_all == 0:
		num_all = num_all_temp
	output.append(num_all)
	output.append(memory)
	output.append(time)

	return output

def read_all_MCS(input_file_path):
	all_PI = []
	num_all = 0
	memory = 0
	time = 0.0

	output = []

	f = open(input_file_path, 'r')
	for line in f:
		line = line.strip('\n')
		words = line.split(' ')
		if line[0] == 'b':
			memory = int(words[1])
		elif line[0] == 't':
			time = float(words[1])
		elif line[0] == 'm':
			continue
		elif line[0] == 's':
			continue
		elif line[0] == 'n':
			num_all = int(words[1])
		else:
			term = []
			for word in words:
				lit = int(word)
				if lit != 0:
					index = lit / 2
					sign = lit % 2
					if sign == 1:
						lit = 0 - index
					else:
						lit = index
					term.append(lit)
			all_PI.append(term)

	f.close()

	output.append(all_PI)
	if num_all == 0:
		num_all = len(all_PI)
	output.append(num_all)
	output.append(memory)
	output.append(time)

	return output

