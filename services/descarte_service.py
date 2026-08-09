#type: ignore
from sqlalchemy.orm import Session
from database.repositories import RegistroDescarteRepository, AuditoriaRepository
from database.models import RegistroDescarte

class DescarteService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RegistroDescarteRepository(db)
        self.audit_repo = AuditoriaRepository(db)

    def registrar(self, dados: dict, usuario_id: int, usuario_nome: str):
        if dados['quantidade'] < 0:
            return False, "A quantidade não pode ser negativa."

        data_formatada = dados['data'].strftime("%d/%m/%Y")

        novo_registro = RegistroDescarte(
            data=data_formatada,
            maquina=dados['maquina'],
            turno=dados['turno'],
            matriz=dados['matriz'],
            modelo=dados['modelo'],
            reduzido=dados['reduzido'],
            tamanho=dados['tamanho'],
            quantidade=dados['quantidade'],
            motivo=dados['motivo'],
            ficha=dados['ficha'],
            observacao=dados['observacao'],
            criado_por=usuario_id,
            atualizado_por=usuario_id
        )
        
        registro_salvo = self.repo.criar(novo_registro)

        self.audit_repo.registrar(
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            acao="REGISTRO_CRIADO",
            entidade="registros_descarte",
            registro_id=registro_salvo.id,
            detalhes=f"Descarte: {data_formatada} - Ficha: {dados['ficha']} - Motivo: {dados['motivo']}"
        )

        return True, "Registo de Descarte guardado com sucesso!"

    def obter_historico(self):
        registos = self.repo.listar_todos()
        dados = []
        for r in registos:
            dados.append({
                "ID": r.id, "Data": r.data, "Máquina": r.maquina, "Turno": r.turno,
                "Matriz": r.matriz, "Modelo": r.modelo, "Reduzido": r.reduzido,
                "Tamanho": r.tamanho, "Quantidade": r.quantidade, "Motivo": r.motivo,
                "Ficha": r.ficha, "Observações": r.observacao
            })
        return dados