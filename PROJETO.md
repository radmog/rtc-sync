# RTC Sync - Projeto Completo

## 📌 O que foi criado

Solução completa em Python para sincronizar Raspberry Pi 4 Model B com um RTC (Real Time Clock) conectado via I2C, com correção automática a cada hora quando conectado à internet.

**Instalação:** `/bin/rtcsync/` com ambiente virtual isolado em `/bin/rtcsync/venv/`

## 📁 Arquivos Inclusos

### 1. **rtc_sync.py** (Script Principal)
- Script principal que sincroniza Pi com RTC
- Verificação de conectividade com internet
- Sincronização com servidor NTP a cada hora exata
- Logging completo em `/var/log/rtcsync/`
- Tratamento de erros robusto
- Local: `/bin/rtcsync/rtc_sync.py`

### 2. **test_rtc.py** (Diagnóstico)
- Script para testar toda a configuração
- Verifica I2C, RTC, internet e NTP
- Identifica problemas automaticamente
- Muito útil para troubleshooting
- Local: `/bin/rtcsync/test_rtc.py`

### 3. **requirements.txt** (Dependências)
- Todas as bibliotecas Python necessárias
- Pronto para usar com `pip install -r requirements.txt`
- Instaladas em `/bin/rtcsync/venv/lib/python3.x/site-packages/`

### 4. **install.sh** (Instalação)
- Script automatizado de instalação
- Cria `/bin/rtcsync/` com ambiente virtual
- Atualiza pacotes, habilita I2C, instala dependências
- Use com `sudo bash install.sh`

### 5. **rtc_sync.service** (Serviço Systemd)
- Configuração para executar script no boot
- Usa o venv automaticamente via `/bin/rtcsync/venv/bin/python3`
- Reinicia automaticamente se falhar
- Gerenciável com `systemctl`
- Local: `/etc/systemd/system/rtc_sync.service`

### 6. **README.md** (Documentação Completa)
- Instruções detalhadas de instalação
- Explicação de funcionamento
- Gerenciamento do serviço
- Solução de problemas
- Local: `/bin/rtcsync/README.md`

### 7. **QUICK_START.md** (Guia Rápido)
- Início rápido em 5 minutos
- Passos simples e diretos
- Perfeito para começar rápido
- Local: `/bin/rtcsync/QUICK_START.md`

### 8. **TROUBLESHOOTING.md** (Resolução de Problemas)
- Problemas comuns e soluções
- Ferramentas de diagnóstico
- Checklist de verificação
- Local: `/bin/rtcsync/TROUBLESHOOTING.md`

## 🚀 Como Usar

### Opção 1: Instalação Completa (Recomendado)
```bash
cd /tmp/rtc-sync  # ou onde estão os arquivos
sudo bash install.sh
sudo systemctl start rtc_sync.service
```

### Opção 2: Teste Manual Primeiro
```bash
cd /tmp/rtc-sync
sudo bash install.sh

# Ativar venv
source /bin/rtcsync/venv/bin/activate

# Testar
sudo python3 /bin/rtcsync/test_rtc.py
sudo python3 /bin/rtcsync/rtc_sync.py
```

## ✨ Características Principais

✅ **Sincronização I2C** - Conecta a RTC via I2C (pinos SCL/SDA)  
✅ **Verificação de Internet** - Detecta automaticamente conexão  
✅ **NTP Automático** - Sincroniza com servidor NTP a cada hora  
✅ **Múltiplos Servidores** - Fallback para servidores alternativos  
✅ **Logging Detalhado** - Registra todas as operações  
✅ **Diagnóstico** - Script de teste integrado  
✅ **Systemd Service** - Executa no boot automaticamente  
✅ **Tratamento de Erros** - Robusto e confiável  
✅ **Ambiente Virtual** - Dependências isoladas em venv  
✅ **Bem Documentado** - Documentação completa  

## 🔌 Hardware Suportado

- **Raspberry Pi:** 4 Model B (também funciona em 3B+, Zero 2W, etc.)
- **RTC:** DS3231, DS1307 (e compatíveis)
- **Conexão:** I2C via GPIO (pinos 3 e 5)
- **Bateria:** CR2032 no RTC (para manter hora sem poder)

## 📊 Funcionamento

```
Inicialização
    ↓
Conecta ao RTC via I2C
    ↓
Lê hora atual do RTC
    ↓
Verifica conexão com internet
    ↓
    ├─ SIM → Sincroniza com NTP → Atualiza RTC
    └─ NÃO → Usa hora do RTC
    ↓
Agenda próxima sincronização (próxima hora exata)
    ↓
Aguarda hora exata
    ↓
Repete sincronização (volta ao passo 3)
```

