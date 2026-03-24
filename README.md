# 📅 Sistema de Agendamento de Consultas

Sistema Cliente-Servidor desenvolvido em **Python** para agendamento
de consultas médicas via comunicação por **Sockets TCP** e **JSON**.

---

## 📁 Estrutura do Projeto
```
Code/
├── servidor_agendamento.py   ← Servidor principal
├── cliente_agendamento.py    ← Cliente interativo
├── agendamentos.json         ← Dados persistidos (gerado automaticamente)
└── README.md
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Uso                          |
|------------|--------|------------------------------|
| Python     | 3.13+  | Linguagem principal          |
| Socket     | stdlib | Comunicação TCP              |
| JSON       | stdlib | Serialização de dados        |
| Threading  | stdlib | Múltiplos clientes           |
| UUID       | stdlib | Geração de protocolos únicos |

---

## ⚙️ Pré-requisitos

- Python 3.13+
- Nenhuma biblioteca externa necessária

---

## 🚀 Como Executar

**1. Iniciar o Servidor**
```bash
python servidor_agendamento.py
```

Deve aparecer:
```
==================================================
Servidor de Agendamento iniciado!
Porta: 5000
==================================================
```

**2. Iniciar o Cliente**
```bash
python cliente_agendamento.py
```

---

## 🌐 Conectar em Rede Local

**1. Descobrir o IP do servidor**
```bash
# Windows
ipconfig

# Linux
hostname -I
```

**2. Atualizar o IP no cliente_agendamento.py**
```python
HOST = "192.168.x.x"
```

**3. Testar conexão**
```bash
ping 192.168.x.x
telnet 192.168.x.x 5000
```

---

## 💬 Funcionalidades

| Operacao  | Descricao                              |
|-----------|----------------------------------------|
| AGENDAR   | Cria nova consulta com protocolo único |
| CONSULTAR | Busca agendamento pelo protocolo       |
| CANCELAR  | Cancela agendamento pelo protocolo     |
| LISTAR    | Lista agendamentos por paciente        |

---

## 📋 Exemplo de Uso

**Agendar consulta:**
```
=== SISTEMA DE AGENDAMENTO ===
1. Agendar consulta
2. Consultar agendamento
3. Cancelar agendamento
4. Listar agendamentos
5. Sair
Opcao: 1

--- NOVA CONSULTA ---
Nome do paciente: João Silva
Tipo (Clinico/Dentista/Exame): Clinico
Data (DD/MM/AAAA): 20/03/2026
Hora (HH:MM): 14:30

Status:    SUCESSO
Mensagem:  Consulta agendada com sucesso!
Protocolo: A1B2C3D4
Data:      20/03/2026 as 14:30
```

**Consultar agendamento:**
```
Opcao: 2
Numero do protocolo: A1B2C3D4

Paciente:  João Silva
Tipo:      Clinico
Data:      20/03/2026 as 14:30
Status:    CONFIRMADO
Criado em: 2026-03-16 10:00:00
```

**Cancelar agendamento:**
```
Opcao: 3
Protocolo para cancelar: A1B2C3D4

Status:   SUCESSO
Mensagem: Agendamento A1B2C3D4 cancelado.
```

---

## 🗄️ Estrutura do JSON persistido
```json
{
  "A1B2C3D4": {
    "protocolo":  "A1B2C3D4",
    "paciente":   "João Silva",
    "tipo":       "Clinico",
    "data":       "20/03/2026",
    "hora":       "14:30",
    "status":     "CONFIRMADO",
    "criado_em":  "2026-03-16 10:00:00"
  }
}
```

---

## 🔄 Fluxo de Comunicação
```
Cliente                        Servidor
   |                               |
   |── { operacao: AGENDAR } ────→ |
   |                               | gera protocolo UUID
   |                               | salva em agendamentos.json
   |← { status: SUCESSO,      ──── |
   |    protocolo: A1B2C3D4 }      |
   |                               |
   |── { operacao: CONSULTAR, ───→ |
   |    protocolo: A1B2C3D4 }      |
   |                               | busca no dicionário
   |← { status: SUCESSO,      ──── |
   |    dados: { ... } }           |
```

---

## 📚 Conceitos Demonstrados

- Arquitetura Cliente-Servidor
- Comunicação via Sockets TCP
- Serialização de dados com JSON
- Multithreading para múltiplos clientes
- Persistência de dados em arquivo
- Geração de protocolos únicos com UUID
- Tratamento de erros em rede

---

## 👨‍💻 Autor

**Rubens Rosa Faria Rodrigues R.A: 202410933**
**João Pedro Ribeiro Barbosa R.A: 202420566**
Estudante de Engenharia de Software — UNIGOIÁS
Disciplina: Redes de Computadores
