# Sistema interno de gestão de planilhas

Protótipo em Python para registrar e consultar dados operacionais, com interface Streamlit, persistência em SQLite via SQLAlchemy e importação e exportação de planilhas.

## Executar localmente

Com Python 3.13 ou superior, execute na pasta do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python init_db.py
python -m streamlit run app.py
```

No Linux ou macOS, ative o ambiente com `source .venv/bin/activate`. Na primeira execução, `init_db.py` cria as tabelas e pede uma senha para o usuário `admin`. Use esse usuário e a senha escolhida para entrar no aplicativo pelo endereço exibido no terminal.

Por padrão, o banco é criado em `sistema.db` na pasta do projeto. Use dados fictícios em demonstrações.
