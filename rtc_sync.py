#!/usr/bin/env python3
"""
Script de Sincronização RTC com Raspberry Pi
Sincroniza o Raspberry Pi com um RTC (DS3231/DS1307) via I2C
Se conectado à internet, atualiza o RTC a cada hora com dados de servidor NTP
"""

import os
import sys
import time
import logging
import subprocess
import socket
from datetime import datetime, timedelta
import board
import busio
from adafruit_ds3231 import DS3231
import ntplib
import schedule
import threading

# ==================== CONFIGURAÇÃO DE LOGGING ====================
log_file = '/var/log/rtcsync/rtc_sync.log'

# Cria diretório de log se não existir
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURAÇÃO ====================
NTP_SERVERS = [
    'pool.ntp.org',
    'time.nist.gov',
    'time.google.com'
]

INTERNET_CHECK_URL = 'https://www.google.com'
INTERNET_TIMEOUT = 3

# ==================== FUNÇÕES DE UTILIDADE ====================

def check_internet_connection():
    """
    Verifica se há conexão com a internet
    Retorna True se conectado, False caso contrário
    """
    try:
        socket.create_connection(('8.8.8.8', 53), timeout=INTERNET_TIMEOUT)
        logger.info("✓ Conexão com internet detectada")
        return True
    except (socket.timeout, socket.error):
        logger.warning("✗ Sem conexão com internet")
        return False


def get_ntp_time(server='pool.ntp.org'):
    """
    Obtém a hora precisa de um servidor NTP
    Retorna um objeto datetime ou None se falhar
    """
    try:
        client = ntplib.NTPClient()
        response = client.request(server, version=3, timeout=10)
        ntp_time = datetime.fromtimestamp(response.tx_time)
        logger.info(f"✓ Hora NTP obtida de {server}: {ntp_time}")
        return ntp_time
    except Exception as e:
        logger.error(f"✗ Erro ao obter hora NTP de {server}: {e}")
        return None


def get_ntp_time_with_fallback():
    """
    Tenta obter hora NTP de múltiplos servidores
    Retorna a primeira resposta bem-sucedida
    """
    for server in NTP_SERVERS:
        ntp_time = get_ntp_time(server)
        if ntp_time:
            return ntp_time
    
    logger.error("✗ Falha ao obter hora de todos os servidores NTP")
    return None


def initialize_rtc():
    """
    Inicializa a conexão I2C e retorna o objeto RTC
    """
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        rtc = DS3231(i2c)
        logger.info("✓ RTC DS3231 inicializado com sucesso")
        return rtc
    except Exception as e:
        logger.error(f"✗ Erro ao inicializar RTC: {e}")
        logger.error("Verifique:")
        logger.error("  - Se o RTC está conectado aos pinos SCL e SDA")
        logger.error("  - Se I2C está habilitado no Raspberry Pi (raspi-config)")
        logger.error("  - Endereço I2C (use 'i2cdetect -y 1' para verificar)")
        sys.exit(1)


def set_rtc_time(rtc, dt):
    """
    Define a hora no RTC
    """
    try:
        rtc.datetime = dt.timetuple()
        logger.info(f"✓ RTC atualizado para: {dt}")
        return True
    except Exception as e:
        logger.error(f"✗ Erro ao atualizar RTC: {e}")
        return False


def sync_rtc_from_ntp(rtc):
    """
    Sincroniza o RTC com a hora NTP
    """
    ntp_time = get_ntp_time_with_fallback()
    
    if not ntp_time:
        logger.warning("✗ Não foi possível obter hora NTP")
        return False
    
    # Adiciona alguns segundos para compensar o atraso de processamento
    ntp_time = ntp_time + timedelta(seconds=1)
    
    if set_rtc_time(rtc, ntp_time):
        # Também atualiza o sistema
        try:
            update_system_time(ntp_time)
            logger.info("✓ Hora do sistema também foi atualizada")
        except Exception as e:
            logger.warning(f"⚠ Erro ao atualizar hora do sistema: {e}")
        
        return True
    
    return False


