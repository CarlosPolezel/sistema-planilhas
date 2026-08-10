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
    
    # Módulos do Setor Desma
    if pode_acessar_desma:
        opcoes_menu.extend([
            "🏭 Desmoldante",
            "🏭 Sola Arrancada",
            "🏭 Descarte"
        ])

    if st.session_state['perfil'] in ['Admin', 'Supervisor']:
        opcoes_menu.append("⚙️ Gestão de Usuários")
        
    menu_escolhido = st.sidebar.radio("Navegação", opcoes_menu)
    if st.sidebar.button("Sair"):
        fazer_logout()

    # --- PÁGINAS ---
    if menu_escolhido == "🏠 Início (Setores)":
        st.title("📊 Painel Operacional")
        st.write("Utilize o menu lateral para navegar entre os módulos autorizados.")

    # --- MÓDULO: GESTÃO DE USUÁRIOS ---
    elif menu_escolhido == "⚙️ Gestão de Usuários":
        st.title("⚙️ Gestão de Usuários")
        st.info("Página de Gestão de Usuários configurada anteriormente.")

    # --- MÓDULO: DESMOLDANTE (Com Importação/Exportação) ---
    elif menu_escolhido == "🏭 Desmoldante":
        st.title("🏭 Setor Desma: Desmoldante")
        tab_registro, tab_historico, tab_importacao = st.tabs(["📝 Lançamento", "📋 Histórico", "📤 Importar Planilha"])
        
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
                
                observacao = st.text_area("Observações", max_chars=300)
                if st.form_submit_button("Guardar Registo"):
                    dados = {
                        "data": data_input, "periodo": periodo_input, "pesagem_1": pesagem_1, 
                        "pesagem_2": pesagem_2, "producao": producao, "compacta": compacta,
                        "arrancada": arrancada, "qtd_descarte": qtd_descarte, "observacao": sanitizar_texto(observacao)
                    }
                    db = SessionLocal()
                    try:
                        sucesso, msg = DesmoldanteService(db).registrar_desmoldante(dados, st.session_state['usuario_id'], st.session_state['nome'])
                        if sucesso: st.success(msg)
                        else: st.error(msg)
                    finally:
                        db.close()

        with tab_historico:
            db = SessionLocal()
            try:
                dados_historico = DesmoldanteService(db).obter_historico()
                if dados_historico:
                    df_historico = pd.DataFrame(dados_historico)
                    st.dataframe(df_historico, use_container_width=True, hide_index=True)
                    
                    st.markdown("### Exportar Dados")
                    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
                    
                    with col_btn1:
                        st.download_button(
                            label="📥 Descarregar Excel (.xlsx)",
                            data=exportar_excel(df_historico),
                            file_name=f"desmoldante_{datetime.date.today()}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            on_click=auditar_download,
                            args=("registros_desmoldante",)
                        )
                    
                    with col_btn2:
                        st.download_button(
                            label="📥 Descarregar CSV",
                            data=exportar_csv(df_historico),
                            file_name=f"desmoldante_{datetime.date.today()}.csv",
                            mime="text/csv",
                            on_click=auditar_download,
                            args=("registros_desmoldante",)
                        )
                else:
                    st.info("Sem registos para exportar.")
            finally:
                db.close()

        with tab_importacao:
            st.subheader("Importar Ficheiro CSV ou Excel")
            st.info("Carregue o ficheiro. O sistema validará as linhas e mostrará uma pré-visualização antes de gravar no banco de dados.")
            
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
                        
                        def formatar_status(val):
                            color = '#ff9999' if '❌' in str(val) else '#99ff99'
                            return f'background-color: {color}'
                        
                        st.dataframe(df_preview.style.map(formatar_status, subset=['status']), use_container_width=True, hide_index=True)
                        
                        qtd_validos = len([r for r in resultados_analise if '✅' in r['status']])
                        
                        if qtd_validos > 0:
                            st.success(f"{qtd_validos} registo(s) válido(s) prontos a importar.")
                            if st.button("Confirmar Importação de Registos Válidos"):
                                inseridos = servico.confirmar_importacao(resultados_analise, st.session_state['usuario_id'], st.session_state['nome'])
                                st.success(f"Importação concluída! {inseridos} registo(s) foram adicionados.")
                        else:
                            st.error("Nenhum registo válido encontrado para importar. Verifique os erros assinalados acima.")
                    finally:
                        db.close()
                else:
                    st.error("Não foi possível ler o ficheiro. Verifique se o formato está correto.")

    # --- MÓDULO: SOLA ARRANCADA ---
    elif menu_escolhido == "🏭 Sola Arrancada":
        st.title("🏭 Setor Desma: Sola Arrancada")
        tab_registro, tab_historico = st.tabs(["📝 Novo Lançamento", "📋 Histórico"])
        
        with tab_registro:
            with st.form("form_sola", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    data_input = st.date_input("Data do Registo", datetime.date.today())
                    turno = st.selectbox("Turno", ["1ºT", "2ºT", "3ºT"])
                    maquina = st.selectbox("Máquina", ["Desma 1", "Desma 2", "Desma 3", "Desma 4"])
                with col2:
                    tamanho = st.text_input("Tamanho (Ex: 41)")
                    quantidade = st.number_input("Quantidade", min_value=0, step=1)
                    motivo = st.selectbox("Motivo / Código", ["111", "222", "637", "Outro"])
                
                observacao = st.text_area("Observações (Obrigatório se motivo for 'Outro')", max_chars=300)
                if st.form_submit_button("Guardar Registo"):
                    dados = {
                        "data": data_input, "turno": turno, "maquina": maquina,
                        "tamanho": sanitizar_texto(tamanho), "quantidade": quantidade,
                        "motivo": motivo, "observacao": sanitizar_texto(observacao)
                    }
                    db = SessionLocal()
                    try:
                        sucesso, msg = SolaArrancadaService(db).registrar(dados, st.session_state['usuario_id'], st.session_state['nome'])
                        if sucesso: st.success(msg)
                        else: st.error(msg)
                    finally:
                        db.close()

        with tab_historico:
            db = SessionLocal()
            try:
                dados_historico = SolaArrancadaService(db).obter_historico()
                if dados_historico:
                    st.dataframe(pd.DataFrame(dados_historico), use_container_width=True, hide_index=True)
                else:
                    st.info("Sem registos.")
            finally:
                db.close()

    # --- MÓDULO: DESCARTE ---
    elif menu_escolhido == "🏭 Descarte":
        st.title("🏭 Setor Desma: Descarte")
        tab_registro, tab_historico = st.tabs(["📝 Novo Lançamento", "📋 Histórico"])
        
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
                    quantidade = st.number_input("Quantidade", min_value=0, step=1)
                    ficha = st.text_input("Ficha (Ex: 11111111)")
                
                motivos_descarte = ["Vazao de PU", "Cabedal danificado pela matriz", "Peças faltando", "Sola arrancada", "Outro"]
                motivo = st.selectbox("Motivo do Descarte", motivos_descarte)
                observacao = st.text_area("Observações", max_chars=300)
                
                if st.form_submit_button("Guardar Registo"):
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
                        if sucesso: st.success(msg)
                        else: st.error(msg)
                    finally:
                        db.close()

        with tab_historico:
            db = SessionLocal()
            try:
                dados_historico = DescarteService(db).obter_historico()
                if dados_historico:
                    st.dataframe(pd.DataFrame(dados_historico), use_container_width=True, hide_index=True)
                else:
                    st.info("Sem registos.")
            finally:
                db.close()