#include <Arduino.h>
#include <DHT.h>

// =====================================================
// FARMTECH SOLUTIONS - FASE 2
// Sistema de irrigacao inteligente com ESP32
// Decisao multicriterio + simulacao ambiental
// Integracao meteorologica com Python + OpenWeather
// =====================================================
//
// SENSORES
// DHT22 -> temperatura e umidade
// LDR   -> simulacao de pH
//
// ENTRADAS
// Switch N -> Nitrogenio
// Switch P -> Fosforo
// Switch K -> Potassio
//
// SAIDAS
// Rele -> bomba de irrigacao
// LED azul -> indicacao visual da bomba
//
// IMPORTANTE:
// Os valores de N, P, K, umidade e pH sao
// simulados para fins academicos.
//
// A meteorologia e recebida do Python
// atraves da comunicacao serial.
//
// =====================================================


// -----------------------------
// PINOS
// -----------------------------

#define PIN_N 18
#define PIN_P 19
#define PIN_K 21

#define PIN_LDR 34
#define PIN_DHT 4

#define PIN_RELAY 16
#define PIN_LED 17

#define DHTTYPE DHT22


// -----------------------------
// OBJETO DHT
// -----------------------------

DHT dht(PIN_DHT, DHTTYPE);


// -----------------------------
// PARAMETROS DO SISTEMA
// -----------------------------

const float UMIDADE_MINIMA = 40.0;
const float UMIDADE_IDEAL_MIN = 60.0;
const float UMIDADE_IDEAL_MAX = 70.0;

const float PH_MINIMO = 5.5;
const float PH_MAXIMO = 7.0;

const float N_IDEAL = 70.0;
const float P_IDEAL = 70.0;
const float K_IDEAL = 70.0;


// -----------------------------
// NIVEIS INICIAIS
// -----------------------------

float nivelN = 35.0;
float nivelP = 50.0;
float nivelK = 40.0;


// -----------------------------
// ESTADOS
// -----------------------------

bool nutrienteNAtendido = false;
bool nutrientePAtendido = false;
bool nutrienteKAtendido = false;

bool bombaLigada = false;

bool ambienteInicializado = false;


// -----------------------------
// AMBIENTE SIMULADO
// -----------------------------

float umidadeSimulada = 35.0;
float phSimulado = 4.5;


// -----------------------------
// DECISAO
// -----------------------------

int pontuacaoIrrigacao = 0;


// ============================================================
// DADOS METEOROLOGICOS RECEBIDOS DO PYTHON
// ============================================================

float chuva3h = 0.0;
float chuva6h = 0.0;
float chuva12h = 0.0;
float chuva24h = 0.0;

String statusMeteorologico = "SEM_DADOS";

bool dadosMeteorologicosRecebidos = false;


// -----------------------------
// CONTROLE DE LOG
// -----------------------------

unsigned long ultimoLog = 0;

const unsigned long INTERVALO_LOG = 15000UL;


// =====================================================
// CALCULO DO PH ATRAVES DO LDR
// =====================================================

float calcularPH(int valorLDR)
{
    float ph = (valorLDR / 4095.0) * 14.0;

    if (ph < 0.0)
    {
        ph = 0.0;
    }

    if (ph > 14.0)
    {
        ph = 14.0;
    }

    return ph;
}


// =====================================================
// ATUALIZA STATUS DOS NUTRIENTES
// =====================================================

void atualizarNutrientes()
{
    if (nivelN >= N_IDEAL)
    {
        nivelN = N_IDEAL;
        nutrienteNAtendido = true;
    }

    if (nivelP >= P_IDEAL)
    {
        nivelP = P_IDEAL;
        nutrientePAtendido = true;
    }

    if (nivelK >= K_IDEAL)
    {
        nivelK = K_IDEAL;
        nutrienteKAtendido = true;
    }
}


// =====================================================
// ATUALIZA AMBIENTE DURANTE IRRIGACAO
// =====================================================

