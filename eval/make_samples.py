"""Genera i 12 documenti di prova nel formato fisso (6 fatture, 6 packing list).

Ogni documento e' un file .txt con il testo e un .json con i valori attesi.
Il generatore e il lettore in doc_extractor/parser.py usano lo stesso formato:
il punteggio di samples/ misura la pipeline di confronto, non la qualita'
di un'estrazione reale.
"""

import json
import random
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
CARTELLA = RADICE / "samples"

FORNITORI = ["Acme Srl", "Nordvik Spa", "Lumen Trading", "Ferro & Co", "Bluewave Srl", "Tessuti Verdi"]
ARTICOLI = ["Bullone M8", "Dado M8", "Guarnizione", "Cavo USB", "Scatola cartone", "Vite 4x20", "Pannello LED"]


def _data(rng: random.Random) -> str:
    mese = rng.randint(1, 12)
    giorno = rng.randint(1, 28)
    return f"2024-{mese:02d}-{giorno:02d}"


def _fattura(indice: int, rng: random.Random) -> tuple[str, dict]:
    numero = f"FT-2024-{indice:03d}"
    data = _data(rng)
    fornitore = rng.choice(FORNITORI)
    righe = []
    for articolo in rng.sample(ARTICOLI, rng.randint(2, 3)):
        quantita = rng.randint(1, 200)
        prezzo = round(rng.uniform(0.10, 99.99), 2)
        righe.append({"descrizione": articolo, "quantita": quantita, "prezzo": prezzo})
    totale = round(sum(r["quantita"] * r["prezzo"] for r in righe), 2)

    corpo = [
        "FATTURA",
        f"Numero: {numero}",
        f"Data: {data}",
        f"Fornitore: {fornitore}",
        "Righe:",
        "Descrizione | Quantita | Prezzo",
    ]
    corpo += [f"{r['descrizione']} | {r['quantita']} | {r['prezzo']:.2f}" for r in righe]
    corpo.append(f"Totale: {totale:.2f}")

    atteso = {
        "tipo": "fattura",
        "numero": numero,
        "data": data,
        "fornitore": fornitore,
        "righe": righe,
        "totale": totale,
    }
    return "\n".join(corpo) + "\n", atteso


def _packing_list(indice: int, rng: random.Random) -> tuple[str, dict]:
    numero = f"PL-2024-{indice:03d}"
    data = _data(rng)
    fornitore = rng.choice(FORNITORI)
    righe = []
    for articolo in rng.sample(ARTICOLI, rng.randint(2, 3)):
        righe.append({"descrizione": articolo, "quantita": rng.randint(1, 50), "prezzo": None})
    totale = sum(r["quantita"] for r in righe)

    corpo = [
        "PACKING LIST",
        f"Numero: {numero}",
        f"Data: {data}",
        f"Fornitore: {fornitore}",
        "Righe:",
        "Descrizione | Quantita",
    ]
    corpo += [f"{r['descrizione']} | {r['quantita']}" for r in righe]
    corpo.append(f"Totale: {totale}")

    atteso = {
        "tipo": "packing_list",
        "numero": numero,
        "data": data,
        "fornitore": fornitore,
        "righe": righe,
        "totale": totale,
    }
    return "\n".join(corpo) + "\n", atteso


def main() -> None:
    CARTELLA.mkdir(exist_ok=True)
    rng = random.Random(42)
    for i in range(1, 7):
        for nome, creatore in (("fattura", _fattura), ("packing", _packing_list)):
            testo, atteso = creatore(i, rng)
            base = CARTELLA / f"{nome}_{i:02d}"
            base.with_suffix(".txt").write_text(testo, encoding="utf-8")
            base.with_suffix(".json").write_text(
                json.dumps(atteso, indent=2, ensure_ascii=False), encoding="utf-8"
            )
    print(f"Creati 12 documenti in {CARTELLA}")


if __name__ == "__main__":
    main()
