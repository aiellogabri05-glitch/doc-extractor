"""Lettore a regole per il formato fisso dei documenti di esempio.

ATTENZIONE: questo NON e' un estrattore basato su LLM. Legge solo il formato
fisso generato da eval/make_samples.py (intestazione FATTURA / PACKING LIST,
chiavi "Numero:", "Data:", "Fornitore:", "Totale:", sezione "Righe:" con
valori separati da "|"). Qualunque altro layout viene rifiutato.
"""

from datetime import date

from .modelli import Documento, Riga

INTESTAZIONI = {"FATTURA": "fattura", "PACKING LIST": "packing_list"}


class DocumentoIlleggibile(ValueError):
    """Il testo non segue il formato fisso riconosciuto dal lettore."""


def _chiavi(righe_testo: list[str]) -> dict[str, str]:
    chiavi: dict[str, str] = {}
    for riga in righe_testo:
        if ":" not in riga:
            continue
        nome, valore = riga.split(":", 1)
        chiavi[nome.strip()] = valore.strip()
    return chiavi


def _righe_documento(righe_testo: list[str], tipo: str) -> list[Riga]:
    if "Righe:" not in righe_testo:
        raise DocumentoIlleggibile("sezione 'Righe:' mancante")
    inizio = righe_testo.index("Righe:") + 1
    # La riga di intestazione della tabella viene saltata.
    dati = righe_testo[inizio + 1:]
    righe: list[Riga] = []
    for riga in dati:
        if riga.startswith("Totale:"):
            break
        celle = [c.strip() for c in riga.split("|")]
        try:
            if tipo == "fattura":
                descrizione, quantita, prezzo = celle
                righe.append(Riga(descrizione=descrizione, quantita=float(quantita), prezzo=float(prezzo)))
            else:
                descrizione, quantita = celle
                righe.append(Riga(descrizione=descrizione, quantita=float(quantita)))
        except ValueError as errore:
            raise DocumentoIlleggibile(f"riga non valida: {riga!r}") from errore
    if not righe:
        raise DocumentoIlleggibile("nessuna riga trovata")
    return righe


def estrai(testo: str, tipo: str) -> Documento:
    """Restituisce il documento validato oppure solleva DocumentoIlleggibile."""
    righe_testo = [r.rstrip() for r in testo.splitlines() if r.strip()]
    if not righe_testo:
        raise DocumentoIlleggibile("testo vuoto")

    tipo_rilevato = INTESTAZIONI.get(righe_testo[0].strip())
    if tipo_rilevato is None:
        raise DocumentoIlleggibile("intestazione non riconosciuta")
    if tipo_rilevato != tipo:
        raise DocumentoIlleggibile(f"il documento e' una {tipo_rilevato}, non una {tipo}")

    chiavi = _chiavi(righe_testo)
    for obbligatoria in ("Numero", "Data", "Fornitore", "Totale"):
        if obbligatoria not in chiavi:
            raise DocumentoIlleggibile(f"campo mancante: {obbligatoria}")

    try:
        data = date.fromisoformat(chiavi["Data"])
        totale = float(chiavi["Totale"])
    except ValueError as errore:
        raise DocumentoIlleggibile("data o totale non validi") from errore

    righe = _righe_documento(righe_testo, tipo)

    return Documento(
        tipo=tipo_rilevato,
        numero=chiavi["Numero"],
        data=data,
        fornitore=chiavi["Fornitore"],
        righe=righe,
        totale=totale,
    )
