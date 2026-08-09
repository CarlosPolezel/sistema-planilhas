#type: ignore
from sqlalchemy.orm import Session
from database.repositories import RegistroSolaArrancadaRepository, AuditoriaRepository
from database.models import RegistroSolaArrancada

class SolaArrancadaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RegistroSolaArrancadaRepository(db)
        self.audit_repo = AuditoriaRepository(db)

    def registrar(self, dados: dict, usuario_id: int, usuario_nome: str):
        # Regra: Observação obrigatória se o motivo for "Outro"
        if dados['motivo'] == "Outro" and not dados['observacao']:
            return False, "A observação é obrigatória quando o motivo selecionado é 'Outro'."
        
        if dados['quantidade'] < 0:
            return False, "A quantidade não pode ser um valor negativo."

        data_formatada = dados['data'].strftime("%d/%m/%Y")

        novo_registro = RegistroSolaArrancada(
            data=data_formatada,
            maquina=dados['maquina'],
            turno=dados['turno'],
            tamanho=dados['tamanho'],
            quantidade=dados['quantidade'],
            motivo=dados['motivo'],
            observacao=dados['observacao'],
            criado_por=usuario_id,
            atualizado_por=usuario_id
        )
        
        registro_salvo = self.repo.criar(novo_registro)

        self.audit_repo.registrar(
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            acao="REGISTRO_CRIADO",
            entidade="registros_sola_arrancada",
            registro_id=registro_salvo.id,
            detalhes=f"Sola Arrancada: {data_formatada} - Maquina: {dados['maquina']} - Qtd: {dados['quantidade']}"
        )

        return True, "Registo de Sola Arrancada guardado com sucesso!"

    def obter_historico(self):
        registos = self.repo.listar_todos()
        dados = []
        for r in registos:
            dados.append({
                "ID": r.id, "Data": r.data, "Máquina": r.maquina, 
                "Turno": r.turno, "Tamanho": r.tamanho, 
                "Quantidade": r.quantidade, "Motivo": r.motivo, "Observações": r.observacao
            })
        return dados