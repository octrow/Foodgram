import logging

from django.core.cache import cache
from django.db.models import signals
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Tag

logger = logging.getLogger(__name__)


def cache_get_or_set(model_name, ids, get_func):
    """Получает данные из кэша или из базы данных.

    Args:
        model_name (str): Имя модели, с которой работают данные.
        ids (list[int]): Список идентификаторов объектов модели.
        get_func (callable): Функция для получения данных из базы данных.
    """
    # Ключ для кэша состоит из имени модели и списка id объектов
    cache_key = f"{model_name}:{','.join(str(id) for id in ids)}"
    try:
        # Попытка получить данные из кэша по ключу
        data = cache.get(cache_key)
        if not data:
            # Если данные не найдены в кэше, то получить их из базы данных
            data = get_func(ids)
            # Сохранить данные в кэше по ключу
            cache.set(cache_key, data)
    except Exception as e:
        # Если произошла ошибка при работе с кэшем, то записать ее в журнал
        logger.error(f"Cache error: {e}")
        # Получить данные из базы данных
        data = get_func(ids)
    return data


def get_tags_list(ids):
    """Получает список тегов из базы данных.

    Args:
        ids (list[int]): Список идентификаторов тегов.

    Returns:
        list: Список объектов модели Tag.
    """
    return list(Tag.objects.filter(id__in=ids))


def get_ingredients_dict(ids):
    """Получает словарь с ингредиентами из базы данных.

    Args:
        ids (list[int]): Список идентификаторов ингредиентов.

    Returns:
        dict: Словарь с ключами - объектами модели Ingredient,
            значениями - кортежами с количеством и единицей измерения.
    """
    ingredients_dict = {}
    for ingredient in Ingredient.objects.filter(id__in=ids):
        ingredients_dict[ingredient] = (
            ingredient.amount,
            ingredient.measurement_unit,
        )
    return ingredients_dict


def clear_cache(sender, instance, **kwargs):
    """Очищает данные в кэше при изменении объекта модели.

    Args:
        sender (Model): Модель, которая отправила сигнал.
        instance (Model): Объект модели, который изменился.
        **kwargs: Дополнительные аргументы.
    """
    # Ключ для кэша состоит из имени модели и id объекта
    cache_key = f"{sender.__name__}:{instance.id}"
    # Удалить данные из кэша по ключу
    cache.delete(cache_key)


signals.post_save.connect(clear_cache, sender=Tag)
signals.post_save.connect(clear_cache, sender=Ingredient)
