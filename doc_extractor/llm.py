"""Estrazione con un LLM (OpenAI): legge il testo libero e restituisce un Documento.

La chiave si legge dalla variabile d'ambiente OPENAI_API_KEY e non va mai
scritta nel codice o nei file del progetto. Il modello si puo' cambiare con
OPENAI_MODEL.
"""

import json
import os

from pydantic import ValidationError

from .modelli import Documento
from .parser import DocumentoIlleggibile

MODELLO_PREDEFINITO = "gpt-4o-mini"

ISTRUZIONI = """Estrai i dati dal documento commerciale che ti viene dato.
Rispondi solo con un oggetto JSON con queste chiavi:
- "numero": stringa, il numero del documento
- "data": stringa nel formato YYYY-MM-DD
- "fornitore": stringa, il nome del fornitore
- "righe": lista di oggetti con "descrizione" (stringa), "quantita" (numero) e "prezzo" (numero, oppure null se il documento non lo riporta)
- "totale": numero, il totale del documento

Usa il punto come separatore decimale. Se un valore non c'e', usa null."""


class ChiaveMancante(RuntimeError):
    """OPENAI_API_KEY non e' impostata nell'ambiente."""


def _client():
    chiave = os.environ.get("OPENAI_API_KEY")
    if not chiave:
        raise ChiaveMancante("OPENAI_API_KEY non impostata: vedi la sezione 'Chiave OpenAI' del README")
    from openai import OpenAI

    return OpenAI(api_key=chiave)


def estrai_llm(testo: str, tipo: str) -> Documento:
    """Chiede al modello i campi del documento e li valida con i modelli del progetto."""
    modello = os.environ.get("OPENAI_MODEL", MODELLO_PREDEFINITO)
    risposta = _client().chat.completions.create(
        model=modello,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": ISTRUZIONI},
            {"role": "user", "content": f"Tipo di documento: {tipo}\n\n{testo}"},
        ],
    )
    dati = json.loads(risposta.choices[0].message.content)
    dati["tipo"] = tipo
    try:
        return Documento.model_validate(dati)
    except ValidationError as errore:
        raise DocumentoIlleggibile(f"risposta del modello non valida: {errore.errors()[0]['msg']}") from errore
