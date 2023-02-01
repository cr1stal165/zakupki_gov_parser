from pydantic import BaseModel


class FZ44(BaseModel):
    purchase_number: str
    result_cost: float
    inn: str


class FZ223(BaseModel):
    purchase_number: str
    status: str
    purchase_method: str
    inn: str
    inn_impl: str
    start_cost: float
    result_cost: float
