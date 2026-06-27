import json
import os

from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_migrate import Migrate
from sqlalchemy.engine import URL

from core.cenarios import gerar_cenarios
from core.chat import gerar_resposta_chat
from core.ia_explicacao import gerar_explicacao
from core.models import (
    Goal,
    MealSuggestion,
    NutritionPlan,
    PhysicalProfile,
    ProgressCheckIn,
    User,
    db,
)
from core.refeicoes import gerar_refeicao, gerar_todas_refeicoes


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "musculacao_Vitracka")

database_url = os.getenv("DATABASE_URL")
if not database_url:
    db_user = os.getenv("MYSQL_USER", "root")
    db_password = os.getenv("MYSQL_PASSWORD", "p@$$w0rd")
    db_host = os.getenv("MYSQL_HOST", "localhost")
    db_name = os.getenv("MYSQL_DATABASE", "vitracka")
    database_url = URL.create(
        "mysql+pymysql",
        username=db_user,
        password=db_password,
        host=db_host,
        database=db_name,
        query={"charset": "utf8mb4"},
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Entre na sua conta para continuar."
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Banco de dados inicializado.")


def get_current_profile():
    return (
        PhysicalProfile.query.filter_by(user_id=current_user.id)
        .order_by(PhysicalProfile.created_at.desc())
        .first()
    )


def get_current_goal():
    return (
        Goal.query.filter_by(user_id=current_user.id, is_active=True)
        .order_by(Goal.created_at.desc())
        .first()
    )


def get_current_plan():
    return (
        NutritionPlan.query.filter_by(user_id=current_user.id)
        .order_by(NutritionPlan.created_at.desc())
        .first()
    )


def plan_to_template(plan):
    if not plan:
        return None

    return {
        "nome": plan.name,
        "calorias": plan.calories,
        "proteina": plan.protein,
        "carboidratos": plan.carbs,
        "gordura": plan.fat,
    }


def clear_generated_meals():
    session.pop("refeicoes", None)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form["nome"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["senha"]

        if User.query.filter_by(email=email).first():
            flash("Esse e-mail ja esta cadastrado. Entre na sua conta.")
            return redirect(url_for("login"))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("objetivo"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["senha"]
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("E-mail ou senha invalidos.")
            return redirect(url_for("login"))

        login_user(user)
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)

        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    check_ins = (
        ProgressCheckIn.query.filter_by(user_id=current_user.id)
        .order_by(ProgressCheckIn.created_at.desc())
        .limit(8)
        .all()
    )

    return render_template(
        "dashboard.html",
        profile=get_current_profile(),
        goal=get_current_goal(),
        plan=get_current_plan(),
        check_ins=check_ins,
    )


@app.route("/objetivo")
@login_required
def objetivo():
    return render_template("objetivo.html")


@app.route("/salvar-objetivo", methods=["POST"])
@login_required
def salvar_objetivo():
    objective = request.form["objetivo"]
    session["objetivo"] = objective

    Goal.query.filter_by(user_id=current_user.id, is_active=True).update({"is_active": False})
    db.session.add(Goal(user_id=current_user.id, objective=objective))
    db.session.commit()

    return redirect(url_for("dados"))


@app.route("/dados", methods=["GET", "POST"])
@login_required
def dados():
    goal = get_current_goal()

    if request.method == "POST":
        gender = request.form["genero"]
        weight = float(request.form["peso"])
        height = float(request.form["altura"])
        age = int(request.form["idade"])

        session["genero"] = gender
        session["peso"] = weight
        session["altura"] = height
        session["idade"] = age

        db.session.add(
            PhysicalProfile(
                user_id=current_user.id,
                gender=gender,
                weight=weight,
                height=height,
                age=age,
            )
        )
        db.session.commit()

        return redirect(url_for("atividade"))

    return render_template("dados.html", objetivo=goal.objective if goal else None)


@app.route("/atividade", methods=["GET", "POST"])
@login_required
def atividade():
    if request.method == "POST":
        activity_level = request.form["atividade"]
        session["atividade"] = activity_level

        profile = get_current_profile()
        if profile:
            profile.activity_level = activity_level
            db.session.commit()

        return redirect(url_for("calcular"))

    return render_template("atividade.html")


@app.route("/calcular")
@login_required
def calcular():
    profile = get_current_profile()
    goal = get_current_goal()

    if not profile or not goal or not profile.activity_level:
        return redirect(url_for("objetivo"))

    gender = profile.gender
    weight = profile.weight
    height = profile.height
    age = profile.age
    objective = goal.objective
    activity = profile.activity_level

    if gender == "masculino":
        tmb = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        tmb = 10 * weight + 6.25 * height - 5 * age - 161

    factors = {
        "sedentario": 1.2,
        "leve": 1.375,
        "moderado": 1.55,
        "intenso": 1.725,
    }

    tdee = tmb * factors.get(activity, 1.2)
    scenarios = gerar_cenarios(tdee, weight, objective)

    for scenario in scenarios:
        calories = scenario["calorias"]
        protein = weight * scenario["fator_proteina"]
        fat = weight * scenario["fator_gordura"]
        carbs = (calories - (protein * 4 + fat * 9)) / 4

        scenario["proteina"] = round(protein)
        scenario["gordura"] = round(fat)
        scenario["carboidratos"] = round(carbs)
        scenario["calorias"] = round(calories)

    return render_template("resultado.html", cenarios=scenarios)


@app.route("/selecionar-plano", methods=["POST"])
@login_required
def selecionar_plano():
    clear_generated_meals()

    plan = NutritionPlan(
        user_id=current_user.id,
        name=request.form["nome"],
        calories=int(request.form["calorias"]),
        protein=int(request.form["proteina"]),
        carbs=int(request.form["carboidratos"]),
        fat=int(request.form["gordura"]),
    )
    db.session.add(plan)
    db.session.commit()

    session["plano_nome"] = plan.name
    session["plano_calorias"] = plan.calories
    session["plano_proteina"] = plan.protein
    session["plano_carboidratos"] = plan.carbs
    session["plano_gordura"] = plan.fat

    return redirect(url_for("explicacao"))


@app.route("/explicacao")
@login_required
def explicacao():
    plan = get_current_plan()
    profile = get_current_profile()

    if not plan:
        return redirect(url_for("dashboard"))

    template_plan = plan_to_template(plan)
    goal = get_current_goal()

    texto_ia = gerar_explicacao(
        plano=template_plan["nome"],
        objetivo=goal.objective if goal else None,
        peso=profile.weight if profile else None,
        atividade=profile.activity_level if profile else None,
    )

    return render_template("explicacao.html", plano=template_plan, texto_ia=texto_ia)


@app.route("/refeicoes")
@login_required
def refeicoes():
    plan = get_current_plan()

    if not plan:
        return redirect(url_for("dashboard"))

    template_plan = plan_to_template(plan)

    if "refeicoes" not in session:
        saved_meals = (
            MealSuggestion.query.filter_by(user_id=current_user.id, nutrition_plan_id=plan.id)
            .order_by(MealSuggestion.created_at.desc())
            .first()
        )

        if saved_meals:
            session["refeicoes"] = json.loads(saved_meals.meals_json)
        else:
            session["refeicoes"] = gerar_todas_refeicoes(template_plan)
            db.session.add(
                MealSuggestion(
                    user_id=current_user.id,
                    nutrition_plan_id=plan.id,
                    meals_json=json.dumps(session["refeicoes"], ensure_ascii=False),
                )
            )
            db.session.commit()

        session.modified = True

    return render_template("refeicoes.html", plano=template_plan, refeicoes=session["refeicoes"])


@app.route("/regenerar-refeicao", methods=["POST"])
@login_required
def regenerar_refeicao():
    plan = get_current_plan()

    if not plan:
        return redirect(url_for("dashboard"))

    meal_name = request.form["refeicao"]
    template_plan = plan_to_template(plan)
    meals = session.get("refeicoes", {})
    meals[meal_name] = gerar_refeicao(meal_name, template_plan)
    session["refeicoes"] = meals
    session.modified = True

    db.session.add(
        MealSuggestion(
            user_id=current_user.id,
            nutrition_plan_id=plan.id,
            meals_json=json.dumps(meals, ensure_ascii=False),
        )
    )
    db.session.commit()

    return redirect(url_for("refeicoes"))


@app.route("/check-in", methods=["GET", "POST"])
@login_required
def check_in():
    if request.method == "POST":
        waist = request.form.get("cintura", "").strip()
        notes = request.form.get("observacoes", "").strip()

        db.session.add(
            ProgressCheckIn(
                user_id=current_user.id,
                weight=float(request.form["peso"]),
                waist=float(waist) if waist else None,
                notes=notes or None,
            )
        )
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("check_in.html")


@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    if "historico_chat" not in session:
        session["historico_chat"] = []

    if request.method == "POST":
        question = request.form["pergunta"]
        history = session["historico_chat"]
        history.append({"role": "user", "content": question})

        answer = gerar_resposta_chat(history)

        history.append({"role": "assistant", "content": answer})
        session["historico_chat"] = history
        session.modified = True

    return render_template("chat.html", historico=session.get("historico_chat", []))


@app.route("/limpar-chat", methods=["POST"])
@login_required
def limpar_chat():
    session.pop("historico_chat", None)
    return redirect(url_for("chat"))


if __name__ == "__main__":
    app.run(debug=True)
