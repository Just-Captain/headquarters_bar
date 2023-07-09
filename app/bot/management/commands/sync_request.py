
from asgiref.sync import sync_to_async
import asyncio
from concurrent.futures import ThreadPoolExecutor

# создаем экземпляр ThreadPoolExecutor
executor = ThreadPoolExecutor()

async def get_data_id_async(model, user_id):
    return await sync_to_async(model.objects.get, thread_sensitive=True)(external_id=user_id)

async def get_data_phone_async(model, phone_number):
    return await sync_to_async(model.objects.get, thread_sensitive=True)(phone_number=phone_number)

async def create_data_id_phone_async(model, user_id, phone_number):
    return await sync_to_async(model.objects.create, thread_sensitive=True)(external_id=user_id, phone_number=phone_number)

async def create_data_check(model, user_profile, worker_profile, amount):
    return await sync_to_async(model.objects.create, thread_sensitive=True)(user_profile=user_profile, worker_profile=worker_profile, amount=amount)

# функция сохранения данных в базе данных
async def save_data_async(my_model_object):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, my_model_object.save)

