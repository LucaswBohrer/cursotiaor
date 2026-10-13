import requests
import serial
import time
from datetime import datetime

# ============================================================
# CONFIGURACOES
# ============================================================

API_KEY = "COLOQUE_SUA_API_KEY_AQUI"

CIDADE = "Novo Hamburgo"
PAIS = "BR"

UNITS = "metric"
LANG = "pt_br"

URL = "https://api.openweathermap.org/data/2.5/forecast"

RFC2217_URL = "rfc2217://localhost:4000"
BAUDRATE = 115200


# ============================================================
# OPENWEATHER
# ============================================================

def consultar_previsao():

    parametros = {
        "q": f"{CIDADE},{PAIS}",
        "appid": API_KEY,
        "units": UNITS,
        "lang": LANG,
        "cnt": 8
    }

    resposta = requests.get(
        URL,
        params=parametros,
        timeout=10
    )

    resposta.raise_for_status()

    return resposta.json()


# ============================================================
# CALCULO DA PRECIPITACAO
# ============================================================

def calcular_precipitacao(previsoes):

    chuva_3h = 0.0
    chuva_6h = 0.0
    chuva_12h = 0.0
    chuva_24h = 0.0

    for indice, previsao in enumerate(previsoes):

        chuva = previsao.get("rain", {})

        chuva_3h_valor = chuva.get(
            "3h",
            0.0
        )

        if indice < 1:
            chuva_3h += chuva_3h_valor

        if indice < 2:
            chuva_6h += chuva_3h_valor

        if indice < 4:
            chuva_12h += chuva_3h_valor

        if indice < 8:
            chuva_24h += chuva_3h_valor

    return {
        "3h": chuva_3h,
        "6h": chuva_6h,
        "12h": chuva_12h,
        "24h": chuva_24h
    }


# ============================================================
# CLASSIFICACAO METEOROLOGICA
# ============================================================

def classificar_meteorologia(precipitacao):

    chuva_3h = precipitacao["3h"]
    chuva_6h = precipitacao["6h"]
    chuva_12h = precipitacao["12h"]

    if chuva_3h >= 10.0:
        return "CHUVA_FORTE_PROXIMA"

    if chuva_6h >= 15.0:
        return "CHUVA_SIGNIFICATIVA"

    if chuva_12h >= 10.0:
        return "CHUVA_RELEVANTE"

    if chuva_12h > 0.0:
        return "CHUVA_LEVE"

    return "SEM_CHUVA_RELEVANTE"


# ============================================================
# ANALISE
# ============================================================

def analisar_previsao(dados):

    previsoes = dados.get(
        "list",
        []
    )

    precipitacao = calcular_precipitacao(
        previsoes
    )

    classificacao = classificar_meteorologia(
        precipitacao
    )

    chuva_prevista = (
        precipitacao["24h"] > 0
    )

    return {
        "chuva_prevista": chuva_prevista,
        "precipitacao_3h": precipitacao["3h"],
        "precipitacao_6h": precipitacao["6h"],
        "precipitacao_12h": precipitacao["12h"],
        "precipitacao_24h": precipitacao["24h"],
        "classificacao": classificacao
    }


# ============================================================
# EXIBICAO
# ============================================================

def exibir_previsao(dados, analise):

    print()
    print("=" * 60)
    print("       FARMTECH SOLUTIONS - METEOROLOGIA")
    print("=" * 60)
    print()

    print(f"Local: {CIDADE} - {PAIS}")

    print()
    print("PREVISAO DAS PROXIMAS HORAS")
    print("-" * 60)

    for previsao in dados.get("list", []):

        timestamp = previsao["dt"]

        data_hora = datetime.fromtimestamp(
            timestamp
        )

        temperatura = previsao["main"]["temp"]

        umidade = previsao["main"]["humidity"]

        clima = previsao["weather"][0]

        descricao = clima["description"]

        chuva = previsao.get(
            "rain",
            {}
        )

        chuva_3h = chuva.get(
            "3h",
            0.0
        )

        print(
            f"{data_hora.strftime('%d/%m %H:%M')} | "
            f"{temperatura:.1f} C | "
            f"Umidade {umidade}% | "
            f"{descricao} | "
            f"Chuva {chuva_3h:.2f} mm"
        )

    print()

    print("ANALISE POR HORIZONTE")
    print("-" * 60)

    print(
        f"Proximas 3 horas : "
        f"{analise['precipitacao_3h']:.2f} mm"
    )

    print(
        f"Proximas 6 horas : "
        f"{analise['precipitacao_6h']:.2f} mm"
    )

    print(
        f"Proximas 12 horas: "
        f"{analise['precipitacao_12h']:.2f} mm"
    )

    print(
        f"Proximas 24 horas: "
        f"{analise['precipitacao_24h']:.2f} mm"
    )

    print()

    print("DECISAO METEOROLOGICA")
    print("-" * 60)

    print(
        "Chuva prevista: "
        + (
            "SIM"
            if analise["chuva_prevista"]
            else "NAO"
        )
    )

    print(
        f"Classificacao: "
        f"{analise['classificacao']}"
    )

    print()


