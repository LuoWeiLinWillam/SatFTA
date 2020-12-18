# coding=utf-8
import subprocess
import time
import re
import os
import sys
import threading

def get_dual_rail(var_index_map):

	output = []
	var_index_dual_rail = {}
	index_var_dual_rail = {}
	for key in var_index_map:
		if 'e' in key:
			var_index_dual_rail[key] = var_index_map[key] * 2
			var_index_dual_rail['-'+ key] = var_index_map[key] * 2 - 1
			index_var_dual_rail[var_index_map[key] * 2] = key
			index_var_dual_rail[var_index_map[key] * 2 - 1] = '-'+ key

	output.append(var_index_dual_rail)
	output.append(index_var_dual_rail)
	return output
	

def decode(literal):
	var = literal / 2
	sign = literal % 2
	return var * 2 - sign 

def get_cdnf(file_name, cnf, index_var_dual_rail):
	output = []
	pi = []
	min = []
	fact = []
	dr = []

	appear = []
	literal_clause_map = {}

	# encode prime implicate
	i = 0
	for clause in cnf:
		clause_d = []
		for literal in clause:
			literal_d = decode(literal)
			clause_d.append(literal_d)
			if literal_d not in appear:
				appear.append(literal_d)

		assert(len(clause) == len(clause_d))

		pi.append(clause_d)
		# node the clause'index of appearing literal
		for literal in clause_d:
			if literal not in literal_clause_map:
				appear_list = []
				appear_list.append(i)
				literal_clause_map[literal] = appear_list
			else:
				literal_clause_map[literal].append(i)

		i = i + 1
	
	assert(len(pi) == len(cnf))

	# encode fact constraints
	for var in index_var_dual_rail:
		if var not in appear:
			clause_d = []
			clause_d.append(0 - var)
			fact.append(clause_d)

	# encode dual rail encode constraints
	for var in index_var_dual_rail:
		if var % 2 == 1:
			if (var in appear) & ((var+1) in appear):
				clause_d = []
				clause_d.append(0 - var)
				clause_d.append(0 - (var+1))
				dr.append(clause_d)

	assert(len(min) == 0)

	output.append(pi)
	output.append(min)
	output.append(fact)
	output.append(dr)
	return output

def get_cdnf_min(file_name, cnf, index_var_dual_rail):
	output = []
	pi = []
	min = []
	fact = []
	dr = []

	appear = []
	literal_clause_map = {}

	# encode prime implicate
	i = 0
	for clause in cnf:
		clause_d = []
		for literal in clause:
			literal_d = decode(literal)
			clause_d.append(literal_d)
			if literal_d not in appear:
				appear.append(literal_d)

		assert(len(clause) == len(clause_d))

		pi.append(clause_d)
		# node the clause'index of appearing literal
		for literal in clause_d:
			if literal not in literal_clause_map:
				appear_list = []
				appear_list.append(i)
				literal_clause_map[literal] = appear_list
			else:
				literal_clause_map[literal].append(i)

		i = i + 1
	
	assert(len(pi) == len(cnf))

	# get minimal constraints
	for literal in literal_clause_map:
		appear_list = literal_clause_map[literal]
		items = []
		item = []
		item.append(0 - literal)
		items.append(item)
		for i in appear_list:
			clause = pi[i]
			if len(clause) > 1:
				item = []
				is_literal = False
				for l in clause:
					if l != literal:
						item.append(0 - l)
					else:
						is_literal = True
				assert(is_literal)
				items.append(item)
			else:
				assert(clause[0] == literal)
		# if len(items) = 1 means the literal must be true
		if len(items) > 1:
			min.append(items)

	# encode fact constraints
	for var in index_var_dual_rail:
		if var not in appear:
			clause_d = []
			clause_d.append(0 - var)
			fact.append(clause_d)

	# encode dual rail encode constraints
	for var in index_var_dual_rail:
		if var % 2 == 1:
			if (var in appear) & ((var+1) in appear):
				clause_d = []
				clause_d.append(0 - var)
				clause_d.append(0 - (var+1))
				dr.append(clause_d)

	output.append(pi)
	output.append(min)
	output.append(fact)
	output.append(dr)
	return output

