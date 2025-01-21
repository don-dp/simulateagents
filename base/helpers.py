import requests
from django.conf import settings
from django.contrib import messages
import os

def check_turnstile(request):
    turnstile_token = request.POST.get('cf-turnstile-response')
    if turnstile_token:
        siteverify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
        data = {
            'secret': settings.TURNSTILE_SECRET_KEY,
            'response': turnstile_token,
        }
        
        try:
            response = requests.post(siteverify_url, data=data)
            result = response.json()

            if result['success']:
                return True
            else:
                error_codes = result.get('error-codes', [])
                if 'timeout-or-duplicate' in error_codes:
                    messages.error(request, 'Verification timeout or duplicate submission')
                elif 'invalid-input-response' in error_codes:
                    messages.error(request, 'Invalid or expired captcha')
                else:
                    messages.error(request, 'Captcha verification failed')
                return False
        except Exception as e:
            messages.error(request, 'Error verifying captcha')
            return False
    else:
        messages.error(request, 'Captcha missing')
        return False