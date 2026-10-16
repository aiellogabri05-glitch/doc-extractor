"""Valuta il lettore su una cartella di documenti.

Uso:
    python eval/evaluate.py samples
    python eval/evaluate.py samples_hard
    python eval/evaluate.py samples_hard --motore llm

Per ogni file .txt cerca il .json con i valori attesi, esegue il lettore e
confronta ogni campo atteso (quelli non nulli) con il valore estratto.
Un documento che il lettore rifiuta conta tutti i suoi campi come sbagliati.
Con --motore llm il lettore e' il client OpenAI (serve OPENAI_API_KEY).
"""

import json
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE))

from doc_extractor.llm import ChiaveMancante, estrai_llm  # noqa: E402
from doc_extractor.parser import DocumentoIlleggibile, estrai  # noqa: E402

TOLLERANZA = 0.005


def campi(atteso: dict) -> dict[str, object]:
    """Appiattisce i valori attesi in coppie campo -> valore (null esclusi)."""
    piatti = {
        "numero": atteso["numero"],
        "data": atteso["data"],
        "fornitore": atteso["fornitore"],
        "totale": atteso["totale"],
    }
    for i, riga in enumerate(atteso["righe"]):
        piatti[f"righe[{i}].descrizione"] = riga["descrizione"]
        piatti[f"righe[{i}].quantita"] = riga["quantita"]
        if riga["prezzo"] is not None:
            piatti[f"righe[{i}].prezzo"] = riga["prezzo"]
    return piatti


def estratti(documento: dict) -> dict[str, object]:
    piatti = {
        "numero": documento["numero"],
        "data": documento["data"],
        "fornitore": documento["fornitore"],
        "totale": documento["totale"],
    }
    for i, riga in enumerate(documento["righe"]):
        piatti[f"righe[{i}].descrizione"] = riga["descrizione"]
        piatti[f"righe[{i}].quantita"] = riga["quantita"]
        piatti[f"righe[{i}].prezzo"] = riga["prezzo"]
    return piatti


def uguali(atteso: object, ottenuto: object) -> bool:
    if isinstance(atteso, float) or isinstance(ottenuto, float):
        try:
            return abs(float(atteso) - float(ottenuto)) < TOLLERANZA
        except (TypeError, ValueError):
            return False
    return str(atteso).strip() == str(ottenuto).strip()


def valuta_documento(file_txt: Path, motore) -> tuple[int, int, str | None]:
    atteso = json.loads(file_txt.with_suffix(".json").read_text(encoding="utf-8"))
    attesi = campi(atteso)
    try:
        ottenuto = motore(file_txt.read_text(encoding="utf-8"), atteso["tipo"])
        trovati = estratti(json.loads(ottenuto.model_dump_json()))
        errore = None
    except DocumentoIlleggibile as errore_lettura:
        trovati = {}
        errore = str(errore_lettura)

    corretti = sum(1 for nome, valore in attesi.items() if nome in trovati and uguali(valore, trovati[nome]))
    return corretti, len(attesi), errore


def main() -> None:
    argomenti = sys.argv[1:]
    motore_nome = "regole"
    if "--motore" in argomenti:
        posizione = argomenti.index("--motore")
        motore_nome = argomenti[posizione + 1] if posizione + 1 < len(argomenti) else ""
        del argomenti[posizione:posizione + 2]
    if len(argomenti) != 1 or motore_nome not in ("regole", "llm"):
        print("Uso: python eval/evaluate.py <cartella> [--motore regole|llm]")
        sys.exit(1)
    motore = estrai_llm if motore_nome == "llm" else estrai

    cartella = (RADICE / argomenti[0]).resolve()
    file_txt = sorted(cartella.glob("*.txt"))
    if not file_txt:
        print(f"Nessun .txt in {cartella}")
        sys.exit(1)

    totale_corretti = 0
    totale_campi = 0
    letti = 0
    print(f"Motore: {motore_nome}")
    for file in file_txt:
        try:
            corretti, campi_tot, errore = valuta_documento(file, motore)
        except ChiaveMancante as errore_chiave:
            print(f"Interrotto: {errore_chiave}")
            sys.exit(1)
        totale_corretti += corretti
        totale_campi += campi_tot
        if errore is None:
            letti += 1
        stato = "letto" if errore is None else f"NON LETTO ({errore})"
        print(f"{file.name:16} {corretti:>3}/{campi_tot:<3} {stato}")

    percentuale = 100 * totale_corretti / totale_campi if totale_campi else 0.0
    print("-" * 60)
    print(f"Documenti letti: {letti}/{len(file_txt)}")
    print(f"Campi corretti: {totale_corretti}/{totale_campi} ({percentuale:.1f}%)")


if __name__ == "__main__":
    main()