void atualizarAmbiente(
    bool nitrogenioAtivo,
    bool fosforoAtivo,
    bool potassioAtivo
)
{
    if (!bombaLigada)
    {
        return;
    }


    // ---------------------------------------------
    // EFEITO DOS NUTRIENTES NA UMIDADE
    // ---------------------------------------------

    if (nitrogenioAtivo && !nutrienteNAtendido)
    {
        umidadeSimulada += 2.0;
    }

    if (fosforoAtivo && !nutrientePAtendido)
    {
        umidadeSimulada += 2.0;
    }

    if (potassioAtivo && !nutrienteKAtendido)
    {
        umidadeSimulada += 2.0;
    }


    // Limite superior
    if (umidadeSimulada > 100.0)
    {
        umidadeSimulada = 100.0;
    }


    // ---------------------------------------------
    // EFEITO NO PH
    // ---------------------------------------------
    //
    // Estes valores sao parametros de simulacao
    // academica, nao representam uma recomendacao
    // agronomica real.
    //

    const float PH_ALVO = 6.25;

    if (nitrogenioAtivo && !nutrienteNAtendido)
    {
        if (phSimulado < PH_ALVO)
        {
            phSimulado += 0.10;
        }
        else if (phSimulado > PH_ALVO)
        {
            phSimulado -= 0.10;
        }
    }

    if (fosforoAtivo && !nutrientePAtendido)
    {
        if (phSimulado < PH_ALVO)
        {
            phSimulado += 0.15;
        }
        else if (phSimulado > PH_ALVO)
        {
            phSimulado -= 0.15;
        }
    }

    if (potassioAtivo && !nutrienteKAtendido)
    {
        if (phSimulado < PH_ALVO)
        {
            phSimulado += 0.20;
        }
        else if (phSimulado > PH_ALVO)
        {
            phSimulado -= 0.20;
        }
    }


    // ---------------------------------------------
    // EVOLUCAO DOS NUTRIENTES
    // ---------------------------------------------

    if (nitrogenioAtivo && !nutrienteNAtendido)
    {
        nivelN += 4.0;

        if (nivelN >= N_IDEAL)
        {
            nivelN = N_IDEAL;
            nutrienteNAtendido = true;
        }
    }


    if (fosforoAtivo && !nutrientePAtendido)
    {
        nivelP += 2.0;

        if (nivelP >= P_IDEAL)
        {
            nivelP = P_IDEAL;
            nutrientePAtendido = true;
        }
    }


    if (potassioAtivo && !nutrienteKAtendido)
    {
        nivelK += 3.0;

        if (nivelK >= K_IDEAL)
        {
            nivelK = K_IDEAL;
            nutrienteKAtendido = true;
        }
    }


    // ---------------------------------------------
    // LIMITES DO PH
    // ---------------------------------------------

    if (phSimulado > PH_ALVO &&
        phSimulado < PH_ALVO + 0.05)
    {
        phSimulado = PH_ALVO;
    }

    if (phSimulado < PH_ALVO &&
        phSimulado > PH_ALVO - 0.05)
    {
        phSimulado = PH_ALVO;
    }


    atualizarNutrientes();
}


// =====================================================
// CALCULA PONTUACAO MULTICRITERIO
// =====================================================

int calcularPontuacao(
    bool nitrogenioAtivo,
    bool fosforoAtivo,
    bool potassioAtivo
)
{
    int pontos = 0;


    // ---------------------------------------------
    // UMIDADE
    // ---------------------------------------------

    if (umidadeSimulada < 40.0)
    {
        pontos += 4;
    }
    else if (umidadeSimulada < UMIDADE_IDEAL_MIN)
    {
        pontos += 2;
    }


    // ---------------------------------------------
    // PH
    // ---------------------------------------------

    if (phSimulado < 4.0 || phSimulado > 8.0)
    {
        pontos += 3;
    }
    else if (
        phSimulado < PH_MINIMO ||
        phSimulado > PH_MAXIMO
    )
    {
        pontos += 2;
    }


    // ---------------------------------------------
    // NITROGENIO
    // ---------------------------------------------

    if (
        nitrogenioAtivo &&
        !nutrienteNAtendido &&
        nivelN < N_IDEAL
    )
    {
        pontos += 1;
    }


    // ---------------------------------------------
    // FOSFORO
    // ---------------------------------------------

    if (
        fosforoAtivo &&
        !nutrientePAtendido &&
        nivelP < P_IDEAL
    )
    {
        pontos += 1;
    }


    // ---------------------------------------------
    // POTASSIO
    // ---------------------------------------------

    if (
        potassioAtivo &&
        !nutrienteKAtendido &&
        nivelK < K_IDEAL
    )
    {
        pontos += 1;
    }


    return pontos;
}


