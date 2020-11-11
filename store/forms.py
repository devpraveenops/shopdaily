from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, UserProfile

PAYMENT_CHOICES =(
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

def should_be_empty(value):
    if value:
        raise forms.ValidatoinError('Field is not empty')

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email", error_messages={'exists':'Email already exist'},
            widget= forms.EmailInput(attrs={'class':'form-control','placeholder': 'Enter username'}))
    password1 = forms.CharField(label='Password', widget= forms.PasswordInput(attrs={'class':'form-control','placeholder': 'Enter username'}))
    password2 = forms.CharField(label='Confirm Password',widget= forms.PasswordInput(attrs={'class':'form-control','placeholder': 'Enter username'}))
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username':forms.TextInput(attrs={'class':'form-control','placeholder': 'Enter username'})           
        }

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = False
        if commit:
            user.save()
        return user

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError(self.fields['email'].error_messages['exists'])
        return self.cleaned_data['email']




class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)

class RefundForm(forms.Form):
    ref_code = forms.CharField()
    messages = forms.CharField(widget=forms.Textarea(attrs={
        'rows':4
    }))
    email = forms.EmailField()

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','phone','s_address','city','state']
        labels = {
            'first_name' : 'First Name',
            'phone' : 'Phone',
            's_address' : 'Address',
            'city' : 'City ',
            'state' : 'State'
        }
        widgets = {
            'first_name':forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter First Name'}),
            'phone': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter Phone'}),
            's_address':forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter Addrress'}),
            'city' : forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter City'}),
            'state': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter state'})
        }

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name','last_name','email','phone','address','city','state','zipcode']
        labels = {
            'first_name' : 'First Name',
            'last_name' : 'Last Name',
            'email' : 'Email',
            'phone' : 'Phone',
            'address' : 'Address',
            'city' : 'City ',
            'state' : 'State',
            'zipcode' : 'Zipcode'
        }
        widgets = {
            'first_name':forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter First Name'}),
            'last_name':forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter Last Name'}),
            'email':forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter Email'}),
            'phone': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter Phone'}),
            'address':forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter Addrress'}),
            'city' : forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter City'}),
            'state': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter state'}),
            'zipcode': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter Zipcode'})
        }
    
    