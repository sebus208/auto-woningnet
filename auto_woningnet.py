import config
import time
import subprocess as s
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN = "https://www.woningnetregioamsterdam.nl/Inloggen"
LOTING = "https://www.woningnetregioamsterdam.nl/Zoeken#model[Loting]~predef[2]"

## TODO Make headless


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


def reagerenSuccess(b):
    reageren_button = ".interactionColumn .primary.button"
    reageren_button = b.find_element_by_css_selector(reageren_button)
    reageren_button_text = reageren_button.get_attribute("innerText")

    if reageren_button_text == "Reageren":
        reageren_button.click()
        time.sleep(3)

        try:
            b.find_element_by_css_selector(".tabMenuContainer dd:not(.active)").click()
        except:
            return False

        b.find_element_by_css_selector("#akkoordContainer label").click()
        b.find_element_by_id("formsubmitbutton").click()
        time.sleep(5)

        return True
    else:
        return False


def reageer():
    time.sleep(5)
    unit_selector = ".searchContainer .content .unitContainer > a.unitLink:first-of-type"
    units = b.find_elements_by_css_selector(unit_selector)

    i = 0
    for unit in units:
        if i < 3:
            link = unit.get_attribute("href")
            b.execute_script("window.open('" + link + "', '_blank');")
            b.switch_to.window(b.window_handles[1])
            time.sleep(3)

            if reagerenSuccess(b):
                i += 1
                b.close()
                print("Reacted on woning: " + link)
            else:
                print("Not possible to react on woning: " + link)
                b.close()

            b.switch_to.window(b.window_handles[0])

    print("No woningen left to react on.")
    s.call(["notify-send", "foo", "bar"])
    b.quit()


b = webdriver.Firefox()
b.get(LOGIN)
b.maximize_window()

noCookies()
login()
b.get(LOTING)
reageer()
