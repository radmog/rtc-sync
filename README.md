# RTC Sync para Raspberry Pi

Script Python para sincronizar o Raspberry Pi 4 Model B com um RTC (Real Time Clock) via I2C, com sincronização automática via NTP a cada hora quando conectado à internet.

## 📋 Requisitos

- **Hardware:**
  - Raspberry Pi 4 Model B
  - RTC DS3231 ou DS1307 conectado aos pinos I2C (SCL e SDA)
  - Conexão GPIO adequada

- **Software:**
  - Raspberry Pi OS (Debian-based)
  - Python 3.7+
  - I2C habilitado no Raspberry Pi

## 🔌 Conexão do RTC

### Pinos I2C do Raspberry Pi 4:
- **SCL**: GPIO 3 (pino 5 do conector GPIO)
- **SDA**: GPIO 2 (pino 3 do conector GPIO)
- **VCC**: 3.3V ou 5V (de acordo com o RTC)
- **GND**: GND

### Verificar Conexão I2C:
```bash
i2cdetect -y 1
```

Você deve ver algo como:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

O valor `68` indica que o RTC DS3231 está detectado (pode variar).

## 🚀 Instalação

### 1. Habilitar I2C no Raspberry Pi

```bash
sudo raspi-config
```

Vá para: `Interfacing Options` → `I2C` → `Enable`

### 2. Clonar/Copiar Arquivos

Clone ou copie os arquivos para qualquer local temporário:

```bash
cd /tmp
git clone https://seu-repo/rtc-sync.git rtc-sync
cd rtc-sync
```

Ou se já tiver os arquivos, navegue até eles:

```bash
cd /caminho/para/rtc-sync
```

### 3. Executar Script de Instalação

```bash
sudo bash install.sh
```

Este script irá:
- Atualizar pacotes do sistema
- Instalar Python 3 e venv
- Criar ambiente virtual em `/bin/rtcsync/venv`
- Instalar dependências Python no venv
- Copiar scripts para `/bin/rtcsync/`
- Criar diretório de logs em `/var/log/rtcsync/`
- Configurar serviço systemd
- Habilitar I2C (se necessário)

**Nota:** Se I2C foi habilitado, você será solicitado a reiniciar o Raspberry Pi.

## 📦 Dependências Python

As seguintes bibliotecas serão instaladas no ambiente virtual:

```
adafruit-circuitpython-ds3231==2.4.28 # Controle do RTC DS3231
adafruit-blinka==8.47.0                # Abstração de GPIO
ntplib==0.4.0                          # Cliente NTP
schedule==1.2.0                        # Agendamento de tarefas
requests==2.31.0                       # Requisições HTTP
```

Tudo é instalado isoladamente em `/bin/rtcsync/venv/`, sem afetar o sistema.

## 🧪 Teste Manual

Antes de configurar como serviço, teste o script manualmente:

```bash
# Ativar ambiente virtual
source /bin/rtcsync/venv/bin/activate

# Executar script
python3 /bin/rtcsync/rtc_sync.py
```

Você deve ver algo como:

```
2026-06-04 14:30:25,123 - INFO - Iniciando RTC Sync para Raspberry Pi
2026-06-04 14:30:25,124 - INFO - Hora do sistema: 2026-06-04 14:30:25.123456
2026-06-04 14:30:26,234 - INFO - ✓ RTC DS3231 inicializado com sucesso
2026-06-04 14:30:27,345 - INFO - Hora lida do RTC: 2026-06-04 14:30:27
2026-06-04 14:30:28,456 - INFO - ✓ Conexão com internet detectada
2026-06-04 14:30:29,567 - INFO - ✓ Hora NTP obtida de pool.ntp.org
2026-06-04 14:30:29,678 - INFO - ✓ RTC atualizado para: 2026-06-04 14:30:29
```

