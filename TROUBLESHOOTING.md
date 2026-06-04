# Guia de Troubleshooting - RTC Sync

## 🚨 Problemas Comuns e Soluções

### Problema 1: "Erro ao inicializar RTC"

**Mensagem de erro:**
```
✗ Erro ao inicializar RTC: Could not find i2c bus
```

**Causas possíveis:**
1. I2C não está habilitado no Raspberry Pi
2. RTC não está fisicamente conectado
3. Pinos SCL/SDA estão soltos ou danificados
4. Script não está sendo executado como root

**Soluções:**

### 1. **Verificar se I2C está habilitado:**
   ```bash
   sudo raspi-config
   ```
   - Vá para `Interfacing Options` → `I2C` → `Enable`
   - Reinicie o Pi: `sudo reboot`

2. **Verificar conexão física:**
   - Verifique se os cabos SCL e SDA estão bem conectados
   - Inspecione visualmente os conectores
   - Tente outro cabo ou placa

3. **Verificar detecção I2C:**
   ```bash
   sudo i2cdetect -y 1
   ```
   - Procure por `68` (DS3231) ou `67` (DS1307)
   - Se não aparecer nada, o RTC não está detectado

4. **Executar como root:**
   ```bash
   # Ativar ambiente virtual
   source /bin/rtcsync/venv/bin/activate
   sudo python3 /bin/rtcsync/rtc_sync.py
   ```

---

### Problema 2: "Sem conexão com internet"

**Mensagem de erro:**
```
✗ Sem conexão com internet
```

**Causas possíveis:**
1. Pi não está conectado à rede
2. Problemas com DNS
3. Firewall bloqueando conexão
4. Provedor de internet fora do ar

**Soluções:**

1. **Verificar conectividade:**
   ```bash
   ping -c 3 8.8.8.8
   ```
   - Se funcionar, o Pi tem internet
   - Se não funcionar, configure a rede:
     ```bash
     sudo raspi-config
     ```
     Vá para `System Options` → `Wireless LAN`

2. **Verificar DNS:**
   ```bash
   nslookup pool.ntp.org
   ```
   - Se não resolver, tente com IP direto: `nslookup 8.8.8.8`

3. **Se sem internet é esperado:**
   - O RTC funcionará normalmente
   - O Pi usará a hora armazenada no RTC
   - A sincronização NTP será pulada

---

### Problema 3: "Falha ao obter hora NTP"

**Mensagem de erro:**
```
✗ Erro ao obter hora NTP de pool.ntp.org
```

**Causas possíveis:**
1. Conexão com internet instável
2. Servidores NTP indisponíveis
3. Firewall/proxy bloqueando porta 123 (NTP)
4. Latência de rede muito alta

**Soluções:**

1. **Testar conectividade com servidor NTP:**
   ```bash
   sudo ntpdate -d pool.ntp.org
   ```

2. **Verificar firewall:**
   ```bash
   sudo ufw status
   ```
   - A porta 123 (UDP) deve estar aberta para NTP

3. **Testar script de diagnóstico:**
   ```bash
   sudo python3 test_rtc.py
   ```

4. **Se vários servidores falharem:**
   - Pode ser problema de conexão com internet
   - Verifique sua rede/ISP

---

### Problema 4: "Permissão negada ao atualizar hora do sistema"

**Mensagem de erro:**
```
⚠ Erro ao atualizar hora do sistema: [Errno 1]
```

**Causas possíveis:**
1. Script não está sendo executado como root
2. Sudo não está configurado corretamente
3. SELinux ou AppArmor bloqueando

**Soluções:**

1. **Executar como root:**
   ```bash
   sudo python3 rtc_sync.py
   ```

2. **Se usar systemd:**
   - Verifique se User=root em rtc_sync.service:
     ```bash
     sudo systemctl cat rtc_sync.service | grep User
     ```

3. **Configurar sudo sem senha (opcional e com cautela):**
   ```bash
   sudo visudo
   ```
   Adicione ao final:
   ```
   pi ALL=(ALL) NOPASSWD: /usr/bin/python3
   ```

---

### Problema 5: "RTC não está sincronizando"

**Sintoma:** 
- O RTC continua com hora errada mesmo após sincronização

**Causas possíveis:**
1. Bateria do RTC descarregada
2. Arquivo de log mostra erro durante sincronização
3. RTC está com defeito
4. Problema com I2C intermitente

**Soluções:**

1. **Verificar bateria do RTC:**
   - O RTC DS3231 tem bateria interna (CR2032 típica)
   - Se tiver bateria descarregada, o RTC perderá a hora
   - Substitua a bateria se necessário

2. **Forçar sincronização manual:**
   ```bash
   sudo python3 rtc_sync.py
   ```
   - Veja os logs em detalhes

3. **Ver logs detalhados:**
   ```bash
   sudo tail -f /var/log/rtcsync/rtc_sync.log
   ```
   - Procure por mensagens de erro

4. **Testar RTC com diagnóstico:**
   ```bash
   source /bin/rtcsync/venv/bin/activate
   sudo python3 /bin/rtcsync/test_rtc.py
   ```

5. **Se RTC estiver com defeito:**
   - Tente outro RTC ou outro Pi para confirmar
   - Pode ser necessário substituir o RTC

