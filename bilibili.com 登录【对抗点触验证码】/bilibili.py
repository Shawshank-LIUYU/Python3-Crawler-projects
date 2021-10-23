# -*- coding = utf-8 -*-
# @Time : 2021/10/21 9:48
# @Author : LIUYU
# @File : bilibili_1.2.2.py
# @Software : PyCharm
import random
import time
from datetime import datetime
from io import BytesIO
import pathlib

from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chaojiyingforpy3 import Chaojiying

USERNAME = 'xxxxxxxxx'
PASSWORD = 'xxxxxxxxx'
# 超级鹰用户名、密码、软件 ID、验证码类型
CHAOJIYING_USERNAME = 'xxxxxxxxxx'
CHAOJIYING_PASSWORD = 'xxxxxxxxxx'
CHAOJIYING_SOFT_ID = 893590
CHAOJIYING_KIND = 9004

class CrackTouClick:
    def __init__(self):
        self.url = 'https://passport.bilibili.com/login?from_spm_id=333.1007.top_bar.login'
        s = Service("D:\Software\webdrivers\chromedriver.exe")
        options = Options()
        options.add_argument('--start-maximized')
        self.browser = webdriver.Chrome(service=s,options=options)
        self.wait = WebDriverWait(self.browser, 5)
        self.username = USERNAME
        self.password = PASSWORD
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)

    def __del__(self):
        self.browser.close()

    def open(self):
        """
        打开网页输入用户名密码
        :return: None
        """
        self.browser.get(self.url)
        # self.browser.execute_script('document.body.style.zoom="0.667"')
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        username.send_keys(self.username)
        password.send_keys(self.password)

    def get_touclick_button(self):
        """
        获取初始验证按钮
        :return: 登录按钮对象
        """
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@class,"btn btn-login")]')))
        return button

    def get_geetest_commit(self):
        """
        获取验证码界面的 '确定'
        :return: 确定按钮对象
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip')))
        return button

    def get_geetest_head(self):
        """
        获取验证码区域头部:含验证码
        :return: 验证码对象
        """
        element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_head')))
        return element

    def get_touclick_element(self):
        """
        获取验证图片对象
        :return: 图片对象
        """
        element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_item_img')))
        return element

    def get_geetest_refresh(self):
        """
        获取刷新按钮对象
        :return: 刷新按钮对象
        """
        element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_refresh')))
        return element

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        head_element = self.get_geetest_head()
        touclick_element = self.get_touclick_element()

        head_location = head_element.location
        touclick_location = touclick_element.location
        size = touclick_element.size

        top = head_location['y']
        bottom = touclick_location['y'] + size['height']
        left = touclick_location['x']
        right = touclick_location['x'] + size['width']

        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_touclick_image(self, name='0_bilibiliTouClick'):
        """
        获取验证码图片
        :return: 图片对象
        """
        now = datetime.now() # current date and time
        now_time = now.strftime("%H_%M_%S")

        top, bottom, left, right = self.get_position()
        screenshot = self.get_screenshot()

        p = pathlib.Path(r'D:\SOP\Crawler\Demos\VerificationCodedemo\HandleBilibiliTouclick\screenshot & captcha')
        screenshot_name = '0_screenshot__{}.png'.format(now_time)
        screenshot_pathlib_object = p/screenshot_name
        screenshot.save(screenshot_pathlib_object)

        captcha = screenshot.crop((left, top, right, bottom))
        captcha_name = name+'__{}.png'.format(now_time)
        captcha_pathlib_object = p/captcha_name
        captcha.save(captcha_pathlib_object)
        return captcha


    def distinguish_locations(self, captcha_result):
        """
        解析识别结果
        :param captcha_result: 识别结果
        :return: 转化后的结果
        """
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def touch_click_words(self, locations):
        """
        点击验证图片
        :param locations: 点击位置
        :return: None
        """
        for location in locations:
            print(location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_touclick_element(), location[0],location[1]).click().perform()
            time.sleep(random.random())

    def touch_click_verify(self):
        """
        点击验证按钮
        :return: None
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip')))
        button.click()

    def login(self):
        """
        登录
        :return: None
        """
        submit = self.get_geetest_commit()
        self.browser.execute_script("arguments[0].click();", submit)


    def crack(self):
        """
        破解入口
        :return: None
        """
        self.open()
        touclick_button = self.get_touclick_button()
        self.browser.execute_script("arguments[0].click();", touclick_button)

        refresh_time = 0
        while 1:

            image = self.get_touclick_image()
            bytes_array = BytesIO()
            image.save(bytes_array, format='PNG')
            result = self.chaojiying.post_pic(bytes_array.getvalue(),CHAOJIYING_KIND)
            locations = self.distinguish_locations(result)
            self.touch_click_words(locations)
            self.login()

            try:
                success = self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'geetest_panel_success_title'), '通过验证'))
                print(success)
                self.login()
                break

            except TimeoutException:
                self.chaojiying.report_error(result['pic_id'])
                if refresh_time <= 2:
                    refresh_time += 1
                    continue
                else:
                    time.sleep(random.random()*3)
                    self.crack()

        print("Success!!!")
        time.sleep(10)
        self.browser.close()

if __name__ == '__main__':
    crack = CrackTouClick()
    crack.crack()



