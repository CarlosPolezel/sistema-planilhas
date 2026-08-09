#type: ignore
import streamlit as st
from database.connection import SessionLocal
from database.repositories import UsuarioRepository
from services.auth_service import AuthService
from utils.auth import gerar_hash
from utils.validators import validar_username, validar_senha, sanitizar_texto

st.set_page_config(page_title="Sistema Interno de Planilhas", page_icon="📊", layout="wide")

# --- INICIALIZAÇÃO DE SESSÃO DA ETAPA 9 ---
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
            # Lemos todos os dados ANTES de fechar a base de dados
            st.session_state['autenticado'] = True
            st.session_state['usuario_id'] = usuario.id
            st.session_state['nome'] = usuario.nome
            st.session_state['perfil'] = usuario.nivel_acesso
            st.session_state['setor'] = usuario.setor
            st.rerun()
        else:
            st.error(mensagem)
    finally:
        # O 'finally' garante que o db.close() acontece sempre no final, 
        # independentemente de o login ter sucesso ou falhado.
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
    st.write("Insira as suas credenciais para aceder ao sistema de gestão.")
    
    with st.form("form_login"):
        username = st.text_input("Nome de Utilizador")
        password = st.text_input("Palavra-passe", type="password")
        submit = st.form_submit_button("Entrar")
        if submit:
            if username and password:
                realizar_login(username, password)
            else:
                st.warning("Por favor, preencha todos os campos.")

else:
    # --- MENU LATERAL (ROTEAMENTO BASEADO EM PERFIS) ---
    st.sidebar.title(f"Olá, {st.session_state['nome']}")
    st.sidebar.info(f"Perfil: {st.session_state['perfil']} | Setor: {st.session_state['setor']}")
    
    opcoes_menu = ["🏠 Início (Setores)"]
    if st.session_state['perfil'] in ['Admin', 'Supervisor']:
        opcoes_menu.append("⚙️ Gestão de Usuários")
        
    menu_escolhido = st.sidebar.radio("Navegação", opcoes_menu)
    
    if st.sidebar.button("Sair"):
        fazer_logout()

    # --- PÁGINA: INÍCIO (SETORES) ---
    if menu_escolhido == "🏠 Início (Setores)":
        st.title("📊 Painel Operacional")
        st.write("Aceda aos módulos operacionais do seu setor autorizado.")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        pode_acessar_desma = st.session_state['perfil'] == 'Admin' or st.session_state['setor'] in ['Desma', 'Todos']
        
        with col1:
            st.subheader("Setor Desma")
            if pode_acessar_desma:
                st.success("✅ Acesso Permitido")
                st.button("📂 Abrir Módulo Desma", use_container_width=True)
            else:
                st.error("❌ Acesso Bloqueado")
                st.button("🔒 Acesso Restrito", disabled=True, use_container_width=True)
                
        with col2:
            st.subheader("Setor Financeiro")
            st.warning("🚧 Em desenvolvimento")
            st.button("🔒 Acesso Restrito", disabled=True, use_container_width=True)

    # --- PÁGINA: GESTÃO DE USUÁRIOS ---
    elif menu_escolhido == "⚙️ Gestão de Usuários":
        st.title("⚙️ Gestão de Usuários e Auditoria")
        st.write("Cadastre novos utilizadores e controle permissões.")
        
        with st.form("form_novo_usuario"):
            novo_nome = st.text_input("Nome Completo")
            novo_username = st.text_input("Nome de Utilizador")
            nova_senha = st.text_input("Palavra-passe", type="password")
            
            niveis_disponiveis = ["Padrao"]
            if st.session_state['perfil'] == 'Admin':
                niveis_disponiveis.extend(["Supervisor", "Admin"])
                
            novo_nivel = st.selectbox("Nível de Acesso", niveis_disponiveis)
            novo_setor = st.selectbox("Setor", ["Desma", "Financeiro", "RH", "Todos"])
            
            submit_novo = st.form_submit_button("Cadastrar Utilizador")
            
            if submit_novo:
                if novo_nome and novo_username and nova_senha:
                    nome_seguro = sanitizar_texto(novo_nome)
                    user_valido, user_msg = validar_username(novo_username)
                    senha_valida, senha_msg = validar_senha(nova_senha)
                    
                    if not user_valido:
                        st.error(user_msg)
                    elif not senha_valida:
                        st.error(senha_msg)
                    else:
                        db = SessionLocal()
                        user_repo = UsuarioRepository(db)
                        
                        if user_repo.buscar_por_username(novo_username):
                            st.error("Este Nome de Utilizador já está registado!")
                        else:
                            from database.models import Usuario
                            novo_usuario = Usuario(
                                nome=nome_seguro,
                                username=novo_username,
                                senha_hash=gerar_hash(nova_senha),
                                nivel_acesso=novo_nivel,
                                setor=novo_setor,
                                ativo=True
                            )
                            user_repo.criar(novo_usuario)
                            st.success(f"Utilizador '{novo_username}' criado com sucesso!")
                        db.close()
                else:
                    st.warning("Preencha todos os campos do formulário.")