// =====================================================
// VERIFICA SE A CHUVA E RELEVANTE
// =====================================================
//
// A previsao meteorologica atua como uma camada
// adicional de seguranca da irrigacao.
//
// CHUVA_FORTE_PROXIMA:
// 3h >= 10 mm
//
// CHUVA_SIGNIFICATIVA:
// 6h >= 15 mm
//
// CHUVA_RELEVANTE:
// 12h >= 10 mm
//
// CHUVA_LEVE:
// chuva > 0 mm, mas abaixo dos limites acima.
//
// A chuva leve nao bloqueia a irrigacao.
// A chuva relevante ou forte bloqueia.
//

bool existeChuvaRelevante()
{
    if (!dadosMeteorologicosRecebidos)
    {
        return false;
    }

    if (chuva3h >= 10.0)
    {
        return true;
    }

    if (chuva6h >= 15.0)
    {
        return true;
    }

    if (chuva12h >= 10.0)
    {
        return true;
    }

    return false;
}


// =====================================================
// CONTROLE DA BOMBA
// =====================================================

void controlarBomba(bool ligar)
{
    if (ligar)
    {
        if (!bombaLigada)
        {
            Serial.println();
            Serial.println(">>> BOMBA: LIGADA");
        }

        digitalWrite(PIN_RELAY, HIGH);
        digitalWrite(PIN_LED, HIGH);

        bombaLigada = true;
    }
    else
    {
        if (bombaLigada)
        {
            Serial.println();
            Serial.println(">>> BOMBA: DESLIGADA");
        }

        digitalWrite(PIN_RELAY, LOW);
        digitalWrite(PIN_LED, LOW);

        bombaLigada = false;
    }
}


// =====================================================
// EXIBE NUTRIENTES
// =====================================================

void exibirNutriente(
    const char* nome,
    bool ativo,
    float nivel,
    bool atendido
)
{
    Serial.print(nome);
    Serial.print(": ");

    if (ativo)
    {
        Serial.print("ATIVO");
    }
    else
    {
        Serial.print("INATIVO");
    }

    Serial.print(" | Nivel: ");
    Serial.print(nivel, 1);
    Serial.print(" | ");

    if (!ativo)
    {
        Serial.println("FORA DO CICLO");
    }
    else if (atendido)
    {
        Serial.println("ATENDIDO");
    }
    else
    {
        Serial.println("NECESSIDADE");
    }
}


void exibirNutrientes(
    bool nitrogenioAtivo,
    bool fosforoAtivo,
    bool potassioAtivo
)
{
    Serial.println("NUTRIENTES:");

    exibirNutriente(
        "Nitrogenio (N)",
        nitrogenioAtivo,
        nivelN,
        nutrienteNAtendido
    );

    exibirNutriente(
        "Fosforo (P)",
        fosforoAtivo,
        nivelP,
        nutrientePAtendido
    );

    exibirNutriente(
        "Potassio (K)",
        potassioAtivo,
        nivelK,
        nutrienteKAtendido
    );
}


// =====================================================
// RELATORIO COMPLETO
// =====================================================

