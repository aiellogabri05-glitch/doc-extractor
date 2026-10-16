from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel


class Riga(BaseModel):
    descrizione: str
    quantita: float
    # Nelle packing list il prezzo non c'e': resta None.
    prezzo: Optional[float] = None


class Documento(BaseModel):
    tipo: Literal["fattura", "packing_list"]
    numero: str
    data: date
    fornitore: str
    righe: list[Riga]
    totale: float


class RichiestaEstrazione(BaseModel):
    testo: str
    tipo: Literal["fattura", "packing_list"]
