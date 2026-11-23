import uuid
from abc import ABC, abstractmethod

from app.domain.catalogos import Gravedad, TipoSituacion
from app.domain.excepciones import (
    AvisoNoPendienteError,
    AvisoYaEvaluadoError,
    DatoInvalidoError,
    JustificacionVaciaError,
    texto_obligatorio,
)


def fecha_obligatoria(valor, campo):
    if valor is None:
        raise DatoInvalidoError(f"Falta la {campo}")
    return valor



class Ubicacion():
    def __init__(self, descripcion):
        self._descripcion = texto_obligatorio(descripcion, "ubicación")

    @property
    def descripcion(self):
        return self._descripcion


class Nota():
    def __init__(self, autor, texto, escrita_en):
        self._autor = texto_obligatorio(autor, "autor de la nota")
        self._texto = texto_obligatorio(texto, "texto de la nota")
        self._escrita_en = fecha_obligatoria(escrita_en, "fecha de la nota")

    @property
    def autor(self):
        return self._autor

    @property
    def texto(self):
        return self._texto

    @property
    def escrita_en(self):
        return self._escrita_en


class Descarte():
    def __init__(self, justificacion, descartado_en):
        if not justificacion or not justificacion.strip():
            raise JustificacionVaciaError("Para descartar un aviso hay que justificarlo")
        self._justificacion = justificacion
        self._descartado_en = fecha_obligatoria(descartado_en, "fecha del descarte")

    @property
    def justificacion(self):
        return self._justificacion

    @property
    def descartado_en(self):
        return self._descartado_en


#ESTADOS DEL AVISOS
# Cada estado decide qué se puede hacer y devuelve el estado siguiente.
# El único que guarda el estado es el aviso.

class EstadoAviso(ABC):
    @abstractmethod
    def nombre(self):
        pass

    @abstractmethod
    def verificar_admite_notas(self):
        pass

    @abstractmethod
    def descartar(self, justificacion, fecha):
        pass

    def descarte(self):
        return None


class Pendiente(EstadoAviso):
    def nombre(self):
        return "pendiente"

    def verificar_admite_notas(self):
        pass

    def descartar(self, justificacion, fecha):
        return Descartado(Descarte(justificacion, fecha))


class Aceptado(EstadoAviso):
    def __init__(self, aceptado_en):
        self._aceptado_en = fecha_obligatoria(aceptado_en, "fecha de aceptación")

    @property
    def aceptado_en(self):
        return self._aceptado_en

    def nombre(self):
        return "aceptado"

    def verificar_admite_notas(self):
        raise AvisoNoPendienteError("El aviso ya fue aceptado, no admite notas")

    def descartar(self, justificacion, fecha):
        raise AvisoYaEvaluadoError("El aviso ya fue aceptado, no se puede descartar")


class Descartado(EstadoAviso):
    def __init__(self, descarte):
        self._descarte = descarte

    def nombre(self):
        return "descartado"

    def verificar_admite_notas(self):
        raise AvisoNoPendienteError("El aviso fue descartado, no admite notas")

    def descartar(self, justificacion, fecha):
        raise AvisoYaEvaluadoError("El aviso ya fue descartado")

    def descarte(self):
        return self._descarte




class Aviso():
    def __init__(self, id, reportante, ubicacion, tipo, gravedad_estimada,
                 descripcion, registrado_en, estado, notas):
        # la consigna pide que un valor fuera del catálogo no llegue al aviso, por eso uso isinstance
        if not isinstance(tipo, TipoSituacion):
            raise DatoInvalidoError("El tipo de situación no está en el catálogo")
        if not isinstance(gravedad_estimada, Gravedad):
            raise DatoInvalidoError("La gravedad no está en el catálogo")

        self._id = texto_obligatorio(id, "id del aviso")
        self._reportante = texto_obligatorio(reportante, "reportante")
        self._ubicacion = ubicacion
        self._tipo = tipo
        self._gravedad_estimada = gravedad_estimada
        self._descripcion = texto_obligatorio(descripcion, "descripción")
        self._registrado_en = fecha_obligatoria(registrado_en, "fecha de registro")
        self._estado = estado
        self._notas = list(notas)

    @classmethod
    def registrar(cls, reportante, ubicacion, tipo, gravedad_estimada, descripcion, registrado_en):
        # camino normal: todo aviso nace pendiente y sin notas (R1)
        return cls(str(uuid.uuid4()), reportante, ubicacion, tipo, gravedad_estimada,
                   descripcion, registrado_en, Pendiente(), [])

    @classmethod
    def reconstruir(cls, id, reportante, ubicacion, tipo, gravedad_estimada,
                    descripcion, registrado_en, estado, notas):
        # Para volver a armar un aviso tal como estaba guardado (lo va a usar el
        # repositorio). No cambia el estado de ningún aviso que ya exista.
        return cls(id, reportante, ubicacion, tipo, gravedad_estimada,
                   descripcion, registrado_en, estado, notas)

    # --- consultas ---

    @property
    def id(self):
        return self._id

    @property
    def reportante(self):
        return self._reportante

    @property
    def ubicacion(self):
        return self._ubicacion

    @property
    def tipo(self):
        return self._tipo

    @property
    def gravedad_estimada(self):
        return self._gravedad_estimada

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def registrado_en(self):
        return self._registrado_en

    @property
    def estado(self):
        return self._estado

    @property
    def notas(self):
        return tuple(self._notas)  

    @property
    def descarte(self):
        return self._estado.descarte()


    def agregar_nota(self, autor, texto, fecha):
        # primero se verifica todo, después se modifica
        self._estado.verificar_admite_notas() #delego en estado
        nota = Nota(autor, texto, fecha)
        self._notas.append(nota)
        return nota

    def descartar(self, justificacion, fecha):
     # si el estado o el descarte rechazan, la excepción sale antes de la asignación
        self._estado = self._estado.descartar(justificacion, fecha)
