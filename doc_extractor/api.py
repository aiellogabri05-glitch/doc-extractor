from fastapi import FastAPI, HTTPException

from .modelli import Documento, RichiestaEstrazione
from .parser import DocumentoIlleggibile, estrai

app = FastAPI(title="doc-extractor")


@app.get("/health")
def health() -> dict[str, str]:
    return {"stato": "ok"}


@app.post("/extract", response_model=Documento)
def extract(richiesta: RichiestaEstrazione) -> Documento:
    try:
        return estrai(richiesta.testo, richiesta.tipo)
    except DocumentoIlleggibile as errore:
        raise HTTPException(status_code=422, detail=str(errore))