void imprimirRelatorio(
    bool nitrogenioAtivo,
    bool fosforoAtivo,
    bool potassioAtivo,
    float temperatura,
    float umidadeSensor,
    int valorLDR
)
{
    Serial.println();
    Serial.println("============================================================");
    Serial.println("              FARMTECH SOLUTIONS - LOG");
    Serial.println("============================================================");

    Serial.println();

    Serial.println("STATUS DA IRRIGACAO");

    Serial.print("Bomba: ");

    if (bombaLigada)
    {
        Serial.println("ATIVA");
    }
    else
    {
        Serial.println("INATIVA");
    }

    Serial.print("Pontuacao multicriterio: ");
    Serial.println(pontuacaoIrrigacao);

    Serial.println();


    // ---------------------------------------------
    // NUTRIENTES
    // ---------------------------------------------

    exibirNutrientes(
        nitrogenioAtivo,
        fosforoAtivo,
        potassioAtivo
    );

    Serial.println();


    // ---------------------------------------------
    // SENSORES
    // ---------------------------------------------

    Serial.println("SENSORES:");

    Serial.print("DHT22 - Temperatura: ");
    Serial.print(temperatura, 2);
    Serial.println(" C");

    Serial.print("DHT22 - Umidade medida: ");
    Serial.print(umidadeSensor, 2);
    Serial.println(" %");

    Serial.print("Umidade simulada: ");
    Serial.print(umidadeSimulada, 2);
    Serial.println(" %");

    Serial.print("LDR: ");
    Serial.println(valorLDR);

    Serial.print("pH simulado: ");
    Serial.println(phSimulado, 2);

    Serial.println();


    // ---------------------------------------------
    // METEOROLOGIA
    // ---------------------------------------------

    Serial.println("METEOROLOGIA:");

    if (dadosMeteorologicosRecebidos)
    {
        Serial.print("Chuva prevista 3h : ");
        Serial.print(chuva3h, 2);
        Serial.println(" mm");

        Serial.print("Chuva prevista 6h : ");
        Serial.print(chuva6h, 2);
        Serial.println(" mm");

        Serial.print("Chuva prevista 12h: ");
        Serial.print(chuva12h, 2);
        Serial.println(" mm");

        Serial.print("Chuva prevista 24h: ");
        Serial.print(chuva24h, 2);
        Serial.println(" mm");

        Serial.print("Status meteorologico: ");
        Serial.println(statusMeteorologico);
    }
    else
    {
        Serial.println(
            "Nenhum dado meteorologico recebido."
        );
    }


    // ---------------------------------------------
    // DECISAO MULTICRITERIO
    // ---------------------------------------------

    Serial.println();
    Serial.println("DECISAO MULTICRITERIO:");

    Serial.print("Pontuacao: ");
    Serial.println(pontuacaoIrrigacao);

    if (umidadeSimulada < 40.0)
    {
        Serial.println(
            "+4 Umidade criticamente baixa"
        );
    }
    else if (umidadeSimulada < UMIDADE_IDEAL_MIN)
    {
        Serial.println(
            "+2 Umidade abaixo do ideal"
        );
    }
    else
    {
        Serial.println(
            "+0 Umidade adequada"
        );
    }


    if (phSimulado < 4.0 || phSimulado > 8.0)
    {
        Serial.println(
            "+3 pH muito fora da faixa"
        );
    }
    else if (
        phSimulado < PH_MINIMO ||
        phSimulado > PH_MAXIMO
    )
    {
        Serial.println(
            "+2 pH fora da faixa"
        );
    }
    else
    {
        Serial.println(
            "+0 pH adequado"
        );
    }


    if (
        nitrogenioAtivo &&
        !nutrienteNAtendido
    )
    {
        Serial.println(
            "+1 Necessidade de Nitrogenio"
        );
    }


    if (
        fosforoAtivo &&
        !nutrientePAtendido
    )
    {
        Serial.println(
            "+1 Necessidade de Fosforo"
        );
    }


    if (
        potassioAtivo &&
        !nutrienteKAtendido
    )
    {
        Serial.println(
            "+1 Necessidade de Potassio"
        );
    }


    Serial.println();


    // ---------------------------------------------
    // DECISAO METEOROLOGICA
    // ---------------------------------------------

    bool chuvaRelevante =
        existeChuvaRelevante();

    if (dadosMeteorologicosRecebidos)
    {
        Serial.println(
            "DECISAO METEOROLOGICA:"
        );

        if (chuvaRelevante)
        {
            Serial.println(
                "Chuva relevante prevista."
            );

            Serial.print(
                "Precipitacao prevista em 3h: "
            );

            Serial.print(
                chuva3h,
                2
            );

            Serial.println(" mm");

            Serial.print(
                "Status: "
            );

            Serial.println(
                statusMeteorologico
            );

            Serial.println(
                "Irrigacao podera ser suspensa."
            );
        }
        else
        {
            Serial.println(
                "Sem chuva relevante prevista."
            );

            Serial.print(
                "Status: "
            );

            Serial.println(
                statusMeteorologico
            );

            Serial.println(
                "Irrigacao meteorologicamente permitida."
            );
        }

        Serial.println();
    }


    // ---------------------------------------------
    // DECISAO FINAL
    // ---------------------------------------------

    bool existeNutrienteAtivo =
        nitrogenioAtivo ||
        fosforoAtivo ||
        potassioAtivo;

    bool irrigar = false;


    // ---------------------------------------------
    // REGRA 1
    // Nenhum nutriente ativo
    // ---------------------------------------------

    if (!existeNutrienteAtivo)
    {
        irrigar = false;

        Serial.println(
            "DECISAO: NAO IRRIGAR"
        );

        Serial.println(
            "Motivo: nenhum nutriente esta ativo."
        );
    }


    // ---------------------------------------------
    // REGRA 2
    // Pontuacao insuficiente
    // ---------------------------------------------

    else if (pontuacaoIrrigacao < 3)
    {
        irrigar = false;

        Serial.println(
            "DECISAO: NAO IRRIGAR"
        );

        Serial.println(
            "Motivo: pontuacao multicriterio abaixo do limite."
        );
    }


    // ---------------------------------------------
    // REGRA 3
    // Chuva relevante prevista
    // ---------------------------------------------

    else if (chuvaRelevante)
    {
        irrigar = false;

        Serial.println(
            "DECISAO: NAO IRRIGAR"
        );

        Serial.println(
            "Motivo: chuva relevante prevista."
        );
    }


    // ---------------------------------------------
    // REGRA 4
    // Irrigacao autorizada
    // ---------------------------------------------

    else
    {
        irrigar = true;

        Serial.println(
            "DECISAO: IRRIGAR"
        );

        Serial.println(
            "Motivo: necessidade multicriterio "
            "e ausencia de chuva relevante."
        );
    }


    controlarBomba(irrigar);


    Serial.println();

    if (bombaLigada)
    {
        Serial.println(
            "STATUS: IRRIGACAO ATIVA"
        );
    }
    else
    {
        Serial.println(
            "STATUS: IRRIGACAO INATIVA"
        );
    }


    Serial.println(
        "============================================================"
    );
}


