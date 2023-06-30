from bot.models import JobProfile, UserProfile
from asgiref.sync import sync_to_async
import asyncio
from concurrent.futures import ThreadPoolExecutor
# создаем экземпляр ThreadPoolExecutor
executor = ThreadPoolExecutor()

async def get_data_async(model, user_id):
    return await sync_to_async(model.objects.get, thread_sensitive=True)(external_id=user_id)

async def create_data_async(model, user_id, phone_number):
    return await sync_to_async(model.objects.create, thread_sensitive=True)(external_id=user_id, phone_number=phone_number)

# функция сохранения данных в базе данных
async def save_data_async(my_model_object):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, my_model_object.save)

"""
async def save_data_async(my_model_object):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, my_model_object.save._wrapped)
"""
