from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
import numpy as np
import cv2


import tensorflow as tf

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render


def landing(request):
    return render(request, 'landing.html')


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        
        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

       
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()
        return redirect('login')
    return render(request, 'signup.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

from django.contrib.auth.models import User

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # ✅ Get total users
    total_users = User.objects.count()

    return render(request, "dashboard.html", {
        "total_users": total_users,   # 🔥 IMPORTANT
        "cinnamon_model": best_cinnamon_name,
        "cinnamon_score": round(best_cinnamon_score, 2),
        "burnout_model": best_name,
        "burnout_score": round(best_score, 2)
    })
   
def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    return render(request, 'profile.html', {
        'user': user,
        'profile': profile
    })

import pandas as pd
from django.shortcuts import render

# Classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

# Regression
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor


# =========================
# 🚀 TRAIN MODELS (RUN ONCE)
# =========================

# ---------- 🍂 Cinnamon ----------
cinnamon_df = pd.read_csv(r"D:\Internship-Project\Dataset\cinnamon\balanced_cinnamon_quality_dataset.csv")

# Remove unwanted columns (like Sample_ID)
cinnamon_df = cinnamon_df.drop(["Sample_ID"], axis=1)

# Clean column names (remove spaces & symbols)
cinnamon_df.columns = [
    "moisture",
    "ash",
    "volatile_oil",
    "acid_insoluble_ash",
    "chromium",
    "coumarin",
    "quality"
]

# Features & Target
X_cin = cinnamon_df.drop("quality", axis=1)
y_cin = cinnamon_df["quality"]

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_cin, y_cin, test_size=0.2)

models_c = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(),
    "Decision Tree": DecisionTreeClassifier(),
    "KNN": KNeighborsClassifier()
}

best_cinnamon_model = None
best_cinnamon_score = 0
best_cinnamon_name = ""

for name, model in models_c.items():
    model.fit(X_train_c, y_train_c)
    pred = model.predict(X_test_c)
    acc = accuracy_score(y_test_c, pred)

    if acc > best_cinnamon_score:
        best_cinnamon_score = acc
        best_cinnamon_model = model
        best_cinnamon_name = name


# ---------- 🔥 Burnout ----------
burnout_df = pd.read_csv(r"D:\Internship-Project\Dataset\Work From Home Employee Burnout Dataset\work_from_home_burnout_dataset.csv")

burnout_df.columns = burnout_df.columns.str.strip()

# Convert day_type
burnout_df["day_type"] = burnout_df["day_type"].map({
    "Weekday": 0,
    "Weekend": 1
})

# Drop user_id
burnout_df = burnout_df.drop(["user_id"], axis=1)

# 🔥 IMPORTANT CHANGE HERE
X_burn = burnout_df.drop(["burnout_score", "burnout_risk"], axis=1)
y_burn = burnout_df["burnout_risk"]   # ✅ NOW CLASSIFICATION

# Train multiple models
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

X_train, X_test, y_train, y_test = train_test_split(X_burn, y_burn, test_size=0.2)

models = {
    "Random Forest": RandomForestClassifier(),
    "Decision Tree": DecisionTreeClassifier(),
    "KNN": KNeighborsClassifier()
}

best_model = None
best_score = 0
best_name = ""

for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)

    if acc > best_score:
        best_score = acc
        best_model = model
        best_name = name


# =========================
# 🔮 VIEWS
# =========================

# ---------- 🍂 Cinnamon ----------
def cinnamon(request):
    result = None

    if request.method == "POST":
        data = [[
            float(request.POST.get("moisture")),
            float(request.POST.get("ash")),
            float(request.POST.get("volatile_oil")),
            float(request.POST.get("acid_insoluble_ash")),
            float(request.POST.get("chromium")),
            float(request.POST.get("coumarin")),
        ]]

        result = best_cinnamon_model.predict(data)[0]

    return render(request, "cinnamon.html", {
        "result": result,
        "model": best_cinnamon_name,
        "accuracy": round(best_cinnamon_score, 2)
    })


# ---------- 🔥 Burnout ----------
def burnout(request):
    result = None

    if request.method == "POST":

        day_type = request.POST.get("day_type")

        if day_type == "Weekend":
            day_type_val = 1
        else:
            day_type_val = 0

        data = [[
            day_type_val,
            float(request.POST.get("work_hours")),
            float(request.POST.get("screen_time_hours")),
            float(request.POST.get("meetings_count")),
            float(request.POST.get("breaks_taken")),
            float(request.POST.get("after_hours_work")),
            float(request.POST.get("sleep_hours")),
            float(request.POST.get("task_completion_rate")),
        ]]

        prediction = best_model.predict(data)

        result = prediction[0]   # 👉 Low / Medium / High

    return render(request, "burnout.html", {
         "result": result,
         "best_name": best_name,
        "best_score": round(best_score, 2)
    })


import os
import numpy as np
from django.shortcuts import render
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from django.conf import settings

# ✅ Load model only once
MODEL_PATH = r'D:\Internship-Project\MLprojects\ml_face_detection\deepfake_model.keras'
model = load_model(MODEL_PATH)

def AI(request):
    context = {}

    if request.method == 'POST' and request.FILES.get('image'):
        img_file = request.FILES['image']

        # ✅ Save image to media folder
        file_path = os.path.join(settings.MEDIA_ROOT, img_file.name)

        with open(file_path, 'wb+') as f:
            for chunk in img_file.chunks():
                f.write(chunk)

        # ✅ Preprocess image (MATCH TRAINING)
        img = image.load_img(file_path, target_size=(128, 128))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # ✅ Prediction
        prediction = model.predict(img_array)[0][0]

        confidence = float(prediction * 100)

        # ✅ Label logic
        if prediction > 0.5:
            label = "Real"
            real_conf = confidence
            fake_conf = 100 - confidence
        else:
            label = "Fake"
            real_conf = 100 - confidence
            fake_conf = confidence

        # ✅ Confidence level
        if max(real_conf, fake_conf) > 85:
            level = "High Confidence"
        elif max(real_conf, fake_conf) > 65:
            level = "Medium Confidence"
        else:
            level = "Low Confidence"

        context = {
            'label': label,
            'real_conf': round(real_conf, 2),
            'fake_conf': round(fake_conf, 2),
            'level': level,
            'image_url': settings.MEDIA_URL + img_file.name
        }

    return render(request, 'AI.html', context)


def user_logout(request):
    logout(request)
    return redirect('landing')