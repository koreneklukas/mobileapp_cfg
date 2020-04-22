from django.shortcuts import render
import pandas as pd
from django.http import HttpResponseRedirect
from .work import CreateJSON
from .build_cfg_package import save_request_content, make_request, check_version
import json

partner_logo_paths = ['ageo.png', 'akvazoo.png', 'aquacitypoprad.png', 'aquapalace.png', 'aquapalacehotel.png',
                    'booking.png', 'broadway.png', 'businessmedia.png' ,'corial.png', 'damejidlo.png', 'datart.png',
                    'eddies.png', 'eiffeloptic.png', 'english.png', 'euronics.png', 'eurooil.png', 'exasoft.png',
                    'fidlovacka.png', 'florea.png', 'fokusoptic.png', 'fotolab_cz.png', 'gpay.png', 'gpay_t.png',
                    'hadivadlo.png', 'homecredit.png', 'husky.png', 'hybernia.png', 'hzh.png', 'chata.png', 'jafra.png',
                    'kalich.png', 'knihcentrum_cz.png', 'laguna.png', 'leifheit.png', 'lekarna.png',
                    'luxusnipradlo.png', 'mastercard.png', 'mountfield.png', 'optikdodomu.png', 'orea.png',
                    'padowetz.png', 'panskydvurtelc.png', 'petrklic.png', 'pivnilaznebernard.png', 'prodeti.png',
                    'pytlounhotely.png', 'quickshoes.png', 'rental_cars.png', 'rohlenka.png', 'rozbaleno.png',
                    'scanquilt.png', 'seneca.png', 'senzoor.png', 'supersoused_cz.png', 'tamsin_cz.png', 'tempish.png',
                    'tesco.png', 'ticketstream.png', 'topgal.png', 'toptime.png', 'vesnican.png', 'vinodoc.png',
                    'wellness_kurim.png', 'wellnessmajestic.png', 'ypsilonka.png', 'zdravykos.png']

partner_offer_paths = ['adventnikalendar.png', 'ageo_1.png', 'ageo_2.png', 'akvazoo.png', 'aquacitypoprad.png',
                       'aquapalacehotel.png', 'booking.png', 'broadway.png', 'businessmedia.png', 'corial.png',
                       'damejidlo.png', 'datart.png', 'eddies.png', 'english.png', 'eurooil.png', 'exasoft.png',
                       'fidlovacka.png', 'florea.png', 'fokusoptic.png', 'fotolab_cz.png', 'gpay.png', 'gpay_t.png',
                       'husky_cz.png', 'hybernia.png', 'hzh.png', 'chata.png', 'jafra_cz.png', 'kalich.png',
                       'knihcentrum_cz.png', 'laguna.png', 'leifheit.png', 'lekarna.png', 'luxusnipradlo.png',
                       'mastercard.png', 'mountfield.png', 'optikdodomu.png', 'orea.png', 'padowetz.png',
                       'panskydvurtelc.png', 'petrklic.png', 'pivnilaznebernard.png', 'pytlounhotely.png',
                       'quickshoes.png', 'rental_cars.png', 'scanquilt_1.png', 'senzoor.png', 'supersoused_cz.png',
                       'tamsin_cz.png', 'tempish.png', 'tesco.png', 'ticketstream_1.png', 'topgal.png', 'toptime.png',
                       'vesnican.png', 'vinodoc.png', 'wellnessmajestic.png', 'zdravykos.png']

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
                      {'result': 'You are inserting XLSX file for different country or another file. Check the file.',
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
            print(version)
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
            else:
                return render(request, page,
                              {'result': 'The version in XLSX file is not matching with the entered version.',
                               'version': versionx, 'country': countryx})
        except:
            return render(request, page,
                          {'result': 'XSLX file is not in expected format or may be malformed.',
                           'version': versionx, 'country': countryx})
    return render(request, 'loyalty_step_2.html',
                  {'version': versionx, 'country': countryx})


def step_two(request, page, versionx, countryx):
    logo_file = request.FILES.getlist('filelogo')
    if logo_file:
        for logo in logo_file:
            if '.png' or '.jpg' in logo:
                save_request_content(logo.read(), 'OfferSettings\\{}\\logo\\{}'.format(versionx, logo), countryx)
            else:
                return render(request, page,
                            {'result': 'Inserted logo file is not in JPG/PNG format.',
                            'version': versionx, 'country': countryx})
    offer_file = request.FILES.getlist('fileoffer')
    if offer_file:
        for offer in offer_file:
            if '.png' or '.jpg' in offer:
                save_request_content(offer.read(), 'OfferSettings\\{}\\offer\\{}'.format(versionx, offer), countryx)
            else:
                return render(request, page,
                            {'result': 'Inserted offer file is not in JPG/PNG format.',
                            'version': versionx, 'country': countryx})
    poo, version = check_version(versionx, countryx)
    logo_path_get = 'OfferSettings\\{}\\logo\\'.format(version)
    logo_path_save = 'OfferSettings\\{}\\logo\\'.format(versionx)
    offer_path_get = 'OfferSettings\\{}\\offer\\'.format(version)
    offer_path_save = 'OfferSettings\\{}\\offer\\'.format(versionx)
    for l in partner_logo_paths:
        req = make_request(countryx, logo_path_get + l)
        save_request_content(req, logo_path_save + l, countryx)
    for o in partner_offer_paths:
        req = make_request(countryx, offer_path_get + o)
        save_request_content(req, offer_path_save + o, countryx)
    return HttpResponseRedirect("/success")

