from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from main.models import Environment, Agent, Simulation, Turn, AIModel
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from main.logic.chess import generate_chess_move
from django.http import JsonResponse
from asgiref.sync import sync_to_async

class CreateChessSimulationView(LoginRequiredMixin, View):
    template_name = 'main/create_chess_simulation.html'
    
    def get(self, request, *args, **kwargs):
        ai_models = AIModel.objects.all()
        context = {'ai_models': ai_models}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        try:
            environment = Environment.objects.get(name='chess')
        except Environment.DoesNotExist:
            messages.error(request, "Chess environment not configured.")
            return redirect('main:create_chess_simulation')
        
        ai_model_ids = [model_id.strip() for model_id in request.POST.getlist('ai_model_ids[]') if model_id.strip()]
        
        if len(ai_model_ids) != 2:
            messages.error(request, "Exactly two AI models are required.")
            return redirect('main:create_chess_simulation')
        
        ai_model_white = get_object_or_404(AIModel, id=ai_model_ids[0])
        ai_model_black = get_object_or_404(AIModel, id=ai_model_ids[1])
        
        title = f"{ai_model_white.name} vs {ai_model_black.name}"
        
        initial_state = {
            'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            'white_agent_id': None,
            'black_agent_id': None,
        }
        
        simulation = Simulation.objects.create(
            title=title,
            environment=environment,
            current_state=initial_state,
            user=request.user
        )
        
        white_agent = Agent.objects.create(simulation=simulation, name=ai_model_white.name, prompt="", ai_model=ai_model_white)
        black_agent = Agent.objects.create(simulation=simulation, name=ai_model_black.name, prompt="", ai_model=ai_model_black)
        
        simulation.current_state.update({
            'white_agent_id': white_agent.id,
            'black_agent_id': black_agent.id,
        })
        simulation.save()
        
        messages.success(request, f'Chess simulation "{title}" created successfully.')
        return redirect('main:chess_simulation', simulation_id=simulation.id)

class ChessSimulationView(View):
    template_name = 'main/chess_simulation.html'

    def get(self, request, simulation_id, *args, **kwargs):
        simulation = get_object_or_404(Simulation, id=simulation_id)
        white_agent = Agent.objects.get(id=simulation.current_state['white_agent_id'])
        black_agent = Agent.objects.get(id=simulation.current_state['black_agent_id'])
        agents = [white_agent, black_agent]
        context = {
            'simulation': simulation,
            'agents': agents,
            'fen': simulation.current_state['fen'],
            'state': simulation.current_state,
            'game_status': simulation.current_state.get('status', 'Ongoing'),
            'is_game_over': simulation.current_state.get('is_game_over', False),
            'turns': Turn.objects.filter(simulation=simulation).order_by('created_at')
        }
        return render(request, self.template_name, context)

class ChessSimulationMoveView(View):
    async def post(self, request, simulation_id, *args, **kwargs):
        is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
        if not is_authenticated:
            return JsonResponse({
                'error': 'Authentication credentials were not provided.'
            }, status=401)
        
        simulation = await sync_to_async(get_object_or_404)(Simulation, id=simulation_id)
        user_id = await sync_to_async(lambda: request.user.id)()
        if simulation.user_id != user_id:
            return JsonResponse({
                'error': 'You do not have permission to modify this simulation.'
            }, status=403)
        
        acquired, lock_timestamp = await sync_to_async(simulation.acquire_lock)(timeout=30)
        if not acquired:
            return JsonResponse({
                'error': 'Another request is processing this simulation. Please try again later.'
            }, status=409)
        try:
            turn, new_state = await sync_to_async(generate_chess_move)(simulation, lock_timestamp)
            if turn:
                return JsonResponse({
                    'success': True,
                    'state': new_state,
                    'turn': {
                        'move': turn.output_data['move'],
                        'explanation': turn.output_data['explanation'],
                        'agent_name': turn.agent.name
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': new_state.get('status', ''),
                    'state': new_state,
                    'is_game_over': True
                })
        except ValueError as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
        finally:
            await sync_to_async(simulation.release_lock)()
