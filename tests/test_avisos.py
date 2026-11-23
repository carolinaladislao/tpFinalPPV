from datetime import datetime

import pytest

from app.domain.avisos import Aceptado, Aviso, Descartado, Nota, Pendiente, Ubicacion
from app.domain.catalogos import Alta, Incendio, Inundacion, Media
from app.domain.excepciones import (
    AvisoNoPendienteError,
    AvisoYaEvaluadoError,
    DatoInvalidoError,
    JustificacionVaciaError,
)


# ---------- R1: un aviso nace pendiente con todos sus datos ----------

def test_r1_aviso_registrado_esta_pendiente_sin_notas_y_sin_descarte():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    assert isinstance(aviso.estado, Pendiente)
    assert aviso.notas == ()
    assert aviso.descarte is None


def test_r1_aviso_registrado_conserva_todos_sus_datos():
    ubicacion = Ubicacion("Ruta 3 km 2800")
    tipo = Incendio()
    gravedad = Alta()
    aviso = Aviso.registrar("rep-01", ubicacion, tipo, gravedad,
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    assert aviso.reportante == "rep-01"
    assert aviso.ubicacion is ubicacion
    assert aviso.tipo is tipo
    assert aviso.gravedad_estimada is gravedad
    assert aviso.descripcion == "Humo en el bosque"
    assert aviso.registrado_en == datetime(2026, 11, 22, 10, 0)
    assert aviso.id != ""


def test_r1_dos_avisos_con_los_mismos_datos_son_avisos_distintos():
    primero = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                              "Humo en el bosque", datetime(2026, 11, 22, 10, 0))
    segundo = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                              "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    assert primero.id != segundo.id


def test_r1_rechaza_aviso_sin_descripcion():
    with pytest.raises(DatoInvalidoError):
        Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                        "   ", datetime(2026, 11, 22, 10, 0))


def test_r1_rechaza_aviso_sin_reportante():
    with pytest.raises(DatoInvalidoError):
        Aviso.registrar("", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                        "Humo en el bosque", datetime(2026, 11, 22, 10, 0))


def test_r1_rechaza_ubicacion_vacia():
    with pytest.raises(DatoInvalidoError):
        Ubicacion("")


def test_r1_rechaza_gravedad_fuera_del_catalogo():
    with pytest.raises(DatoInvalidoError):
        Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), "altísima",
                        "Humo en el bosque", datetime(2026, 11, 22, 10, 0))


def test_r1_rechaza_tipo_fuera_del_catalogo():
    with pytest.raises(DatoInvalidoError):
        Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), "terremoto", Alta(),
                        "Humo en el bosque", datetime(2026, 11, 22, 10, 0))


def test_r1_rechaza_aviso_sin_fecha_de_registro():
    with pytest.raises(DatoInvalidoError):
        Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                        "Humo en el bosque", None)


# ---------- R2: notas mientras el aviso está pendiente ----------

def test_r2_nota_en_aviso_pendiente_conserva_autor_fecha_y_hora():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    nota = aviso.agregar_nota("rep-01", "Se ven llamas", datetime(2026, 11, 22, 10, 15))

    assert aviso.notas == (nota,)
    assert nota.autor == "rep-01"
    assert nota.texto == "Se ven llamas"
    assert nota.escrita_en == datetime(2026, 11, 22, 10, 15)


def test_r2_dos_notas_se_conservan_en_el_orden_en_que_llegaron():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    primera = aviso.agregar_nota("rep-01", "Se ven llamas", datetime(2026, 11, 22, 10, 15))
    segunda = aviso.agregar_nota("rep-01", "El viento cambió", datetime(2026, 11, 22, 10, 40))

    assert aviso.notas == (primera, segunda)


def test_r2_rechaza_nota_sin_texto_y_las_notas_no_cambian():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    with pytest.raises(DatoInvalidoError):
        aviso.agregar_nota("rep-01", "  ", datetime(2026, 11, 22, 10, 15))

    assert aviso.notas == ()


def test_r2_rechaza_nota_sin_autor():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    with pytest.raises(DatoInvalidoError):
        aviso.agregar_nota("", "Se ven llamas", datetime(2026, 11, 22, 10, 15))

    assert aviso.notas == ()


def test_r2_las_notas_no_se_pueden_agregar_por_fuera_del_aviso():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    with pytest.raises(AttributeError):
        aviso.notas.append(Nota("rep-01", "Nota trucha", datetime(2026, 11, 22, 11, 0)))

    assert aviso.notas == ()


def test_r2_una_nota_no_se_puede_modificar():
    nota = Nota("rep-01", "Se ven llamas", datetime(2026, 11, 22, 10, 15))

    with pytest.raises(AttributeError):
        nota.texto = "Otro texto"

    assert nota.texto == "Se ven llamas"


# ---------- R3: agregar notas no cambia los datos originales ----------

