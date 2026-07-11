from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user

from core.chat import gerar_resposta_chat
from core.models import Conversation, ChatMessage, db

chat_bp = Blueprint("chat", __name__)


def gerar_titulo(pergunta):
    titulo = pergunta.strip()
    if len(titulo) > 40:
        titulo = titulo[:40].rstrip() + "..."
    return titulo


@chat_bp.route("/chat")
@login_required
def chat():
    conversas = (
        Conversation.query.filter_by(user_id=current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    conversa_ativa = conversas[0] if conversas else None

    return render_template(
        "chat.html",
        conversas=conversas,
        conversa_ativa=conversa_ativa,
        mensagens=conversa_ativa.messages if conversa_ativa else [],
    )


@chat_bp.route("/chat/<int:conversation_id>")
@login_required
def abrir_conversa(conversation_id):
    conversas = (
        Conversation.query.filter_by(user_id=current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    conversa_ativa = next(
        (c for c in conversas if c.id == conversation_id), None
    )

    if not conversa_ativa:
        return redirect(url_for("chat.chat"))

    return render_template(
        "chat.html",
        conversas=conversas,
        conversa_ativa=conversa_ativa,
        mensagens=conversa_ativa.messages,
    )


@chat_bp.route("/chat/nova", methods=["POST"])
@login_required
def nova_conversa():
    conversa = Conversation(user_id=current_user.id, title="Nova conversa")
    db.session.add(conversa)
    db.session.commit()
    return jsonify({"conversation_id": conversa.id, "title": conversa.title})


@chat_bp.route("/chat/mensagem", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json()
    question = data.get("pergunta", "").strip()
    conversation_id = data.get("conversation_id")

    if not question:
        return jsonify({"erro": "Mensagem vazia"}), 400

    if conversation_id:
        conversa = Conversation.query.filter_by(
            id=conversation_id, user_id=current_user.id
        ).first()
    else:
        conversa = None

    if not conversa:
        conversa = Conversation(user_id=current_user.id, title=gerar_titulo(question))
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
    })


@chat_bp.route("/chat/<int:conversation_id>/excluir", methods=["POST"])
@login_required
def excluir_conversa(conversation_id):
    conversa = Conversation.query.filter_by(
        id=conversation_id, user_id=current_user.id
    ).first()

    if conversa:
        db.session.delete(conversa)
        db.session.commit()

    return jsonify({"ok": True})

@chat_bp.route("/chat/<int:conversation_id>/mensagens")
@login_required
def mensagens_conversa(conversation_id):
    conversa = Conversation.query.filter_by(
        id=conversation_id, user_id=current_user.id
    ).first()

    if not conversa:
        return jsonify({"erro": "Conversa não encontrada"}), 404

    return jsonify({
        "mensagens": [
            {"role": m.role, "content": m.content} for m in conversa.messages
        ]
    })