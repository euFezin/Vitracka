from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from core.models import db

from core.models import User

api_auth_bp = Blueprint("api_auth", __name__, url_prefix="/api")


@api_auth_bp.route("/login", methods=["POST"])
def api_login():
    data = request.get_json()

    if not data or "email" not in data or "senha" not in data:
        return jsonify({"erro": "Email e senha sao obrigatorios."}), 400

    email = data["email"].strip().lower()
    password = data["senha"]

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"erro": "Email ou senha invalidos."}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": access_token,
        "usuario": {
            "id": user.id,
            "nome": user.name,
            "email": user.email
        }
    }), 200
    
@api_auth_bp.route("/cadastro", methods=["POST"])
def api_cadastro():
    data = request.get_json()

    if not data or "nome" not in data or "email" not in data or "senha" not in data:
        return jsonify({"erro": "Nome, email e senha sao obrigatorios."}), 400

    name = data["nome"].strip()
    email = data["email"].strip().lower()
    password = data["senha"]

    if not name or not email or len(password) < 6:
        return jsonify({"erro": "Dados invalidos. A senha deve ter pelo menos 6 caracteres."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"erro": "Esse email ja esta cadastrado."}), 409

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": access_token,
        "usuario": {
            "id": user.id,
            "nome": user.name,
            "email": user.email
        }
    }), 201    

@api_auth_bp.route("/me", methods=["GET"])
@jwt_required()
def api_me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({"erro": "Usuario nao encontrado."}), 404

    return jsonify({
        "id": user.id,
        "nome": user.name,
        "email": user.email
    }), 200