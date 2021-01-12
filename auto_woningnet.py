import config
import re
import time
import subprocess as s
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WONINGNET = "https://www.woningnetregioamsterdam.nl/"
LOGIN = WONINGNET + "Inloggen"
LOTING = WONINGNET + "Zoeken#model[Loting]~predef[2]"
REGULIER = WONINGNET + "Zoeken#model[Regulier%20aanbod]~soort[Jongerenwoning]~predef[]"
MAX_REACTIES = 2

## TODO Make it run on the GreenGeeks server


def noCookies():
    b.find_element_by_css_selector(".cc-cookie-decline").click()
    time.sleep(2)
    b.find_element_by_css_selector(".growl-notification .close").click()


def login():
    b.get(LOGIN)
    b.find_element_by_id("gebruikersnaam").send_keys(config.username)
    b.find_element_by_id("password").send_keys(config.password)
    b.find_element_by_id("loginButton").click()


def notify(msg):
    s.call(["notify-send", "-u", "critical", "-t", "0", "Auto WoningNet", msg])


def reagerenGelukt(b):
    reageren_button = b.find_element_by_css_selector(".interactionColumn .primary.button")
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


def reageerOp(url, aantal_reacties):
    b.get(url)
    time.sleep(5)
    unit_links = b.find_elements_by_css_selector(".unitContainer > a.unitLink:first-of-type")

    i = 0
    for unit in unit_links:
        if i < aantal_reacties:
            link = unit.get_attribute("href")
            b.execute_script("window.open('" + link + "', '_blank');")
            b.switch_to.window(b.window_handles[1])
            time.sleep(3)

            if reagerenGelukt(b):
                i += 1
                b.close()
                notify("Reacted to woning: " + link)
            else:
                notify("Already reacted to woning: " + link)
                b.close()

            b.switch_to.window(b.window_handles[0])


def lotingBeschikbaar():
    b.get(LOTING)
    active_tab = b.find_element_by_css_selector(".tabMenu li.active a")
    active_tab_text = active_tab.get_attribute("innerText")
    active_tab_title = re.sub("\s\(\d+\)", "", active_tab_text)

    if active_tab_text == "Loting":
        return True
    else:
        notify("No Loting woningen available")
        return False


def aantalReacties(url):
    b.get(url)
    time.sleep(5)
    unit_links = b.find_elements_by_css_selector(".unitContainer > a.unitLink:first-of-type")

    visible_notifications = 0
    unit_notifications = b.find_elements_by_css_selector(".unitNotification")
    for n in unit_notifications:
        if n.is_displayed():
            visible_notifications += 1

    if len(unit_links) == visible_notifications:
        notify("No woningen left to react on.")
        return 0
    else:
        print(visible_notifications)
        return visible_notifications


opts = Options()
opts.headless = False
b = webdriver.Firefox(options=opts, service_log_path="/dev/null")

b.get(WONINGNET)
noCookies()
login()

aantal_reguliere_reacties = aantalReacties(REGULIER)
if aantal_reguliere_reacties < MAX_REACTIES:
    reageerOp(REGULIER, aantal_reguliere_reacties)
else:
    notify("No reguliere woning reacties left")

if lotingBeschikbaar():
    aantal_loting_reacties = aantalReacties(LOTING)
    if aantal_reguliere_reacties < MAX_REACTIES:
        reageerOp(LOTING, aantal_loting_reacties)
    else:
        notify("No loting woning reacties left")

b.quit()
