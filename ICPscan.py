#!/usr/bin/env python
# -*- coding:utf-8 -*-
#author:Sh4d0w_小白

from requests import get,Session
from sys import argv
from queue import Queue
from threading import Thread
from time import sleep
from re import *
from bs4 import BeautifulSoup
from lxml import etree
import os
# from fake_useragent import UserAgent
# from requests.adapters import HTTPAdapter
from tqdm import tqdm
import urllib3

q = Queue()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
icp = "https://icplishi.com/"
flag = 0
# ua = UserAgent()
result = []
number = ""
tasknumber = 0

header = {
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4621.0 Safari/537.36"
}

# session = Session()
# session.mount('http://', HTTPAdapter(max_retries=2))
# session.mount('https://', HTTPAdapter(max_retries=2))

def Usage():
	print("[Usage]python ICPscan.py (domian/ICP)")

def Output():
	global result,pbar
	while(q.empty() == False):
		url = "http://" + q.get()
		try:
			r = get(url = url, headers = header, allow_redirects = True, timeout = 1, verify = False)
			r.raise_for_status()
			# print(url)
			result.append(url.strip())
		except:
			pass
		finally:
			q.task_done()
			pbar.update(1)
		


def GetDomain(html):
	global tasknumber
	soup = BeautifulSoup(html,'lxml')
	text = str(soup.find_all("td"))
	text = etree.HTML(text = text)
	text = text.xpath('string(.)')
	text = compile(r'.*\w+\.\w+').findall(text)
	for i in text:
		q.put(i)
		tasknumber += 1

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
		r = get(url = url,headers = header, allow_redirects = True, timeout = 2, verify = False)
		r.raise_for_status()
	except:
		print("连接超时，请稍后重试")
		os._exit(0)
	finally:
		if(flag == 1):
			icp2 = GetICP(r.text)
			url = icp + icp2
			try:
				r = get(url = url,headers = header, allow_redirects = True, timeout = 2, verify = False)
				r.raise_for_status()
			except:
				print("连接超时，请稍后重试")
				os._exit(0)
			sleep(0.1)
			GetDomain(r.text)
		elif(flag == 2):
			GetDomain(r.text)


if __name__=="__main__":
	global pbar
	try:
		scan = argv[1]
		print("开始进行扫描：")
		Scan(scan)
		pbar = tqdm(total = tasknumber)
		for i in range(20):
			t = Thread(target = Output)
			sleep(0.1)
			t.start()
			t.join(1)
		pbar.close()
		os.system("cls")
		print("扫描结束！输出结果")
		with open("result.txt","w+",encoding='utf8') as f:
			f.write(number + "\n")
			for i in result:
				print(i)
				f.write(i + "\n")
		print("已保存到result.txt文件中，按回车键退出程序！")
		input()
		os._exit(0)
	except:
		Usage()
