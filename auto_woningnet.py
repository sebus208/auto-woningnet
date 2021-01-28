import config
import re
import os
import time
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
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
## TODO Improve logging by making messages more specific
## TODO Prevent crashing by wrapping clicks in try except blocks
# def find_element_click(
#     self, by, expression, search_window=None, timeout=32, ignore_exception=None, poll_frequency=4
# ):
#     if ignore_exception is None:
#         ignore_exception = []

#     ignore_exception.append(NoSuchElementException)
#     ignore_exception.append(ElementClickInterceptedException)
#     ignore_exception.append(ElementNotInteractableException)
#     if search_window is None:
#         search_window = self.driver

#     end_time = time.time() + timeout
#     while True:
#         try:
#             web_element = search_window.find_element(by=by, value=expression)
#             web_element.click()
#             return True
#         except tuple(ignore_exception) as e:
#             self.logger.debug(str(e))
#             if time.time() > end_time:
#                 self.logger.exception(e)
#                 time.sleep(poll_frequency)
#                 break
#         except Exception as e:
#             raise
#     return False


def jsClick(el):
    b.execute_script("arguments[0].click();", el)


def noCookies():
    b.find_element_by_css_selector(".cc-cookie-decline").click()
    time.sleep(2)
    b.find_element_by_css_selector(".growl-notification .close").click()


def login():
    b.get(LOGIN)
    b.find_element_by_id("gebruikersnaam").send_keys(config.username)
    b.find_element_by_id("password").send_keys(config.password)
    b.find_element_by_id("loginButton").click()


def reagerenGelukt(b):
    reageren_button = b.find_element_by_css_selector(".interactionColumn .primary.button")
    reageren_button_innerText = reageren_button.get_attribute("innerText")
    reageren_button_text = re.sub("[^a-z^A-Z]+", "", reageren_button_innerText)

    if reageren_button_text == "Reageren":
        jsClick(reageren_button)
        time.sleep(3)

        try:
            tab = b.find_element_by_css_selector(".tabMenuContainer dd:not(.active)")
            jsClick(tab)
        except:
            return False

        checkbox = b.find_element_by_css_selector("#akkoordContainer label")
        jsClick(checkbox)

        submit = b.find_element_by_id("formsubmitbutton")
        jsClick(submit)

        time.sleep(5)

        return True
    else:
        return False


def reageerOp(url, aantal_reacties):
    b.get(url)
    time.sleep(5)
    unit_links = b.find_elements_by_css_selector(".unitContainer > a.unitLink:first-of-type")
    aantal_reacties_over = MAX_REACTIES - aantal_reacties

    i = 0
    for unit in unit_links:
        if i < aantal_reacties_over:
            link = unit.get_attribute("href")
            b.execute_script("window.open('" + link + "', '_blank');")
            b.switch_to.window(b.window_handles[1])
            time.sleep(3)

            if reagerenGelukt(b):
                i += 1
                b.close()
                logging.info("Reacted to woning: " + link)
            else:
                logging.info("Already reacted to woning: " + link)
                b.close()

            b.switch_to.window(b.window_handles[0])


def lotingBeschikbaar():
    b.get(LOTING)
    time.sleep(8)
    active_tab = b.find_element_by_css_selector(".tabMenu li.active a")
    active_tab_text = active_tab.get_attribute("innerText")
    active_tab_title = re.sub("[^a-z^A-Z]+", "", active_tab_text)

    if active_tab_title == "Loting":
        return True
    else:
        logging.info("No Loting woningen available")
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
        logging.info("No woningen on " + url + " left to react on.")
        return 0
    return visible_notifications


logging.basicConfig(filename=config.log_path, level=logging.INFO)
# logging.debug("This message should go to the log file")
# logging.info("So should this")
# logging.warning("And this, too")
# logging.error("And non-ASCII stuff, too")

opts = Options()
opts.headless = True
b = webdriver.Firefox(options=opts, service_log_path="/dev/null")
# b.maximize_window()

b.get(WONINGNET)
noCookies()
login()

aantal_reguliere_reacties = aantalReacties(REGULIER)
if aantal_reguliere_reacties < MAX_REACTIES:
    reageerOp(REGULIER, aantal_reguliere_reacties)
else:
    logging.info("No reguliere woning reacties left")

if lotingBeschikbaar():
    aantal_loting_reacties = aantalReacties(LOTING)
    if aantal_loting_reacties < MAX_REACTIES:
        reageerOp(LOTING, aantal_loting_reacties)
    else:
        logging.info("No loting woning reacties left")

b.quit()

msg = MIMEMultipart()
msg["Subject"] = "Log"
msg["From"] = "Auto WoningNet <" + config.send_email + ">"
msg["To"] = config.receive_email
msg.attach(MIMEText(open(config.log_path).read()))

try:
    smtpObj = smtplib.SMTP_SSL(config.outgoing_smtp)
    smtpObj.connect(config.outgoing_smtp, 465)
    smtpObj.ehlo()
    smtpObj.login(config.send_email, config.email_pass)
    smtpObj.sendmail(config.send_email, config.receive_email, msg.as_string())
    smtpObj.quit()
except Exception as e:
    print(e)
else:
    if os.path.exists(config.log_path):
        os.remove(config.log_path)
