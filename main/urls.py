from django.urls import path
from .views import (
    HomePageView, CommentSimulationView, SimulationListView, 
    CreateCommentSimulationView, EditCommentSimulationView, CreateSimulationView
)
from .chess_views import CreateChessSimulationView, ChessSimulationView, ChessSimulationMoveView

app_name = 'main'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('comment_simulation/<int:simulation_id>/', CommentSimulationView.as_view(), name='comment_simulation'),
    path('simulations/', SimulationListView.as_view(), name='simulation_list'),
    path('simulations/create/', CreateSimulationView.as_view(), name='create_simulation'),
    path('simulations/create/comment/', CreateCommentSimulationView.as_view(), name='create_comment_simulation'),
    path('simulation/<int:simulation_id>/edit/', EditCommentSimulationView.as_view(), name='edit_comment_simulation'),
    path('simulations/create/chess/', CreateChessSimulationView.as_view(), name='create_chess_simulation'),
    path('chess/<int:simulation_id>/', ChessSimulationView.as_view(), name='chess_simulation'),
    path('chess/<int:simulation_id>/move/', ChessSimulationMoveView.as_view(), name='chess_simulation_move'),
]
