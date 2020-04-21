import requests, json, smtplib
from email.message import EmailMessage
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def send_email(res, content):
    msg = EmailMessage()
    msg.set_content(content)
    gmail_user = 'hcpingmonster@gmail.com'
    gmail_password = 'aphomer123'
    msg['From'] = 'HC PING'
    msg['To'] = ['Jakub.Legindi@homecredit.cz']
    msg['Subject'] = res
    server = smtplib.SMTP('smtp.gmail.com:25')
    server.starttls()
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.send_message(msg)
    print('email sent')
    server.close()

def open_json():
    with open('Master2.json', 'r') as master_json:
        loaded_json = json.loads(master_json.read())
    return loaded_json

def get_banners_json(system):
    loaded_json = open_json()
    if system == 'android':
        banners = loaded_json["MasterJSON"]["bannersSettings"][0]["banners"]
    elif system == 'ios':
        banners = loaded_json["MasterJSON"]["bannersSettings_iOS"][0]["banners"]
    else:
        return "Not Found"
    return banners

def check_image(system):
    banners = get_banners_json(system)
    for banner in banners:
        path = banner["filePath"]
        try:
            open(path)
            #print('alles gute')
        except:
            print('Tady bude odeslan alert')
            #send_email('Obrazek nenalezen', 'Obrazek zadany v configu, nebyl nalezeny v dane slozce.')

def check_urls(system):
    banners = get_banners_json(system)
    for banner in banners:
        path = banner["bannerUrl"]
        if banner["bannerType"] == 'browser':
            try:
                req = requests.get(path, verify=False)
                verify_status = req.status_code
            except:
                print('Tady bude odeslan alert')

systems = ['ios', 'android']
if __name__ == '__main__':
    for s in systems:
        check_image(s)
        check_urls(s)