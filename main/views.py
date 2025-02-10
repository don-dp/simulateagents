from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.conf import settings
from openai import OpenAI
from main.models import Environment, Agent, Simulation, Turn
from main.logic.comment import generate_ai_comment
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class HomePageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'main/home.html')

class CommentSimulationView(View):
    template_name = 'main/comment_simulation.html'

    def get(self, request, simulation_id, *args, **kwargs):
        simulation = get_object_or_404(Simulation, id=simulation_id, active=True)
        agents = simulation.agents.all()
        
        context = {
            'simulation': simulation,
            'environment': simulation.environment,
            'agents': agents,
            'state': simulation.current_state
        }
        
        return render(request, self.template_name, context)
    
    @method_decorator(login_required)
    def post(self, request, simulation_id, *args, **kwargs):
        simulation = get_object_or_404(Simulation, id=simulation_id, active=True)
        
        if simulation.user != request.user:
            messages.error(request, 'You do not have permission to modify this simulation, create your own!')
            return redirect('main:comment_simulation', simulation_id=simulation_id)
            
        agent_id = request.POST.get('agent_id')
        if not agent_id:
            messages.error(request, 'Please select an agent to comment.')
            return redirect('main:comment_simulation', simulation_id=simulation_id)
            
        agent = get_object_or_404(Agent, id=agent_id)
        
        turn, new_state = generate_ai_comment(simulation, agent)
        messages.success(request, f'New comment added by {agent.name}.')
        
        return redirect('main:comment_simulation', simulation_id=simulation_id)

class SimulationListView(View):
    template_name = 'main/simulation_list.html'
    
    def get(self, request, *args, **kwargs):
        simulations = Simulation.objects.all().order_by('-created_at')
        
        simulation_data = []
        for simulation in simulations:
            url = ""
            if simulation.environment.name == 'comment':
                url = reverse('main:comment_simulation', kwargs={'simulation_id': simulation.id})
            elif simulation.environment.name == 'chess':
                url = reverse('main:chess_simulation', kwargs={'simulation_id': simulation.id})
                
            simulation_data.append({
                'simulation': simulation,
                'url': url
            })
            
        context = {
            'simulation_data': simulation_data
        }
        return render(request, self.template_name, context)

class CreateSimulationView(View):
    template_name = 'main/create_simulation.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class CreateCommentSimulationView(LoginRequiredMixin, View):
    template_name = 'main/create_comment_simulation.html'
    
    def get(self, request, *args, **kwargs):
        environments = Environment.objects.all()
        context = {
            'environments': environments
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        title = request.POST.get('title')
        environment_id = request.POST.get('environment')
        prompt = request.POST.get('prompt')
        
        environment = Environment.objects.get(id=environment_id)
        initial_state = {}
        
        if environment.name == 'comment':
            initial_state = {
                'title': request.POST.get('article_title'),
                'content': request.POST.get('article_content'),
                'comments': []
            }
        
        simulation = Simulation.objects.create(
            title=title,
            environment_id=environment_id,
            prompt=prompt,
            current_state=initial_state,
            user=request.user
        )
        
        agent_names = request.POST.getlist('agent_names[]')
        agent_prompts = request.POST.getlist('agent_prompts[]')
        
        for name, agent_prompt in zip(agent_names, agent_prompts):
            if name and agent_prompt:
                Agent.objects.create(
                    simulation=simulation,
                    name=name,
                    prompt=agent_prompt
                )
        
        messages.success(request, f'Simulation "{title}" created successfully.')
        
        if simulation.environment.name == 'comment':
            return redirect('main:comment_simulation', simulation_id=simulation.id)
        return redirect('main:simulation_list')

class EditCommentSimulationView(LoginRequiredMixin, View):
    template_name = 'main/edit_comment_simulation.html'
    
    def get(self, request, simulation_id, *args, **kwargs):
        simulation = get_object_or_404(Simulation, id=simulation_id)
        
        if simulation.user != request.user:
            messages.error(request, 'You do not have permission to edit this simulation.')
            return redirect('main:simulation_list')
            
        environments = Environment.objects.all()
        
        context = {
            'simulation': simulation,
            'environments': environments,
            'initial_state': simulation.current_state,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, simulation_id, *args, **kwargs):
        simulation = get_object_or_404(Simulation, id=simulation_id)
        
        if simulation.user != request.user:
            messages.error(request, 'You do not have permission to edit this simulation.')
            return redirect('main:simulation_list')
            
        simulation.title = request.POST.get('title')
        simulation.environment_id = request.POST.get('environment')
        simulation.prompt = request.POST.get('prompt')
        
        simulation.current_state = {
            'title': request.POST.get('article_title'),
            'content': request.POST.get('article_content'),
            'comments': simulation.current_state.get('comments', [])
        }
        
        simulation.save()
        
        agent_names = request.POST.getlist('agent_names[]')
        agent_prompts = request.POST.getlist('agent_prompts[]')
        agent_ids = request.POST.getlist('agent_ids[]')
        
        updated_agent_ids = []
        for name, agent_prompt, agent_id in zip(agent_names, agent_prompts, agent_ids):
            if name and agent_prompt:
                if agent_id:
                    agent = Agent.objects.get(id=agent_id, simulation=simulation)
                    agent.name = name
                    agent.prompt = agent_prompt
                    agent.save()
                else:
                    agent = Agent.objects.create(
                        simulation=simulation,
                        name=name,
                        prompt=agent_prompt
                    )
                updated_agent_ids.append(agent.id)
        
        simulation.agents.exclude(id__in=updated_agent_ids).delete()
        
        messages.success(request, f'Simulation "{simulation.title}" updated successfully.')
        
        if simulation.environment.name == 'comment':
            return redirect('main:comment_simulation', simulation_id=simulation.id)
        return redirect('main:simulation_list')