from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from .forms import AddProductForm
from .models import Product
from .forms import ChatInputForm
from .forms import AddToCartForm
from .forms import CreateChatForm
from .forms import ChatOutputForm
# Создаем здесь представления.

import sqlite3 as sq
class Database_construction:
    @staticmethod
    def creating_tables(db):
        try:
            db.execute("CREATE TABLE products(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       " label TEXT,"
                       " likes INTEGER,"
                       " id_category TEXT,"
                       " price INTEGER, "
                       " username TEXT, "
                       " url_img TEXT)")
            db.execute("CREATE TABLE users_products(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       " id_product INTEGER,"
                       " id_user INTEGER)")
            db.execute("CREATE TABLE categories(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "name TEXT)")
            db.execute("CREATE TABLE likes(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       " id_user INTEGER,"
                       " id_category INTEGER,"
                       " amount INTEGER)")
        except:
            print("Таблицы уже созданы!")

def get_base_context(request, receiver):
    menu = [
        {"link": "/chat_list/", "text": "Чаты"},
        {"link": "/shopping_cart/", "text": "Корзина"},
        {"link": "/new_product/", "text": "Добавить товар"},
    ]
    db = sq.connect("db.sqlite3")
    Database_construction.creating_tables(db)
    products = (db.execute("SELECT * FROM products")).fetchall()
    print(products)
    username = str(request.user)
    chat = db.execute("SELECT * FROM chat WHERE receiver = ?", (username,)).fetchall()
    if receiver != "Anonuser":
        arr = (username, receiver)
        messages = db.execute("SELECT * FROM messages WHERE receiver = ?", (receiver,)).fetchall()
        print(messages)
        return {"messages": messages}
    db.close()
    return {"menu": menu, "user": request.user, "products": products, "chat": chat}

def create_chat(request):
    db = sq.connect("db.sqlite3")
    if request.method == "POST":
        form = CreateChatForm(request.POST)
        receiver = form.data["username"]
        sender = str(request.user)
        with db:
            arr = (sender, receiver)
            arr2 = (receiver, sender)
            db.execute("INSERT INTO chat(sender, receiver) VALUES(?, ?)", arr)
            db.execute("INSERT INTO chat(sender, receiver) VALUES(?, ?)", arr2)
    db.close()
    return render(request, "chat_list.html")

def chat_input(request):
    context = get_base_context(request, "Anonuser")
    db = sq.connect("db.sqlite3")
    if request.method == "POST":
        form = ChatInputForm(request.POST)
        username = str(request.user)
        message = form.data["mes"]
        if form.is_valid():
            with db:
                tr_data1 = db.execute("SELECT receiver FROM chat WHERE sender = ?",(username,)).fetchall()
                tr_data2 = db.execute("SELECT chat_id FROM chat WHERE sender = ?", (username,)).fetchall()
                receiver = egor_letov(tr_data1)
                id_chat = egor_letov(tr_data2)
                arr = (message, username, receiver, id_chat)
                db.execute("INSERT INTO messages(message, username, receiver, id_chat) VALUES(?, ?, ?, ?)", arr)
            context["form"] = form
    else:
        form = ChatInputForm()
        context["form"] = form
    db.close()
    return redirect("https://dogdotcom.herokuapp.com/room")

"""def chat_output(request, receiver):
    context = get_base_context(request)
    db = sq.connect("db.sqlite3")
    if request.method == "POST":
        username = str(request.user)
        print(1)
        with db:
            arr = (username, receiver)
            messages = db.execute("SELECT * FROM messages WHERE username = ? AND receiver = ?", arr).fetchall()
            print(messages)
    db.close()
    return render(request, "room.html", {"messages": messages})"""

def chat_list(request):
    context = get_base_context(request, "Anonuser")
    if request.method == "POST":
        db = sq.connect("db.sqlite3")
        Database_construction.creating_tables(db)
        db.close()
        return render(request, "chat_list.html", context)
    elif request.method == "GET":
        db = sq.connect("db.sqlite3")
        Database_construction.creating_tables(db)
        db.close()
        return render(request, "chat_list.html", context)

