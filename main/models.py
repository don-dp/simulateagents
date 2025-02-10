from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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


class Simulation(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE)
    prompt = models.TextField(blank=True, null=True, validators=[MaxLengthValidator(100000)])
    current_state = models.JSONField(default=dict, blank=True, validators=[validate_json_size])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def acquire_lock(self, timeout=30):
        now = timezone.now()
        lock_timestamp = self.current_state.get('lock_acquired_at')
        if not lock_timestamp:
            self.current_state['lock_acquired_at'] = now.isoformat()
            self.save(update_fields=['current_state'])
            return True, self.current_state['lock_acquired_at']
        else:
            current_lock_time = timezone.datetime.fromisoformat(lock_timestamp)
            elapsed = (now - current_lock_time).total_seconds()
            if elapsed > timeout:
                self.current_state['lock_acquired_at'] = now.isoformat()
                self.save(update_fields=['current_state'])
                return True, self.current_state['lock_acquired_at']
        return False, lock_timestamp

    def release_lock(self):
        if self.current_state.get('lock_acquired_at'):
            self.current_state['lock_acquired_at'] = None
            self.save(update_fields=['current_state'])

    def is_lock_valid(self, timeout=30):
        lock_timestamp = self.current_state.get('lock_acquired_at')
        if not lock_timestamp:
            return False
        now = timezone.now()
        current_lock_time = timezone.datetime.fromisoformat(lock_timestamp)
        elapsed = (now - current_lock_time).total_seconds()
        return elapsed < timeout

class AIModel(models.Model):
    name = models.CharField(max_length=300)
    value = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Agent(models.Model):
    name = models.CharField(max_length=100)
    prompt = models.TextField(blank=True, null=True, validators=[MaxLengthValidator(100000)])
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='agents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Turn(models.Model):
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    input_data = models.JSONField(default=dict, blank=True, validators=[validate_json_size])
    output_data = models.JSONField(default=dict, blank=True, validators=[validate_json_size])
    state_after_turn = models.JSONField(default=dict, blank=True, validators=[validate_json_size])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Turn {self.pk} in Simulation {self.simulation.pk}"
