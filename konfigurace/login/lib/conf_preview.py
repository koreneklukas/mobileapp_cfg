#author: Marian.Jaworski
#version: 0

import json
from yattag import Doc
import os

script_dir = os.path.dirname(__file__)


def loadJson(path):
    """Load JSON from file

    Parameter:
        path - path to JSON file

    Returns:
        Loaded JSON
    """
    abs_json_path = os.path.join(script_dir, path)
    # read file
    with open(abs_json_path, 'rt', encoding='utf8') as myfile:
        data = myfile.read()
    # parse file
    return json.loads(data)


def previewBanners(doc, tag, text, bannerSettingsJsonName):
    for banner_setting in master_json_root[bannerSettingsJsonName]:
        for banner in banner_setting["banners"]:
            with tag("table", border="1", style="width:100%"):
                with tag("tr"):
                    with tag("th"):
                        text("brand")
                    with tag("td"):
                        text(banner["brand"])
                with tag("tr"):
                    with tag("th"):
                        text("URL")
                    with tag("td"):
                        with tag('a', href=banner["bannerUrl"]):
                            text(banner["bannerUrl"])
                with tag("tr"):
                    with tag("th"):
                        text("Image")
                    with tag("td"):
                        doc.stag('img', src=banner["filePath"], height="300")
                with tag("tr"):
                    with tag("th"):
                        text("Type")
                    with tag("td"):
                        text(banner["bannerType"])
            with tag("br"):
                text("  ")


def previewOffers(doc, tag, text):
    for offer_setting in master_json_root["unpersonifiedOfferSettings"]:
        loyaltyTypeOffers = offer_setting["loyaltyTypeOffers"]
        for loyalty_type_offer in loyaltyTypeOffers:
            offer_json = loadJson(loyalty_type_offer["filePath"])
        with tag("h2"):
            text(loyalty_type_offer["loyaltyType"])

        for offer in offer_json['OfferJSON']:
            with tag("table", border="1", style="width:100%"):
                with tag("tr"):
                    with tag("th"):
                        text("Partner")
                    with tag("td"):
                        text(offer['partner'])
                with tag("tr"):
                    with tag("th"):
                        text("Category")
                    with tag("td"):
                        text(offer['categoryName'])
                with tag("tr"):
                    with tag("th"):
                        text("Description")
                    with tag("td"):
                        text(offer['description'])
                with tag("tr"):
                    with tag("th"):
                        text("Description detail")
                    with tag("td"):
                        doc.asis(offer['descriptionDetail'])
                with tag("tr"):
                    with tag("th"):
                        text("Size")
                    with tag("td"):
                        text(offer['size'])
                with tag("tr"):
                    with tag("th"):
                        text("Cashback")
                    with tag("td"):
                        text(offer['cashback'])
                with tag("tr"):
                    with tag("th"):
                        text("Image SMALL")
                    with tag("td"):
                        doc.stag('img', src=offer["pictureOverviewSmallFilePath"],
                                 alt=offer["pictureOverviewSmallFilePath"], height="300")
                with tag("tr"):
                    with tag("th"):
                        text("Image LARGE")
                    with tag("td"):
                        doc.stag('img', src=offer["pictureOverviewLargeFilePath"],
                                 alt=offer["pictureOverviewLargeFilePath"], height="300")
                with tag("br"):
                    text("  ")


master_json = loadJson("Master2.json")

abs_html_path = os.path.join(script_dir, "index.html")
html_file = open(abs_html_path, "w", encoding='utf8')

doc, tag, text = Doc().tagtext()
# doc, tag, text, line = Doc().ttl()

with tag('html'):
    with tag('body'):
        master_json_root = master_json["MasterJSON"]
        # Banners
        with tag("h1"):
            text("Banners Android")
        previewBanners(doc, tag, text, "bannersSettings")
        with tag("h1"):
            text("Banners iOS")
        previewBanners(doc, tag, text, "bannersSettings_iOS")

        # Offers
        with tag("h1"):
            text("Offers")
        previewOffers(doc, tag, text)

html_file.write(doc.getvalue())

html_file.close()