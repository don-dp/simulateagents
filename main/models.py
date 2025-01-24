from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

def validate_json_size(value):
    if len(str(value)) > 100000:
        raise ValidationError('JSON content cannot exceed 100,000 characters')

class Environment(models.Model):
    name = models.CharField(max_length=100)
    rules = models.TextField(validators=[MaxLengthValidator(100000)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Agent(models.Model):
    name = models.CharField(max_length=100)
    prompt = models.TextField(validators=[MaxLengthValidator(100000)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Simulation(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    agents = models.ManyToManyField(Agent)
    prompt = models.TextField(validators=[MaxLengthValidator(100000)])
    current_state = models.JSONField(default=dict, blank=True, validators=[validate_json_size])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Turn(models.Model):
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    input_data = models.TextField(validators=[MaxLengthValidator(100000)])
    output_data = models.TextField(validators=[MaxLengthValidator(100000)])
    state_after_turn = models.JSONField(default=dict, blank=True, validators=[validate_json_size])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Turn {self.pk} in Simulation {self.simulation.pk}"
