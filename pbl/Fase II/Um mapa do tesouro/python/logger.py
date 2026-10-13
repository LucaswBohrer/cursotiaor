import serial
import os
import time
from datetime import datetime


# ============================================================
# FARMTECH SOLUTIONS - LOGGER
# Logger para Wokwi Simulator
# ============================================================

BAUDRATE = 115200

RFC2217_URL = "rfc2217://localhost:4000"


# ============================================================
# DIRETORIOS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

LOG_DIR = os.path.join(
    BASE_DIR,
    "logs"
)

os.makedirs(
    LOG_DIR,
    exist_ok=True
)


# ============================================================
# CABECALHO
# ============================================================

def imprimir_cabecalho():

    print()
    print("=" * 60)
    print("       FARMTECH SOLUTIONS - LOGGER")
    print("       WOKWI SERIAL LOGGER")
    print("=" * 60)
    print()

    print(
        f"Conexao: {RFC2217_URL}"
    )

    print(
        f"Baudrate: {BAUDRATE}"
    )

    print(
        f"Pasta dos logs: {LOG_DIR}"
    )

    print()


# ============================================================
# CRIA NOME DO ARQUIVO
# ============================================================

def criar_nome_arquivo():

    agora = datetime.now()

    nome = agora.strftime(
        "%Y-%m-%d_%H-%M-%S.txt"
    )

    caminho = os.path.join(
        LOG_DIR,
        nome
    )

    return caminho


# ============================================================
# SALVA LOG
# ============================================================

def salvar_log(linhas):

    caminho = criar_nome_arquivo()

    agora = datetime.now()

    cabecalho = [
        "============================================================",
        "        FARMTECH SOLUTIONS - REGISTRO DE LOG",
        "============================================================",
        "",
        "Data/hora da captura: "
        + agora.strftime("%d/%m/%Y %H:%M:%S"),
        "",
        "============================================================",
        ""
    ]


    conteudo = (
        cabecalho
        + linhas
        + [
            "",
            "============================================================",
            "                 FIM DO REGISTRO",
            "============================================================",
            ""
        ]
    )


    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(
            "\n".join(conteudo)
        )


    print()
    print("############################################################")
    print("# LOG SALVO")
    print("############################################################")
    print(
        f"Arquivo: {caminho}"
    )
    print()


# ============================================================
# CAPTURA DA SERIAL
# ============================================================

def capturar_logs(ser):

    capturando = False
    buffer = []


    print(
        "Conectado ao Wokwi."
    )

    print(
        "Aguardando LOG_INICIO..."
    )

    print(
        "Pressione CTRL+C para encerrar."
    )

    print()


    while True:

        linha = ser.readline()

        if not linha:
            continue


        texto = linha.decode(
            "utf-8",
            errors="replace"
        ).rstrip()


        # ----------------------------------------------------
        # MOSTRA TUDO NO TERMINAL
        # ----------------------------------------------------

        print(texto)


        # ----------------------------------------------------
        # INICIO DO LOG
        # ----------------------------------------------------

        if (
            "########## LOG_INICIO ##########"
            in texto
        ):

            capturando = True

            buffer = []

            continue


        # ----------------------------------------------------
        # CAPTURA
        # ----------------------------------------------------

        if capturando:

            buffer.append(texto)


        # ----------------------------------------------------
        # FINAL DO LOG
        # ----------------------------------------------------

        if (
            "########### LOG_FIM ###########"
            in texto
        ):

            capturando = False

            salvar_log(
                buffer
            )

            buffer = []


# ============================================================
# MAIN
# ============================================================

def main():

    imprimir_cabecalho()


    print("Tentando conectar ao Wokwi...")
    print()
    print("Aguardando o servidor RFC2217 na porta 4000...")
    print("Inicie o Wokwi quando quiser.")
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

            break

        except Exception:
            print(
                "Wokwi ainda nao disponivel. "
                "Tentando novamente em 1 segundo..."
            )

            time.sleep(1)


    try:

        capturar_logs(
            ser
        )


    except KeyboardInterrupt:

        print()
        print()
        print(
            "Logger encerrado pelo usuario."
        )


    except Exception as erro:

        print()
        print(
            "ERRO DURANTE A CAPTURA:"
        )

        print(
            erro
        )


    finally:

        ser.close()

        print()
        print(
            "Conexao com o Wokwi encerrada."
        )


# ============================================================
# EXECUCAO
# ============================================================

if __name__ == "__main__":

    main()