// ============================================================
// RECEBE DADOS METEOROLOGICOS DO PYTHON
// ============================================================

void receberDadosMeteorologicos()
{
    if (!Serial.available())
    {
        return;
    }


    String mensagem =
        Serial.readStringUntil('\n');

    mensagem.trim();


    if (!mensagem.startsWith("WEATHER,"))
    {
        return;
    }


    Serial.println();
    Serial.println(
        ">>> DADOS METEOROLOGICOS RECEBIDOS"
    );

    Serial.println(
        mensagem
    );


    int posRain3h =
        mensagem.indexOf("RAIN_3H=");

    int posRain6h =
        mensagem.indexOf("RAIN_6H=");

    int posRain12h =
        mensagem.indexOf("RAIN_12H=");

    int posRain24h =
        mensagem.indexOf("RAIN_24H=");

    int posStatus =
        mensagem.indexOf("STATUS=");


    if (
        posRain3h == -1 ||
        posRain6h == -1 ||
        posRain12h == -1 ||
        posRain24h == -1 ||
        posStatus == -1
    )
    {
        Serial.println(
            "ERRO: formato meteorologico invalido."
        );

        return;
    }


    // ---------------------------------------------
    // RAIN_3H
    // ---------------------------------------------

    int fimRain3h =
        mensagem.indexOf(
            ",",
            posRain3h
        );

    if (fimRain3h == -1)
    {
        fimRain3h = mensagem.length();
    }

    chuva3h =
        mensagem.substring(
            posRain3h + 8,
            fimRain3h
        ).toFloat();


    // ---------------------------------------------
    // RAIN_6H
    // ---------------------------------------------

    int fimRain6h =
        mensagem.indexOf(
            ",",
            posRain6h
        );

    if (fimRain6h == -1)
    {
        fimRain6h = mensagem.length();
    }

    chuva6h =
        mensagem.substring(
            posRain6h + 8,
            fimRain6h
        ).toFloat();


    // ---------------------------------------------
    // RAIN_12H
    // ---------------------------------------------

    int fimRain12h =
        mensagem.indexOf(
            ",",
            posRain12h
        );

    if (fimRain12h == -1)
    {
        fimRain12h = mensagem.length();
    }

    chuva12h =
        mensagem.substring(
            posRain12h + 9,
            fimRain12h
        ).toFloat();


    // ---------------------------------------------
    // RAIN_24H
    // ---------------------------------------------

    int fimRain24h =
        mensagem.indexOf(
            ",",
            posRain24h
        );

    if (fimRain24h == -1)
    {
        fimRain24h = mensagem.length();
    }

    chuva24h =
        mensagem.substring(
            posRain24h + 9,
            fimRain24h
        ).toFloat();


    // ---------------------------------------------
    // STATUS
    // ---------------------------------------------

    int fimStatus =
        mensagem.indexOf(
            ",",
            posStatus
        );

    if (fimStatus == -1)
    {
        fimStatus = mensagem.length();
    }

    statusMeteorologico =
        mensagem.substring(
            posStatus + 7,
            fimStatus
        );

    statusMeteorologico.trim();


    dadosMeteorologicosRecebidos =
        true;


    // ---------------------------------------------
    // CONFIRMACAO
    // ---------------------------------------------

    Serial.println();

    Serial.println(
        "METEOROLOGIA INTERPRETADA:"
    );

    Serial.print(
        "Chuva 3h : "
    );

    Serial.print(
        chuva3h,
        2
    );

    Serial.println(
        " mm"
    );


    Serial.print(
        "Chuva 6h : "
    );

    Serial.print(
        chuva6h,
        2
    );

    Serial.println(
        " mm"
    );


    Serial.print(
        "Chuva 12h: "
    );

    Serial.print(
        chuva12h,
        2
    );

    Serial.println(
        " mm"
    );


    Serial.print(
        "Chuva 24h: "
    );

    Serial.print(
        chuva24h,
        2
    );

    Serial.println(
        " mm"
    );


    Serial.print(
        "Status: "
    );

    Serial.println(
        statusMeteorologico
    );

    Serial.println();
}


