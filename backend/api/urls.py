from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (UserViewSet, IngredientViewSet, RecipeViewSet,
                       TagViewSet)

app_name = "api"

router = DefaultRouter()

router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    # path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
