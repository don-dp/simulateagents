from django.contrib import admin
from .models import Environment, Agent, Simulation, Turn

@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    list_display = ('title', 'environment', 'user', 'prompt', 'active', 'created_at')
    list_filter = ('active', 'environment')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('agents',)

@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'simulation', 'agent', 'created_at')
    list_filter = ('simulation', 'agent')
    readonly_fields = ('created_at', 'updated_at')
