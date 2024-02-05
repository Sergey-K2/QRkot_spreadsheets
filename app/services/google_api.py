from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from datetime import datetime

from app.core.config import settings
from app.models import CharityProject

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
INFO = {
    'type': settings.type,
    'project_id': settings.project_id,
    'private_key_id': settings.private_key_id,
    'private_key': settings.private_key,
    'client_email': settings.client_email,
    'client_id': settings.client_id,
    'auth_uri': settings.auth_uri,
    'token_uri': settings.token_uri,
    'auth_provider_x509_cert_url': settings.auth_provider_x509_cert_url,
    'client_x509_cert_url': settings.client_x509_cert_url,
    'universe_domain': settings.universe_domain
}

FORMAT = "%Y/%m/%d %H:%M:%S"
SPREADSHEET_ROWCOUNT = 100
SPREADSHEET_COLUMNCOUNT = 10
SPREADSHEET_BODY = dict(
    properties=dict(
        title='',
        locale='ru_RU',
    ),
    sheets=[dict(properties=dict(
        sheetType='GRID',
        sheetId=0,
        title='Лист1',
        gridProperties=dict(
            rowCount=SPREADSHEET_ROWCOUNT,
            columnCount=SPREADSHEET_COLUMNCOUNT
        )
    ))]
)

TABLE_PATTERN = [
    ['Отчет от', ],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]
ROW_COLUMN_COUNT_LIMIT_ERROR = ('Количество строк - {rows_value}, а'
                                'столбцов - {columns_value}, превышает лимит'
                                'количество строк не'
                                'должно превышать {rowcount_limit}, '
                                'a столбцов - {columncount_limit}')

credentials = ServiceAccountCreds(scopes=SCOPES, **INFO)


async def get_service():
    async with Aiogoogle(service_account_creds=credentials) as aiogoogle:
        yield aiogoogle


async def spreadsheets_create(aiogoogle: Aiogoogle) -> str:
    service = await aiogoogle.discover('sheets', 'v4')
    spreadsheets_body = SPREADSHEET_BODY.copy()
    spreadsheets_body['properties']['title'] += datetime.now().strftime(FORMAT)
    response = await aiogoogle.as_service_account(
        service.spreadsheets.create(json=SPREADSHEET_BODY)
    )
    return response['spreadsheetId']


async def set_user_permissions(
        spreadsheet_id: str,
        aiogoogle: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await aiogoogle.discover('drive', 'v3')
    await aiogoogle.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        charity_project: list[CharityProject],
        aiogoogle: Aiogoogle
) -> str:
    service = await aiogoogle.discover('sheets', 'v4')
    table_values = TABLE_PATTERN.copy()
    table_values[0].append(datetime.now().strftime(FORMAT))
    table_values = [*table_values,
                    *[list(map(str,
                               [project.name,
                                project.close_date - project.create_date,
                                project.description])) for project in
                      charity_project]
                    ]
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    columns_value = max(len(items)
                        for items in table_values)
    rows_value = len(table_values)
    if (SPREADSHEET_ROWCOUNT < rows_value or
            SPREADSHEET_COLUMNCOUNT < columns_value):
        raise ValueError(ROW_COLUMN_COUNT_LIMIT_ERROR.format(
            rows_value=rows_value,
            columns_value=columns_value,
            rowcount_limit=SPREADSHEET_ROWCOUNT,
            columncount_limit=SPREADSHEET_COLUMNCOUNT))

    await aiogoogle.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{rows_value}C{columns_value}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
    return spreadsheet_id