// =====================================================
// SETUP
// =====================================================

void setup()
{
    Serial.begin(115200);

    delay(1000);


    Serial.println();

    Serial.println(
        "=============================================="
    );

    Serial.println(
        "       FARMTECH SOLUTIONS - FASE 2"
    );

    Serial.println(
        "       SISTEMA DE IRRIGACAO INTELIGENTE"
    );

    Serial.println(
        "       MULTICRITERIO + SIMULACAO"
    );

    Serial.println(
        "=============================================="
    );

    Serial.println();


    // ---------------------------------------------
    // ENTRADAS
    // ---------------------------------------------

    pinMode(PIN_N, INPUT);
    pinMode(PIN_P, INPUT);
    pinMode(PIN_K, INPUT);

    pinMode(PIN_LDR, INPUT);


    // ---------------------------------------------
    // SAIDAS
    // ---------------------------------------------

    pinMode(PIN_RELAY, OUTPUT);
    pinMode(PIN_LED, OUTPUT);


    controlarBomba(false);


    // ---------------------------------------------
    // DHT
    // ---------------------------------------------

    dht.begin();


    // ---------------------------------------------
    // ESTADOS INICIAIS
    // ---------------------------------------------

    atualizarNutrientes();


    Serial.println(
        "Sistema inicializado."
    );

    Serial.println();

    Serial.println(
        "Aguardando leitura dos sensores..."
    );

    Serial.println();
}


// =====================================================
// LOOP
// =====================================================