## 🔄 Sincronização Horária

- **Quando:** A cada hora exata (00:00, 01:00, 02:00, etc.)
- **Como:** Obtém hora de servidor NTP
- **Se sem internet:** Pula sincronização (RTC continua funcionando)
- **Frequência:** Configurável (padrão: a cada hora)

## 📝 Estrutura de Logs

```
2026-06-04 14:30:25,123 - INFO - Iniciando RTC Sync para Raspberry Pi
2026-06-04 14:30:26,234 - INFO - ✓ RTC DS3231 inicializado com sucesso
2026-06-04 14:30:27,345 - INFO - ✓ Hora lida do RTC: 2026-06-04 14:30:27
2026-06-04 14:30:28,456 - INFO - ✓ Conexão com internet detectada
2026-06-04 14:30:29,567 - INFO - ✓ Hora NTP obtida de pool.ntp.org
2026-06-04 14:30:29,678 - INFO - ✓ RTC atualizado para: 2026-06-04 14:30:29
```

## 🛠️ Dependências

As dependências são instaladas no ambiente virtual em `/bin/rtcsync/venv/`:

- Python 3.7+ (no sistema)
- Adafruit CircuitPython DS3231
- Adafruit Blinka (abstração GPIO)
- ntplib (cliente NTP)
- schedule (agendamento)
- requests (requisições HTTP)

**Nenhuma dependência é instalada globalmente, tudo fica isolado no venv.**

## 📁 Estrutura de Arquivos

```
/bin/rtcsync/                      # Instalação principal
├── rtc_sync.py                   # Script de sincronização
├── test_rtc.py                   # Script de diagnóstico
├── requirements.txt              # Dependências (referência)
├── venv/                         # Ambiente virtual Python isolado
│   ├── bin/
│   │   ├── python3               # Python do venv
│   │   ├── pip                   # Pip do venv
│   │   └── ...                   # Ferramentas do venv
│   ├── lib/                      # Bibliotecas Python
│   ├── include/                  # Headers
│   └── pyvenv.cfg               # Configuração do venv
├── README.md                     # Documentação completa
├── QUICK_START.md               # Guia rápido
├── TROUBLESHOOTING.md           # Solução de problemas
└── PROJETO.md                   # Este arquivo

/var/log/rtcsync/                 # Diretório de logs
└── rtc_sync.log                  # Log do serviço

/etc/systemd/system/              # Serviços do sistema
└── rtc_sync.service              # Serviço RTC Sync
```

## 🔒 Permissões

O script requer:
- Acesso root para I2C e atualizar hora do sistema
- Permissão de escrita em `/var/log/rtcsync/`

Execução:
- Via systemd: automático como root
- Manual: `sudo python3 /bin/rtcsync/rtc_sync.py`

## 📌 Notas Importantes

1. **Ambiente Virtual:** Isolado em `/bin/rtcsync/venv/`
2. **Bateria do RTC:** Certifique-se de que está instalada
3. **I2C Habilitado:** Execute `sudo raspi-config` se necessário
4. **Primeira Execução:** Sempre teste manualmente antes de usar como serviço
5. **Logs:** Em `/var/log/rtcsync/rtc_sync.log` para troubleshooting
6. **Sem Internet:** O Pi continuará funcionando, apenas sem sincronização NTP
7. **Atualização:** Ambiente virtual é totalmente isolado, fácil manter/atualizar

## 🎯 Objetivo Alcançado

✅ Script Python para sincronizar Raspberry Pi com RTC  
✅ Sincronização automática a cada hora com internet  
✅ Precisão horária mantida  
✅ Funciona offline também  
✅ Fácil instalação com venv  
✅ Dependências isoladas  
✅ Robusto e confiável  

## 📚 Documentação

- [README.md](/bin/rtcsync/README.md) - Documentação completa
- [QUICK_START.md](/bin/rtcsync/QUICK_START.md) - Guia rápido
- [TROUBLESHOOTING.md](/bin/rtcsync/TROUBLESHOOTING.md) - Solução de problemas

## 📞 Suporte

Para problemas:
1. Veja [TROUBLESHOOTING.md](/bin/rtcsync/TROUBLESHOOTING.md)
2. Execute `source /bin/rtcsync/venv/bin/activate && sudo python3 /bin/rtcsync/test_rtc.py`
3. Verifique `/var/log/rtcsync/rtc_sync.log`

