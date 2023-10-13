from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('authors', views.AuthorViewSet)
router.register('books', views.BookViewSet)

books_router = routers.NestedDefaultRouter(router, 'users', lookup='user')
books_router.register(
    'author_books', views.AuthorBooksViewSet, basename='author-books')

urlpatterns = router.urls+books_router.urls
