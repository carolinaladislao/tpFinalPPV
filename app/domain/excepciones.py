class ErrorDeDominio(Exception):
    pass

class DatoInvalidoError(ErrorDeDominio):
    pass

class JustificacionVaciaError(DatoInvalidoError):
    pass

class AvisoNoPendienteError(ErrorDeDominio):
    pass


class AvisoYaEvaluadoError(ErrorDeDominio):
    pass

def texto_obligatorio(valor, campo):
    #UN texto vacío o solo espacios cuenta como que no lo completaron
    if not valor or not valor.strip():
        raise DatoInvalidoError(f"Falta completar: {campo}")
    return valor
