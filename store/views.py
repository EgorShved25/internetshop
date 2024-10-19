from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart


def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        if not searched:
            messages.success(request, 'Этот товар не найден... попробуйте снова')
            return render(request, 'search.html', {})
        else:
            return render(request, 'search.html', {'searched': searched})
    else:
        return render(request, 'search.html', {})


def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories': categories})


def category(request, foo):
    foo = foo.replace('-', ' ')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except:
        messages.success(request, ('Этой категории существует....'))
        return redirect('home')


def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})


def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})


def about(request):
    return render(request, 'about.html', {})


def about_shop(request):
    return render(request, 'about_shop.html', {})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Сделать что-нибудь с карзиной покупок
            current_user = Profile.objects.get(user__id=request.user.id)
            # Получите их сохраненную базу данных форм корзины.
            saved_cart = current_user.old_cart
            # Преобразование строки базы данных в словарь Python
            if saved_cart:
                # Преобразование в словарь с использованием JSON
                converted_cart = json.loads(saved_cart)
                # Добавьте загруженный словарь корзины в нашу сессию
                # Получение корзины
                cart = Cart(request)
                # Перемещайтесь по корзине и добавляйте товары из базы данных.
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, ('Вы вошли в учетную запись!'))
            return redirect('home')
        else:
            messages.success(request, ('Произошла ошибка, попробуйте еще раз...'))
            return redirect('login')
    else:
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, ('Вы вышли из учетной записи'))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ('Пользователь создан!'))
            return redirect('home')
        else:
            messages.success(request, ('Упс! Возникла проблема с регистрацией, пожалуйста, попробуйте еще раз...'))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})
