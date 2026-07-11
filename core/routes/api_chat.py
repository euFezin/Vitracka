from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.chat import gerar_resposta_chat
from core.models import Conversation, ChatMessage, db

api_chat_bp = Blueprint("api_chat", __name__, url_prefix="/api")


def gerar_titulo(pergunta):
    titulo = pergunta.strip()
    if len(titulo) > 40:
        titulo = titulo[:40].rstrip() + "..."
    return titulo


@api_chat_bp.route("/conversas", methods=["GET"])
@jwt_required()
def api_listar_conversas():
    user_id = int(get_jwt_identity())
    conversas = (
        Conversation.query.filter_by(user_id=user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    return jsonify({
        "conversas": [
            {"id": c.id, "titulo": c.title} for c in conversas
        ]
    }), 200


@api_chat_bp.route("/conversas/<int:conversation_id>/mensagens", methods=["GET"])
@jwt_required()
def api_mensagens_conversa(conversation_id):
    user_id = int(get_jwt_identity())
    conversa = Conversation.query.filter_by(
        id=conversation_id, user_id=user_id
    ).first()

    if not conversa:
        return jsonify({"erro": "Conversa nao encontrada."}), 404

    return jsonify({
        "mensagens": [
            {"role": m.role, "content": m.content} for m in conversa.messages
        ]
    }), 200


@api_chat_bp.route("/chat", methods=["POST"])
@jwt_required()
def api_chat_mensagem():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    question = data.get("pergunta", "").strip() if data else ""
    conversation_id = data.get("conversation_id") if data else None

    if not question:
        return jsonify({"erro": "Mensagem vazia."}), 400

    if conversation_id:
        conversa = Conversation.query.filter_by(
            id=conversation_id, user_id=user_id
        ).first()
    else:
        conversa = None

    if not conversa:
        conversa = Conversation(user_id=user_id, title=gerar_titulo(question))
        db.session.add(conversa)
        db.session.commit()
    elif conversa.title == "Nova conversa":
        conversa.title = gerar_titulo(question)

    db.session.add(
        ChatMessage(conversation_id=conversa.id, role="user", content=question)
    )
    db.session.commit()

    historico = [
        {"role": m.role, "content": m.content} for m in conversa.messages
    ]

    answer = gerar_resposta_chat(historico)

    db.session.add(
        ChatMessage(conversation_id=conversa.id, role="assistant", content=answer)
    )
    conversa.updated_at = db.func.now()
    db.session.commit()

    return jsonify({
        "answer": answer,
        "conversation_id": conversa.id,
        "title": conversa.title,
    }), 200


@api_chat_bp.route("/conversas/<int:conversation_id>/excluir", methods=["POST"])
@jwt_required()
def api_excluir_conversa(conversation_id):
    user_id = int(get_jwt_identity())
    conversa = Conversation.query.filter_by(
        id=conversation_id, user_id=user_id
    ).first()

    if conversa:
        db.session.delete(conversa)
        db.session.commit()

    return jsonify({"ok": True}), 200