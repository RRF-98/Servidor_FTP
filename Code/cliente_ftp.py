from ftplib import FTP
import os

HOST  = "localhost"
PORTA = 21

def conectar():
    ftp = FTP()
    ftp.connect(HOST, PORTA)
    print(ftp.getwelcome())

    usuario = input("Usuario (Enter para anonimo): ").strip()
    senha   = input("Senha:   ").strip()

    if usuario == "":
        ftp.login()
    else:
        ftp.login(user=usuario, passwd=senha)

    print(f"Conectado como: {usuario or 'anonimo'}")
    return ftp

def listar_arquivos(ftp):
    print("\n--- Arquivos no servidor ---")
    ftp.dir()

def fazer_upload(ftp):
    caminho = input("Caminho do arquivo local: ").strip()
    if not os.path.exists(caminho):
        print("Arquivo nao encontrado!")
        return

    nome = os.path.basename(caminho)
    with open(caminho, "rb") as f:
        ftp.storbinary(f"STOR {nome}", f)
    print(f"Upload concluido: {nome}")

def fazer_download(ftp):
    nome = input("Nome do arquivo para baixar: ").strip()
    with open(nome, "wb") as f:
        ftp.retrbinary(f"RETR {nome}", f.write)
    print(f"Download concluido: {nome}")

def deletar_arquivo(ftp):
    nome = input("Nome do arquivo para deletar: ").strip()
    ftp.delete(nome)
    print(f"Arquivo deletado: {nome}")

def menu(ftp):
    while True:
        print("\n=== MENU FTP ===")
        print("1. Listar arquivos")
        print("2. Upload")
        print("3. Download")
        print("4. Deletar arquivo")
        print("5. Sair")

        opcao = input("Opcao: ").strip()

        if opcao == "1":
            listar_arquivos(ftp)
        elif opcao == "2":
            fazer_upload(ftp)
        elif opcao == "3":
            fazer_download(ftp)
        elif opcao == "4":
            deletar_arquivo(ftp)
        elif opcao == "5":
            ftp.quit()
            print("Desconectado.")
            break
        else:
            print("Opcao invalida!")

if __name__ == "__main__":
    ftp = conectar()
    menu(ftp)