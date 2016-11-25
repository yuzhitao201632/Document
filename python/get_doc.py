#!/bin/env python
#_*_coding:utf-8_*_
import sys
def get_doc(module):
	'''返回导入模块的帮助文档'''
	mod = __import__(module)
	print mod.__doc__

if __name__ == '__main__':
	get_doc(sys.argv[1])
