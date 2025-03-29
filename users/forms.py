from django import forms 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  
from .models import User, Products, Sale

class RegisterationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = User 
        fields = ['username', 'email', 'password1', 'password2', 'role']
        


class LoginForm(AuthenticationForm):
    class Meta:
        model = User 
        fields = ['username', 'password']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name','cost_price', 'price', 'description', 'stock']
        
    
class SalesForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity','selling_price','mode_of_payment', 'customer_details']
        
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        product = self.cleaned_data.get('product')
        
        if quantity > product.stock:
            raise forms.ValidationError("Not enough stock available")
        
        return quantity