import re

emotes_dict = {
    ":araAra:": "<:araAra:1293244790787543142>",
    ":chloeComfy:": "<:chloeComfy:1293246858096803880>",
    ":hatsuneSleep:": "<:hatsuneSleep:1293246864002519192>",
    ":hatsuneXD:": "<:hatsuneXD:1293244834613825680>",
    ":kokkoroThink:": "<:kokkoroThink:1293246859644637315>",
    ":kyaruBox:": "<:kyaruBox:1293244821971931146>",
    ":kyaruCook:": "<:kyaruCook:1293244782616907776>",
    ":kyaruCry:": "<:kyaruCry:1293244823868018801>",
    ":kyaruHead:": "<:kyaruHead:1293245627207123046>",
    ":kyaruHuh:": "<:kyaruHuh:1293244809850650625>",
    ":kyaruMad:": "<:kyaruMad:1293244813726056559>",
    ":kyaruNooo:": "<:kyaruNooo:1293244831199657995>",
    ":kyaruPat:": "<:kyaruPat:1293244778464542720>",
    ":kyaruPlead:": "<:kyaruPlead:1293245625785122846>",
    ":kyaruPunch:": "<:kyaruPunch:1293244818138599505>",
    ":kyaruSad:": "<:kyaruSad:1293244827361742889>",
    ":kyaruSleep:": "<:kyaruSleep:1293246860974096458>",
    ":kyaruStare:": "<:kyaruStare:1293244803198226575>",
    ":kyaruSurprise:": "<:kyaruSurprise:1293244808365871185>",
    ":kyaruThumbs:": "<:kyaruThumbs:1293244786354032683>",
    ":kyaruTired:": "<:kyaruTired:1293245624119988385>",
    ":kyaruWhat:": "<:kyaruWhat:1293240417470382153>",
    ":kyaruWut:": "<:kyaruWut:1293245622454980679>",
    ":kyaruXD:": "<:kyaruXD:1293245619699449857>",
    ":kyoukaClown:": "<:kyoukaClown:1293244796038545459>",
    ":kyoukaComfy:": "<:kyoukaComfy:1293244798945198145>",
    ":kyoukaGun:": "<:kyoukaGun:1293244780419219601>",
    ":mahoSmile:": "<:mahoSmile:1293244794126209108>",
    ":pecoBlob:": "<:pecoBlob:1293246856612020265>",
    ":pecoBoobs:": "<:pecoBoobs:1293244792645488771>",
    ":priconneJewel:": "<:priconneJewel:1293244797657808896>",
    ":puddingGhost:": "<:puddingGhost:1293244784630304898>",
    ":tsumugiPog:": "<:tsumugiPog:1293245607028457624>",
    ":wakanaShoo~1:": "<:wakanaShoo~1:1449471149695176897>",
    ":yukiPotato:": "<:yukiPotato:1293244788627210290>",
}

def format_response(raw_response: str):
    pattern = '|'.join(re.escape(key) for key in emotes_dict.keys())
    return re.sub(pattern, lambda m: emotes_dict[m.group()], raw_response)