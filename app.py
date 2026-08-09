#type: ignore
import streamlit as st

# 1. Configuração inicial da página (deve ser o primeiro comando do Streamlit)
# Define o título da aba do navegador, o ícone e usa o layout "wide" para ocupar mais espaço na tela.
st.set_page_config(
    page_title="Sistema Interno de Planilhas",
    page_icon="📊",
    layout="wide"
)

# 2. Barra lateral (Sidebar)
# O Streamlit facilita a criação de menus laterais. Usaremos isso no futuro para navegação.
st.sidebar.title("Menu de Navegação")
st.sidebar.info("As opções de menu e setores aparecerão aqui após o login.")

# 3. Cabeçalho e Título Principal
st.title("📊 Sistema Interno de Gestão de Planilhas")
st.markdown("---") # Cria uma linha horizontal de separação

# 4. Ambiente de QA (Testes)
st.header("Página Inicial (Ambiente de QA)")
st.write(
    "Bem-vindo! Este é o ambiente de testes da interface do sistema. "
    "O objetivo é facilitar a manipulação e o preenchimento de planilhas de forma restrita e padronizada."
)

# 5. Simulação de Regras de Negócio e Setores
st.subheader("Visão de Setores (Simulação visual)")
st.info(
    "Nenhuma regra de banco de dados ou permissão está ativa no momento. "
    "No futuro, a renderização abaixo será dinâmica com base no nível de acesso do usuário logado."
)

# 6. Layout em Colunas
# Aqui usamos st.columns para dividir a tela. O bloco 'with' garante que o que está dentro 
# seja renderizado apenas na respectiva coluna.
col1, col2, col3 = st.columns(3)

with col1:
    # Simulando o setor 'Desma' mencionado no README
    st.button("📂 Acessar Setor Desma", use_container_width=True)

with col2:
    # Simulando um setor sem permissão (botão desabilitado)
    st.button("🔒 Setor B (Acesso Restrito)", disabled=True, use_container_width=True)

with col3:
    # Simulando a área de supervisão/admin
    st.button("⚙️ Painel do Supervisor", disabled=True, use_container_width=True)