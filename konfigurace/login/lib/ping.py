from requests import get
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ping_hostnames():
    host_list = []
    ok = []
    nok = []
    for host in hostnames:
        try:
            response = get(host, verify=False)
            if response.status_code == 200:
                print(host, 'is up!')
                ok.append(host)
        except:
            host_list.append(host)
            print(host, 'is down!')
    if len(host_list) != 0:
        host_list_again = []
        for host_again in host_list:
            try:
                response = get(host_again, verify=False)
                if response.status_code == 200:
                    print(host_again, 'is now up!')
                    ok.append(host_again)
            except:
                host_list_again.append(host_again)
                print(host_again, 'is still down, returning NOK')
                nok.append(host_again)

        resp = {"host": []}
        if len(host_list_again) != 0:
            for n in nok:
                status = {n: {"status": "NOK"}}
                resp["host"].append(status)
            for o in ok:
                status = {o: {"status": "OK"}}
                resp["host"].append(status)
        else:
            for o in ok:
                status = {o: {"status": "OK"}}
                resp["host"].append(status)
        return json.dumps(resp, indent=4)


hostnames = [
    "https://partner.homecredit.cz",  # WC CZ
    "https://partner.homecredit.net",  # WC CZ (.net)
    "https://predajca.homecredit.sk/",  # WC SK
    "https://predajca.homecredit.netx/",  # WC SK (.net)
    "https://i-shop.homecredit.cz/ishop/entry.do",  # iShop CZ
    "https://i-shop.homecredit.net/ishop/entry.do",  # iShop CZ (.net)
    "https://i-shop.homecredit.sk/ishop/entry.do",  # iShop SK
    "https://i-shopsk.homecredit.net/ishop/entry.do",  # iShop SK (.net)
    "https://ecc.homecredit.cz",  # ECC CZ
    "https://eccsk.homecredit.net/",  # ECC SK
    "https://www.spravcefinanci.cz/prihlaseni",  # SF login CZ
    "https://www.spravcefinanci.cz/registrace",  # SF reg CZ
    "https://www.spravcafinancii.sk/prihlasenie",  # SF login SK
    "https://www.spravcafinancii.sk/registracia",  # SF reg SK
    # "https://zabezpeceni.spravcefinanci.cz/",                 #CIP FE CZ (zatim stopped)
    # "https://zabezpecenie.spravcafinancii.sk/",               #CIP FE SK (zatim stopped)
    "https://nasplatky.homecredit.cz/identifikace/krok-1",  # MyLoan CZ
    "https://nasplatky.homecredit.sk/identifikace/krok-1",  # MyLoan SK
    "https://prodejna.homecredit.cz/prihlaseni",  # ePos CZ
    "https://predajna.homecredit.sk/prihlasenie"  # ePos SK
]


if __name__ == '__main__':
    ping_hostnames()