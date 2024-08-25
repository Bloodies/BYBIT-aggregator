import inject

from src.bybit.bybit import Bybit
from src.settings import ApplicationSettings


@inject.autoparams()
async def worker(app_settings: ApplicationSettings, bybit_con: Bybit):
    print(app_settings)
