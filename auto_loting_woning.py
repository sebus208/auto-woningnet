import config
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GECKO_PATH = "/home/kove/code/python/drivers/geckodriver"
CHROME_PATH = "/home/kove/code/python/drivers/chromedriver"

WONINGNET = "https://www.woningnetregioamsterdam.nl/Inloggen"


def no_cookies():
    b.find_element_by_css_selector(".cc-cookie-decline").click()
    time.sleep(3)
    b.get(WONINGNET)


def login():
    b.find_element_by_id("gebruikersnaam").send_keys(config.username)
    b.find_element_by_id("password").send_keys(config.password)
    b.find_element_by_id("loginButton").click()


b = webdriver.Chrome(CHROME_PATH)
b.get(WONINGNET)
b.maximize_window()

no_cookies()
login()
