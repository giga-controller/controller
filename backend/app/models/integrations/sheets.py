from pydantic import BaseModel


class SheetsGetRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: str
