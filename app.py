import streamlit as st
import pandas as pd
import json
import os

# =========================
# FUNÇÕES
# =========================

def load(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

ING_PATH = "data/ingredientes.json"
REC_PATH = "data/receitas.json"
USER_PATH = "data/usuarios.json"

ingredientes = load(ING_PATH)
receitas = load(REC_PATH)
usuarios = load(USER_PATH)

# =========================
# LOGIN
# =========================

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🍫 ChocoJoy Login")

    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        for u in usuarios:
            if u["username"] == user and u["password"] == pwd:
                st.session_state.logado = True
                st.success("Login realizado!")
                st.rerun()
        st.error("Credenciais inválidas")

    st.stop()

# =========================
# APP
# =========================

st.title("🍰 ChocoJoy - Gestão de Confeitaria")

menu = st.sidebar.selectbox("Menu", ["Ingredientes", "Receitas", "Simulação", "Logout"])

# =========================
# INGREDIENTES
# =========================

if menu == "Ingredientes":
    st.header("Ingredientes")

    nome = st.text_input("Nome")
    preco = st.number_input("Preço", min_value=0.0)
    unidade = st.selectbox("Unidade", ["kg", "g", "L", "ml", "un"])

    if st.button("Adicionar"):
        ingredientes.append({"nome": nome, "preco": preco, "unidade": unidade})
        save(ING_PATH, ingredientes)
        st.success("Adicionado!")

    st.subheader("Lista")

    for i, ing in enumerate(ingredientes):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.write(ing["nome"])
        with col2:
            st.write(ing["preco"])
        with col3:
            st.write(ing["unidade"])

        with col4:
            if st.button("🗑️", key=f"del_ing_{i}"):
                ingredientes.pop(i)
                save(ING_PATH, ingredientes)
                st.rerun()

# =========================
# RECEITAS
# =========================

elif menu == "Receitas":
    st.header("Receitas")

    nome_receita = st.text_input("Nome da receita")

    if ingredientes:
        nomes = [i["nome"] for i in ingredientes]
        ing_sel = st.selectbox("Ingrediente", nomes)
        qtd = st.number_input("Quantidade", min_value=0.0)

        if "temp" not in st.session_state:
            st.session_state.temp = []

        if st.button("Adicionar item"):
            st.session_state.temp.append({"nome": ing_sel, "quantidade": qtd})

        if st.session_state.temp:
            st.dataframe(pd.DataFrame(st.session_state.temp))

        if st.button("Salvar receita"):
            receitas.append({
                "nome": nome_receita,
                "itens": st.session_state.temp
            })
            save(REC_PATH, receitas)
            st.session_state.temp = []
            st.success("Receita salva!")

    st.subheader("Receitas cadastradas")

    for i, r in enumerate(receitas):
        col1, col2 = st.columns([3,1])

        with col1:
            st.write(r["nome"])

        with col2:
            if st.button("🗑️", key=f"del_rec_{i}"):
                receitas.pop(i)
                save(REC_PATH, receitas)
                st.rerun()

# =========================
# SIMULAÇÃO
# =========================

elif menu == "Simulação":
    st.header("Precificação")

    if receitas:
        nomes = [r["nome"] for r in receitas]
        escolha = st.selectbox("Receita", nomes)

        receita = next(r for r in receitas if r["nome"] == escolha)

        custo = 0

        for item in receita["itens"]:
            ing = next(i for i in ingredientes if i["nome"] == item["nome"])
            custo += ing["preco"] * item["quantidade"]

        margem = st.slider("Margem (%)", 0, 300, 100)

        preco = custo * (1 + margem/100)

        st.metric("Custo", f"R$ {custo:.2f}")
        st.metric("Preço sugerido", f"R$ {preco:.2f}")

# =========================
# LOGOUT
# =========================

elif menu == "Logout":
    st.session_state.logado = False
    st.rerun()