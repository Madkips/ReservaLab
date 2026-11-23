from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

import os

app.secret_key = os.environ["SECRET_KEY"]

def criar_banco():

    conexao = sqlite3.connect("reservalab.db")
    cursor = conexao.cursor()

    # Criar tabela de professores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)

    # Criar tabela de laboratórios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS laboratorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            capacidade INTEGER NOT NULL
        )
    """)

    # Verificar se existem laboratórios cadastrados
    cursor.execute("SELECT COUNT(*) FROM laboratorios")

    quantidade = cursor.fetchone()[0]

    # Cadastrar laboratórios iniciais
    if quantidade == 0:

        cursor.execute("""
            INSERT INTO laboratorios (nome, capacidade)
            VALUES (?, ?)
        """, ("Laboratório de Informática 1", 30))

        cursor.execute("""
            INSERT INTO laboratorios (nome, capacidade)
            VALUES (?, ?)
        """, ("Laboratório de Informática 2", 25))

        cursor.execute("""
            INSERT INTO laboratorios (nome, capacidade)
            VALUES (?, ?)
        """, ("Laboratório de Redes", 20))

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER NOT NULL,
                laboratorio_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                horario TEXT NOT NULL,
                FOREIGN KEY (professor_id) REFERENCES professores(id),
                FOREIGN KEY (laboratorio_id) REFERENCES laboratorios(id),
                UNIQUE (laboratorio_id, data, horario)
            )
        """)

    conexao.commit()
    conexao.close()

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        conexao = sqlite3.connect("reservalab.db")
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT id, nome, senha FROM professores WHERE email = ?",
            (email,)
        )

        professor = cursor.fetchone()
        conexao.close()

        if professor and check_password_hash(professor[2], senha):
            session.clear()
            session["professor_id"] = professor[0]
            session["professor_nome"] = professor[1]

            return redirect(url_for("painel"))

        return render_template(
            "mensagem.html",
            titulo="Erro no Login!",
            mensagem="E-mail ou senha incorretos. Verifique seus dados e tente novamente.",
            destino="login",
            texto_botao="Voltar ao Login"
        )

    return render_template("login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar_senha")

        if senha != confirmar_senha:
            return render_template(
                "mensagem.html",
                titulo="Senhas Diferentes!",
                mensagem="As senhas informadas não coincidem. Verifique os dados e tente novamente.",
                destino="cadastro",
                texto_botao="Voltar ao Cadastro"
            )

        if not nome or not email or not senha or not confirmar_senha:
            return render_template(
                "mensagem.html",
                titulo="Campos Obrigatórios!",
                mensagem="Preencha todos os campos do formulário para realizar seu cadastro.",
                destino="cadastro",
                texto_botao="Voltar ao Cadastro"
            )

        senha_protegida = generate_password_hash(senha)

        conexao = sqlite3.connect("reservalab.db")
        cursor = conexao.cursor()

        try:
            cursor.execute("""
                INSERT INTO professores (nome, email, senha)
                VALUES (?, ?, ?)
            """, (nome, email, senha_protegida))

            conexao.commit()

        except sqlite3.IntegrityError:
            return render_template(
                "mensagem.html",
                titulo="E-mail Já Cadastrado!",
                mensagem="Este e-mail já possui uma conta no ReservaLab. Utilize outro e-mail ou faça login.",
                destino="cadastro",
                texto_botao="Voltar ao Cadastro"
            )

        finally:
            conexao.close()

        return render_template(
            "mensagem.html",
            titulo="Cadastro Realizado!",
            mensagem="Sua conta foi criada com sucesso! Agora você pode entrar no sistema.",
            destino="login",
            texto_botao="Ir para o Login"
        )

    return render_template("cadastro.html")

@app.route("/painel")
def painel():

    if "professor_id" not in session:
        return redirect(url_for("login"))

    return render_template("painel.html")

@app.route("/laboratorios")
def laboratorios():

    conexao = sqlite3.connect("reservalab.db")

    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM laboratorios")

    lista_laboratorios = cursor.fetchall()

    conexao.close()

    return render_template(
        "laboratorios.html",
        laboratorios=lista_laboratorios
    )

@app.route("/reserva", methods=["GET", "POST"])
def reserva():

    # Verificar se o professor está logado
    if "professor_id" not in session:
        return redirect(url_for("login"))

    conexao = sqlite3.connect("reservalab.db")
    conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()

    # Quando o professor confirmar a reserva
    if request.method == "POST":

        laboratorio_id = request.form.get("laboratorio_id")
        data = request.form.get("data")
        horario = request.form.get("horario")
        professor_id = session["professor_id"]

        # Verificar se todos os campos foram preenchidos
        if not laboratorio_id or not data or not horario:
            conexao.close()
            return "Preencha todos os campos!"
        
