from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
import os
import logging
import shutil
from datetime import datetime

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
PASTA_FTP  = os.path.join(PASTA_BASE, "ftp_arquivos")
PASTA_LOGS = os.path.join(PASTA_BASE, "logs")

os.makedirs(PASTA_FTP,  exist_ok=True)
os.makedirs(PASTA_LOGS, exist_ok=True)

# -------------------------------------------------------
# Sistema de Logs
# -------------------------------------------------------
ARQUIVO_LOG         = os.path.join(PASTA_LOGS, "ftp_servidor.log")
ARQUIVO_LOG_TRANSF  = os.path.join(PASTA_LOGS, "transferencias.log")
ARQUIVO_LOG_ACESSO  = os.path.join(PASTA_LOGS, "acessos.log")

def configurar_logs():

    # Log geral do servidor
    logging.basicConfig(
        filename=ARQUIVO_LOG,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Log de transferencias
    log_transf = logging.getLogger("transferencias")
    log_transf.setLevel(logging.INFO)
    handler_transf = logging.FileHandler(ARQUIVO_LOG_TRANSF, encoding="utf-8")
    handler_transf.setFormatter(logging.Formatter(
        "%(asctime)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    log_transf.addHandler(handler_transf)

    # Log de acessos
    log_acesso = logging.getLogger("acessos")
    log_acesso.setLevel(logging.INFO)
    handler_acesso = logging.FileHandler(ARQUIVO_LOG_ACESSO, encoding="utf-8")
    handler_acesso.setFormatter(logging.Formatter(
        "%(asctime)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    log_acesso.addHandler(handler_acesso)

    return log_transf, log_acesso

log_transf, log_acesso = configurar_logs()

# -------------------------------------------------------
# Handler customizado com logs detalhados
# -------------------------------------------------------
class FTPHandlerComLog(FTPHandler):

    def on_connect(self):
        msg = f"CONEXAO   | IP: {self.remote_ip} | Porta: {self.remote_port}"
        log_acesso.info(msg)
        logging.info(msg)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def on_disconnect(self):
        msg = f"DESCONEXAO | IP: {self.remote_ip} | Usuario: {self.username or 'nao autenticado'}"
        log_acesso.info(msg)
        logging.info(msg)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def on_login(self, username):
        msg = f"LOGIN     | Usuario: {username} | IP: {self.remote_ip}"
        log_acesso.info(msg)
        logging.info(msg)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def on_login_failed(self, username, password):
        msg = f"LOGIN FALHOU | Usuario: {username} | IP: {self.remote_ip}"
        log_acesso.warning(msg)
        logging.warning(msg)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] AVISO: {msg}")

    def on_logout(self, username):
        msg = f"LOGOUT    | Usuario: {username} | IP: {self.remote_ip}"
        log_acesso.info(msg)
        logging.info(msg)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def on_file_sent(self, file):
        tamanho = os.path.getsize(file) if os.path.exists(file) else 0
        tamanho_kb = tamanho / 1024
        msg = (
            f"DOWNLOAD  | Usuario: {self.username} | "
            f"Arquivo: {os.path.basename(file)} | "
            f"Tamanho: {tamanho_kb:.2f} KB | "
            f"IP: {self.remote_ip} | "
            f"Status: SUCESSO"
        )
        log_transf.info(msg)
        logging.info(msg)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def on_file_received(self, file):
        tamanho = os.path.getsize(file) if os.path.exists(file) else 0
        tamanho_kb = tamanho / 1024
        msg = (
            f"UPLOAD    | Usuario: {self.username} | "
            f"Arquivo: {os.path.basename(file)} | "
            f"Tamanho: {tamanho_kb:.2f} KB | "
            f"IP: {self.remote_ip} | "
            f"Status: SUCESSO"
        )
        log_transf.info(msg)
        logging.info(msg)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def on_incomplete_file_sent(self, file):
        msg = (
            f"DOWNLOAD INCOMPLETO | Usuario: {self.username} | "
            f"Arquivo: {os.path.basename(file)} | "
            f"IP: {self.remote_ip} | "
            f"Status: FALHA"
        )
        log_transf.warning(msg)
        logging.warning(msg)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] AVISO: {msg}")

    def on_incomplete_file_received(self, file):
        # Remove arquivo incompleto
        if os.path.exists(file):
            os.remove(file)
        msg = (
            f"UPLOAD INCOMPLETO | Usuario: {self.username} | "
            f"Arquivo: {os.path.basename(file)} | "
            f"IP: {self.remote_ip} | "
            f"Status: FALHA — arquivo removido"
        )
        log_transf.warning(msg)
        logging.warning(msg)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] AVISO: {msg}")

# -------------------------------------------------------
# Copia JSONs para pasta FTP
# -------------------------------------------------------
def copiar_jsons():
    arquivos = ["agendamentos.json", "reclamacoes.json"]
    for arquivo in arquivos:
        origem  = os.path.join(PASTA_BASE, arquivo)
        destino = os.path.join(PASTA_FTP,  arquivo)
        if os.path.exists(origem):
            shutil.copy2(origem, destino)
            print(f"[INFO] Copiado: {arquivo} → ftp_arquivos/")
        else:
            print(f"[AVISO] Nao encontrado: {arquivo}")

# -------------------------------------------------------
# Inicialização
# -------------------------------------------------------
def iniciar_servidor_ftp():

    autorizador = DummyAuthorizer()
    autorizador.add_user("admin",   "admin123", PASTA_FTP, perm="elrawdm")
    autorizador.add_user("usuario", "user123",  PASTA_FTP, perm="elr")
    autorizador.add_anonymous(PASTA_FTP, perm="elr")

    handler               = FTPHandlerComLog
    handler.authorizer    = autorizador
    handler.banner        = "Bem-vindo ao servidor FTP!"
    handler.passive_ports = range(60000, 60100)

    servidor                 = FTPServer(("0.0.0.0", 21), handler)
    servidor.max_cons        = 50
    servidor.max_cons_per_ip = 5

    print("=" * 60)
    print("Servidor FTP iniciado!")
    print("Porta:    21")
    print(f"Pasta:    {PASTA_FTP}")
    print("Usuarios:")
    print("  admin   / admin123 (leitura e escrita)")
    print("  usuario / user123  (somente leitura)")
    print("  anonymous          (somente leitura)")
    print("=" * 60)
    print("Logs:")
    print(f"  Geral:          {ARQUIVO_LOG}")
    print(f"  Transferencias: {ARQUIVO_LOG_TRANSF}")
    print(f"  Acessos:        {ARQUIVO_LOG_ACESSO}")
    print("=" * 60)

    copiar_jsons()

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Servidor FTP encerrado.")

if __name__ == "__main__":
    iniciar_servidor_ftp()
