import os
import sys


from selenium.webdriver.common.by import By
from selenium import webdriver

import time
import pytz
from datetime import timedelta, datetime
from dateutil.parser import parse

import smtplib 
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import json
start = time.time()

CLIENT_SECRET_FILE='client_secret.json'
API_NAME='calendar'
API_VERSION='v3'
SCOPES=['https://www.googleapis.com/auth/calendar.readonly']

USERNAME_INPUT="ContentSection_txtIdentificador"
PASSWORD_INPUT="ContentSection_txtContrasena"
LOGIN_BUTTON="ContentSection_lnkEntrar"
DATE_INPUT="ContentSection_uVentaEntradas_uVentaEntradasDetalle_txtValidezInicial"
ADD_BUTTON="ContentSection_uVentaEntradas_uVentaEntradasDetalle_btnContinuar"
CONFIRM_BUTTON="ContentSection_lnkConfirmar"
CONTINUE_BUTTON="ContentSection_aSeguirComprando"
DELETE_BUTTON="ContentSection_aEliminar"

RESERVA_SCREENSHOT="reserva.png"
FALLO1_SCREENSHOT="fallo_hora_1.png"
FALLO2_SCREENSHOT="fallo_hora_2.png"
FALLO_FINAL="fallo_final.png"

username='efdfewsf'
password='WEWEFwf'

mail_username='asfsfs@gmail.com'
mail_password='asgfsfgsf'

weekDays = ("Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

BROWSER_OPTION="Firefox"
test=False

def close_driver():
    if os.path.exists(RESERVA_SCREENSHOT):
        os.remove(RESERVA_SCREENSHOT)

    if os.path.exists(FALLO1_SCREENSHOT):
        os.remove(FALLO1_SCREENSHOT)

    if os.path.exists(FALLO2_SCREENSHOT):
        os.remove(FALLO2_SCREENSHOT)
    
    if os.path.exists(FALLO_FINAL):
        os.remove(FALLO_FINAL)
    
    browser.close()
    print("RUNTIME: ", time.time() - start)
    

def test_call():
    time.sleep(2)
    #print(browser.page_source)
    try:
        browser.save_screenshot("screenshot.png")
        close_driver()
    except NameError:
        print("RUNTIME: ", time.time() - start)
        pass
    sys.exit(0)

def sendMail(username, password, body, attachments):

    print("Enviando correo de confirmación.....")
    msg = MIMEMultipart()
    msg['Subject'] = "Reserva de cita para gimnasio del día " + gym_day
    msg['From'] = username
    msg['To'] = "sswdefsdew@gmail.com"

    text=MIMEText(body)
    msg.attach(text)

    for attachement in attachments:
        img_data = open(attachement, 'rb').read()
        image=MIMEImage(img_data, name=os.path.basename(attachement))
        msg.attach(image)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(username, password)
    s.sendmail(username, msg['To'], msg.as_string())
    s.quit()

    print("Correo enviado.\n")


#-----------------------------------------------------------------
#------------------ GOOGLE CALENDAR-------------------------------
#-----------------------------------------------------------------

"""Shows basic usage of the Google Calendar API.
Prints the start and name of the next 10 events on the user's calendar.
"""
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE, SCOPES)
        flow.authorization_url(access_type='offline')
        creds = flow.run_local_server(port=0)
        # TODO enviar mensaje si falla
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


service = build(API_NAME, API_VERSION, credentials=creds)

weekDays = ("Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo")
gym_datetime=datetime.now(pytz.timezone('Europe/Madrid')) + timedelta(days=2)
gym_day=gym_datetime.strftime("%d/%m/%Y")
gym_weekDay=weekDays[gym_datetime.weekday()]

timeMin=gym_datetime.replace(hour=0, minute=0, second=0, microsecond=0).astimezone().isoformat()
timeMax=(gym_datetime + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).astimezone().isoformat()

print("Hora de ejecución: ", (gym_datetime - timedelta(days=2)))
events = service.events().list(calendarId='jaimitoacostag@gmail.com', showDeleted=False, singleEvents=True, timeMin=timeMin, timeMax=timeMax).execute() # pylint: disable=maybe-no-member

gym_calendar_time = None
for event in events['items']:
    if ('summary' in event and 
    (event['summary'] == "Gimnasio" 
    or event['summary'] == 'Gym' 
    or event['summary'] == 'gimnasio')):
        gym_calendar_time=parse(event['start']['dateTime'])
        print ("Cita encontrada en el calendario\n\t- Titulo: " + event['summary'] + ", inicio: " 
        + event['start']['dateTime'] + ", fin: " + event['end']['dateTime'] + "\n")
        break

if gym_calendar_time == None:
    body_text=("Se ha intentado reservar para el "  + gym_weekDay +  " día " + gym_day + ", pero es día de descanso.\n")
    print(body_text)
    sendMail(mail_username, mail_password, body_text, [])
    sys.exit()
