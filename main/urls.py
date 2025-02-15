from django.urls import path
from .chess_views import CreateChessSimulationView, ChessSimulationView, ChessSimulationMoveView
from .views import HomePageView, SimulationListView, CreateSimulationView

app_name = 'main'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('simulations/', SimulationListView.as_view(), name='simulation_list'),
    path('simulations/create/', CreateSimulationView.as_view(), name='create_simulation'),
    path('simulations/create/chess/', CreateChessSimulationView.as_view(), name='create_chess_simulation'),
    path('chess/<int:simulation_id>/', ChessSimulationView.as_view(), name='chess_simulation'),
    path('chess/<int:simulation_id>/move/', ChessSimulationMoveView.as_view(), name='chess_simulation_move'),
]
