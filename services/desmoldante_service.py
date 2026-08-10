#type: ignore
from sqlalchemy.orm import Session
from database.repositories import RegistroDesmoldanteRepository, AuditoriaRepository
from database.models import RegistroDesmoldante

class DesmoldanteService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RegistroDesmoldanteRepository(db)
        self.audit_repo = AuditoriaRepository(db)

    def registrar_desmoldante(self, dados: dict, usuario_id: int, usuario_nome: str):
        # 1. Validação de Regra de Negócio
        if dados['pesagem_1'] < 0 or dados['pesagem_2'] < 0:
            return False, "As pesagens não podem ser valores negativos."
        
        # 2. Cálculos Automáticos
        diferenca = abs(dados['pesagem_1'] - dados['pesagem_2'])
        
        meses_pt = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 
                    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        
        data_formatada = dados['data'].strftime("%d/%m/%Y")
        mes_nome = meses_pt[dados['data'].month]
        ano = dados['data'].year

        # 3. Criação do Modelo
        novo_registro = RegistroDesmoldante(
            data=data_formatada,
            periodo=dados['periodo'],
            mes=mes_nome,
            ano=ano,
            pesagem_1=dados['pesagem_1'],
            pesagem_2=dados['pesagem_2'],
            diferenca=diferenca,
            producao=dados['producao'],
            compacta=dados['compacta'],
            arrancada=dados['arrancada'],
            qtd_descarte=dados['qtd_descarte'],
            observacao=dados['observacao'],
            criado_por=usuario_id,
            atualizado_por=usuario_id
        )
        
        # 4. Guardar na Base de Dados
        registro_salvo = self.repo.criar(novo_registro)

        # 5. Auditoria de Lançamento (Transparente para o utilizador)
        self.audit_repo.registrar(
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            acao="REGISTRO_CRIADO",
            entidade="registros_desmoldante",
            registro_id=registro_salvo.id,
            detalhes=f"Lançamento Desmoldante: {data_formatada} ({dados['periodo']}) - Produção: {dados['producao']}"
        )

        return True, "Registo guardado com sucesso!"

    def obter_historico(self):
        # Busca os dados e formata-os para serem lidos pelo Pandas no ecrã
        registos = self.repo.listar_todos()
        dados = []
        for r in registos:
            dados.append({
                "ID": r.id,
                "Data": r.data,
                "Período": r.periodo,
                "Mês": r.mes,
                "Ano": r.ano,
                "Pesagem 1 (kg)": r.pesagem_1,
                "Pesagem 2 (kg)": r.pesagem_2,
                "Diferença (kg)": round(r.diferenca, 3),
                "Produção": r.producao,
                "Compacta": r.compacta,
                "Arrancada": r.arrancada,
                "Descarte": r.qtd_descarte,
                "Observações": r.observacao
            })
        return dados

    def analisar_importacao(self, df):
        """Analisa o DataFrame carregado e devolve uma lista com o status de cada linha."""
        resultados = []
        
        # O Pandas renomeia colunas duplicadas (ex: duas colunas 'pesagem' viram 'pesagem' e 'pesagem.1')
        for index, row in df.iterrows():
            linha_valida = True
            motivo_erro = ""
            
            try:
                data_val = str(row.get('data', ''))
                periodo_val = str(row.get('periodo', '')).capitalize()
                
                # Regras de Negócio Básicas
                if not data_val or not periodo_val:
                    linha_valida, motivo_erro = False, "Data ou Período ausentes"
                elif periodo_val not in ["Manha", "Tarde", "Noite"]:
                    linha_valida, motivo_erro = False, "Período inválido"
                else:
                    # Verificação de Duplicados (Mesma data e período já existem no banco?)
                    duplicado = self.db.query(RegistroDesmoldante).filter(
                        RegistroDesmoldante.data == data_val,
                        RegistroDesmoldante.periodo == periodo_val
                    ).first()
                    
                    if duplicado:
                        linha_valida, motivo_erro = False, "Duplicado: Registo já existe no sistema"
                
                # Recolhe os dados normalizados (ajuste para as colunas do seu CSV)
                dados_linha = {
                    "linha_excel": index + 2, # +2 por causa do cabeçalho e índice 0
                    "data": data_val,
                    "periodo": periodo_val,
                    "pesagem_1": float(row.get('pesagem', 0)),
                    "pesagem_2": float(row.get('pesagem.1', 0)), # Segunda coluna 'pesagem'
                    "producao": int(row.get('producao', 0)),
                    "compacta": int(row.get('compacta', 0)),
                    "arrancada": int(row.get('arrancada', 0)),
                    "qtd_descarte": int(row.get('qtd descarte', 0)),
                    "status": "✅ Válido" if linha_valida else f"❌ Inválido ({motivo_erro})"
                }
                resultados.append(dados_linha)
                
            except ValueError:
                resultados.append({
                    "linha_excel": index + 2, "data": row.get('data'), "periodo": row.get('periodo'),
                    "status": "❌ Inválido (Erro de formatação/Tipo de dado incorreto)"
                })
                
        return resultados

    def confirmar_importacao(self, dados_validos: list, usuario_id: int, usuario_nome: str):
        """Insere apenas os registos válidos e dispara a auditoria."""
        registos_inseridos = 0
        from datetime import datetime
        
        meses_pt = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 
                    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

        for d in dados_validos:
            if "✅ Válido" in d['status']:
                # Converte string DD/MM/YYYY para extrair mês e ano
                try:
                    dt = datetime.strptime(d['data'], "%d/%m/%Y")
                    mes_nome = meses_pt[dt.month]
                    ano = dt.year
                except:
                    mes_nome, ano = "Desconhecido", 0
                
                diferenca = abs(d['pesagem_1'] - d['pesagem_2'])

                novo_registro = RegistroDesmoldante(
                    data=d['data'], periodo=d['periodo'], mes=mes_nome, ano=ano,
                    pesagem_1=d['pesagem_1'], pesagem_2=d['pesagem_2'], diferenca=diferenca,
                    producao=d['producao'], compacta=d['compacta'], arrancada=d['arrancada'],
                    qtd_descarte=d['qtd_descarte'], observacao="Importado via ficheiro",
                    criado_por=usuario_id, atualizado_por=usuario_id
                )
                self.repo.criar(novo_registro)
                registos_inseridos += 1

        self.audit_repo.registrar(
            usuario_id=usuario_id, usuario_nome=usuario_nome,
            acao="IMPORTACAO_REALIZADA", entidade="registros_desmoldante",
            detalhes=f"Importados {registos_inseridos} registos com sucesso."
        )
        return registos_inseridos