---

### Problema 6: "Serviço systemd não inicia"

**Mensagem de erro:**
```
Job for rtc_sync.service failed because the control process exited with error code.
```

**Causas possíveis:**
1. Dependência não instalada
2. Caminho do arquivo incorreto
3. Permissões incorretas
4. RTC não está conectado

**Soluções:**

1. **Ver detalhes do erro:**
   ```bash
   sudo systemctl status rtc_sync.service
   ```
   ```bash
   journalctl -u rtc_sync.service -n 20
   ```

2. **Verificar se arquivo de serviço está correto:**
   ```bash
   sudo cat /etc/systemd/system/rtc_sync.service
   ```
   - Procure por `ExecStart` e verifique se caminho está correto

3. **Recarregar e reiniciar:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart rtc_sync.service
   ```

4. **Testar manualmente primeiro:**
   ```bash
   sudo python3 /home/rguedes/Python/RTC/rtc_sync.py
   ```
   - Se funcionar manualmente, o problema é com systemd

---

### Problema 7: Arquivo de log cresce muito

**Sintoma:**
- `/var/log/rtcsync/rtc_sync.log` fica muito grande

**Soluções:**

1. **Limpar log atual:**
   ```bash
   sudo truncate -s 0 /var/log/rtcsync/rtc_sync.log
   ```

2. **Configurar rotação de logs (logrotate):**
   ```bash
   sudo cat > /etc/logrotate.d/rtc_sync << EOF
   /var/log/rtcsync/rtc_sync.log {
       daily
       rotate 7
       compress
       delaycompress
       notifempty
       create 0666 root root
   }
   EOF
   ```

3. **Usar journald (systemd) em vez de arquivo:**
   - O systemd mantém limite automático de tamanho

---

### Problema 8: RTC não está salvando hora (perde hora ao desligar)

**Sintoma:**
- Ao desligar o Pi e ligar novamente, RTC perdeu a hora

**Causas possíveis:**
1. Bateria do RTC descarregada ou faltando
2. RTC não está sincronizando corretamente
3. RTC é apenas leitura no seu modelo

**Soluções:**

1. **Verificar bateria:**
   - Abra o RTC e verifique se bateria está presente
   - Teste a bateria com multímetro (deve estar ~3V para CR2032)
   - Substitua a bateria se necessário

2. **Forçar sincronização:**
   ```bash
   sudo python3 rtc_sync.py
   ```

3. **Verificar modelo do RTC:**
   - DS3231 é recomendado (com bateria interna)
   - Alguns DS1307 genéricos podem ter qualidade duvidosa

---

## 🔍 Ferramentas de Diagnóstico

### 1. Script de teste integrado:
```bash
source /bin/rtcsync/venv/bin/activate
sudo python3 /bin/rtcsync/test_rtc.py
```

### 2. Verificar I2C:
```bash
i2cdetect -y 1
```

### 3. Ver logs em tempo real:
```bash
sudo tail -f /var/log/rtcsync/rtc_sync.log
```

### 4. Ver logs do systemd:
```bash
journalctl -u rtc_sync.service -f
```

### 5. Verificar hora do sistema:
```bash
date
```

### 6. Sincronizar manualmente com NTP:
```bash
sudo ntpdate pool.ntp.org
```

### 7. Verificar status do serviço:
```bash
sudo systemctl status rtc_sync.service
```

---

## ✅ Checklist de Verificação

Antes de assumir que algo está quebrado, verifique:

- [ ] RTC DS3231/DS1307 está fisicamente conectado
- [ ] Pinos SCL e SDA têm conexão firme
- [ ] Bateria do RTC está instalada e carregada
- [ ] I2C está habilitado no Raspberry Pi
- [ ] `sudo i2cdetect -y 1` mostra o RTC (0x68 ou 0x67)
- [ ] Script funciona manualmente: `source /bin/rtcsync/venv/bin/activate && sudo python3 /bin/rtcsync/rtc_sync.py`
- [ ] Dependências Python instaladas em `/bin/rtcsync/venv/`
- [ ] Arquivo de log tem permissão: `ls -l /var/log/rtcsync/rtc_sync.log`
- [ ] Pi tem conexão com internet (quando disponível)
- [ ] Hora do Pi está aproximadamente correta: `date`
- [ ] Serviço systemd registrado: `sudo systemctl list-unit-files | grep rtc_sync`

---

## 📞 Mais Ajuda

Se o problema persistir:

1. Verifique todos os logs:
   ```bash
   sudo cat /var/log/rtcsync/rtc_sync.log | tail -100
   ```

2. Execute o diagnóstico:
   ```bash
   source /bin/rtcsync/venv/bin/activate
   sudo python3 /bin/rtcsync/test_rtc.py
   ```

3. Verifique a documentação:
   ```bash
   cat /bin/rtcsync/README.md
   ```

4. Consulte a documentação do Adafruit:
   - https://github.com/adafruit/Adafruit_CircuitPython_DS3231
   - https://learn.adafruit.com/

5. Verifique o ambiente virtual:
   ```bash
   source /bin/rtcsync/venv/bin/activate
   pip list
   ```

---

**Última atualização:** Junho de 2026