def room(request):
    if request.method == "POST":
        receiver = request.POST.get('username')
        context = get_base_context(request, receiver)
        db = sq.connect("db.sqlite3")
        Database_construction.creating_tables(db)
        db.close()
        return render(request, "room.html", context)
    elif request.method == "GET":
        db = sq.connect("db.sqlite3")
        Database_construction.creating_tables(db)
        db.close()
        return render(request, "room.html")

def home(request):
    context = get_base_context(request, "Anonuser")
    if request.method == "POST":
        db = sq.connect("db.sqlite3")
        Database_construction.creating_tables(db)
        db.close()
        return render(request, "home.html", context)
    elif request.method == "GET":
        db = sq.connect("db.sqlite3")
        Database_construction.creating_tables(db)
        db.close()
        return render(request, "home.html", context)

def shopping_cart(request):
    context = get_base_context(request, "Anonuser")
    if request.method == "POST":
        db = sq.connect("db.sqlite3")
        Database_construction.creating_tables(db)
        main_username = str(request.user)
        tr_data = db.execute("SELECT id FROM shopping_cart WHERE main_username = ?", (main_username,)).fetchall()
        if len(tr_data) == 0:
            return render(request, "shopping_cart.html")
        else:
            id_product = egor_letov(tr_data)
            shopping_cart = db.execute("SELECT * FROM products WHERE id = ?", (id_product,)).fetchall()
            db.close()
            return render(request, "shopping_cart.html", {"shopping_cart": shopping_cart})
    elif request.method == "GET":
        db = sq.connect("db.sqlite3")
        Database_construction.creating_tables(db)
        main_username = str(request.user)
        tr_data = db.execute("SELECT id FROM shopping_cart WHERE main_username = ?", (main_username,)).fetchall()
        if len(tr_data) == 0:
            return render(request, "shopping_cart.html")
        else:
            id_product = egor_letov(tr_data)
            shopping_cart = db.execute("SELECT * FROM products WHERE id = ?", (id_product,)).fetchall()
            db.close()
            return render(request, "shopping_cart.html", {"shopping_cart": shopping_cart})

def add_sc(request):
    db = sq.connect("db.sqlite3")
    if request.method == "POST":
        form = AddToCartForm(request.POST)
        main_username = str(request.user)
        username = str(form.data["username"])
        print(username)
        with db:
            tr_data = db.execute("SELECT id FROM products WHERE username = ?", (username,)).fetchall()
            id_product = egor_letov(tr_data)
            arr = (id_product, main_username, username)
            db.execute("INSERT INTO shopping_cart(id, main_username, username) VALUES(?, ?, ?)", arr)
        db.close()
        return redirect("https://dogdotcom.herokuapp.com/")

def egor_letov(list):
    print(list)
    tuple = list[0]
    object = tuple[0]
    return object

def new_product(request):
    context = get_base_context(request, "Anonuser")
    db = sq.connect("db.sqlite3")
    if request.method == "POST":
        form = AddProductForm(request.POST)
        label = form.data["label"]
        price = form.data["price"]
        url_img = form.data["url_img"]
        user = str(request.user)
        likes = 0
        id_category = form.data["category"]
        if form.is_valid():
            with db:
                arr = (label,likes,id_category, price, url_img, user)
                db.execute("INSERT INTO products(label, likes, id_category, price, url_img, username) VALUES(?, ?, ?, ?, ?, ?)", arr)
            context["form"] = form
        return redirect("https://dogdotcom.herokuapp.com/")

    else:
        form = AddProductForm()
        context["form"] = form
    db.close()
    return render(request, "new_product.html", context)

def account(request):
    context = get_base_context(request, "Anonuser")
    return render(request, "account.html", context)

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
