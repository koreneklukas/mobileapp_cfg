from django.shortcuts import render
import pandas as pd
from django.http import HttpResponseRedirect
from .work import CreateJSON
from .build_cfg_package import save_request_content, make_request, get_version, change_decision
import json, csv


def step_one(request, page, versionx, countryx):
    pre_excel = request.FILES
    excel = pre_excel["file"]
    if '.xlsx' not in str(excel):
        return render(request, page,
                      {'result': 'Vložený soubor není ve formátu XLSX.',
                       'version': versionx, 'country': countryx})
    df = pd.ExcelFile(excel)
    sheets = []
    country_now = countryx
    if country_now.lower() not in ",".join(df.sheet_names).lower():
        return render(request, page,
                      {'result': 'Snažíš se vložit XLSX soubor pro jinou zemi, nebo jiný soubor.',
                       'version': versionx, 'country': countryx})
    for sheet in df.sheet_names:
        if sheet == 'SK - Premia' or sheet == 'CZ - Premia' or sheet == 'SK - Premium' or sheet == 'CZ - Premium':
            print(sheet)
            sheets.append(sheet)
    for sheetx in sheets:
        dfx = pd.read_excel(excel, sheet_name=sheetx)
        try:
            version = str(dfx['Unnamed: 8'][1])
            if version == versionx:
                json_tree = CreateJSON(excel).create_json_file()
                for key in json_tree.keys():
                    if 'cz' in key.lower() and 'premia' in key.lower():
                        filename = 'offersPremia.json'
                        dest = 'CZ'
                    elif 'cz' in key.lower() and 'premium' in key.lower():
                        filename = 'offersPremium.json'
                        dest = 'CZ'
                    elif 'premia' in key.lower() and 'sk' in key.lower():
                        filename = 'offersPremia.json'
                        dest = 'SK'
                    elif 'premium' in key.lower() and 'sk' in key.lower():
                        filename = 'offersPremium.json'
                        dest = 'SK'
                    elif 'json' in key.lower() or 'mapování' in key.lower():
                        continue
                    else:
                        return render(request, page,
                                      {'result': 'XSLX soubor není v očekávaném formátu, nebo je poškozen.', 'version':
                                          versionx, 'country': countryx})
                    try:
                        path = CreateJSON(excel).create_dirs(str(version), dest)
                    except:
                        continue
                    with open('{}/{}'.format(path, filename), 'w+',
                              encoding='utf-8') as outfile:
                        json.dump(json_tree[key], outfile, indent=4, ensure_ascii=False)
                    with open('{}/{}'.format(path, filename), 'rt',
                              encoding='utf-8') as file_to_fix:
                        f = file_to_fix.read()
                    with open('{}/{}'.format(path, filename), 'wt',
                              encoding='utf-8') as file_to_save:
                        fs = f.replace('\\\\\\', '\\')
                        file_to_save.write(fs)
            else:
                return render(request, page,
                              {'result': 'Verze v XLSX souboru neodpovídá zadané verzi v aplikaci.',
                               'version': versionx, 'country': countryx})
        except:
            return render(request, page,
                          {'result': 'XSLX soubor není v očekávaném formátu, nebo je poškozen.',
                           'version': versionx, 'country': countryx})
    return render(request, 'loyalty_step_2.html',
                  {'version': versionx, 'country': countryx})


def step_two(request, page, versionx, countryx):
    logo_file = request.FILES.getlist('filelogo')
    offer_file = request.FILES.getlist('fileoffer')
    version = get_version(countryx, 'unpersonifiedOfferSettings', versionx)[0]
    logo_path_get = 'OfferSettings/{}/logo/'.format(version)
    logo_path_save = 'OfferSettings/{}/logo/'.format(versionx)
    offer_path_get = 'OfferSettings/{}/offer/'.format(version)
    offer_path_save = 'OfferSettings/{}/offer/'.format(versionx)

    with open('{}_partner_logo.csv'.format(countryx.upper()), 'r', encoding='utf-8') as logo_paths:
        reader_logo = csv.reader(logo_paths)
        for partner_logo_paths in reader_logo:
            for l in partner_logo_paths:
                req = make_request(countryx, logo_path_get + l)
                save_request_content(req, logo_path_save + l, countryx, versionx)

    with open('{}_partner_offer.csv'.format(countryx.upper()), 'r', encoding='utf-8') as offer_paths:
        reader_offer = csv.reader(offer_paths)
        for partner_offer_paths in reader_offer:
            for o in partner_offer_paths:
                req = make_request(countryx, offer_path_get + o)
                save_request_content(req, offer_path_save + o, countryx, versionx)

    if offer_file:
        for offer in offer_file:
            offer_path = 'OfferSettings/{}/offer/{}'.format(versionx, offer)
            if '.png' or '.jpg' in offer:
                save_request_content(offer.read(), offer_path, countryx, versionx)
                with open('{}_partner_offer.csv'.format(countryx.upper()), 'a', encoding='utf-8') as fd:
                    fd.write('\n{}'.format(offer))
            else:
                return render(request, page,
                            {'result': 'Vložený offer file není ve formátu .jpg nebo .png.',
                            'version': versionx, 'country': countryx})

    if logo_file:
        for logo in logo_file:
            logo_path = 'OfferSettings/{}/logo/{}'.format(versionx, logo)
            if '.png' or '.jpg' in logo:
                save_request_content(logo.read(), logo_path, countryx, versionx)
                with open('{}_partner_logo.csv'.format(countryx.upper()), 'a', encoding='utf-8') as fd:
                    fd.write('\n{}'.format(logo))
            else:
                return render(request, page,
                            {'result': 'Vložený logo file není ve formátu .jpg nebo .png.',
                            'version': versionx, 'country': countryx})

    change_decision(countryx, 'loyalty', versionx)
    return HttpResponseRedirect("/success")
