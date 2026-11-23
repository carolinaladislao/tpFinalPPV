from abc import ABC, abstractmethod


# Catálogos cerrados (§3 y §4 de la consigna).
# Por ahora solo responden su nombre; cuando lleguen las misiones
# TipoSituacion va a tener que decir qué misiones admite.

class TipoSituacion(ABC):
    @abstractmethod
    def nombre(self):
        pass


class Inundacion(TipoSituacion):
    def nombre(self):
        return "inundación"


class Incendio(TipoSituacion):
    def nombre(self):
        return "incendio"


class AccidenteVial(TipoSituacion):
    def nombre(self):
        return "accidente vial"


class Gravedad(ABC):
    @abstractmethod
    def nombre(self):
        pass


class Baja(Gravedad):
    def nombre(self):
        return "baja"


class Media(Gravedad):
    def nombre(self):
        return "media"


class Alta(Gravedad):
    def nombre(self):
        return "alta"