# Verificar se a data da reserva é válida
        try:
            data_reserva = datetime.strptime(data, "%Y-%m-%d").date()
        except ValueError:
            conexao.close()
            return "Data inválida!"

        # Impedir reservas em datas anteriores à atual
        if data_reserva < datetime.now().date():
            conexao.close()
            return render_template(
                "mensagem.html",
                titulo="Data Inválida!",
                mensagem="Não é possível reservar laboratórios em datas passadas. Escolha uma data futura."
            )
        # Impedir reservas em horários que já passaram
        try:
            horario_reserva = datetime.strptime(horario, "%H:%M").time()
        except ValueError:
            conexao.close()
            return "Horário inválido!"

        agora = datetime.now()

        if data_reserva == agora.date() and horario_reserva <= agora.time():
            conexao.close()
            return render_template(
                "mensagem.html",
                titulo="Horário Inválido!",
                mensagem="O horário selecionado já passou. Escolha outro horário disponível."
            )
            conexao.close()
            return render_template(
                "mensagem.html",
                titulo="Data Inválida!",
                mensagem="Não é possível reservar laboratórios em datas passadas. Escolha uma data futura."
            )
        
        # Verificar se o laboratório existe
        cursor.execute(
            "SELECT id FROM laboratorios WHERE id = ?",
            (laboratorio_id,)
        )

        if cursor.fetchone() is None:
            conexao.close()
            return "Laboratório inválido!"

        # Tentar registrar a reserva
        try:
            cursor.execute("""
                INSERT INTO reservas
                (professor_id, laboratorio_id, data, horario)
                VALUES (?, ?, ?, ?)
            """, (professor_id, laboratorio_id, data, horario))

            conexao.commit()
            conexao.close()

            return render_template(
                "mensagem.html",
                titulo="Reserva Confirmada!",
                mensagem="Sua reserva foi realizada com sucesso!"
            )

        except sqlite3.IntegrityError:
            conexao.rollback()
            conexao.close()
            return render_template(
                "mensagem.html",
                titulo="Horário Indisponível!",
                mensagem="Este laboratório já está reservado na data e no horário selecionados. Escolha outro horário."
            ) 

    # Buscar laboratórios disponíveis
    cursor.execute("SELECT * FROM laboratorios")
    laboratorios = cursor.fetchall()

    conexao.close()

    return render_template(
    "reserva.html",
    laboratorios=laboratorios,
    hoje=datetime.now().strftime("%Y-%m-%d")
)

@app.route("/minhas_reservas")
def minhas_reservas():

    if "professor_id" not in session:
        return redirect(url_for("login"))

    professor_id = session["professor_id"]

    conexao = sqlite3.connect("reservalab.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            reservas.id,
            laboratorios.nome,
            reservas.data,
            reservas.horario
        FROM reservas
        INNER JOIN laboratorios
        ON reservas.laboratorio_id = laboratorios.id
        WHERE reservas.professor_id = ?
        ORDER BY reservas.data, reservas.horario
    """, (professor_id,))

    reservas = cursor.fetchall()

    conexao.close()

    return render_template(
        "minhas_reservas.html",
        reservas=reservas
    )

@app.route("/cancelar_reserva/<int:reserva_id>", methods=["POST"])
def cancelar_reserva(reserva_id):

    # Verificar se o professor está conectado
    if "professor_id" not in session:
        return redirect(url_for("login"))

    professor_id = session["professor_id"]

    # Conectar ao banco de dados
    conexao = sqlite3.connect("reservalab.db")
    cursor = conexao.cursor()

    # Excluir somente reservas do professor conectado
    cursor.execute("""
        DELETE FROM reservas
        WHERE id = ? AND professor_id = ?
    """, (reserva_id, professor_id))

    conexao.commit()
    conexao.close()

    # Voltar para a página Minhas Reservas
    return redirect(url_for("minhas_reservas"))

@app.route("/horarios_ocupados")
def horarios_ocupados():

    # Verificar se o professor está logado
    if "professor_id" not in session:
        return jsonify({"erro": "Acesso não autorizado"}), 401

    # Receber laboratório e data
    laboratorio_id = request.args.get("laboratorio_id")
    data = request.args.get("data")

    # Verificar se os campos foram informados
    if not laboratorio_id or not data:
        return jsonify({"horarios_ocupados": []})

    # Conectar ao banco de dados
    conexao = sqlite3.connect("reservalab.db")
    cursor = conexao.cursor()

    # Consultar horários já reservados
    cursor.execute(
        """
        SELECT horario
        FROM reservas
        WHERE laboratorio_id = ? AND data = ?
        """,
        (laboratorio_id, data)
    )

    resultados = cursor.fetchall()

    conexao.close()

    # Criar uma lista com os horários ocupados
    horarios = [resultado[0] for resultado in resultados]

    # Enviar os horários para o navegador
    return jsonify({"horarios_ocupados": horarios})

@app.route("/logout", methods=["POST"])
def logout():

    # Encerrar a sessão do professor
    session.clear()

    # Redirecionar para a página de login
    return redirect(url_for("login"))

if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)