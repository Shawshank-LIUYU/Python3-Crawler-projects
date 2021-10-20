# -*- coding = utf-8 -*-
# @Time : 2021/10/14 10:26
# @Author : LIUYU
# @File : douban_250_crawler.py
# @Software : PyCharm

import random
import time
import requests
from lxml import etree
import cchardet
import re
import csv
import traceback

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

def index_page(film_rank_number):
    index_url = 'https://movie.douban.com/top250?start={}&filter='.format(film_rank_number)
    index_res = requests.get(url=index_url, headers=headers)
    encoding = cchardet.detect(index_res.content)['encoding']
    index_html = index_res.content.decode(encoding)
    index_tree = etree.HTML(index_html)
    details_urls = index_tree.xpath("//li/div/div/a/@href")
    return details_urls

def parse_movie_page(url):
    # 1. get tree
    movie_page_res = requests.get(url=url, headers=headers)
    movie_page_encoding = cchardet.detect(movie_page_res.content)['encoding']
    movie_page_html = movie_page_res.content.decode(movie_page_encoding)
    movie_page_tree = etree.HTML(movie_page_html)

    # 2. Xpath
    # 排名
    ranking = movie_page_tree.xpath('//span[@class="top250-no"]/text()')
    # 电影名
    name = movie_page_tree.xpath('//h1/span[1]/text()')
    # 评分
    score = movie_page_tree.xpath('//strong/text()')
    # 评价人数
    review_number = movie_page_tree.xpath('//a/span[@property="v:votes"]/text()')
    # 类型
    list_type = movie_page_tree.xpath('//span[@property="v:genre"]/text()')
    types = ["/".join(list_type)]
    # 制片国家/地区
    nation = re.findall(r'<span class="pl">制片国家/地区:</span>(.*?)<br/?\\?>', movie_page_html)
    # 语言
    language = re.findall(r'<span class="pl">语言:</span>(.*?)<br/?\\?>', movie_page_html)
    # 时长
    time_span = movie_page_tree.xpath('//span[@property="v:runtime"]/text()')
    # 导演
    director_list = movie_page_tree.xpath("//div[@id='info']/span[1]/span[@class='attrs']/a/text()")
    director = ["".join(director_list)]
    # 编剧
    scripter_list = movie_page_tree.xpath("//div[@id='info']/span[2]/span[@class='attrs']/a/text()")
    scripter = ["".join(scripter_list)]
    # 主演
    performer_list = movie_page_tree.xpath("//div[@id='info']/span[3]//text()")
    if len(performer_list) >= 3:
        del performer_list[0]
        del performer_list[0]
        performer = ["".join(performer_list)]       # 纪录片是例外
    else:
        performer = performer_list
    # IMDb
    imdb_url = re.findall('<span class="pl">IMDb:</span>(.*?)<br>', movie_page_html)

    # return list
    return ranking + name + score + review_number + types + nation + language + time_span + director + scripter + performer + imdb_url

def save_rows_to_csv(rows):
    with open('douban.csv', 'a', encoding="utf-8-sig", newline='') as file:
        f_csv = csv.writer(file)
        f_csv.writerows(rows)


if __name__ == '__main__':
    # 1. 初始化rows列表
    csv_headers = ['排名','电影名','评分','评价人数','电影类型','国家','语言','时长','导演','编剧','主演','IMDb链接']
    csv_rows = [csv_headers]

    # 2. 循环: 爬取详情页网址 + 爬取详情页信息 + 拼接详情页信息 + 打印电影信息是否拼接成功
    try:
        for i in range(0,10):
            movie_urls = index_page(i*25)
            for movie_url in movie_urls:
                res = parse_movie_page(movie_url)
                csv_rows.append(res)
                print('第 {} 条电影信息存入内存！'.format(len(csv_rows)-1))
                time.sleep(random.random()*3)
    except:
        traceback.print_exc()

    # 3. 保存
    save_rows_to_csv(csv_rows)



