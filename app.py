#type: ignore
import streamlit as st
import pandas as pd
import datetime
from database.connection import SessionLocal
from database.repositories import UsuarioRepository
from services.auth_service import AuthService
from services.desmoldante_service import DesmoldanteService
from utils.auth import gerar_hash
from utils.validators import validar_username, validar_senha, sanitizar_texto

st.set_page_config(page_title="Sistema Interno de Planilhas", page_icon="📊", layout="wide")

# --- INICIALIZAÇÃO DE SESSÃO ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'usuario_id' not in st.session_state:
    st.session_state['usuario_id'] = None
if 'nome' not in st.session_state:
    st.session_state['nome'] = ""
if 'perfil' not in st.session_state:
    st.session_state['perfil'] = ""
if 'setor' not in st.session_state:
    st.session_state['setor'] = ""

def realizar_login(username, password):
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        sucesso, mensagem, usuario = auth_service.autenticar(username, password)
        if sucesso:
            st.session_state['autenticado'] = True
            st.session_state['usuario_id'] = usuario.id
            st.session_state['nome'] = usuario.nome
            st.session_state['perfil'] = usuario.nivel_acesso
            st.session_state['setor'] = usuario.setor
            st.rerun()
        else:
            st.error(mensagem)
    finally:
        db.close()

def fazer_logout():
    if st.session_state['autenticado']:
        db = SessionLocal()
        auth_service = AuthService(db)
        auth_service.registrar_logout(st.session_state['usuario_id'], st.session_state['nome'])
        db.close()

    st.session_state['autenticado'] = False
    st.session_state['usuario_id'] = None
    st.session_state['nome'] = ""
    st.session_state['perfil'] = ""
    st.session_state['setor'] = ""
    st.rerun()

# --- INTERFACE ---
if not st.session_state['autenticado']:
    st.title("🔒 Acesso ao Sistema")
    with st.form("form_login"):
        username = st.text_input("Nome de Utilizador")
        password = st.text_input("Palavra-passe", type="password")
        submit = st.form_submit_button("Entrar")
        if submit:
            realizar_login(username, password)

else:
    # --- ROTEAMENTO E PERMISSÕES ---
    st.sidebar.title(f"Olá, {st.session_state['nome']}")
    st.sidebar.info(f"Perfil: {st.session_state['perfil']} | Setor: {st.session_state['setor']}")
    
    opcoes_menu = ["🏠 Início (Setores)"]
    pode_acessar_desma = st.session_state['perfil'] == 'Admin' or st.session_state['setor'] in ['Desma', 'Todos']
    
    # Exibe o módulo de desmoldante apenas para quem tem permissão no setor Desma
    if pode_acessar_desma:
        opcoes_menu.append("🏭 Módulo: Desmoldante")

    if st.session_state['perfil'] in ['Admin', 'Supervisor']:
        opcoes_menu.append("⚙️ Gestão de Usuários")
        
    menu_escolhido = st.sidebar.radio("Navegação", opcoes_menu)
    if st.sidebar.button("Sair"):
        fazer_logout()

    # --- PÁGINAS ---
    if menu_escolhido == "🏠 Início (Setores)":
        st.title("📊 Painel Operacional")
        st.write("Utilize o menu lateral para navegar entre os módulos autorizados.")

    elif menu_escolhido == "⚙️ Gestão de Usuários":
        st.title("⚙️ Gestão de Usuários")
        st.write("Funcionalidade de registo operacional a decorrer noutra página.")
        # (Aqui manteve-se o formulário de utilizador, omitido para focar na parte nova, mas não apague o seu código original desta aba)
        st.info("Página de Gestão já configurada anteriormente.")

    # --- NOVO MÓDULO: DESMOLDANTE ---
    elif menu_escolhido == "🏭 Módulo: Desmoldante":
        st.title("🏭 Setor Desma: Registo de Desmoldante")
        st.write("Insira e consulte os dados diários do processo de Desmoldante.")
        
        tab_registro, tab_historico = st.tabs(["📝 Novo Lançamento", "📋 Histórico de Lançamentos"])
        
        with tab_registro:
            with st.form("form_desmoldante", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    data_input = st.date_input("Data do Registo", datetime.date.today())
                    periodo_input = st.selectbox("Período", ["Manha", "Tarde", "Noite"])
                    pesagem_1 = st.number_input("Pesagem Inicial (kg)", min_value=0.0, format="%.3f")
                    pesagem_2 = st.number_input("Pesagem Final (kg)", min_value=0.0, format="%.3f")
                
                with col2:
                    producao = st.number_input("Produção Total", min_value=0, step=1)
                    compacta = st.number_input("Sola Compacta", min_value=0, step=1)
                    arrancada = st.number_input("Sola Arrancada", min_value=0, step=1)
                    qtd_descarte = st.number_input("Quantidade Descarte", min_value=0, step=1)
                
                observacao = st.text_area("Observações (Exigido em caso de anomalia)", max_chars=300)
                
                submit_desmoldante = st.form_submit_button("Guardar Registo")
                
                if submit_desmoldante:
                    dados = {
                        "data": data_input, "periodo": periodo_input,
                        "pesagem_1": pesagem_1, "pesagem_2": pesagem_2,
                        "producao": producao, "compacta": compacta,
                        "arrancada": arrancada, "qtd_descarte": qtd_descarte,
                        "observacao": sanitizar_texto(observacao)
                    }
                    
                    db = SessionLocal()
                    try:
                        servico = DesmoldanteService(db)
                        sucesso, msg = servico.registrar_desmoldante(
                            dados, st.session_state['usuario_id'], st.session_state['nome']
                        )
                        if sucesso:
                            st.success(msg)
                        else:
                            st.error(msg)
                    finally:
                        db.close()

        with tab_historico:
            st.subheader("Base de Dados Recente")
            db = SessionLocal()
            try:
                servico = DesmoldanteService(db)
                historico_dados = servico.obter_historico()
                if historico_dados:
                    # Usamos o Pandas para renderizar uma tabela bonita e interativa
                    df = pd.DataFrame(historico_dados)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("Ainda não existem registos lançados no sistema.")
            finally:
                db.close()