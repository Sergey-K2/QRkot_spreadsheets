import copy

from aiogoogle import Aiogoogle
from datetime import datetime

from app.core.config import settings
from app.models.charity_project import CharityProject


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
ROW_COLUMN_COUNT_LIMIT_ERROR = (
    'Количество строк - {rows_value}, а'
    'столбцов - {columns_value}, превышает лимит'
    'количество строк не'
    'должно превышать {SPREADSHEET_ROWCOUNT}, '
    'a столбцов - {SPREADSHEET_COLUMNCOUNT}'
)


async def spreadsheets_create(aiogoogle: Aiogoogle) -> str:
    service = await aiogoogle.discover('sheets', 'v4')
    spreadsheets_body = copy.deepcopy(SPREADSHEET_BODY)
    spreadsheets_body['properties']['title'] += datetime.now().strftime(FORMAT)
    response = await aiogoogle.as_service_account(
        service.spreadsheets.create(json=spreadsheets_body)
    )
    return (response['spreadsheetId'], response['url'])


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
    table_values = copy.deepcopy(TABLE_PATTERN)
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
    if (
        SPREADSHEET_ROWCOUNT < rows_value or
        SPREADSHEET_COLUMNCOUNT < columns_value
    ):
        raise ValueError(ROW_COLUMN_COUNT_LIMIT_ERROR.format(
            rows_value=rows_value,
            columns_value=columns_value))

    await aiogoogle.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{rows_value}C{columns_value}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
