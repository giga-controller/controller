from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.models.integrations.sheets import SheetsGetRequest

TOKEN_URI = "https://oauth2.googleapis.com/token"


class GoogleSheetsClient:

    def __init__(
        self, access_token: str, refresh_token: str, client_id: str, client_secret: str
    ):
        self.service = build(
            "sheets",
            "v4",
            credentials=Credentials(
                token=access_token,
                refresh_token=refresh_token,
                client_id=client_id,
                client_secret=client_secret,
                token_uri=TOKEN_URI,
            ),
        )

    def read_sheet(self, request: SheetsGetRequest):
        sheet = self.service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=request.spreadsheet_id, range=request.sheet_name)
            .execute()
        )
        return result.get("values", [])

    # def write_sheet(self, range_name, values):
    #     body = {"values": values}
    #     sheet = self.service.spreadsheets()
    #     result = (
    #         sheet.values()
    #         .update(
    #             spreadsheetId=self.spreadsheet_id,
    #             range=range_name,
    #             valueInputOption="RAW",
    #             body=body,
    #         )
    #         .execute()
    #     )
    #     return result

    # def append_sheet(self, range_name, values):
    #     body = {"values": values}
    #     sheet = self.service.spreadsheets()
    #     result = (
    #         sheet.values()
    #         .append(
    #             spreadsheetId=self.spreadsheet_id,
    #             range=range_name,
    #             valueInputOption="RAW",
    #             body=body,
    #         )
    #         .execute()
    #     )
    #     return result
