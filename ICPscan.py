#!/usr/bin/env python
# -*- coding:utf-8 -*-
#author:Sh4d0w_小白

import grequests
import argparse
from requests import get
from re import *
from bs4 import BeautifulSoup
from lxml import etree
from os import system, _exit
import platform
import urllib3
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ap = argparse.ArgumentParser()
ap.add_argument("-u", "--url", help = "Input IP/DOMAIN/URL/ICP", metavar = "www.baidu.com", required = True)
icp = "https://icplishi.com/"
flag = 0
ICPnumber = ""
rs = []
good = []

header = {
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4621.0 Safari/537.36"
}

def clear():
	if(platform.system() == "Windows"):
		system("cls")
	else:
		system("clear")	

def GetDomain(html):
	soup = BeautifulSoup(html,'lxml')
	text = str(soup.select("body > div > div.container > div > div.module.mod-panel > div > div:nth-child(2) > div.c-bd > div"))
	text = etree.HTML(text = text)
	text = text.xpath('string(.)')
	text = compile(r'.*\w+\.\w+').findall(text)
	for i in text:
		try:
			rs.append(grequests.get("http://" + i, headers = header, timeout = 3, verify = False)) #扫描
		except:
			pass
	for i in grequests.map(rs):
		if i.status_code == 200:
			good.append(i.url)


def GetICP(html):
	global ICPnumber
	soup = BeautifulSoup(html,'lxml')
	text = str(soup.select("body > div > div.container > div > div.module.mod-panel > div.bd > div:nth-child(2) > div.c-bd"))
	text = etree.HTML(text = text)
	text = text.xpath('string(.)')
	text = search(r".ICP.\d{6,}.", text) #获取备案号
	if (text != None):
		ICPnumber = text.group()

def Check(url):
	global flag,ICPnumber
	if(search(r"(http|https)\:\/\/", url)): # 当输入URL时提取出域名
	    url = sub(r"(http|https)\:\/\/", "", url)
	    if (search(r"(\/|\\).*", url)):
	        url = sub(r"(\/|\\).*", "", url)
	
	if match(r"^([a-zA-Z0-9]([a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,11}$", url): #匹配域名
		flag = 1 #域名
		return url

	if(search(r".ICP.\d{6,}.",url)):
		if(search(r".ICP.\d{6,}.-\d{1,}",url)):
			url = sub("-\d{1,}", "", url) #提取主备案号
		ICPnumber = url
		flag = 2 #备案号
		return url

def Scan(url):
	try:
		url = Check(url)
		if flag == 0:
			raise Exception("请检查输入是否正确")
		url = icp + url
		r = get(url = url, headers = header, timeout = 2, verify = False)
		if(flag == 1):
			GetICP(r.text) #通过域名提取ICP号
			if ICPnumber == "":
				raise Exception("该域名无法提取备案号")
		url = icp + ICPnumber
		r = get(url = url, headers = header, timeout = 2, verify = False)
		GetDomain(r.text)
	except Exception as err:
		print(err)


if __name__=="__main__":
	args = ap.parse_args()
	url = args.url
	print("开始进行扫描：")
	Scan(url)
	clear()
	print("扫描结束！")
	with open("result.txt","w+",encoding='utf8') as f:
		f.write(ICPnumber + "\n")
		print(ICPnumber)
		for i in good:
			print(i)
			f.write(i + "\n")
	print("已保存到result.txt文件中，按回车键退出程序！")
	input()
	_exit(0)
