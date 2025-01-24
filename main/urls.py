from django.urls import path
from .views import HomePageView, CommentSimulationView, SimulationListView, CreateSimulationView, EditSimulationView

app_name = 'main'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('comment_simulation/<int:simulation_id>/', CommentSimulationView.as_view(), name='comment_simulation'),
    path('simulations/', SimulationListView.as_view(), name='simulation_list'),
    path('simulations/create/', CreateSimulationView.as_view(), name='create_simulation'),
    path('simulation/<int:simulation_id>/edit/', EditSimulationView.as_view(), name='edit_simulation'),
]