void loop()
{
    // ---------------------------------------------
    // RECEBE METEOROLOGIA
    // ---------------------------------------------

    receberDadosMeteorologicos();


    // ---------------------------------------------
    // LEITURA DOS SWITCHES
    // ---------------------------------------------

    bool nitrogenioAtivo =
        (digitalRead(PIN_N) == LOW);

    bool fosforoAtivo =
        (digitalRead(PIN_P) == LOW);

    bool potassioAtivo =
        (digitalRead(PIN_K) == LOW);


    // ---------------------------------------------
    // LEITURA DHT
    // ---------------------------------------------

    float temperatura =
        dht.readTemperature();

    float umidadeSensor =
        dht.readHumidity();


    // ---------------------------------------------
    // VERIFICACAO DHT
    // ---------------------------------------------

    if (
        isnan(temperatura) ||
        isnan(umidadeSensor)
    )
    {
        Serial.println(
            "ERRO: Falha na leitura do DHT22."
        );

        controlarBomba(false);

        delay(2500);

        return;
    }


    // ---------------------------------------------
    // LDR
    // ---------------------------------------------

    int valorLDR =
        analogRead(PIN_LDR);


    // ---------------------------------------------
    // PRIMEIRA LEITURA
    // ---------------------------------------------

    if (!ambienteInicializado)
    {
        umidadeSimulada =
            umidadeSensor;

        phSimulado =
            calcularPH(valorLDR);

        ambienteInicializado = true;


        Serial.println();

        Serial.println(
            "AMBIENTE SIMULADO INICIALIZADO"
        );


        Serial.print(
            "Umidade inicial: "
        );

        Serial.print(
            umidadeSimulada,
            2
        );

        Serial.println(
            " %"
        );


        Serial.print(
            "pH inicial: "
        );

        Serial.println(
            phSimulado,
            2
        );
    }


    // ---------------------------------------------
    // ATUALIZA NUTRIENTES
    // ---------------------------------------------

    atualizarNutrientes();


    // ---------------------------------------------
    // CALCULA PONTUACAO
    // ---------------------------------------------

    pontuacaoIrrigacao =
        calcularPontuacao(
            nitrogenioAtivo,
            fosforoAtivo,
            potassioAtivo
        );


    // ---------------------------------------------
    // RELATORIO NORMAL
    // ---------------------------------------------

    imprimirRelatorio(
        nitrogenioAtivo,
        fosforoAtivo,
        potassioAtivo,
        temperatura,
        umidadeSensor,
        valorLDR
    );


    // ---------------------------------------------
    // CONTROLE DO AMBIENTE
    // ---------------------------------------------

    if (bombaLigada)
    {
        float umidadeAntes =
            umidadeSimulada;

        float phAntes =
            phSimulado;

        float nAntes =
            nivelN;

        float pAntes =
            nivelP;

        float kAntes =
            nivelK;


        atualizarAmbiente(
            nitrogenioAtivo,
            fosforoAtivo,
            potassioAtivo
        );


        Serial.println();

        Serial.println(
            "ALTERACAO DO AMBIENTE:"
        );


        Serial.print(
            "Umidade: "
        );

        Serial.print(
            umidadeAntes,
            2
        );

        Serial.print(
            " -> "
        );

        Serial.print(
            umidadeSimulada,
            2
        );

        Serial.println(
            " %"
        );


        Serial.print(
            "pH: "
        );

        Serial.print(
            phAntes,
            2
        );

        Serial.print(
            " -> "
        );

        Serial.println(
            phSimulado,
            2
        );


        Serial.print(
            "N: "
        );

        Serial.print(
            nAntes,
            1
        );

        Serial.print(
            " -> "
        );

        Serial.println(
            nivelN,
            1
        );


        Serial.print(
            "P: "
        );

        Serial.print(
            pAntes,
            1
        );

        Serial.print(
            " -> "
        );

        Serial.println(
            nivelP,
            1
        );


        Serial.print(
            "K: "
        );

        Serial.print(
            kAntes,
            1
        );

        Serial.print(
            " -> "
        );

        Serial.println(
            nivelK,
            1
        );
    }


    // =================================================
    // LOG A CADA 15 SEGUNDOS
    // =================================================

    if (
        millis() - ultimoLog >=
        INTERVALO_LOG
    )
    {
        ultimoLog = millis();


        Serial.println();

        Serial.println(
            "########## LOG_INICIO ##########"
        );


        imprimirRelatorio(
            nitrogenioAtivo,
            fosforoAtivo,
            potassioAtivo,
            temperatura,
            umidadeSensor,
            valorLDR
        );


        Serial.println(
            "########### LOG_FIM ###########"
        );

        Serial.println();
    }


    delay(2500);
}