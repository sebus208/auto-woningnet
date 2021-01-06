import config
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GECKO_PATH = "/home/kove/code/python/drivers/geckodriver"
CHROME_PATH = "/home/kove/code/python/drivers/chromedriver"

LOGIN = "https://www.woningnetregioamsterdam.nl/Inloggen"
LOTING = "https://www.woningnetregioamsterdam.nl/Zoeken#model[Loting]~sort[kamersmax,DESC]"


def noCookies():
    b.find_element_by_css_selector(".cc-cookie-decline").click()
    time.sleep(2)
    b.find_element_by_css_selector(".growl-notification .close").click()
    time.sleep(2)
    b.get(LOGIN)
    time.sleep(2)


def login():
    b.find_element_by_id("gebruikersnaam").send_keys(config.username)
    b.find_element_by_id("password").send_keys(config.password)
    b.find_element_by_id("loginButton").click()


def reagerenLoting(b):
    reageren_button = ".interactionColumn .primary.button"
    b.find_element_by_css_selector(reageren_button).click()
    time.sleep(3)

    b.find_element_by_css_selector(".tabMenuContainer dd:not(.active)").click()
    b.find_element_by_css_selector("#akkoordContainer label").click()
    b.find_element_by_id("formsubmitbutton").click()
    time.sleep(5)


def openLotingen():
    b.get(LOTING)
    time.sleep(5)
    unit_selector = ".searchContainer .content .unitContainer > a.unitLink:first-of-type"
    units = b.find_elements_by_css_selector(unit_selector)

    for unit in units:
        link = unit.get_attribute("href")
        b.execute_script("window.open('" + link + "', '_blank');")
        b.switch_to.window(b.window_handles[1])
        time.sleep(3)
        reagerenLoting(b)
        b.close()


b = webdriver.Chrome(CHROME_PATH)
b.get(LOGIN)
b.maximize_window()

noCookies()
login()
openLotingen()
