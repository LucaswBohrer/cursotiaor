import serial
import time

RFC2217_URL = "rfc2217://localhost:4000"

mensagem = (
    "WEATHER,"
    "RAIN_3H=0.00,"
    "RAIN_6H=0.00,"
    "RAIN_12H=0.00,"
    "RAIN_24H=0.00,"
    "STATUS=SEM_CHUVA_RELEVANTE"
)

print()
print("=" * 60)
print("       TESTE METEOROLOGICO MANUAL")
print("=" * 60)
print()

print("Mensagem:")
print(mensagem)
print()

try:

    ser = serial.serial_for_url(
        RFC2217_URL,
        baudrate=115200,
        timeout=1
    )

    print("Conectado ao Wokwi.")
    print("Enviando dados meteorologicos...")

    time.sleep(0.5)

    ser.write(
        (mensagem + "\n").encode("utf-8")
    )

    ser.flush()

    time.sleep(1)

    print("Mensagem enviada com sucesso.")

    ser.close()

    print("Conexao encerrada.")

except Exception as erro:

    print()
    print("ERRO:")
    print(erro)