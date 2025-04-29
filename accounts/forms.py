from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(forms.ModelForm):
    """Проверяет существование пользователя и корректность пароля"""
    password = forms.CharField(widget = forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        
        user = User.objects.filter(username = username).first()
        if not user:
            raise forms.ValidationError(f'Пользователь с логином {username} не найден в системе.')
        if not user.check_password(password):
            raise forms.ValidationError('Неправильный пароль. Попробуйте еще раз.')
        return self.cleaned_data
    
class RegistrationForm(forms.ModelForm):
    """Отображает форму регистрации с полями для создания нового пользователя"""
    password = forms.CharField(widget = forms.PasswordInput)
    confirm_password = forms.CharField(widget = forms.PasswordInput)
    phone = forms.CharField(required = False)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['confirm_password'].label = 'Подтвердите пароль'
        self.fields['phone'].label = 'Номер телефона'
        self.fields['email'].label = 'Электронная почта'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        
    def clean_email(self):
        email = self.cleaned_data['email']
        disposable_domains = ['mailinator.com', 'tempmail.com', '10minutemail.com']  # Список временных доменов
        domain = email.split('@')[-1]
        local_part = email.split('@')[0]

        if domain in disposable_domains:
            raise forms.ValidationError('Использование временных email-адресов запрещено.')
        if any(char in local_part for char in ['!', '#', '$', '%', '^', '&', '*']):
            raise forms.ValidationError('Локальная часть email содержит запрещенные символы.')
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError(f'Пользователь с почтой {email} уже существует.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username = username).exists():
            raise forms.ValidationError(f'Имя {username} уже занято. Попробуйте другое.')
        return username
    
    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают.')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password', 'confirm_password']

class ProfileEditForm(forms.ModelForm):
    phone = forms.CharField(max_length = 25, required = False, label = 'Телефон')
    address = forms.CharField(max_length = 255, required = False, label = 'Адрес')
    first_name = forms.CharField(max_length = 150, required = False, label = "Имя")
    last_name = forms.CharField(max_length = 150, required = False, label = "Фамилия")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)
        if self.customer:
            self.fields['phone'].initial = self.customer.phone
            self.fields['address'].initial = self.customer.address
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-sm block w-full rounded-lg pl-12 pr-4 py-3 bg-transparent border-b-1 border-gray-200 focus:border-b-blue-500 outline-none transition-all duration-300 placeholder-gray-400',
                'placeholder': field.label,
                'disabled': 'disabled',
            })

    def save(self, commit = True):
        user = super().save(commit = commit)
        if self.customer:
            self.customer.phone = self.cleaned_data['phone']
            self.customer.address = self.cleaned_data['address']
            if commit:
                self.customer.save()
        return user