# Copyright (c) 2026 Yao0124
# SPDX-License-Identifier: MIT
import requests
import json
import argparse
from cyberatlas_finder import Finder
import os
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pyfiglet
import sys

BLUE = '\033[94m'
RESET = '\033[0m'
logo = pyfiglet.figlet_format("SUBScanx", font="standard")
print(f"{BLUE}{logo}{RESET}")
print('by Yao0124')
ua = UserAgent()
HEAD = ua.random
parser = argparse.ArgumentParser(
    description='被动子域名收集工具'
)
parser.add_argument('-u','--URL',dest='URL',help='目标域名')
parser.add_argument('-c','--CRT',dest='CRT',action='store_true',help='使用CRT数据源')
parser.add_argument('-hk','--HACK',dest='HACK',action='store_true',help='使用HACK数据源')
parser.add_argument('-f','--FIND',dest='FIND',action='store_true',help='使用FINDER数据源')
parser.add_argument('-ce','--CENT',dest='CENT',action='store_true',help='使用CENTER数据源')
parser.add_argument('-r','--RAPID',dest='RAPID',action='store_true',help='使用RAPID数据源')
parser.add_argument('-a','--all',dest='all',action='store_true',help='调用全部数据源')

def main():
    args = parser.parse_args()
    URL = args.URL
    CRT = args.CRT
    HACK = args.HACK
    FIND = args.FIND
    CENT = args.CENT
    RAPID = args.RAPID
    all = args.all
    
    if args.URL is None:
        parser.print_help()
        exit(0)

    mainset = set()
    start_all(args,mainset)

def start_all(args,mainset):
    if args.CRT:
        print(f'调用CRT数据源:{args.URL}')
        mainset.update(crt(HEAD,args.URL,args.CRT))
    elif args.HACK:
        print(f'调用hack数据源:{args.URL}')
        mainset.update(hackert(HEAD,args.URL,args.HACK))
    elif args.FIND:
        print(f'调用FINDER数据源:{args.URL}')
        mainset.update(finderstart(args.URL,args.FIND))
    elif args.CENT:
        print(f'调用CENTER数据源:{args.URL}')
        mainset.update(center(HEAD,args.URL,args.CENT))
    elif args.RAPID:
        print(f'调用RAPID数据源：{args.URL}') 
        mainset.update(rapid(HEAD,args.URL,args.RAPID))
    elif args.all:
        print(f'使用全部数据源:{args.URL}')
        mainset.update(crt(HEAD,args.URL,args.CRT))
        mainset.update(hackert(HEAD,args.URL,args.HACK))
        mainset.update(finderstart(args.URL,args.FIND))
        mainset.update(center(HEAD,args.URL,args.CENT))
        mainset.update(rapid(HEAD,args.URL,args.RAPID))
    
    if mainset:
        print(f'一共扫描到{len(mainset)}个子域名')
        for sub in mainset:
            print(sub)
    else:
        print('没有找到任何子域名')

def crt(HEAD,URL,CRT):
    crturl = "https://crt.sh/"
    params = {
    'q': f'%.{URL}',
    'output': 'json'
}
    headers = {
    'User-Agent': HEAD
}
    crtset = set()
    try:
        crt_res = requests.get(crturl,headers=headers,params=params,timeout=10)
        CRT_List = crt_res.json()
    except Exception:
        return set()
    for crt_ext in CRT_List:
        crtset.add(crt_ext['name_value'])
    return crtset

def hackert(HEAD,URL,HACK):
    hackerturl = f'https://api.hackertarget.com/hostsearch/?q={URL}'
    headers = {
    'User-Agent': HEAD
    }
    try:
        hackert_res = requests.get(hackerturl,headers=headers,timeout=10)
        if "exceeded" in hackert_res.text or "error" in hackert_res.text.lower():
                return set()
        return set(hackert_res.text.replace(',',' ').split())
    except Exception:
        return set()
    
def finderstart(URL,FIND):
    try:
        finder = Finder()
        return {str(host).strip() for host in finder.iter_domains(f'*.{URL}')}
    except Exception:
        return set()

def center(HEAD,URL,CENT):
    centerurl = f'https://api.subdomain.center/?domain={URL}'
    headers = {
        'User-Agent': HEAD
    }
    censet = set()
    try:
        center_res = requests.get(centerurl,headers=headers,timeout=10)
        CENTER_List = center_res.json()
        for cen in CENTER_List:
            if cen:
                setparse = cen.split('\n')
                for setp in setparse:
                    censet.add(setp.strip())
    except Exception:
            return set()
    return censet

def rapid(HEAD,URL,RAPID):
    rapidurl = f'https://rapiddns.io/subdomain/{URL}?full=1' 
    headers = {
        'User-Agent': HEAD
    }
    rapset = set()
    try:
        rapid_res = requests.get(rapidurl,headers=headers,timeout=10)
        soup = BeautifulSoup(rapid_res.text,'html.parser')
        rap = soup.find_all('tr')
        rapdata = []
        for rapid1 in rap:
            tdtag = rapid1.find('td')
            if tdtag:
                rapset.add(tdtag.text.strip())
    except Exception:
            return set()
    return rapset

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('再见')
        sys.exit(0)