def update_system_time(dt):
    """
    Atualiza a hora do sistema (requer privilégios de root)
    """
    try:
        # Converte para formato aceito por date
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        subprocess.run(
            ['sudo', 'date', '-s', time_str],
            check=True,
            capture_output=True
        )
        logger.info(f"✓ Hora do sistema atualizada para: {time_str}")
    except Exception as e:
        logger.warning(f"⚠ Não foi possível atualizar hora do sistema: {e}")


def read_rtc_time(rtc):
    """
    Lê a hora atual do RTC
    """
    try:
        dt = rtc.datetime
        # Converte time.struct_time para datetime
        dt_obj = datetime(*dt[:6])
        logger.info(f"✓ Hora lida do RTC: {dt_obj}")
        return dt_obj
    except Exception as e:
        logger.error(f"✗ Erro ao ler hora do RTC: {e}")
        return None


def get_temperature(rtc):
    """
    Lê a temperatura do DS3231 (se disponível)
    """
    try:
        temp = rtc.temperature
        logger.info(f"   Temperatura do RTC: {temp}°C")
        return temp
    except Exception as e:
        logger.debug(f"Temperatura não disponível: {e}")
        return None


def hourly_sync_job(rtc):
    """
    Job que é executado a cada hora para sincronizar com NTP
    """
    logger.info("=" * 60)
    logger.info("Iniciando sincronização horária com NTP...")
    logger.info("=" * 60)
    
    # Verifica hora atual do RTC
    current_rtc_time = read_rtc_time(rtc)
    get_temperature(rtc)
    
    # Verifica conexão com internet
    if not check_internet_connection():
        logger.warning("Sem internet. RTC não será atualizado.")
        return
    
    # Sincroniza com NTP
    if sync_rtc_from_ntp(rtc):
        logger.info("✓ Sincronização horária concluída com sucesso!")
    else:
        logger.error("✗ Sincronização horária falhou")
    
    logger.info("=" * 60)


def initial_sync(rtc):
    """
    Sincronização inicial do RTC com NTP (se disponível)
    Se não tiver internet, apenas lê a hora do RTC
    """
    logger.info("=" * 60)
    logger.info("SINCRONIZAÇÃO INICIAL")
    logger.info("=" * 60)
    
    # Lê hora do RTC
    rtc_time = read_rtc_time(rtc)
    get_temperature(rtc)
    
    # Tenta sincronizar com NTP se tiver internet
    if check_internet_connection():
        if sync_rtc_from_ntp(rtc):
            logger.info("✓ Sincronização inicial bem-sucedida!")
        else:
            logger.warning("⚠ Falha na sincronização inicial com NTP")
    else:
        logger.info("Sem internet. Usando hora do RTC.")
    
    logger.info("=" * 60)


def schedule_sync_next_hour(rtc):
    """
    Agenda a próxima sincronização para o próximo horário exato
    """
    now = datetime.now()
    # Calcula a hora exata do próximo horário
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    seconds_until = (next_hour - now).total_seconds()
    
    logger.info(f"Próxima sincronização agendada para: {next_hour} (em {seconds_until:.0f}s)")
    schedule.every().hour.at(":00").do(hourly_sync_job, rtc=rtc)


def run_scheduler(rtc):
    """
    Executa o scheduler de sincronização em thread separada
    """
    def scheduler_loop():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto
    
    scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
    scheduler_thread.start()
    logger.info("✓ Scheduler iniciado em thread separada")


def main():
    """
    Função principal
    """
    logger.info("Iniciando RTC Sync para Raspberry Pi")
    logger.info(f"Hora do sistema: {datetime.now()}")
    
    # Inicializa o RTC
    rtc = initialize_rtc()
    
    # Sincronização inicial
    initial_sync(rtc)
    
    # Agenda sincronização horária
    schedule_sync_next_hour(rtc)
    
    # Inicia o scheduler em thread separada
    run_scheduler(rtc)
    
    logger.info("✓ Script pronto. Sincronizações agendadas para cada hora exata.")
    logger.info("Pressione Ctrl+C para encerrar.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("\nScript finalizado pelo usuário")
        sys.exit(0)


if __name__ == '__main__':
    main()
