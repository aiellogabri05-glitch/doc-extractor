# doc-extractor

Estrae da fatture e packing list i campi: numero, data, fornitore, righe e totale.

## Stato attuale

Il lettore in `doc_extractor/parser.py` **non è un LLM**. È un lettore a regole che riconosce solo il formato fisso dei documenti in `samples/`. Qualunque altro layout viene rifiutato con errore 422.

Accanto al lettore a regole c'è il client OpenAI in `doc_extractor/llm.py`, che legge il testo libero. È pronto ma **non è ancora stato eseguito**: manca la chiave API, che va impostata sul tuo PC come variabile d'ambiente (vedi sotto).

## Avvio

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn doc_extractor.api:app --reload
```

Endpoint:
- `GET /health` restituisce `{"stato": "ok"}`
- `POST /extract` con corpo `{"testo": "...", "tipo": "fattura"}` restituisce il record validato, oppure 422 se il documento non è leggibile

## Valutazione

```bash
python eval/make_samples.py        # rigenera samples/ (12 documenti)
python eval/evaluate.py samples
python eval/evaluate.py samples_hard
python eval/evaluate.py samples_hard --motore llm   # usa OpenAI, richiede la chiave
```

## Chiave OpenAI

La chiave non va scritta nel codice né in questo file. Impostala tu come variabile d'ambiente:

- Windows: apri "Modifica le variabili d'ambiente per il tuo account", aggiungi `OPENAI_API_KEY` con la tua chiave, poi riapri il terminale.
- Oppure in PowerShell, nella tua sessione: `$env:OPENAI_API_KEY = "la-tua-chiave"`

Il modello è `gpt-4o-mini` per default. Per cambiarlo imposta `OPENAI_MODEL`.

Se la chiave manca, `--motore llm` si ferma con un messaggio che lo dice.

| Set | Documenti | Letti | Campi corretti |
|---|---|---|---|
| `samples/` | 12 (6 fatture, 6 packing list), generati dallo stesso formato del lettore | 12/12 | 126/126 (100%) |
| `samples_hard/` | 8 fatture scritte a mano, layout diversi, lingue diverse | 0/8 | 0/77 (0%) |

**Come leggere i numeri.** Il 100% su `samples/` dimostra che lo script di confronto funziona. Non misura la qualità dell'estrazione: formato di generazione e lettore coincidono. Lo 0% su `samples_hard/` è il risultato reale del lettore a regole, e non è stato corretto aggiungendo regole per quei layout.

Un numero utile per un portfolio si ottiene solo con un estrattore basato su LLM, valutato su documenti che non abbiamo scritto noi.