def get_cdnf_SATMCS(output_file_path, cnf, index_var_map):
	f = file(output_file_path, 'w+')

	num_clause = len(cnf)

	num_var = 0
	for key in index_var_map:
		if 'e' in index_var_map[key]:
			num_var = num_var + 1
			# f.writelines('m ')
			# output = str(key) + ' = ' + index_var_map[key]
			# f.writelines(output)
			# f.writelines('\n')

	f.writelines('c\n')

	f.writelines('p cnf ' + str(num_var) + ' ' + str(num_clause) + '\n')
	for clause in cnf:
		for literal in clause:
			if literal % 2 == 1:
				f.writelines( '-' + str(literal/2) + ' ')
			else:
				f.writelines( str(literal/2) + ' ')
		f.writelines('0\n')
	f.writelines('0')
	f.close()

def get_cdnf_Primer(output_file_path, cnf, index_var_map):
	f = file(output_file_path, 'w+')

	num_clause = len(cnf)

	num_var = 0
	for key in index_var_map:
		if 'e' in index_var_map[key]:
			num_var = num_var + 1

	f.writelines('p cnf ' + str(num_var) + ' ' + str(num_clause) + '\n')
	for clause in cnf:
		for literal in clause:
			if literal % 2 == 1:
				f.writelines( '-' + str(literal/2) + ' ')
			else:
				f.writelines( str(literal/2) + ' ')
		f.writelines('0\n')
	f.writelines('0')
	f.close()

def output_cnf(output_file_path, var_index_dual_rail, pi, min, dr, fact):
	
	assert(len(min) == 0)

	f = file(output_file_path, 'w+')

	num_var = len(var_index_dual_rail)
	num_clause = len(pi) + len(dr) + len(fact)
	f.writelines('p cnf ' + str(num_var) + ' ' + str(num_clause) + '\n')
	for clause in pi:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')
	for clause in dr:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')
	for clause in fact:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')
	
	# f.writelines('0')
	f.close()

def output_cnf_min(output_file_path, var_index_dual_rail, pi, min, dr, fact):

	new_index = len(var_index_dual_rail)

	min_cnf_1 = []
	min_cnf_2 = []
	
	for item in min:

		to_min_cnf_1 = []
		for item2 in item:

			new_index = new_index + 1
			new_var = new_index
			to_min_cnf_1.append(new_var)

			to_min_cnf_2_3 = []
			to_min_cnf_2_3.append(new_var)
			for item3 in item2:
				to_min_cnf_2 = []
				to_min_cnf_2.append(0 - new_var)
				to_min_cnf_2.append(item3)
				to_min_cnf_2_3.append(0 - item3)
				min_cnf_2.append(to_min_cnf_2)
				
			min_cnf_2.append(to_min_cnf_2_3)

		min_cnf_1.append(to_min_cnf_1)

		
	f = file(output_file_path, 'w+')

	num_var = len(var_index_dual_rail)
	num_clause = len(pi) + len(dr) + len(fact) + len(min_cnf_1) + len(min_cnf_2)
	f.writelines('p cnf ' + str(num_var) + ' ' + str(num_clause) + '\n')
	for clause in pi:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')
	for clause in dr:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')
	for clause in fact:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')
	for clause in min_cnf_1:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')
	for clause in min_cnf_2:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')
	
	f.writelines('0')
	f.close()

def output_cdnf(output_file_path, var_index_dual_rail, pi, min, dr, fact):
	f = file(output_file_path, 'w+')

	num_var = len(var_index_dual_rail)
	num_clause = len(pi) + len(dr) + len(fact)
	f.writelines('p cnf ' + str(num_var) + ' ' + str(num_clause) + '\n')
	for clause in pi:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')
	for clause in dr:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')
	for clause in fact:
		for literal in clause:
			f.writelines(str(literal) + ' ')
		f.writelines('0\n')

	num_clause = len(min)
	f.writelines('p dnf ' + str(num_var) + ' ' + str(num_clause) + '\n')
	for dnf in min:
		for item in dnf:
			for literal in item:
				f.writelines(str(literal) + ' ')
			f.writelines('0 ')
		f.writelines('\n')

	f.writelines('0')
	f.close()

# def output_information(file_name):
#     output_file_path = input_file_path + file_name + '.inf'
#     f = file(output_file_path,'w+')
#     mem_info = 'b ' + mem_map[file_name] + '\n'
#     f.writelines(mem_info)
#     time_info = 't ' + str(float(time_map[file_name][1]) - float(time_map[file_name][0])) + '\n'
#     f.writelines(time_info)
#     for var in var_name_dual_rail:
#         dual_rail_info = 'm ' + str(var) + ' ' + var_name_dual_rail[var] + '\n'
#         f.writelines(dual_rail_info)
#     f.close()