def test_r3_agregar_nota_no_cambia_los_datos_originales():
    ubicacion = Ubicacion("Ruta 3 km 2800")
    tipo = Incendio()
    gravedad = Alta()
    aviso = Aviso.registrar("rep-01", ubicacion, tipo, gravedad,
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    aviso.agregar_nota("rep-01", "En realidad es una inundación", datetime(2026, 11, 22, 10, 15))

    assert aviso.ubicacion is ubicacion
    assert aviso.tipo is tipo
    assert aviso.gravedad_estimada is gravedad
    assert aviso.descripcion == "Humo en el bosque"
    assert aviso.reportante == "rep-01"
    assert aviso.registrado_en == datetime(2026, 11, 22, 10, 0)


def test_r3_los_datos_originales_no_se_pueden_reemplazar_desde_afuera():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    with pytest.raises(AttributeError):
        aviso.descripcion = "Otra cosa"
    with pytest.raises(AttributeError):
        aviso.gravedad_estimada = Media()

    assert aviso.descripcion == "Humo en el bosque"
    assert aviso.gravedad_estimada.nombre() == "alta"


# ---------- R4: descartar exige justificación ----------

def test_r4_descartar_con_justificacion_conserva_justificacion_y_fecha():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    aviso.descartar("Era una quema autorizada", datetime(2026, 11, 22, 11, 0))

    assert isinstance(aviso.estado, Descartado)
    assert aviso.descarte.justificacion == "Era una quema autorizada"
    assert aviso.descarte.descartado_en == datetime(2026, 11, 22, 11, 0)


@pytest.mark.parametrize("justificacion", ["", "    "])
def test_r4_r6_justificacion_vacia_se_rechaza_y_el_aviso_sigue_pendiente(justificacion):
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    with pytest.raises(JustificacionVaciaError):
        aviso.descartar(justificacion, datetime(2026, 11, 22, 11, 0))

    assert isinstance(aviso.estado, Pendiente)
    assert aviso.descarte is None


def test_r4_un_aviso_pendiente_rechazado_por_justificacion_vacia_se_puede_descartar_bien_despues():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))

    with pytest.raises(JustificacionVaciaError):
        aviso.descartar("", datetime(2026, 11, 22, 11, 0))
    aviso.descartar("Aviso duplicado", datetime(2026, 11, 22, 11, 5))

    assert aviso.descarte.justificacion == "Aviso duplicado"


# ---------- R5: un aviso que ya no está pendiente rechaza notas y evaluaciones ----------

def test_r5_r6_aviso_descartado_rechaza_nuevas_notas_y_las_notas_no_cambian():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))
    nota = aviso.agregar_nota("rep-01", "Se ven llamas", datetime(2026, 11, 22, 10, 15))
    aviso.descartar("Era una quema autorizada", datetime(2026, 11, 22, 11, 0))

    with pytest.raises(AvisoNoPendienteError):
        aviso.agregar_nota("rep-01", "Ahora hay más humo", datetime(2026, 11, 22, 11, 30))

    assert aviso.notas == (nota,)


def test_r5_r6_segundo_descarte_se_rechaza_y_conserva_la_justificacion_original():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))
    aviso.descartar("Era una quema autorizada", datetime(2026, 11, 22, 11, 0))

    with pytest.raises(AvisoYaEvaluadoError):
        aviso.descartar("Otro motivo", datetime(2026, 11, 22, 12, 0))

    assert aviso.descarte.justificacion == "Era una quema autorizada"
    assert aviso.descarte.descartado_en == datetime(2026, 11, 22, 11, 0)


def test_r5_aviso_aceptado_rechaza_nuevas_notas():
    # aceptar todavía no está implementado: se arma el aviso ya aceptado,
    # como lo haría el repositorio al leerlo de la base
    aviso = Aviso.reconstruir("av-07", "rep-01", Ubicacion("Barrio Centro"), Inundacion(), Media(),
                              "Calle anegada", datetime(2026, 11, 22, 9, 0),
                              Aceptado(datetime(2026, 11, 22, 9, 30)), [])

    with pytest.raises(AvisoNoPendienteError):
        aviso.agregar_nota("rep-01", "Sube el agua", datetime(2026, 11, 22, 10, 0))

    assert aviso.notas == ()


def test_r5_r6_aviso_aceptado_rechaza_descarte_y_sigue_aceptado():
    aviso = Aviso.reconstruir("av-07", "rep-01", Ubicacion("Barrio Centro"), Inundacion(), Media(),
                              "Calle anegada", datetime(2026, 11, 22, 9, 0),
                              Aceptado(datetime(2026, 11, 22, 9, 30)), [])

    with pytest.raises(AvisoYaEvaluadoError):
        aviso.descartar("Ya no hace falta", datetime(2026, 11, 22, 10, 0))

    assert isinstance(aviso.estado, Aceptado)
    assert aviso.descarte is None


def test_r5_aviso_reconstruido_conserva_las_notas_que_tenia():
    nota = Nota("rep-01", "Sube el agua", datetime(2026, 11, 22, 9, 10))
    aviso = Aviso.reconstruir("av-07", "rep-01", Ubicacion("Barrio Centro"), Inundacion(), Media(),
                              "Calle anegada", datetime(2026, 11, 22, 9, 0),
                              Aceptado(datetime(2026, 11, 22, 9, 30)), [nota])

    assert aviso.notas == (nota,)
    assert aviso.id == "av-07"


# ---------- R6: una operación rechazada no deja cambios ----------

def test_r6_nota_invalida_en_aviso_descartado_no_cambia_nada():
    aviso = Aviso.registrar("rep-01", Ubicacion("Ruta 3 km 2800"), Incendio(), Alta(),
                            "Humo en el bosque", datetime(2026, 11, 22, 10, 0))
    aviso.descartar("Era una quema autorizada", datetime(2026, 11, 22, 11, 0))

    with pytest.raises(AvisoNoPendienteError):
        aviso.agregar_nota("rep-01", "", datetime(2026, 11, 22, 11, 30))

    assert aviso.notas == ()
    assert isinstance(aviso.estado, Descartado)


def test_r6_descarte_rechazado_en_aviso_aceptado_no_importa_la_justificacion():
    aviso = Aviso.reconstruir("av-07", "rep-01", Ubicacion("Barrio Centro"), Inundacion(), Media(),
                              "Calle anegada", datetime(2026, 11, 22, 9, 0),
                              Aceptado(datetime(2026, 11, 22, 9, 30)), [])

    with pytest.raises(AvisoYaEvaluadoError):
        aviso.descartar("", datetime(2026, 11, 22, 10, 0))

    assert isinstance(aviso.estado, Aceptado)
