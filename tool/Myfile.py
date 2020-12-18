#coding=utf-8
import os
import shutil
import time

def mkdir(path):

	# 去除首位空格
	path=path.strip()
	# 去除尾部 \ 符号
	path=path.rstrip("\\")
 
	# 判断路径是否存在
	# 存在     True
	# 不存在   False
	isExists=os.path.exists(path)
 
	# 判断结果
	if not isExists:
		# 如果不存在则创建目录
		# 创建目录操作函数
		os.makedirs(path) 
 
		print path+' 创建成功'
		return True
	else:
		# 如果目录存在则不创建，并提示目录已存在
		print path+' 目录已存在'
		return False

def move_file(srcfile, dstfile):

	shutil.copyfile(srcfile, dstfile)

def create_benchmark(from_path, to_path):

	pathDir = os.listdir(from_path)
	file_names=[]
	for allDir in pathDir:
		file_name = allDir.split('.')[0]
		file_names.append(file_name)

	file_names = list(set(file_names))

	for item in file_names:
		mkdir(to_path + item)
		time.sleep(0.1)
		srcfile = from_path + item + '.dag'
		dstfile = to_path + item + '/' + item + '.dag'
		shutil.copyfile(srcfile,dstfile)

def clean_file(file_path, ignore_file):
	pathDir = os.listdir(file_path)
	for allDir in pathDir:
		delete_file_path = file_path + allDir
 		if not (allDir in ignore_file):
			os.remove(delete_file_path)

# if __name__=="__main__":
	
# 	pathDir =  os.listdir('./qg6')
# 	file_names=[]
# 	for allDir in pathDir:
# 		file_name = allDir.split('.')[0]
# 		file_names.append(file_name)

# 		file_names = list(set(file_names))

# 	for item in file_names:
# 		mkdir('./qg6/' + item)
# 		time.sleep(1)
# 		srcfile = './qg6/' + item + '.dag'
# 		dstfile = './qg6/' + item + '/' + item + '.dag'
# 		shutil.copyfile(srcfile,dstfile)