Se houver erro, veja [TROUBLESHOOTING.md](/bin/rtcsync/TROUBLESHOOTING.md)
2026-06-04 14:30:29,567 - INFO - ✓ Hora NTP obtida de pool.ntp.org: 2026-06-04 14:30:29
2026-06-04 14:30:29,678 - INFO - ✓ RTC atualizado para: 2026-06-04 14:30:29
```

## 🔧 Configuração como Serviço Systemd

Para que o script execute automaticamente no boot:

### 1. Verificar se serviço está registrado:

```bash
sudo systemctl list-unit-files | grep rtc_sync
```

Deve aparecer: `rtc_sync.service`

### 2. Habilitar serviço (inicia no boot):

```bash
sudo systemctl enable rtc_sync.service
```

### 3. Iniciar serviço:

```bash
sudo systemctl start rtc_sync.service
```

O script está configurado para usar o ambiente virtual em `/bin/rtcsync/venv/`

**Nota:** O arquivo de serviço foi copiado para `/etc/systemd/system/` automaticamente pelo `install.sh`

## 📊 Gerenciamento do Serviço

### Ver status:
```bash
sudo systemctl status rtc_sync.service
```

### Ver logs em tempo real:
```bash
sudo tail -f /var/log/rtcsync/rtc_sync.log
```

### Ver logs históricos:
```bash
journalctl -u rtc_sync.service -n 50
```

### Ver logs com mais detalhes:
```bash
journalctl -u rtc_sync.service -f
```

### Parar serviço:
```bash
sudo systemctl stop rtc_sync.service
```

### Reiniciar serviço:
```bash
sudo systemctl restart rtc_sync.service
```

### Desabilitar serviço (não inicia no boot):
```bash
sudo systemctl disable rtc_sync.service
```

## 🔄 Funcionamento

1. **Inicialização:**
   - Conecta ao RTC via I2C
   - Lê a hora atual do RTC
   - Se conectado à internet, sincroniza com servidor NTP

2. **Sincronização Horária:**
   - A cada hora exata (00:00, 01:00, 02:00, etc.)
   - Verifica conexão com internet
   - Se conectado, obtém hora de servidor NTP
   - Atualiza o RTC com hora precisa
   - Também atualiza a hora do sistema (se possível)

3. **Servidores NTP Utilizados:**
   - pool.ntp.org (principal)
   - time.nist.gov (fallback)
   - time.google.com (fallback)

## 📝 Logs

Os logs são salvos em `/var/log/rtcsync/rtc_sync.log` e também exibidos no console.

Formato dos logs:
```
[Timestamp] - [LEVEL] - [Mensagem]
```

Símbolos nos logs:
- ✓ Operação bem-sucedida
- ✗ Erro
- ⚠ Aviso
- = Separador de seções

**Localização dos Arquivos de Instalação:**
```
/bin/rtcsync/                 # Diretório principal
├── rtc_sync.py              # Script principal
├── test_rtc.py              # Script de diagnóstico
├── requirements.txt         # Dependências (referência)
├── venv/                    # Ambiente virtual Python
│   ├── bin/                 # Executáveis
│   │   ├── python3          # Python do venv
│   │   └── ...
│   ├── lib/                 # Bibliotecas Python
│   └── ...
├── README.md                # Documentação completa
├── QUICK_START.md           # Guia rápido
├── TROUBLESHOOTING.md       # Solução de problemas
└── PROJETO.md               # Resumo do projeto

/var/log/rtcsync/            # Diretório de logs
└── rtc_sync.log             # Log do serviço

/etc/systemd/system/         # Serviços do sistema
└── rtc_sync.service         # Serviço RTC Sync
```

## 🔒 Permissões

O script requer privilégios de root para:
- Acessar I2C
- Atualizar hora do sistema
- Acessar arquivo de log em `/var/log/`

## ❓ Solução de Problemas

### "Erro ao inicializar RTC"

1. Verifique conexão I2C:
   ```bash
   i2cdetect -y 1
   ```

2. Verifique se I2C está habilitado:
   ```bash
   sudo raspi-config
   ```

3. Verifique conexão física dos cabos SCL/SDA

### "Sem conexão com internet"

- Verifique se o Pi tem acesso à internet
- Ping em 8.8.8.8 deve funcionar
- Verifique firewall/proxy

### "Falha ao atualizar hora do sistema"

- O script pode estar sem privilégios sudo
- Verifique se é executado como root

### "RTC não está sincronizando"

1. Verifique se a bateria do RTC está funcionando
2. Verifique os logs para mensagens de erro
3. Teste manualmente com `sudo python3 rtc_sync.py`

## 📌 Notas Importantes

- O RTC preserva a hora mesmo sem energia (bateria interna)
- A sincronização NTP é mais precisa que confiar apenas no RTC
- A sincronização ocorre automaticamente a cada hora exata
- Se sem internet, o Pi usa a hora do RTC

## 📄 Licença

Este script é fornecido como está para uso pessoal e educacional.

## 👨‍💻 Autor

Script criado para Raspberry Pi 4 Model B com RTC DS3231

---

**Última atualização:** Junho de 2026
