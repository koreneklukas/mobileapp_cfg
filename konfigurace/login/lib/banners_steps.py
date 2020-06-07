from django.shortcuts import render
from django.http import HttpResponseRedirect
import json
from .build_cfg_package import change_decision, json_content, get_version, save_request_content, make_request


url_list = []


def get_banners_json(request, page, dest, version):
    with open('tmp/{}/{}/{}'.format(dest, version, 'Master2.json'), "rt", encoding='UTF-8') as f:
        mjson = json.loads(f.read())

    android_banners = str(mjson["MasterJSON"]["bannersSettings"][0]["banners"])\
        .replace('\'', '\"').replace('{}'.format(mjson["MasterJSON"]["bannersSettings"][0]["version"]), version)

    ios_banners = str(mjson["MasterJSON"]["bannersSettings_iOS"][0]["banners"]).replace('\'', '\"')\
        .replace('{}'.format(mjson["MasterJSON"]["bannersSettings_iOS"][0]["version"]), version)

    return render(request, page, {'version': version, 'country': dest, 'ios_banners': ios_banners,
                                  'android_banners': android_banners})


def save_banners_android(request, dest, version):
    mjson = json_content(dest, version)
    dumped = json.dumps(mjson, indent=4,ensure_ascii=False,sort_keys=False)
    new_jsonicek = json.loads(request.POST["brand"])
    get_new_banners_url(url_list, new_jsonicek)

    mjson["MasterJSON"]["bannersSettings"][0]["banners"].clear()

    for i in new_jsonicek:
        mjson["MasterJSON"]["bannersSettings"][0]["banners"].append(i)
    substitute_banners = dumped.split("bannersSettings\"")[1].split("banners\": ")[1].split("\"bannersSettings_iOS")[0]
    new_banners = json.dumps(mjson, indent=4,ensure_ascii=False,sort_keys=False).split("bannersSettings\"")[1].split("banners\": ")[1].split("\"bannersSettings_iOS")[0]

    with open('tmp/{}/{}/{}'.format(dest, version, 'Master2.json'), "rt", encoding='UTF-8') as f:
        ready = f.read()\
            .replace("bannersSettings\"{}{}{}".format(dumped.split("bannersSettings\"")[1].split("banners\": ")[0],
                                                      "banners\": ", substitute_banners),
                     "bannersSettings\"{}{}{}".format(dumped.split("bannersSettings\"")[1].split("banners\": ")[0],
                                                      "banners\": ", new_banners))

    with open('tmp/{}/{}/{}'.format(dest, version, 'Master2.json'), "wt", encoding='UTF-8') as fw:
        fw.write(ready)


    change_decision(dest, 'banners_android', version)


def save_banners_ios(request, dest, version):
    mjson = json_content(dest, version)
    dumped = json.dumps(mjson, indent=4,ensure_ascii=False,sort_keys=False)
    new_jsonicek = json.loads(request.POST["brand"])
    mjson["MasterJSON"]["bannersSettings_iOS"][0]["banners"].clear()

    for i in new_jsonicek:
        mjson["MasterJSON"]["bannersSettings_iOS"][0]["banners"].append(i)
    substitute_banners = dumped.split("bannersSettings_iOS\"")[1].split("banners\": ")[1].split("\"cardSettings")[0]
    new_banners = json.dumps(mjson, indent=4,ensure_ascii=False,sort_keys=False).split("bannersSettings_iOS\"")[1].split("banners\": ")[1].split("\"cardSettings")[0]

    with open('tmp/{}/{}/{}'.format(dest, version, 'Master2.json'), "rt", encoding='UTF-8') as f:
        subst = "bannersSettings_iOS\"{}{}{}".format(dumped.split("bannersSettings_iOS\"")[1].split("banners\": ")[0],
                                                      "banners\": ", substitute_banners)
        newb = "bannersSettings_iOS\"{}{}{}".format(dumped.split("bannersSettings_iOS\"")[1].split("banners\": ")[0],
                                                      "banners\": ", new_banners)
        ready = f.read().replace(subst, newb)

    with open('tmp/{}/{}/{}'.format(dest, version, 'Master2.json'), "wt", encoding='UTF-8') as fw:
        fw.write(ready)

    change_decision(dest, 'banners_ios', version)


def get_new_banners_url(json_banners):
    for url in json_banners:
        one = url["filePath"]
        store_banners(one)


def store_banners(urls=None):
    if urls:
        url_list.append(urls)
    else:
        return url_list


def upload_function(request, dest, versionx):
    page = 'upload_banner_images.html'
    banner_file = request.FILES.getlist('filebanner')
    banner_urls = store_banners()

    version = get_version(dest, 'bannersSettings', versionx)[0]
    banner_path_get = 'BannerSettings/{}/'.format(version)
    banner_path_save = 'BannerSettings/{}/'.format(versionx)

    for u in banner_urls:
        fname = u.split('/')[2]
        req = make_request(dest, banner_path_get + fname)
        save_request_content(req, banner_path_save + fname, dest, versionx)

    if banner_file:
        for banner in banner_file:
            banner_path = 'BannerSettings/{}/{}'.format(versionx, banner)
            if '.png' or '.jpg' in banner:
                save_request_content(banner.read(), banner_path, dest, versionx)
            else:
                return render(request, page,
                            {'result': 'Vložený banner file není ve formátu .jpg nebo .png.',
                            'version': versionx, 'country': dest})

    return HttpResponseRedirect("/success")
