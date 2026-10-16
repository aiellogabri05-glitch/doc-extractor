import pytest

from doc_extractor.parser import DocumentoIlleggibile, estrai

FATTURA = """FATTURA
Numero: FT-TEST-1
Data: 2024-03-15
Fornitore: Acme Srl
Righe:
Descrizione | Quantita | Prezzo
Bullone M8 | 100 | 0.25
Dado M8 | 100 | 0.10
Totale: 35.00
"""

PACKING_LIST = """PACKING LIST
Numero: PL-TEST-1
Data: 2024-03-15
Fornitore: Acme Srl
Righe:
Descrizione | Quantita
Scatola cartone | 12
Totale: 12
"""


def test_legge_fattura_valida():
    doc = estrai(FATTURA, "fattura")
    assert doc.numero == "FT-TEST-1"
    assert doc.fornitore == "Acme Srl"
    assert doc.totale == 35.00
    assert len(doc.righe) == 2
    assert doc.righe[0].descrizione == "Bullone M8"
    assert doc.righe[0].prezzo == 0.25


def test_legge_packing_list_valida():
    doc = estrai(PACKING_LIST, "packing_list")
    assert doc.numero == "PL-TEST-1"
    assert doc.totale == 12
    assert doc.righe[0].prezzo is None


def test_rifiuta_testo_vuoto():
    with pytest.raises(DocumentoIlleggibile):
        estrai("   \n  ", "fattura")


def test_rifiuta_tipo_diverso_dall_intestazione():
    with pytest.raises(DocumentoIlleggibile):
        estrai(FATTURA, "packing_list")


def test_rifiuta_data_non_valida():
    testo = FATTURA.replace("2024-03-15", "15/03/2024")
    with pytest.raises(DocumentoIlleggibile):
        estrai(testo, "fattura")


def test_rifiuta_campo_mancante():
    testo = FATTURA.replace("Fornitore: Acme Srl\n", "")
    with pytest.raises(DocumentoIlleggibile):
        estrai(testo, "fattura")
