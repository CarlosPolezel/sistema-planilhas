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