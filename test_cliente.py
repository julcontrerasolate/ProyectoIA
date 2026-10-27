from unittest.mock import patch, Mock
import pytest
import cliente
from src.consumir_gemini import enviar_peticion
from cliente import con_reintento, registrar_costo, consultar_modelo


def test_enviar_peticion_credencial_invalida():
    respuesta_falsa = Mock(status_code=401)
    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError, match="Credencial inválida"):
            enviar_peticion("https://ejemplo.invalid", {"pregunta": "test"})


def test_enviar_peticion_limite_de_uso():
    respuesta_falsa = Mock(status_code=429, headers={"Retry-After": "10"})
    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError, match="10s"):
            enviar_peticion("https://ejemplo.invalid", {"pregunta": "test"})


def test_enviar_peticion_exito():
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto": "respuesta simulada"}
    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion("https://ejemplo.invalid", {"pregunta": "test"})

    assert resultado == {"texto": "respuesta simulada"}


### pruebas cliente

def test_con_reintento_agota_intentos():
    def siempre_falla():
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep"):
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=3)


def test_con_reintento_no_reintenta_value_error():
    funcion = Mock(side_effect=ValueError("credencial inválida"))

    with patch("cliente.time.sleep") as sleep:
        with pytest.raises(ValueError):
            con_reintento(funcion, intentos=3)

    assert funcion.call_count == 1
    sleep.assert_not_called()


def test_registrar_costo_acumula():
    cliente.costo_total_sesion = 0
    respuesta_falsa = {"usageMetadata": {"totalTokenCount": 1000}}
    costo = cliente.registrar_costo(respuesta_falsa)

    assert costo == cliente.COSTO_POR_1000_TOKENS
    assert cliente.costo_total_sesion == cliente.COSTO_POR_1000_TOKENS


def test_consultar_modelo_convierte_error():
    error_simulado = TimeoutError("simulado")

    with patch("cliente.con_reintento", side_effect=error_simulado):
        with pytest.raises(RuntimeError):
            consultar_modelo("pregunta de prueba")


@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    cliente.costo_total_sesion = 0
    yield