import streamlit as st
import pandas as pd
import datetime
from database.connection import SessionLocal
from services.auth_service import AuthService
from services.desmoldante_service import DesmoldanteService
from services.sola_arrancada_service import SolaArrancadaService
from services.descarte_service import DescarteService
from utils.auth import gerar_hash
from utils.validators import validar_username, validar_senha, sanitizar_texto
from utils.excel_handler import exportar_excel, exportar_csv, ler_arquivo_importacao

st.set_page_config(page_title="Sistema Interno de Planilhas", layout="wide")

# CSS Customizado para aplicar os tons semânticos e textos secundários da Bracol
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Cinza-texto para textos secundários e metadados */
    .texto-secundario {
        color: #8a8f9a !important;
        font-size: 0.9em;
    }
    .texto-metadado {
        color: #6a6f7a !important;
        font-size: 0.8em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    /* Força o texto do botão primário (Vermelho Bracol) a ser Branco absoluto */
    button[kind="primary"] {
        color: #ffffff !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

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
        try:
            auth_service = AuthService(db)
            auth_service.registrar_logout(st.session_state['usuario_id'], st.session_state['nome'])
        finally:
            db.close()

    st.session_state['autenticado'] = False
    for key in ['usuario_id', 'nome', 'perfil', 'setor']:
        st.session_state[key] = ""
    st.rerun()

def auditar_download(modulo):
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        auth_service.registrar_exportacao(st.session_state['usuario_id'], st.session_state['nome'], modulo)
    finally:
        db.close()

# --- INTERFACE ---
if not st.session_state['autenticado']:
    st.title("Acesso ao Sistema")
    st.markdown('<p class="texto-secundario">Insira as suas credenciais para aceder ao ambiente operacional.</p>', unsafe_allow_html=True)
    with st.form("form_login"):
        username = st.text_input("Nome de Utilizador")
        password = st.text_input("Palavra-passe", type="password")
        submit = st.form_submit_button("Entrar")
        if submit:
            realizar_login(username, password)

else:
    # --- ROTEAMENTO E PERMISSÕES ---
    st.sidebar.markdown('<p class="texto-metadado">Módulo Interno</p>', unsafe_allow_html=True)
    st.sidebar.title(f"Olá, {st.session_state['nome']}")
    st.sidebar.markdown(f'<p class="texto-secundario">Perfil: {st.session_state["perfil"]} | Setor: {st.session_state["setor"]}</p>', unsafe_allow_html=True)
    
    opcoes_menu = ["Início (Setores)"]
    pode_acessar_desma = st.session_state['perfil'] == 'Admin' or st.session_state['setor'] in ['Desma', 'Todos']
    
    if pode_acessar_desma:
        opcoes_menu.extend(["Desmoldante", "Sola Arrancada", "Descarte"])

    if st.session_state['perfil'] in ['Admin', 'Supervisor']:
        opcoes_menu.append("Gestão de Usuários")
        
    menu_escolhido = st.sidebar.radio("Navegação", opcoes_menu)
    st.sidebar.markdown("---")
    if st.sidebar.button("Sair da Sessão"):
        fazer_logout()

    # --- PÁGINAS ---
    if menu_escolhido == "Início (Setores)":
        st.title("Painel Operacional Central")
        st.markdown('<p class="texto-secundario">Acompanhe os indicadores corporativos e aceda aos seus módulos.</p>', unsafe_allow_html=True)
        st.markdown("---")

        st.subheader("Resumo do Dia (Setor Desma)")
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        col_kpi1.metric(label="Produção Estimada", value="1.240 pares", delta="12% acima da meta")
        col_kpi2.metric(label="Solas Arrancadas", value="34 pares", delta="-5 (melhoria)", delta_color="inverse")
        col_kpi3.metric(label="Descartes Registados", value="12 pares", delta="Estável", delta_color="off")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Mapa da Fábrica")

        # --- LINHA 1 ---
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            with st.container(border=True):
                st.markdown("### Desma")
                st.markdown('<p class="texto-secundario">Gestão de desmoldante, solas e descartes.</p>', unsafe_allow_html=True)
                if pode_acessar_desma:
                    st.success("Acesso Autorizado")
                else:
                    st.error("Acesso Restrito")
                    
        with col_s2:
            with st.container(border=True):
                st.markdown("### Gusbi 8")
                st.markdown('<p class="texto-secundario">Controlo de produção e injeção.</p>', unsafe_allow_html=True)
                st.info("Em desenvolvimento")
                
        with col_s3:
            with st.container(border=True):
                st.markdown("### Gusbi 12")
                st.markdown('<p class="texto-secundario">Controlo de produção e injeção.</p>', unsafe_allow_html=True)
                st.info("Em desenvolvimento")

        # --- LINHA 2 ---
        col_s4, col_s5, col_s6 = st.columns(3)
        with col_s4:
            with st.container(border=True):
                st.markdown("### Gusbi 32")
                st.markdown('<p class="texto-secundario">Controlo de produção e injeção.</p>', unsafe_allow_html=True)
                st.info("Em desenvolvimento")
                
        with col_s5:
            with st.container(border=True):
                st.markdown("### Corte")
                st.markdown('<p class="texto-secundario">Gestão de materiais e matrizes.</p>', unsafe_allow_html=True)
                st.info("Em desenvolvimento")
                
        with col_s6:
            with st.container(border=True):
                st.markdown("### Almoxarifado")
                st.markdown('<p class="texto-secundario">Controlo de stock e entrega de materiais.</p>', unsafe_allow_html=True)
                st.info("Em desenvolvimento")

        # --- LINHA 3 ---
        col_s7, col_s8, col_s9 = st.columns(3)
        with col_s7:
            with st.container(border=True):
                st.markdown("### Expedição")
                st.markdown('<p class="texto-secundario">Logística de saída e envios.</p>', unsafe_allow_html=True)
                st.info("Em desenvolvimento")
                
        with col_s8:
            with st.container(border=True):
                st.markdown("### Manutenção")
                st.markdown('<p class="texto-secundario">Ordens de serviço e reparação de máquinas.</p>', unsafe_allow_html=True)
                st.info("Em desenvolvimento")
                
        with col_s9:
            st.empty() 

    # --- MÓDULO: GESTÃO DE USUÁRIOS ---
    elif menu_escolhido == "Gestão de Usuários":
        st.title("Gestão de Usuários e Auditoria")
        st.markdown('<p class="texto-secundario">Cadastre novos utilizadores e controle permissões.</p>', unsafe_allow_html=True)
        
        with st.form("form_novo_usuario"):
            novo_nome = st.text_input("Nome Completo")
            novo_username = st.text_input("Nome de Utilizador")
            nova_senha = st.text_input("Palavra-passe", type="password")
            
            niveis_disponiveis = ["Padrao"]
            if st.session_state['perfil'] == 'Admin':
                niveis_disponiveis.extend(["Supervisor", "Admin"])
                
            novo_nivel = st.selectbox("Nível de Acesso", niveis_disponiveis)
            novo_setor = st.selectbox("Setor", ["Desma", "Financeiro", "RH", "Todos"])
            
            submit_novo = st.form_submit_button("Adicionar Registro")
            
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
                        try:
                            from database.repositories import UsuarioRepository
                            from database.models import Usuario
                            user_repo = UsuarioRepository(db)
                            
                            if user_repo.buscar_por_username(novo_username):
                                st.error("Este Nome de Utilizador já está registado!")
                            else:
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
                        finally:
                            db.close()
                else:
                    st.warning("Preencha todos os campos do formulário.")

    # --- MÓDULO: DESMOLDANTE ---
    elif menu_escolhido == "Desmoldante":
        st.title("Setor Desma: Desmoldante")
        tab_registro, tab_historico, tab_importacao = st.tabs(["Lançamento", "Histórico", "Importar Planilha"])
        
        with tab_registro:
            with st.form("form_desmoldante", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    data_input = st.date_input("Data do Registo", datetime.date.today())
                    periodo_input = st.selectbox("Período", ["Manha", "Tarde", "Noite"])
                    pesagem_1 = st.number_input("Pesagem Inicial (kg)", min_value=0.0, format="%.3f")
                    pesagem_2 = st.number_input("Pesagem Final (kg)", min_value=0.0, format="%.3f")
                with col2:
                    producao = st.number_input("Produção Total (Pares)", min_value=0, step=1)
                    compacta = st.number_input("Sola Compacta", min_value=0, step=1)
                    arrancada = st.number_input("Sola Arrancada", min_value=0, step=1)
                    qtd_descarte = st.number_input("Quantidade Descarte", min_value=0, step=1)
                
                observacao = st.text_area("Observações", max_chars=300)
                if st.form_submit_button("Adicionar Registro"):
                    dados = {
                        "data": data_input, "periodo": periodo_input, "pesagem_1": pesagem_1, 
                        "pesagem_2": pesagem_2, "producao": producao, "compacta": compacta,
                        "arrancada": arrancada, "qtd_descarte": qtd_descarte, "observacao": sanitizar_texto(observacao)
                    }
                    db = SessionLocal()
                    try:
                        sucesso, msg = DesmoldanteService(db).registrar_desmoldante(dados, st.session_state['usuario_id'], st.session_state['nome'])
                        if sucesso: st.toast(msg)
                        else: st.error(msg)
                    finally:
                        db.close()

        with tab_historico:
            db = SessionLocal()
            try:
                dados_historico = DesmoldanteService(db).obter_historico()
                if dados_historico:
                    df_historico = pd.DataFrame(dados_historico).fillna("-")
                    st.dataframe(df_historico, use_container_width=True, hide_index=True)
                    
                    st.markdown("### Exportar Dados")
                    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
                    
                    with col_btn1:
                        st.download_button(
                            label="Descarregar Excel (.xlsx)",
                            data=exportar_excel(df_historico),
                            file_name=f"desmoldante_{datetime.date.today()}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            on_click=auditar_download,
                            args=("registros_desmoldante",)
                        )
                    with col_btn2:
                        st.download_button(
                            label="Descarregar CSV",
                            data=exportar_csv(df_historico),
                            file_name=f"desmoldante_{datetime.date.today()}.csv",
                            mime="text/csv",
                            on_click=auditar_download,
                            args=("registros_desmoldante",)
                        )
                else:
                    st.markdown('<p class="texto-secundario">Nenhum registro encontrado para exportação.</p>', unsafe_allow_html=True)
            finally:
                db.close()

        with tab_importacao:
            st.subheader("Importar Ficheiro CSV ou Excel")
            st.markdown('<p class="texto-secundario">Carregue o ficheiro. O sistema validará as linhas e mostrará uma pré-visualização.</p>', unsafe_allow_html=True)
            
            arquivo_upload = st.file_uploader("Selecione o ficheiro", type=['csv', 'xlsx'])
            
            if arquivo_upload is not None:
                extensao = arquivo_upload.name.split('.')[-1].lower()
                df = ler_arquivo_importacao(arquivo_upload, extensao)
                
                if df is not None and not df.empty:
                    db = SessionLocal()
                    try:
                        servico = DesmoldanteService(db)
                        resultados_analise = servico.analisar_importacao(df)
                        df_preview = pd.DataFrame(resultados_analise)
                        
                        st.markdown("### Pré-visualização da Validação")
                        
                        # Mapeamento estrito usando o Vermelho Bracol e o Verde Semântico
                        def formatar_status(val):
                            color = '#E24B4A' if 'Inválido' in str(val) else '#6dd58c'
                            text_color = '#ffffff' if 'Inválido' in str(val) else '#0d1117' # Contraste para o verde claro
                            return f'background-color: {color}; color: {text_color}; font-weight: bold;'
                        
                        st.dataframe(df_preview.style.map(formatar_status, subset=['status']), use_container_width=True, hide_index=True)
                        
                        qtd_validos = len([r for r in resultados_analise if 'Válido' in r['status'] and 'Inválido' not in r['status']])
                        
                        if qtd_validos > 0:
                            st.success(f"{qtd_validos} registo(s) válido(s) prontos a importar.")
                            if st.button("Confirmar Importação de Registos Válidos"):
                                inseridos = servico.confirmar_importacao(resultados_analise, st.session_state['usuario_id'], st.session_state['nome'])
                                st.toast(f"Sincronizado: {inseridos} registo(s) adicionados.")
                        else:
                            st.error("Nenhum registo válido encontrado. Verifique os erros.")
                    finally:
                        db.close()

    # --- MÓDULO: SOLA ARRANCADA ---
    elif menu_escolhido == "Sola Arrancada":
        st.title("Setor Desma: Sola Arrancada")
        tab_registro, tab_historico = st.tabs(["Lançamento", "Histórico"])
        
        with tab_registro:
            with st.form("form_sola", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    data_input = st.date_input("Data do Registo", datetime.date.today())
                    turno = st.selectbox("Turno", ["1ºT", "2ºT", "3ºT"])
                    maquina = st.selectbox("Máquina", ["Desma 1", "Desma 2", "Desma 3", "Desma 4"])
                with col2:
                    tamanho = st.text_input("Tamanho (Ex: 41)")
                    quantidade = st.number_input("Quantidade (Pares)", min_value=0, step=1)
                    motivo = st.selectbox("Motivo / Código", ["111", "222", "637", "Outro"])
                
                observacao = st.text_area("Observações (Obrigatório se motivo for 'Outro')", max_chars=300)
                if st.form_submit_button("Adicionar Registro"):
                    dados = {
                        "data": data_input, "turno": turno, "maquina": maquina,
                        "tamanho": sanitizar_texto(tamanho), "quantidade": quantidade,
                        "motivo": motivo, "observacao": sanitizar_texto(observacao)
                    }
                    db = SessionLocal()
                    try:
                        sucesso, msg = SolaArrancadaService(db).registrar(dados, st.session_state['usuario_id'], st.session_state['nome'])
                        if sucesso: st.toast(msg)
                        else: st.error(msg)
                    finally:
                        db.close()

        with tab_historico:
            db = SessionLocal()
            try:
                dados_historico = SolaArrancadaService(db).obter_historico()
                if dados_historico:
                    df_historico = pd.DataFrame(dados_historico).fillna("-")
                    st.dataframe(df_historico, use_container_width=True, hide_index=True)
                else:
                    st.markdown('<p class="texto-secundario">Nenhum registro encontrado.</p>', unsafe_allow_html=True)
            finally:
                db.close()

    # --- MÓDULO: DESCARTE ---
    elif menu_escolhido == "Descarte":
        st.title("Setor Desma: Descarte")
        tab_registro, tab_historico = st.tabs(["Lançamento", "Histórico"])
        
        with tab_registro:
            with st.form("form_descarte", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    data_input = st.date_input("Data do Registo", datetime.date.today())
                    turno = st.selectbox("Turno", ["1ºT", "2ºT", "3ºT"])
                    maquina = st.selectbox("Máquina", ["Desma 1", "Desma 2", "Desma 3", "Desma 4"])
                with col2:
                    matriz = st.text_input("Matriz (Ex: 4031)")
                    modelo = st.text_input("Modelo (Ex: BAEN)")
                    reduzido = st.text_input("Reduzido (Ex: 40123360)")
                with col3:
                    tamanho = st.text_input("Tamanho (Ex: 44)")
                    quantidade = st.number_input("Quantidade (Pares)", min_value=0, step=1)
                    ficha = st.text_input("Ficha (Ex: 11111111)")
                
                motivos_descarte = ["Vazao de PU", "Cabedal danificado pela matriz", "Peças faltando", "Sola arrancada", "Outro"]
                motivo = st.selectbox("Motivo do Descarte", motivos_descarte)
                observacao = st.text_area("Observações", max_chars=300)
                
                if st.form_submit_button("Adicionar Registro"):
                    dados = {
                        "data": data_input, "turno": turno, "maquina": maquina,
                        "matriz": sanitizar_texto(matriz), "modelo": sanitizar_texto(modelo),
                        "reduzido": sanitizar_texto(reduzido), "tamanho": sanitizar_texto(tamanho),
                        "quantidade": quantidade, "motivo": motivo, "ficha": sanitizar_texto(ficha),
                        "observacao": sanitizar_texto(observacao)
                    }
                    db = SessionLocal()
                    try:
                        sucesso, msg = DescarteService(db).registrar(dados, st.session_state['usuario_id'], st.session_state['nome'])
                        if sucesso: st.toast(msg)
                        else: st.error(msg)
                    finally:
                        db.close()

        with tab_historico:
            db = SessionLocal()
            try:
                dados_historico = DescarteService(db).obter_historico()
                if dados_historico:
                    df_historico = pd.DataFrame(dados_historico).fillna("-")
                    st.dataframe(df_historico, use_container_width=True, hide_index=True)
                else:
                    st.markdown('<p class="texto-secundario">Nenhum registro encontrado.</p>', unsafe_allow_html=True)
            finally:
                db.close()