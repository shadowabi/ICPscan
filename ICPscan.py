#!/usr/bin/env python
# -*- coding:utf-8 -*-
#author:Sh4d0w_小白

from requests import get
from sys import argv
from queue import Queue
from threading import Thread
from time import sleep
from re import *
from bs4 import BeautifulSoup
from lxml import etree
import os
from fake_useragent import UserAgent

q = Queue()

icp = "https://icplishi.com/"
flag = 0
ua = UserAgent()
result = []
number = ""

header = {
	"User-Agent":ua.random
}

def Usage():
	print("[Usage]python ICPscan.py (domian/ICP)")

def Output():
	global result
	while(q.empty() == False):
		url = "https://" + q.get()
		try:
			r = get(url = url, headers = header, allow_redirects = True, timeout = 1)
			print(url)
			result.append(url.strip())
		except:
			pass
		finally:
			q.task_done()
		


def GetDomain(html):
	soup = BeautifulSoup(html,'lxml')
	text = str(soup.find_all("td"))
	text = etree.HTML(text = text)
	text = text.xpath('string(.)')
	text = compile(r'.*\w+\.\w+').findall(text)
	for i in text:
		q.put(i)

def Check(url):
	global flag,number
	if(search(r"(http|https)\:\/\/", url)):
		url = (sub(r"(http|https)\:\/\/", "", url)) #去除协议头
		flag = 1 #域名
		return(url)
	elif(search(r".ICP.\d{6}.-\d{1,}",url)):
		url = sub("-\d{1,}", "", url) #提取主备案号
		number = url
		flag = 2 #备案号
		return(url)
	elif(search(r".*\w+\.\w+",url)):
		flag = 1 #域名
		return(url)
	elif(search(r".ICP.\d{6}.",url)):
		number = url
		flag = 2 #备案号
		return(url)
	else:
		print("请检查输入是否正确")
		os._exit(0)


def GetICP(html):
	global number
	soup = BeautifulSoup(html,'lxml')
	text = str(soup.select("body > div > div.container > div > div.module.mod-panel > div.bd > div:nth-child(2) > div.c-bd"))
	text = etree.HTML(text = text)
	text = text.xpath('string(.)')
	text = search(r".ICP.\d{6}.", text) #获取备案号
	if (text != None):
		number = text.group()
		return text.group()
	else:
		print("请检查输入是否正确")
		os._exit(0)

def Scan(url):
	global icp
	url = Check(url)
	url = icp + url
	try:
		r = get(url = url,headers = header, allow_redirects = True, timeout = 5)
		r.raise_for_status()
	except:
		print("连接超时，请稍后重试")
		os._exit(0)
	finally:
		if(flag == 1):
			icp2 = GetICP(r.text)
			url = icp + icp2
			try:
				r = get(url = url,headers = header, allow_redirects = True, timeout = 5)
				r.raise_for_status()
			except:
				print("连接超时，请稍后重试")
				os._exit(0)
			sleep(0.1)
			GetDomain(r.text)
		elif(flag == 2):
			GetDomain(r.text)


if __name__=="__main__":
	try:
		scan = argv[1]
		print("开始进行扫描：")
		Scan(scan)
		for i in range(20):
			t = Thread(target = Output)
			sleep(0.1)
			t.start()
			t.join()
		print("扫描结束！正在写入到文件result.txt中")
		with open("result.txt","w+",encoding='utf8') as f:
			f.write(number + "\n")
			for i in result:
				f.write(i + "\n")
		print("写入完毕，程序退出")
	except:
		Usage()
