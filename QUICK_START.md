# Quick Start - RTC Sync

## ⚡ Início Rápido (5 minutos)

### Pré-requisitos
- Raspberry Pi 4 com RTC DS3231 conectado
- SSH ou acesso direto ao terminal
- Conexão com internet no Pi (opcional)

### Passos

#### 1️⃣ Habilitar I2C (se não estiver)
```bash
sudo raspi-config
# Interfacing Options → I2C → Enable
# Reboot
```

#### 2️⃣ Clonar/Copiar scripts
```bash
cd /tmp
git clone seu-repo rtc-sync  # ou copie manualmente
cd rtc-sync
```

#### 3️⃣ Instalar (cria venv + instala deps)
```bash
sudo bash install.sh
```

A instalação irá:
- Criar `/bin/rtcsync/` com ambiente virtual
- Instalar dependências em `/bin/rtcsync/venv/`
- Configurar logs em `/var/log/rtcsync/`
- Registrar serviço systemd

#### 4️⃣ Testar
```bash
source /bin/rtcsync/venv/bin/activate
python3 /bin/rtcsync/test_rtc.py
```

Deve mostrar: **✓ TODOS OS TESTES PASSARAM**

#### 5️⃣ Executar manualmente (teste)
```bash
source /bin/rtcsync/venv/bin/activate
python3 /bin/rtcsync/rtc_sync.py
```

Deve mostrar:
```
✓ RTC DS3231 inicializado com sucesso
✓ Hora lida do RTC: ...
✓ Conexão com internet detectada
✓ Hora NTP obtida de pool.ntp.org
✓ RTC atualizado para: ...
```

#### 6️⃣ Configurar como serviço (automático no boot)
```bash
sudo systemctl enable rtc_sync.service
sudo systemctl start rtc_sync.service
```

Verificar:
```bash
sudo systemctl status rtc_sync.service
```

---

## 📍 Verificação I2C

Se der erro, verifique I2C:

```bash
i2cdetect -y 1
```

Procure por `68` na tabela. Exemplo:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --
```

Se não aparecer:
1. Verifique cabos SCL/SDA
2. Verifique se I2C está habilitado
3. Reinicie o Pi

---

## 📊 Monitorar

Depois de instalado como serviço:

**Ver status:**
```bash
sudo systemctl status rtc_sync.service
```

**Ver logs em tempo real:**
```bash
sudo tail -f /var/log/rtcsync/rtc_sync.log
```

**Sincronização manual:**
```bash
sudo systemctl restart rtc_sync.service
```

---

## 🆘 Problemas?

Veja: [/bin/rtcsync/TROUBLESHOOTING.md](/bin/rtcsync/TROUBLESHOOTING.md)

---

## 📝 Estrutura de Instalação

```
/bin/rtcsync/                    # Instalação
├── rtc_sync.py                 # Script principal
├── test_rtc.py                 # Diagnóstico
├── venv/                       # Ambiente virtual
│   └── bin/python3             # Python isolado
├── README.md
├── QUICK_START.md
├── TROUBLESHOOTING.md
└── PROJETO.md

/var/log/rtcsync/               # Logs
└── rtc_sync.log

/etc/systemd/system/            # Serviço
└── rtc_sync.service
```

---

## 🔧 Configurações Comuns

### Mudar intervalo de sincronização

Editar `/bin/rtcsync/rtc_sync.py` linha ~330:
```python
schedule.every().hour.at(":00").do(hourly_sync_job, rtc=rtc)
```

Opções:
- `every().minute.do()` - a cada minuto
- `every(5).minutes.do()` - a cada 5 minutos
- `every().hour.do()` - a cada hora (não exato)
- `every().day.at("10:30").do()` - diariamente às 10:30

### Mudar servidores NTP

Editar `/bin/rtcsync/rtc_sync.py` linhas ~30-34:
```python
NTP_SERVERS = [
    'pool.ntp.org',
    'time.nist.gov',
    'time.google.com'
]
```

---

## 💡 Dicas

1. **Ambiente Virtual:** Sempre active o venv antes de executar: `source /bin/rtcsync/venv/bin/activate`

2. **Serviço:** O systemd usa o venv automaticamente, não precisa ativar manualmente

3. **Bateria do RTC:** Verifique se a bateria (CR2032) está presente e carregada

4. **Sem internet:** O script funciona normalmente, apenas pulará sincronização NTP

5. **Logs:** Mantenha os logs para debugar problemas

6. **Sincronização:** A hora é sincronizada EXATA no horário (00:00, 01:00, 02:00, etc.)

---

## 🚀 Próximos Passos

1. ✅ Instalar com `install.sh`
2. ✅ Testar com `test_rtc.py`
3. ✅ Executar manualmente
4. ✅ Configurar como serviço systemd
5. ✅ Monitorar logs

Done! ✨

---

**Última atualização:** Junho de 2026