---

**Projeto:** RTC Sync para Raspberry Pi com venv  
**Versão:** 2.0  
**Data:** Junho de 2026  
**Status:** Pronto para Produção ✅

## ✨ Características Principais

✅ **Sincronização I2C** - Conecta a RTC via I2C (pinos SCL/SDA)  
✅ **Verificação de Internet** - Detecta automaticamente conexão  
✅ **NTP Automático** - Sincroniza com servidor NTP a cada hora  
✅ **Múltiplos Servidores** - Fallback para servidores alternativos  
✅ **Logging Detalhado** - Registra todas as operações  
✅ **Diagnóstico** - Script de teste integrado  
✅ **Systemd Service** - Executa no boot automaticamente  
✅ **Tratamento de Erros** - Robusto e confiável  
✅ **Ambiente Virtual** - Dependências isoladas em venv  
✅ **Bem Documentado** - Documentação completa

## 🔌 Hardware Suportado

- **Raspberry Pi:** 4 Model B (também funciona em 3B+, Zero 2W, etc.)
- **RTC:** DS3231, DS1307 (e compatíveis)
- **Conexão:** I2C via GPIO (pinos 3 e 5)
- **Bateria:** CR2032 no RTC (para manter hora sem poder)

## 📊 Funcionamento

```
Inicialização
    ↓
Conecta ao RTC via I2C
    ↓
Lê hora atual do RTC
    ↓
Verifica conexão com internet
    ↓
    ├─ SIM → Sincroniza com NTP → Atualiza RTC
    └─ NÃO → Usa hora do RTC
    ↓
Agenda próxima sincronização (próxima hora exata)
    ↓
Aguarda hora exata
    ↓
Repete sincronização (volta ao passo 3)
```

## 🔄 Sincronização Horária

- **Quando:** A cada hora exata (00:00, 01:00, 02:00, etc.)
- **Como:** Obtém hora de servidor NTP
- **Se sem internet:** Pula sincronização (RTC continua funcionando)
- **Frequência:** Configurável (padrão: a cada hora)

## 📝 Estrutura de Logs

```
2026-06-04 14:30:25,123 - INFO - Iniciando RTC Sync para Raspberry Pi
2026-06-04 14:30:26,234 - INFO - ✓ RTC DS3231 inicializado com sucesso
2026-06-04 14:30:27,345 - INFO - ✓ Hora lida do RTC: 2026-06-04 14:30:27
2026-06-04 14:30:28,456 - INFO - ✓ Conexão com internet detectada
2026-06-04 14:30:29,567 - INFO - ✓ Hora NTP obtida de pool.ntp.org
2026-06-04 14:30:29,678 - INFO - ✓ RTC atualizado para: 2026-06-04 14:30:29
```

## 🛠️ Dependências

- Python 3.7+
- Adafruit CircuitPython DS3231
- Adafruit Blinka (abstração GPIO)
- ntplib (cliente NTP)
- schedule (agendamento)
- requests (requisições HTTP)

## 🔒 Permissões

O script requer:
- Acesso root para I2C e atualizar hora do sistema
- Permissão de escrita em `/var/log/`

Executar como:
```bash
sudo python3 rtc_sync.py
```

## 📌 Notas Importantes

1. **Bateria do RTC:** Certifique-se de que a bateria está instalada
2. **I2C Habilitado:** Execute `sudo raspi-config` se não estiver habilitado
3. **Primeira Execução:** Sempre teste manualmente antes de adicionar como serviço
4. **Logs:** Verifique `/var/log/rtc_sync.log` para troubleshooting
5. **Sem Internet:** O Pi continuará funcionando, apenas sem sincronização NTP

## 🎯 Objetivo Alcançado

✅ Script Python para sincronizar Raspberry Pi com RTC  
✅ Sincronização automática a cada hora com internet  
✅ Precisão horária mantida  
✅ Funciona offline também  
✅ Fácil instalação  
✅ Robusto e confiável  

## 📚 Documentação

- [README.md](README.md) - Documentação completa
- [QUICK_START.md](QUICK_START.md) - Guia rápido
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Solução de problemas

## 📞 Suporte

Para problemas:
1. Veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Execute `sudo python3 test_rtc.py`
3. Verifique `/var/log/rtc_sync.log`

---

**Projeto:** RTC Sync para Raspberry Pi  
**Versão:** 1.0  
**Data:** Junho de 2026  
**Status:** Pronto para Produção ✅