# ============================================================
# MENSAGEM PARA O ESP32
# ============================================================

def gerar_dados_esp32(analise):

    mensagem = (
        "WEATHER,"
        f"RAIN_3H={analise['precipitacao_3h']:.2f},"
        f"RAIN_6H={analise['precipitacao_6h']:.2f},"
        f"RAIN_12H={analise['precipitacao_12h']:.2f},"
        f"RAIN_24H={analise['precipitacao_24h']:.2f},"
        f"STATUS={analise['classificacao']}"
    )

    return mensagem


# ============================================================
# CONEXAO COM O WOKWI
# ============================================================

def conectar_wokwi():

    print()
    print("============================================================")
    print("       AGUARDANDO WOKWI")
    print("============================================================")
    print()
    print(f"Servidor RFC2217: {RFC2217_URL}")
    print()
    print("O Weather ficara aguardando o Wokwi iniciar.")
    print("Inicie o simulador normalmente.")
    print()

    while True:

        try:

            ser = serial.serial_for_url(
                RFC2217_URL,
                baudrate=BAUDRATE,
                timeout=1
            )

            print()
            print("############################################################")
            print("# WOKWI CONECTADO")
            print("############################################################")
            print()

            return ser

        except Exception:

            print(
                "Wokwi ainda nao disponivel. "
                "Tentando novamente em 1 segundo..."
            )

            time.sleep(1)


# ============================================================
# ENVIO PARA O ESP32
# ============================================================

def enviar_para_esp32(mensagem):

    print()
    print("ENVIO PARA O ESP32")
    print("-" * 60)

    print(
        f"Conectando em: {RFC2217_URL}"
    )

    ser = None

    try:

        ser = conectar_wokwi()

        time.sleep(0.5)

        mensagem_serial = mensagem + "\n"

        print()
        print("Enviando:")
        print(mensagem)

        ser.write(
            mensagem_serial.encode(
                "utf-8"
            )
        )

        ser.flush()

        time.sleep(1)

        print()
        print("Mensagem enviada com sucesso.")

    except KeyboardInterrupt:

        print()
        print("Weather encerrado pelo usuario.")

    except Exception as erro:

        print()
        print("ERRO AO ENVIAR PARA O ESP32:")
        print(erro)

    finally:

        if ser is not None:

            ser.close()

            print()
            print("Conexao RFC2217 encerrada.")


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("============================================================")
    print("       FARMTECH SOLUTIONS - WEATHER")
    print("============================================================")
    print()

    print("Consultando OpenWeather...")

    if API_KEY == "COLOQUE_SUA_API_KEY_AQUI":

        print()
        print("ERRO: API KEY NAO CONFIGURADA.")
        print()

        print(
            "Abra weather.py e coloque "
            "sua chave da OpenWeather."
        )

        return

    try:

        dados = consultar_previsao()

        analise = analisar_previsao(
            dados
        )

        exibir_previsao(
            dados,
            analise
        )

        mensagem = gerar_dados_esp32(
            analise
        )

        print()
        print("=" * 60)
        print("DADOS GERADOS PARA O ESP32")
        print("=" * 60)
        print()
        print(mensagem)

        enviar_para_esp32(
            mensagem
        )

        print()
        print("=" * 60)
        print("FIM DA INTEGRACAO METEOROLOGICA")
        print("=" * 60)
        print()

    except requests.exceptions.HTTPError as erro:

        print()
        print("ERRO HTTP AO CONSULTAR A API:")
        print(erro)
        print()

    except requests.exceptions.RequestException as erro:

        print()
        print("ERRO DE CONEXAO COM A API:")
        print(erro)
        print()

    except KeyboardInterrupt:

        print()
        print()
        print("Weather encerrado pelo usuario.")
        print()

    except Exception as erro:

        print()
        print("ERRO INESPERADO:")
        print(erro)
        print()


if __name__ == "__main__":
    main()