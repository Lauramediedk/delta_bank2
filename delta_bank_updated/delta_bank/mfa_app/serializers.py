from rest_framework import serializers
from bank_app.models import User

class UserSerializer(serializers.ModelSerializer):
    
   class Meta:
      model = User
      fields = ['id', 'username', 'first_name', 'last_name', 'password', 'email', 'otp_enabled', 'otp_verified', 'otp_base32', 'otp_auth_url']

      extra_kwargs = {
          'password': {'write_only': True}
      }

   def create(self, validated_data):
      password = validated_data.pop('password', None)
      instance = self.Meta.model(**validated_data)
      instance.email = instance.email.lower()
      if password is not None:
         instance.set_password(password)
      instance.save()
      return instance