# -*- coding = utf-8 -*-
# @Time : 2021/10/18 15:12
# @Author : LIUYU
# @File : TestFindNextPageButton.py
# @Software : PyCharm

import random
import re
import time
from openpyxl import Workbook
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


s = Service("D:\Software\webdrivers\chromedriver.exe")
driver = webdriver.Chrome(service=s)
driver.get("https://www.amazon.com/")
driver.implicitly_wait(10)
driver.find_element(By.XPATH,"//input[@id='twotabsearchtextbox']").send_keys("huawei")
driver.find_element(By.ID,"nav-search-submit-button").click()
driver.find_element(By.XPATH,"//span[text()='HUAWEI']").click()
ele_framesCount = driver.find_element(By.XPATH,
                    "//h1[contains(@class,'s-desktop-toolbar')]//div[contains(@class,'a-spacing-top-small')]/span[1]")
framesCount = int(re.findall(r'共(.*?)条',ele_framesCount.text)[0])
print('一共有 {} 条商品信息.'.format(framesCount))

myNames = []
myScores = []
myEvaluations = []
infoMissNames = []

overFlag = False

for i in range(100):
    if overFlag:
        break

    driver.implicitly_wait(3)
    text_nowFramesCount = driver.find_element(By.XPATH,"//h1[contains(@class,'s-desktop-toolbar')]//div[contains(@class,'a-spacing-top-small')]/span[1]").text
    nowFramesCount = int(re.findall(r'共(.*?)条', text_nowFramesCount)[0])
    print(nowFramesCount)
    if nowFramesCount > framesCount:
        framesCount = nowFramesCount
        print("Warning[1]: 出现反爬措施: 动态修改商品数量为 {}.".format(framesCount))
    if nowFramesCount < framesCount-3:
        print("warning[2]: 出现反爬限制: 爬取频率过高，界面短时间内无法刷新.")
        print("method: 休息 1min，降低频率后继续爬取")
        driver.back()
        driver.execute_script('window.scrollTo({top: 5200, behavior: "smooth" });')
        time.sleep(60)
        driver.find_element(By.XPATH, "//li[@class = 'a-selected']/following-sibling::li[1]").click()
        continue

    # 滚动暂停，骗过浏览器 Ajax 加载以及检测
    driver.execute_script('window.scrollTo({top: 2600, behavior: "smooth" });')
    time.sleep(1+random.random()*3)
    driver.execute_script('window.scrollTo({top: 5200, behavior: "smooth" });')
    time.sleep(1+random.random()*6)

    frames = driver.find_elements(By.XPATH,"//div[contains(@class,'s-include-content-margin')]//div[@class='a-section']")
    for frame in frames:
        ele_huaweiName = frame.find_element(By.XPATH, ".//span[@class='a-size-medium a-color-base a-text-normal']")
        huaweiName = ele_huaweiName.text
        myNames.append(huaweiName)

        try:
            # ele_averageScore = frame.find_element(By.XPATH, ".//a/i/span")
            ele_averageScore = frame.find_element(By.XPATH, ".//span[contains(@aria-label,'颗')]")
            averageScore = ele_averageScore.get_attribute('aria-label')[0:3]
            myScores.append(averageScore)
        except:
            # print("No Score or No number:", huaweiName)
            infoMissNames.append([huaweiName])
            continue

        try:
            ele_evaluationNumber = frame.find_element(By.XPATH,".//div[contains(@class,'a-spacing-top-micro')]//span/a/span")
            evaluationNumber = ele_evaluationNumber.text.replace(',', '')
            myEvaluations.append(evaluationNumber)
        except:
            # print("No Score or No number:", huaweiName)
            infoMissNames.append([huaweiName])
            continue

    try:
        wait = WebDriverWait(driver, 5)
        nextPageButton = wait.until(EC.presence_of_element_located((By.XPATH,"//a[(contains(text(),'下一页')  or contains(text(),'ext'))]")))

        if nextPageButton.is_enabled():
            try:
                nextPageButton.click()
            except ElementClickInterceptedException:
                driver.execute_script('window.scrollTo({top: 5200, behavior: "smooth" });')
                time.sleep(random.random())
                driver.execute_script('window.scrollTo({top: 6000, behavior: "smooth" });')
                time.sleep(random.random())
                driver.execute_script('window.scrollTo({top: 5200, behavior: "smooth" });')
                nextPageButton.click()
                # 鼠标悬停
                move_to_ads = driver.find_element(By.XPATH,"//div[@data-a-carousel-options]")
                ActionChains(driver).move_to_element(move_to_ads).perform()
                move_to_frame = driver.find_element(By.XPATH,"//div[@id = 'search']")
                ActionChains(driver).move_to_element(move_to_frame).perform()
        else:
            print("warning[3]: '下一页'无法点击，可能是 Chrome 浏览器版本的问题.")
            break

    except TimeoutException:
            # 中途突变的网页
            print("Tips: 找不到可以点击的下一页了... 正在测试是否为反爬...或许我们要成功了！")
            driver.implicitly_wait(3)
            text_nowFramesCount = driver.find_element(By.XPATH,"//h1[contains(@class,'s-desktop-toolbar')]//div[contains(@class,'a-spacing-top-small')]/span[1]").text
            nowFramesCount = int(re.findall(r'共(.*?)条', text_nowFramesCount)[0])
            if nowFramesCount < framesCount - 3:
                print("Warning[2]: 出现反爬限制: 爬取频率过高，界面短时间内无法刷新.")
                print("     - Variation: 商品总量被 robot 修改为 {}".format(nowFramesCount))
                print("Method: 休息 1min，降低频率后继续爬取")
                driver.back()
                driver.execute_script('window.scrollTo({top: 5200, behavior: "smooth" });')
                time.sleep(60)
                driver.find_element(By.XPATH, "//li[@class = 'a-selected']/following-sibling::li[1]").click()
                continue
            else:
                # print("爬取完毕")
                print("Success!!!")
                overFlag = True
                break

finalList = zip(myNames,myScores,myEvaluations)

wb = Workbook()

wb['Sheet'].title = 'Amazon HUAWEI data'
sh1 = wb.active
sh1.append(['产品名称','评分','评分人数'])
for data in list(finalList):
    sh1.append(data)

sh2 = wb.create_sheet()
sh2.title = 'Info_missing HUAWEI data'
sh2.append(['产品名称'])
for name in infoMissNames:
    sh2.append(name)

wb.save("FinalRecords.xlsx")