import socket
import json
import threading
import uuid
import os
from datetime import datetime

HOST      = "0.0.0.0"
PORTA     = 5000
ENCODING  = "utf-8"

# -------------------------------------------------------
# Caminhos relativos ao script
# -------------------------------------------------------
PASTA_BASE   = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_JSON = os.path.join(PASTA_BASE, "agendamentos.json")

agendamentos = {}
lock = threading.Lock()

# -------------------------------------------------------
# Função auxiliar para ler linha sem \r\n do Telnet
# -------------------------------------------------------
def ler_linha(arquivo):
    return arquivo.readline().replace('\r', '').replace('\n', '').strip()

# -------------------------------------------------------
# Persistência
# -------------------------------------------------------
def salvar_json():
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(agendamentos, f, ensure_ascii=False, indent=2)

def carregar_json():
    global agendamentos
    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            agendamentos = json.load(f)
        print(f"[INFO] {len(agendamentos)} agendamentos carregados.")
        print(f"[INFO] Arquivo: {ARQUIVO_JSON}")
    except FileNotFoundError:
        agendamentos = {}
        print(f"[INFO] Nenhum arquivo encontrado. Iniciando vazio.")
        print(f"[INFO] Sera criado em: {ARQUIVO_JSON}")

# -------------------------------------------------------
# Lógica de negócio
# -------------------------------------------------------
def processar_requisicao(dados):
    operacao = dados.get("operacao")

    if operacao == "AGENDAR":
        protocolo = str(uuid.uuid4())[:8].upper()
        agendamento = {
            "protocolo":  protocolo,
            "paciente":   dados.get("paciente"),
            "tipo":       dados.get("tipo"),
            "data":       dados.get("data"),
            "hora":       dados.get("hora"),
            "status":     "CONFIRMADO",
            "criado_em":  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with lock:
            agendamentos[protocolo] = agendamento
            salvar_json()

        return {
            "status":    "SUCESSO",
            "mensagem":  "Consulta agendada com sucesso!",
            "protocolo": protocolo,
            "dados":     agendamento
        }

    elif operacao == "CONSULTAR":
        protocolo = dados.get("protocolo", "").upper()
        with lock:
            agendamento = agendamentos.get(protocolo)

        if agendamento:
            return {"status": "SUCESSO", "dados": agendamento}
        else:
            return {"status": "ERRO", "mensagem": f"Protocolo {protocolo} nao encontrado."}

    elif operacao == "CANCELAR":
        protocolo = dados.get("protocolo", "").upper()
        with lock:
            if protocolo in agendamentos:
                agendamentos[protocolo]["status"] = "CANCELADO"
                salvar_json()
                return {"status": "SUCESSO", "mensagem": f"Agendamento {protocolo} cancelado."}
            else:
                return {"status": "ERRO", "mensagem": f"Protocolo {protocolo} nao encontrado."}

    elif operacao == "LISTAR":
        paciente = dados.get("paciente", "").lower()
        with lock:
            resultado = [
                a for a in agendamentos.values()
                if paciente in a["paciente"].lower()
            ]
        return {"status": "SUCESSO", "agendamentos": resultado, "total": len(resultado)}

    else:
        return {"status": "ERRO", "mensagem": f"Operacao desconhecida: {operacao}"}

# -------------------------------------------------------
# Menu interativo
# -------------------------------------------------------
def enviar(arquivo, texto):
    arquivo.write(texto)
    arquivo.flush()

def mostrar_menu(arquivo):
    enviar(arquivo,
        "\r\n==================================================\r\n"
        "     BEM-VINDO AO SISTEMA DE AGENDAMENTO\r\n"
        "==================================================\r\n"
        "  [1] Agendar consulta\r\n"
        "  [2] Consultar agendamento\r\n"
        "  [3] Cancelar agendamento\r\n"
        "  [4] Listar agendamentos\r\n"
        "  [0] Sair\r\n"
        "==================================================\r\n"
        "Opcao: "
    )

def mostrar_menu_rapido(arquivo):
    enviar(arquivo,
        "\r\n==================================================\r\n"
        "  [1] Agendar   [2] Consultar\r\n"
        "  [3] Cancelar  [4] Listar  [0] Sair\r\n"
        "==================================================\r\n"
        "Opcao: "
    )

def opcao_agendar(arquivo):
    enviar(arquivo, "Nome do paciente: ")
    paciente = ler_linha(arquivo)

    enviar(arquivo, "Tipo (Clinico/Dentista/Exame): ")
    tipo = ler_linha(arquivo)

    enviar(arquivo, "Data (DD/MM/AAAA): ")
    data = ler_linha(arquivo)

    enviar(arquivo, "Hora (HH:MM): ")
    hora = ler_linha(arquivo)

    resposta = processar_requisicao({
        "operacao": "AGENDAR",
        "paciente": paciente,
        "tipo":     tipo,
        "data":     data,
        "hora":     hora
    })

    enviar(arquivo,
        f"\r\nStatus:    {resposta['status']}\r\n"
        f"Mensagem:  {resposta['mensagem']}\r\n"
        f"Protocolo: {resposta['protocolo']}\r\n"
        f"Data:      {resposta['dados']['data']} as {resposta['dados']['hora']}\r\n"
    )

def opcao_consultar(arquivo):
    enviar(arquivo, "Numero do protocolo: ")
    protocolo = ler_linha(arquivo)

    resposta = processar_requisicao({
        "operacao":  "CONSULTAR",
        "protocolo": protocolo
    })

    if resposta["status"] == "SUCESSO":
        d = resposta["dados"]
        enviar(arquivo,
            f"\r\nPaciente:  {d['paciente']}\r\n"
            f"Tipo:      {d['tipo']}\r\n"
            f"Data:      {d['data']} as {d['hora']}\r\n"
            f"Status:    {d['status']}\r\n"
            f"Criado em: {d['criado_em']}\r\n"
        )
    else:
        enviar(arquivo, f"\r\nErro: {resposta['mensagem']}\r\n")

def opcao_cancelar(arquivo):
    enviar(arquivo, "Protocolo para cancelar: ")
    protocolo = ler_linha(arquivo)

    resposta = processar_requisicao({
        "operacao":  "CANCELAR",
        "protocolo": protocolo
    })

    enviar(arquivo,
        f"\r\nStatus:   {resposta['status']}\r\n"
        f"Mensagem: {resposta['mensagem']}\r\n"
    )

def opcao_listar(arquivo):
    enviar(arquivo, "Nome do paciente (Enter para todos): ")
    paciente = ler_linha(arquivo)

    resposta = processar_requisicao({
        "operacao": "LISTAR",
        "paciente": paciente
    })

    enviar(arquivo, f"\r\nTotal encontrado: {resposta['total']}\r\n")
    for a in resposta["agendamentos"]:
        enviar(arquivo,
            f"\r\n  Protocolo: {a['protocolo']}\r\n"
            f"  Paciente:  {a['paciente']}\r\n"
            f"  Tipo:      {a['tipo']}\r\n"
            f"  Data:      {a['data']} as {a['hora']}\r\n"
            f"  Status:    {a['status']}\r\n"
        )

# -------------------------------------------------------
# Atendedor de cliente
# -------------------------------------------------------
def atender_cliente(conn, addr):
    print(f"[AGENDAMENTO] Nova conexao: {addr}")
    try:
        with conn:
            arquivo = conn.makefile('rw', encoding=ENCODING, newline='')
            mostrar_menu(arquivo)

            while True:
                opcao = ler_linha(arquivo)

                if opcao == "0":
                    enviar(arquivo, "\r\nEncerrando. Ate logo!\r\n")
                    break
                elif opcao == "1":
                    opcao_agendar(arquivo)
                elif opcao == "2":
                    opcao_consultar(arquivo)
                elif opcao == "3":
                    opcao_cancelar(arquivo)
                elif opcao == "4":
                    opcao_listar(arquivo)
                else:
                    enviar(arquivo, "\r\nOpcao invalida!\r\n")

                mostrar_menu_rapido(arquivo)

    except Exception as e:
        print(f"[ERRO] {addr}: {e}")
    finally:
        print(f"[AGENDAMENTO] Desconectado: {addr}")

# -------------------------------------------------------
# Inicialização
# -------------------------------------------------------
def iniciar():
    carregar_json()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORTA))
        servidor.listen(10)
        print("=" * 50)
        print("Servidor de Agendamento iniciado!")
        print(f"Porta: {PORTA}")
        print(f"JSON:  {ARQUIVO_JSON}")
        print("=" * 50)

        try:
            while True:
                conn, addr = servidor.accept()
                thread = threading.Thread(
                    target=atender_cliente,
                    args=(conn, addr)
                )
                thread.daemon = True
                thread.start()

        except KeyboardInterrupt:
            print("\n[INFO] Servidor encerrado pelo usuario.")

if __name__ == "__main__":
    iniciar()