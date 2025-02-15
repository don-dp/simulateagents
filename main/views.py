from django.shortcuts import render
from django.views import View
from django.urls import reverse
from main.models import Simulation

class HomePageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'main/home.html')

class SimulationListView(View):
    template_name = 'main/simulation_list.html'
    
    def get(self, request, *args, **kwargs):
        simulations = Simulation.objects.all().order_by('-created_at')
        
        simulation_data = []
        for simulation in simulations:
            url = ""
            if simulation.environment.name == 'chess':
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
    def get(self, request, *args, **kwargs):
        return render(request, 'main/create_simulation.html')
