#type: ignore
from utils.auth import verificar_senha, gerar_hash
from utils.validators import validar_username, validar_senha, sanitizar_texto
#type: ignore
import streamlit as st
from database.connection import SessionLocal
from database.models import Usuario

st.set_page_config(page_title="Sistema Interno de Planilhas", page_icon="📊", layout="wide")

# --- INICIALIZAÇÃO DE SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario_nome'] = ""
    st.session_state['nivel_acesso'] = ""
    st.session_state['setor'] = ""

def realizar_login(username, password):
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    db.close()
    
    if usuario and verificar_senha(password, usuario.senha_hash):
        st.session_state['logado'] = True
        st.session_state['usuario_nome'] = usuario.nome
        st.session_state['nivel_acesso'] = usuario.nivel_acesso
        st.session_state['setor'] = usuario.setor
        st.rerun()
    else:
        st.error("Utilizador ou palavra-passe incorretos.")

def fazer_logout():
    for key in ['logado', 'usuario_nome', 'nivel_acesso', 'setor']:
        st.session_state[key] = ""
    st.session_state['logado'] = False
    st.rerun()

# --- INTERFACE ---
if not st.session_state['logado']:
    st.title("🔒 Acesso ao Sistema")
    with st.form("form_login"):
        username = st.text_input("Nome de Utilizador")
        password = st.text_input("Palavra-passe", type="password")
        submit = st.form_submit_button("Entrar")
        if submit:
            if username and password:
                realizar_login(username, password)
            else:
                st.warning("Preencha ambos os campos.")

else:
    # --- MENU LATERAL (ROTEAMENTO) ---
    st.sidebar.title(f"Olá, {st.session_state['usuario_nome']}")
    st.sidebar.info(f"Nível: {st.session_state['nivel_acesso']} | Setor: {st.session_state['setor']}")
    
    # Define o que o utilizador pode ver no menu
    opcoes_menu = ["🏠 Início (Setores)"]
    if st.session_state['nivel_acesso'] in ['Admin', 'Supervisor']:
        opcoes_menu.append("⚙️ Gestão de Usuários")
        
    menu_escolhido = st.sidebar.radio("Navegação", opcoes_menu)
    
    if st.sidebar.button("Sair"):
        fazer_logout()

    # --- PÁGINA: INÍCIO (SETORES) ---
    if menu_escolhido == "🏠 Início (Setores)":
        st.title("📊 Painel de Planilhas")
        st.write("Selecione o setor para inserir dados. Só tem acesso aos setores autorizados para o seu perfil.")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        # Regra de negócio: Admin acede a tudo. Utilizador normal só acede ao seu próprio setor.
        pode_acessar_desma = st.session_state['nivel_acesso'] == 'Admin' or st.session_state['setor'] == 'Desma'
        
        with col1:
            st.subheader("Setor Desma")
            if pode_acessar_desma:
                st.success("✅ Acesso Permitido")
                st.button("📂 Abrir Planilhas Desma", use_container_width=True)
            else:
                st.error("❌ Acesso Bloqueado")
                st.button("🔒 Abrir Planilhas Desma", disabled=True, use_container_width=True)
                
        with col2:
            st.subheader("Setor Financeiro (Exemplo)")
            st.warning("🚧 Em desenvolvimento")
            st.button("🔒 Acesso Restrito", disabled=True, use_container_width=True)

    # --- PÁGINA: GESTÃO DE USUÁRIOS (APENAS ADMIN/SUPERVISOR) ---
    elif menu_escolhido == "⚙️ Gestão de Usuários":
        st.title("⚙️ Gestão de Usuários")
        st.write("Adicione novos funcionários e defina as suas permissões.")
        
        with st.form("form_novo_usuario"):
            novo_nome = st.text_input("Nome Completo")
            novo_username = st.text_input("Nome de Utilizador (Login)")
            nova_senha = st.text_input("Palavra-passe provisória", type="password")
            
            # Supervisores não podem criar outros Administradores, apenas Padrão ou Supervisores.
            niveis_disponiveis = ["Padrao"]
            if st.session_state['nivel_acesso'] == 'Admin':
                niveis_disponiveis.extend(["Supervisor", "Admin"])
                
            novo_nivel = st.selectbox("Nível de Acesso", niveis_disponiveis)
            novo_setor = st.selectbox("Setor", ["Desma", "Financeiro", "RH", "Todos"])
            
            submit_novo = st.form_submit_button("Cadastrar Utilizador")
            
            if submit_novo:
                if novo_nome and novo_username and nova_senha:
                    # 1. Sanitiza os textos para evitar XSS
                    nome_seguro = sanitizar_texto(novo_nome)
                    
                    # 2. Valida o Username
                    user_valido, user_msg = validar_username(novo_username)
                    # 3. Valida a Senha
                    senha_valida, senha_msg = validar_senha(nova_senha)
                    
                    if not user_valido:
                        st.error(user_msg)
                    elif not senha_valida:
                        st.error(senha_msg)
                    else:
                        # Se passou por todas as validações de segurança, prossegue com o banco
                        db = SessionLocal()
                        existe = db.query(Usuario).filter(Usuario.username == novo_username).first()
                        
                        if existe:
                            st.error("Este Nome de Utilizador já está em uso!")
                        else:
                            senha_hash = gerar_hash(nova_senha)
                            novo_usuario = Usuario(
                                nome=nome_seguro,
                                username=novo_username,
                                senha_hash=senha_hash,
                                nivel_acesso=novo_nivel,
                                setor=novo_setor
                            )
                            db.add(novo_usuario)
                            db.commit()
                            st.success(f"Utilizador '{novo_username}' criado com sucesso, obedecendo às políticas de segurança!")
                        db.close()
                else:
                    st.warning("Por favor, preencha todos os campos do formulário.")