from config.catalogo_agravos import CATALOGO_AGRAVOS

AGRAVOS = {
    item["agravo"]: {
        "ficha": item["ficha_pdf"],
        "cids": item.get("cids", []),
        "campos": item.get("campos", []),
        "palavras": item.get("palavras", []),
    }
    for item in CATALOGO_AGRAVOS
}
