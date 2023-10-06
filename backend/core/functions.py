import logging

from django.core.cache import cache
from django.db.models import signals
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Tag

logger = logging.getLogger(__name__)


def cache_get_or_set(model_name, ids, get_func):
    cache_key = f"{model_name}:{','.join(str(id) for id in ids)}"
    try:
        data = cache.get(cache_key)
        if not data:
            data = get_func(ids)
            cache.set(cache_key, data)
    except Exception as e:
        logger.error(f"Cache error: {e}")
        data = get_func(ids)
    return data


def get_tags_list(ids):
    return list(Tag.objects.filter(id__in=ids))


def get_ingredients_dict(ids):
    ingredients_dict = {}
    for ingredient in Ingredient.objects.filter(id__in=ids):
        ingredients_dict[ingredient] = (
            ingredient.amount,
            ingredient.measurement_unit,
        )
    return ingredients_dict


def clear_cache(sender, instance, **kwargs):
    cache_key = f"{sender.__name__}:{instance.id}"
    cache.delete(cache_key)


signals.post_save.connect(clear_cache, sender=Tag)
signals.post_save.connect(clear_cache, sender=Ingredient)
