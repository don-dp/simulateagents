from django.contrib import admin
from .models import Environment, Agent, Simulation, Turn, AIModel

@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'simulation', 'ai_model', 'created_at', 'updated_at')
    search_fields = ('name', 'ai_model__name')
    readonly_fields = ('created_at', 'updated_at')

class AgentInline(admin.TabularInline):
    model = Agent
    extra = 1
    raw_id_fields = ('ai_model',)

@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    list_display = ('title', 'environment', 'user', 'prompt', 'created_at')
    list_filter = ('environment',)
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AgentInline]

@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'simulation', 'agent', 'created_at')
    list_filter = ('simulation', 'agent')
    readonly_fields = ('created_at', 'updated_at')
