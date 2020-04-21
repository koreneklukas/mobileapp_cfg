from django.shortcuts import render
import pandas as pd
from django.http import HttpResponseRedirect
from .work import CreateJSON
from .build_cfg_package import save_request_content
import json


def step_one(request, page, versionx, countryx):
    pre_excel = request.FILES
    excel = pre_excel["file"]
    if '.xlsx' not in str(excel):
        return render(request, page,
                      {'result': 'Inserted file is not in .XLSX format',
                       'version': versionx, 'country': countryx})
    df = pd.ExcelFile(excel)
    sheets = []
    country_now = countryx
    if country_now.lower() not in ",".join(df.sheet_names).lower():
        return render(request, page,
                      {'result': 'You are inserting XLSX file for different country. Check the sheet names.',
                       'version': versionx, 'country': countryx})
    for sheet in df.sheet_names:
        if "4json" in sheet:
            pass
        elif "mapování" in sheet:
            pass
        else:
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
                    else:
                        return render(request, page,
                                      {'result': 'XSLX file is not in expected format or may be malformed.', 'version':
                                          versionx, 'country': countryx})
                    try:
                        path = CreateJSON(excel).create_dirs(str(version), dest)
                    except:
                        continue
                    with open('{}//{}'.format(path, filename), 'w+',
                              encoding='utf8') as outfile:
                        json.dump(json_tree[key], outfile, indent=4, ensure_ascii=False)
                return render(request, 'loyalty_step_2.html',
                              {'version': versionx, 'country': countryx})
            else:
                return HttpResponseRedirect("/try-again")
        except:
            return render(request, page,
                          {'result': 'XSLX file is not in expected format or may be malformed.',
                           'version': versionx, 'country': countryx})

def step_two(request, page, versionx, countryx):
    logo_file = request.FILES.getlist('filelogo')
    offer_file = request.FILES.getlist('fileoffer')
    for logo in logo_file:
        print('logo',logo)
        save_request_content(logo.read(), 'OfferSettings\\{}\\logo\\{}'.format(versionx, logo), countryx)
    for offer in offer_file:
        save_request_content(offer.read(), 'OfferSettings\\{}\\offer\\{}'.format(versionx, offer), countryx)
