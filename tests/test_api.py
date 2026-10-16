from fastapi.testclient import TestClient

from doc_extractor.api import app

client = TestClient(app)

FATTURA = """FATTURA
Numero: FT-API-1
Data: 2024-05-02
Fornitore: Beta Spa
Righe:
Descrizione | Quantita | Prezzo
Vite | 10 | 0.05
Totale: 0.50
"""

PACKING_LIST = """PACKING LIST
Numero: PL-API-1
Data: 2024-05-02
Fornitore: Beta Spa
Righe:
Descrizione | Quantita
Pallet | 3
Totale: 3
"""


def test_health():
    risposta = client.get("/health")
    assert risposta.status_code == 200
    assert risposta.json() == {"stato": "ok"}


def test_extract_fattura():
    risposta = client.post("/extract", json={"testo": FATTURA, "tipo": "fattura"})
    assert risposta.status_code == 200
    dati = risposta.json()
    assert dati["numero"] == "FT-API-1"
    assert dati["totale"] == 0.5
    assert dati["righe"][0]["quantita"] == 10


def test_extract_packing_list():
    risposta = client.post("/extract", json={"testo": PACKING_LIST, "tipo": "packing_list"})
    assert risposta.status_code == 200
    assert risposta.json()["righe"][0]["prezzo"] is None


def test_extract_documento_illeggibile_restituisce_422():
    risposta = client.post("/extract", json={"testo": "Ciao, sono una mail", "tipo": "fattura"})
    assert risposta.status_code == 422


def test_extract_tipo_non_valido_restituisce_422():
    risposta = client.post("/extract", json={"testo": FATTURA, "tipo": "ricevuta"})
    assert risposta.status_code == 422


def test_extract_tipo_non_corrispondente_restituisce_422():
    risposta = client.post("/extract", json={"testo": FATTURA, "tipo": "packing_list"})
    assert risposta.status_code == 422
