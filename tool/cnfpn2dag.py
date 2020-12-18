#coding = utf-8
import sys,re,os,time

num_original_var = 0
num_all_var = 0

dag = {}
int_dag = {}

f = 0

#
#def get_block(output,inputs):
#    block = {}

#    if output == 0:
#        return block
	
#    block[output] = inputs

#    return block

#def add_block(block):
#    if len(block) == 0:
#        return
#    for key in block:
#        int_dag[key] = block[key]

def get_int_dag(file_path):
	inputs = []
	output = 0
	for line in open(file_path):
		if line[0] is 'c':
			# get the number of original variables
			global num_original_var
			num_original_var = int(re.findall(r"\d+\.?\d*",line)[0])
		elif line[0] is 'p':
			# get the number of all variables
			global num_all_var
			num_all_var = int(re.findall(r"\d+\.?\d*",line)[0])
		else:
			# get a clause
			line = line.strip()
			words = line.split(' ')
			
			if len(words) is 1: #结束符号
				#block = get_block(output,inputs)
				#add_block(block)
				continue
			elif len(words) is 2: #顶事件
				global f
				f = abs(int(words[0]))
				#block = get_block(output,inputs)
				#add_block(block)
			elif len(words) is 3: #子句包含2个文字
				literal_1 = int(words[0])
				literal_2 = int(words[1])
				if output == 0:
					print 'is err!'
				else:
					if (abs(literal_1) != abs(output)) & (abs(literal_2) != abs(output)): #找到相等变量
						if literal_1 * literal_2 < 0:#var_1 = var_1
							temp_list = []
							temp_list.append(abs(literal_2))
							int_dag[abs(literal_1)] = temp_list
						else:#var_1 = -var_1
							temp_list = []
							temp_list.append(0 - abs(literal_2))
							int_dag[abs(literal_1)] = temp_list
					
			else: #子句包含2个以上文字
				inputs = []
				output = 0
				#第一个为输出文字
				output = int(words[0])
				#其他为输入文字
				for i in range(1,len(words)-1):
					inputs.append(int(words[i]))

				int_dag[output] = inputs


def get_name(literal):
	var = abs(literal)
	op = ''
	if literal < 0:
		op = '-'
	else:
		op = ''
	  
	if var == f:
		return op + 'r1'
	elif var <= num_original_var:
		return op + 'e' + str(var)
	else:
		return op + 'g' + str(var)

#未写完
def get_dag():

	for key in int_dag:
		output = key
		inputs = int_dag[key]
		op = ''

		if len(inputs) == 1:#变量相等
			op = '='
			literal_1 = key
			literal_2 = inputs[0]
			name_1 = get_name(literal_1)
			name_2 = get_name(literal_2)
			 
			temp_inputs = []

			temp_inputs.append(op)
			temp_inputs.append(name_2)
			dag[name_1] = temp_inputs
		else:
			if output < 0:# 或门
				op = '|'
				name_1 = get_name(abs(output))
				temp_inputs = []
				temp_inputs.append(op)
				for i in inputs:
					temp_name = get_name(i)
					temp_inputs.append(temp_name)
				dag[name_1] = temp_inputs
			else:# 与门
				op = '&'
				name_1 = get_name(abs(output))
				temp_inputs = []
				temp_inputs.append(op)
				for i in inputs:
					temp_name = get_name(0 - i)
					temp_inputs.append(temp_name)
				dag[name_1] = temp_inputs


def output_dag(output_file_path):

	f = file(output_file_path, 'w+')
	for output in dag:
		line = ''
		if output is 'r1':
			line = 'r1 /* root */ := ( '
		else:
			line = output + ' := ( '
		inputs = dag[output]
	   
		for literal in inputs:
			if literal is inputs[0]:
				op = literal
				if op == '=':
					line = line + inputs[1]+' );'
					break
			elif literal is inputs[-1]:
				line = line+' '+op+' '+literal+' );'
			elif literal is inputs[1]:
				line = line + literal
			else:
				line = line+' '+op+' '+literal
		f.writelines(line + '\n')
	f.close()

def clean():
	global num_original_var
	num_original_var = 0
	global num_all_var
	num_all_var = 0
	global dag
	dag = {}
	global int_dag
	int_dag = {}
	global f
	f = 0

def cnf2dag(file_path, file_name):
	clean()
	input_file_path = file_path + file_name + '/' + file_name + '-p.cnf'
	output_file_path = file_path + file_name + '/' + file_name + '.dag'

	get_int_dag(input_file_path)
	get_dag()
	output_dag(output_file_path)
 
# if __name__=="__main__":

# 	get_int_dag(sys.argv[1])

# 	get_dag()
# 	output_dag()