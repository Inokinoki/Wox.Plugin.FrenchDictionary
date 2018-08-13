#encoding = utf8
from wox import Wox, WoxAPI
import requests
from bs4 import BeautifulSoup as bs
import webbrowser
import json
import re

class FrenchDictionary(Wox):

    def query(self, query):
        results = []

        if len(query.strip()) >= 2:
            r = requests.get('http://www.frdic.com/dicts/prefix/{}'.format(query.strip()))
            response = json.loads(r.text)
            if len(response) > 0:
                for res in response:
                    if not res["recordtype"] or "CG" not in res["recordtype"]:
                        results.append({
                            "Title": res["value"],
                            "SubTitle": res["label"],
                            "IcoPath":"Images\\app.png",
                            "ContextData": res["value"]
                        })
            else:
                results.append({
                    "Title": "Not found {}".format(query.strip()),
                    "SubTitle": "Match result: " + str(len(response)),
                    "IcoPath":"Images\\app.png"
                })
        else:
            results.append({
                "Title": "法语助手插件",
                "SubTitle": "基于 http://www.frdic.com/ 信息来源于网络, 若侵犯您的权益请联系作者删除",
                "IcoPath":"Images\\app.png"
            })
        return results

    def context_menu(self, query):
        results = []
        has_verb = False

        if len(query.strip()) >= 2:
            r = requests.get('http://www.frdic.com/dicts/fr/{}'.format(query.strip()))
            document = bs(r.text, "html.parser")
            #translate_divs = document.find_all("div", id="translate")
            translate_divs = document.find_all("div", id="ExpFC")
        
            if len(translate_divs) > 0:
                caras_spans = translate_divs[0].find_all("span", class_="cara")
                exp_spans = translate_divs[0].find_all("span", class_="exp")
                cara_index = -1
                for exp_span in exp_spans:
                    expression = exp_span.get_text(strip=True)

                    # Detect caracter
                    cara = ""
                    if "1." in expression:
                        cara_index+=1
                    if cara_index != -1 and len(caras_spans) > 0 and cara_index < len(caras_spans):
                        cara = caras_spans[cara_index].get_text(strip=True) 
                        if "v." in cara:
                            has_verb = True

                    # Remove order
                    expression = re.sub(r'[0-9]\.', '', expression)

                    # Get example
                    phrase = ""
                    if exp_span.next_sibling.next_sibling is not None:
                        phrase = exp_span.next_sibling.next_sibling.get_text(strip=True)

                    results.append({
                        "Title": cara + " " + expression,
                        "SubTitle": phrase,
                        "IcoPath":"Images\\app.png"
                    })
                if has_verb:
                    results.append({
                        "Title": "Conjugaison de {}".format(query.strip()),
                        "SubTitle": "查看 {} 的变位".format(query.strip()),
                        "IcoPath":"Images\\app.png",
                        "JsonRPCAction":{
                            "method": "openInBrowser",
                            "parameters":['http://www.frdic.com/dicts/fr/{}?forcecg=true&cgformidx=0'.format(query.strip())],
                            "dontHideAfterAction":False
                        }   
                    })
                results.append({
                    "Title": "More for {}".format(query.strip()),
                    "SubTitle": "更多关于 {} 的翻译".format(query.strip()),
                    "IcoPath":"Images\\app.png",
                    "JsonRPCAction":{
                        "method": "openInBrowser",
                        "parameters":['http://www.frdic.com/dicts/fr/{}'.format(query.strip())],
                        "dontHideAfterAction":False
                    }
                })
            else:
                results.append({
                    "Title": "Not found {}".format(query.strip()),
                    "SubTitle": "点击这里在浏览器中尝试查询", #"Match result: " + str(len(translate_divs)),
                    "IcoPath":"Images\\app.png",
                    "JsonRPCAction":{
                        "method": "openInBrowser",
                        "parameters":['http://www.frdic.com/dicts/fr/{}'.format(query.strip())],
                        "dontHideAfterAction":False
                    }
                })
        return results

    def openInBrowser(self, url):
        webbrowser.open(url)
        WoxAPI.change_query("")

if __name__ == "__main__":
    FrenchDictionary()