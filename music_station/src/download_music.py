import urllib

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from fake_useragent import UserAgent

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

def download_music(mucic_name,href):
    cookie = {
        'Cookie': 'NMTID=00OflZJshHkYqJJbUA1idozEyWA1woAAAGT3cETxQ; _iuqxldmzr_=32; _ntes_nnid=0e2420e22efeb416cbd71eccf7607f12,1734592243313; _ntes_nuid=0e2420e22efeb416cbd71eccf7607f12; WEVNSM=1.0.0; WNMCID=oyufmy.1734592244398.01.0; ntes_utid=tid._.zkVw5Oy5ffxAVwFAAUaTX6Li9FMJ%252FuER._.0; sDeviceId=YD-8r%2F6fBd4eEFAUgEEEVbSSPRSfYNp2c6Z; WM_TID=KoNYbPhyZVFBEVBFURLDHqayoUMNjV4U; __snaker__id=rrtRtcrcjmM8dCmv; gdxidpyhxdE=tqLfTY5C8Y7f0R%2FpLG9AbdEq%2F7hMMe%2FSPXn7CWcz8gMwDfRKEwUmZeRXBJeXpUxzDa9UVjmLnVMwdyKc9kQTXHqzm2IlDI2QczRtfYgfR%5Cnk8Xk%2BPYhCTxSC6O1OOUse4WbycEJcjNtDUKiKa3OrwQAgIhvyQa0jqKLLZ4sNRsa7zzvq%3A1734593187212; __remember_me=true; MUSIC_U=00591B276E7057B242C9C775A6F377B3D4D0027112EC6C2410612353AFD10DCCB05FB787E354E314D2BAA0D0E9E6919973BAEFE64B380A55551A2CB362DD08B646E68EEA8CA52BB0C1B902B9B49507A8B9BC6D71D8E1A4B13BE083D88A1235B1A6ADF1AFAA8684239CCCE3A50972F03928CBC5ACA6116E0AD420ED0B2ED39845B29C3C11DD8B1539D5310DE1103EEFDC0FEB6DCD3A378047D8835D1DABA1B89D6C6A0383CB2B808868AEEA5D1EFFED94E222D0CA367418759301EE6799837E4B5C41FB0D216ED9E3793B4F4F3CD439661531F30505850D7263D39F6CF7AA023A82350E661E4D29A4D4A472BBC065460FED558AB4768BFF1C159D43EFA421C273930ABE3D83751BD0804C7D9327D72B88242F210EF0613EAF8B708E50C1601209D2A510577E8FF0C340E9A26DE34C33C75D749765DAE755C090B323CC1004B6F87D12B82A8268EBBCCD705785F403A86A1DBEBEA6B37A1A5213738549CC850A25C8C9458DDE39AF13B09FCAB607886E628A; __csrf=d3d0ebdb32cca3fe863352cba320842a; P_INFO=18338961259|1734592370|1|music|00&99|null&null&null#CN&null#10#0|&0|null|18338961259; ntes_kaola_ad=1; WM_NI=lByc2EiojlUthbegCJalOxjblPlegR4OUQfpmbLY7YtrMxaewwS4xcJm3bX1wfqVM%2BsmHz%2F2mp8pOsdq11m3GqCvKnI4PM8YkoJdHZ%2FBISTqQgcF7xWzSo6htUzQXPYMaHQ%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee99d279b7b29993f8808c868ea2d55a939f8e83c654b2eea1d9cd5e89e800b0e82af0fea7c3b92ab09eb784b14fabb1a68dd880acbeab88c242a3b48199e96ab090a486e65af8919bb2e57cafbe84bab653b8ae8399e46fb5a99dd5fb698ab3fd83db3bb5babfb7d021b1b3889bae3aafb0f891ce79a8afffd2f03985af8d97ca668beca0aebb53a9b18685cb52ed9e87b4d77b93b9ada7b67495a69d90b564b88bb6b2db5c9b93afa9d437e2a3; JSESSIONID-WYYY=CkWcZ0JoReFpbJbWFirSBw3Xvjo57zld5z5SxvPEuBaYkxY4Ud%5C89dHx1KWDYnznEa3q7%2BgIo4%5C7AlcONkKjxvZbtXk1Ei4OfGfAD8d5yMGzsBeR7u6SA8NnHuZSwskun%2FTokYGkR1Z4wq4qdKdv%5CSITlsJjivgjJ%5CaAXANw%5ChpTvlSc%3A1734881472583; playerid=91121616'
    }
    music_data = requests.get(href, UserAgent().random, cookies=cookie).content
    with open(f'../music/{music_name}.mp3', 'wb') as f:
        f.write(music_data)
    print("下载成功")


def setup():
    options = Options()
    # options.headless = True
    options.add_argument("--headless")#无头模式不开浏览器
    browser = webdriver.Firefox(service=Service('geckodriver.exe'), options=options)
    return browser

name = input("请输入你要听的音乐名：")

browser = setup()

fa_src = 'https://www.myfreemp3.com.cn/?page=audioPage&type=netease&name='
child_src = fa_src + name
# 打开指定的网址
browser.get(child_src)
browser.maximize_window()
# element1 = browser.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div[2]/div[3]/div/div[2]/div[1]/ol/li[1]/span[1]")
element1 = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".aplayer-list-light > span:nth-child(1)"))
    )

browser.execute_script("arguments[0].click();", element1)
# element2 = browser.find_element(by=By.XPATH,value="/html/body/div[3]/div/div/div[2]/div[3]/div[2]/a[1]")
element2 = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.input-group:nth-child(3) > div:nth-child(3) > a:nth-child(1)"))
    )
href = element2.get_attribute('href')

element3 = WebDriverWait(browser, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".aplayer-list-light > span:nth-child(4)"))
)
music_name = element3.text

print(href)
print(music_name)
# print(browser.page_source)
time.sleep(3)
browser.close()
browser.quit()

download_music(music_name, href)

