#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-02-16 完成
# @Author  : AntsPi.com
# @File    : get_college.py
#  获取：http://www.zjgksj.com/ 网站上的大学数据

import requests
import re
import time
import random

import xlsxwriter


def create_college_urls():
    """返回：大学学校列表"""
    college_urls = []
    college_base_url = 'http://www.zjgksj.com/college/'
    # 283页，共2829条数据
    for i in range(1, 284):
        college_urls.append(college_base_url+str(i))
    return college_urls


def get_html_text(url):
    """返回对应文本"""
    try:
        html = requests.get(url, timeout=30)
        html.raise_for_status()
        html.encoding = 'utf-8'  # html.apparent_encoding
        return html.text
    except Exception as err:
        print(err)
        return ""


def get_college_record(college_text):
    """返回：解析的大学数据"""
    # cid 对应cid,网页链接编号
    # cname 对应name,院校名称
    # crankno 对应rankno,院校排名
    # cprovince 对应province,所在地区
    # ctype 对应type,院校类型
    # cpublic 院校举办
    college_text = college_text.strip().replace(' ', '')
    collegeTypes = '综合,工科,艺术,医药,政法,农业,民族,财经,师范,军事,林业,体育,语言'.split(',')
    cid = get_content("cid=\'(.*?)\'", college_text)
    cname = get_content("name=\'(.*?)\'", college_text)
    crankno = get_content("rankno=\'(.*?)\'", college_text)
    if crankno == '':
        crankno = '无'
    cprovince = get_content("province=\'(.*?)\'", college_text)
    # 问题：此处出错，ctype 值达到14，list index out of range
    # 后来发现有2所学校：山东青年政治学院 、 江苏省省级机关管理干部学院
    # 院校类型为：undefined，所以导致转换出错
    ctype = ''
    ctype = get_content("type=collegeType\[(.*?)\]", college_text)
    if ctype == '14':
        ctype = '未定义'
    else:
        ctype = collegeTypes[int(ctype)-1]
    cpublic = get_content('type\+"</td><td>(.*)</td></tr>"', college_text)

    # cid 对应cid,网页链接编号
    # cname 对应name,院校名称
    # crankno 对应rankno,院校排名
    # cprovince 对应province,所在地区
    # ctype 对应type,院校类型
    # cpublic 院校举办
    college_record = [cid, cname, crankno, cprovince, ctype, cpublic]
    return college_record


# 获取内容
def get_content(regex, college_text):
    search_item = re.search(regex, college_text, re.I)
    if search_item:
        ret_content = search_item.group(1)
    else:
        ret_content = ''
    return ret_content


def save_xlsx(book_name, sheet_name, lines_in):
    workbook = xlsxwriter.Workbook(book_name)
    worksheet = workbook.add_worksheet(sheet_name)
    line_data = lines_in.split('\n')
    row = 0
    col = 0
    for line in line_data:
        if line:
            item = line.split('~!~')
            if len(item) == 6:
                for i in range(6):
                    worksheet.write(row, col+i, item[i])
                row += 1
    workbook.close()

if __name__ == '__main__':
    pattern = re.compile('function initTable\(\) {(.*?)}', re.M | re.S)
    college_webs = create_college_urls()
    c_line = ''
    for college_web in college_webs:
        #print(college_web)
        html_text = get_html_text(college_web)
        if html_text != '':
            # 列表转换成字符串
            find_text = ''.join(pattern.findall(html_text)).strip('\n').strip()
            find_lines = find_text.split( '$(".table-mtop").append(tr);')
            #print(find_lines)
            # 大学链接
            cid_base_url = 'http://www.zjgksj.com/college/queryIntroduction/'
            for out_line in find_lines:
                if out_line:
                    #print(out_line)
                    #print(get_college_record(out_line))
                    cinfo = get_college_record(out_line)
                    cinfo[0] = cid_base_url+cinfo[0]
                    c_line += '~!~'.join(cinfo) + '\n'
        print(c_line)
        time.sleep(random.uniform(0.05, 0.3))  # 随机暂停
    with open('college1.txt', 'w', encoding='utf-8', errors='ignore') as fw:
        fw.write(c_line)
    save_xlsx(u'大学列表.xlsx', u'大学名录', c_line)