import socket
import json

HOST     = "localhost"
PORTA    = 5000
ENCODING = "utf-8"

def enviar(dados):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORTA))
        s.sendall(json.dumps(dados).encode(ENCODING))
        resposta = s.recv(4096).decode(ENCODING)
        return json.loads(resposta)

def agendar():
    print("\n--- NOVA CONSULTA ---")
    paciente = input("Nome do paciente: ").strip()
    tipo     = input("Tipo (Clinico/Dentista/Exame): ").strip()
    data     = input("Data (DD/MM/AAAA): ").strip()
    hora     = input("Hora (HH:MM): ").strip()

    resposta = enviar({
        "operacao": "AGENDAR",
        "paciente": paciente,
        "tipo":     tipo,
        "data":     data,
        "hora":     hora
    })

    print(f"\nStatus:    {resposta['status']}")
    print(f"Mensagem:  {resposta['mensagem']}")
    if resposta["status"] == "SUCESSO":
        print(f"Protocolo: {resposta['protocolo']}")
        print(f"Data:      {resposta['dados']['data']} as {resposta['dados']['hora']}")

def consultar():
    protocolo = input("\nNumero do protocolo: ").strip()
    resposta  = enviar({
        "operacao":  "CONSULTAR",
        "protocolo": protocolo
    })

    if resposta["status"] == "SUCESSO":
        d = resposta["dados"]
        print(f"\nPaciente:  {d['paciente']}")
        print(f"Tipo:      {d['tipo']}")
        print(f"Data:      {d['data']} as {d['hora']}")
        print(f"Status:    {d['status']}")
        print(f"Criado em: {d['criado_em']}")
    else:
        print(f"Erro: {resposta['mensagem']}")

def cancelar():
    protocolo = input("\nProtocolo para cancelar: ").strip()
    resposta  = enviar({
        "operacao":  "CANCELAR",
        "protocolo": protocolo
    })
    print(f"Status:   {resposta['status']}")
    print(f"Mensagem: {resposta['mensagem']}")

def listar():
    paciente = input("\nNome do paciente (Enter para todos): ").strip()
    resposta = enviar({
        "operacao": "LISTAR",
        "paciente": paciente
    })

    print(f"\nTotal encontrado: {resposta['total']}")
    for a in resposta["agendamentos"]:
        print(f"\n  Protocolo: {a['protocolo']}")
        print(f"  Paciente:  {a['paciente']}")
        print(f"  Tipo:      {a['tipo']}")
        print(f"  Data:      {a['data']} as {a['hora']}")
        print(f"  Status:    {a['status']}")

def menu():
    while True:
        print("\n=== SISTEMA DE AGENDAMENTO ===")
        print("1. Agendar consulta")
        print("2. Consultar agendamento")
        print("3. Cancelar agendamento")
        print("4. Listar agendamentos")
        print("5. Sair")

        opcao = input("Opcao: ").strip()

        if opcao == "1":
            agendar()
        elif opcao == "2":
            consultar()
        elif opcao == "3":
            cancelar()
        elif opcao == "4":
            listar()
        elif opcao == "5":
            print("Encerrando.")
            break
        else:
            print("Opcao invalida!")

if __name__ == "__main__":
    menu()