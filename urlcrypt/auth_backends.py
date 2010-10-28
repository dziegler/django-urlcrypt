from django.contrib.auth.models import User

class UrlCryptBackend:
    
    def authenticate(self, decoded_data=None):
        
        try:
            return User.objects.get(id=decoded_data['user_id'], password=decoded_data['password'])
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None