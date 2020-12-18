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

def name(module_name):
	if '-' in module_name:
		pattern = '\-'
 		regex = re.compile(pattern, flags = re.IGNORECASE)
  		module_name = regex.split(module_name)[1]
	return module_name