else:
    hour=gym_calendar_time.hour
    if gym_calendar_time.weekday() < 5:
        json_path="workday.json"
    else:
        json_path="weekend.json"

    with open(json_path) as json_file:
        dates = json.load(json_file)
        CITA_1="'" + dates["%02d" % hour] +"'"
        CITA_2="'" + dates["%02d" % (hour+1)] + "'"


#-----------------------------------------------------------------
#-------------------------------BOT-------------------------------
#-----------------------------------------------------------------

print(".........................................................\n"
        + "Reservando para el " + gym_weekDay +  " día " + gym_day + " las citas: \n"
        + "\t - " + CITA_1 + "\n"
        + "\t - " + CITA_2 + "\n" 
        + ".........................................................\n")

# Initiate the browser
#browser  = Chrome(ChromeDriverManager().install())

if BROWSER_OPTION=="Firefox":
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Firefox(options = options)
    browser.set_page_load_timeout(30)
else:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome(options = options)
    browser.set_page_load_timeout(30)

# Get Login Page
browser.get("https://deportes.pozuelodealarcon.org/reservas/Login")

# Login
browser.find_element_by_id(USERNAME_INPUT).send_keys(username)
browser.find_element_by_id(PASSWORD_INPUT).send_keys(password)
browser.find_element_by_id(LOGIN_BUTTON).click()


# FIRST HOUR
browser.get("https://deportes.pozuelodealarcon.org/reservas/Modulos/VentaServicios/EntradasBonosAbonos/VentaEntradas")

browser.find_element(By.XPATH, "//*[text()=" + CITA_1 + "]").click()
time.sleep(0.5)
browser.find_element_by_id(DATE_INPUT).clear()
browser.find_element_by_id(DATE_INPUT).send_keys(gym_day)
browser.find_element_by_id(ADD_BUTTON).click()
time.sleep(0.5)
try:
    browser.find_element_by_id(CONTINUE_BUTTON).click()
    print("Añadida primera hora.")
except:
    print("Error al añadir al carrito la cita " + CITA_1)
    browser.save_screenshot(FALLO1_SCREENSHOT)
    pass


# SECOND HOUR
browser.get("https://deportes.pozuelodealarcon.org/reservas/Modulos/VentaServicios/EntradasBonosAbonos/VentaEntradas")

browser.find_element(By.XPATH, "//*[text()=" + CITA_2 + "]").click()
time.sleep(0.5)
browser.find_element_by_id(DATE_INPUT).clear()
browser.find_element_by_id(DATE_INPUT).send_keys(gym_day)
browser.find_element_by_id(ADD_BUTTON).click()
time.sleep(0.5)

# SUBMIT
try:
    browser.find_element_by_id(CONTINUE_BUTTON).click()
    print("Añadida segunda hora.")
except:
    print("Error al añadir al carrito la cita "+ CITA_2)
    browser.save_screenshot(FALLO2_SCREENSHOT)
    pass

browser.get("https://deportes.pozuelodealarcon.org/reservas/CarritoConfirmar")
time.sleep(0.5)

if (not test):
    try:
        browser.find_element_by_id(CONFIRM_BUTTON).click()
        browser.save_screenshot(RESERVA_SCREENSHOT)  
        print("Se ha finalizado la compra.\n")
    except:
        print("Error al finalizar la compra.")
        browser.save_screenshot(FALLO_FINAL) 
        pass        

attachments = []
body_text=""
if os.path.exists(RESERVA_SCREENSHOT):
    body_text=("Se han reservado las siguientes citas para el día " + gym_day + ":\n"
                + "\t- " + CITA_1 + "\n"
                + "\t- " + CITA_2 + "\n")
    attachments.append(RESERVA_SCREENSHOT)
elif os.path.exists(FALLO1_SCREENSHOT) or os.path.exists(FALLO2_SCREENSHOT) or os.path.exists(FALLO_FINAL):
    body_text="Ha habido un ERROR al reservar las siguientes citas para el día " + gym_day + ":\n"
    if os.path.exists(FALLO1_SCREENSHOT):
        body_text= body_text +  "\t- " + CITA_1 + "\n"
        attachments.append(FALLO1_SCREENSHOT)
    if os.path.exists(FALLO2_SCREENSHOT):
        body_text= body_text +  "\t- " + CITA_2 + "\n"
        attachments.append(FALLO2_SCREENSHOT)
    if os.path.exists(FALLO_FINAL):
        body_text= body_text + "\n\n----- " + "ERROR AL FINALIZAR LA COMPRA" + " -----\n"
        attachments.append(FALLO_FINAL)

sendMail(mail_username, mail_password, body_text, attachments)

# Close driver
close_driver()