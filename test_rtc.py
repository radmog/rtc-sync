#!/usr/bin/env python3
"""
Script de diagnóstico para testar configuração do RTC
Verifica I2C, RTC, conectividade e NTP
"""

import sys
import socket
import subprocess
from datetime import datetime

try:
    import board
    import busio
    from adafruit_ds3231 import DS3231
    import ntplib
except ImportError as e:
    print(f"Erro: Biblioteca não instalada: {e}")
    print("Execute: pip3 install -r requirements.txt")
    sys.exit(1)

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_result(test_name, passed, message=""):
    status = "✓ PASSOU" if passed else "✗ FALHOU"
    print(f"{test_name}: {status}")
    if message:
        print(f"  → {message}")

def test_i2c():
    """Testa se I2C está disponível"""
    print_section("1. TESTE I2C")
    
    try:
        result = subprocess.run(
            ['i2cdetect', '-y', '1'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_result("I2C disponível", True)
            print("\nDispositivospor encontrados:")
            print(result.stdout)
            
            # Procura por 0x68 (DS3231) ou 0x67 (DS1307)
            if '68' in result.stdout:
                print_result("DS3231 detectado", True, "Endereço 0x68")
                return True
            elif '67' in result.stdout:
                print_result("DS1307 detectado", True, "Endereço 0x67")
                return True
            else:
                print_result("RTC detectado", False, "Nenhum RTC comum encontrado (0x68 ou 0x67)")
                return False
        else:
            print_result("i2cdetect", False, result.stderr)
            return False
            
    except FileNotFoundError:
        print_result("i2cdetect", False, "Comando i2cdetect não encontrado. Instale: sudo apt-get install i2c-tools")
        return False
    except Exception as e:
        print_result("I2C", False, str(e))
        return False

def test_rtc_connection():
    """Testa conexão com o RTC"""
    print_section("2. TESTE CONEXÃO RTC")
    
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        rtc = DS3231(i2c)
        print_result("RTC inicializado", True)
        
        # Tenta ler hora
        dt = rtc.datetime
        dt_obj = datetime(*dt[:6])
        print_result("Leitura de hora", True, f"Hora do RTC: {dt_obj}")
        
        # Tenta ler temperatura
        try:
            temp = rtc.temperature
            print_result("Leitura de temperatura", True, f"Temperatura: {temp}°C")
        except:
            print_result("Leitura de temperatura", False, "Não disponível")
        
        return rtc, dt_obj
        
    except Exception as e:
        print_result("RTC", False, str(e))
        return None, None

def test_internet():
    """Testa conectividade com internet"""
    print_section("3. TESTE CONECTIVIDADE")
    
    try:
        socket.create_connection(('8.8.8.8', 53), timeout=3)
        print_result("Conexão com internet", True, "Conectado ao 8.8.8.8:53")
        return True
    except (socket.timeout, socket.error) as e:
        print_result("Conexão com internet", False, "Sem conexão")
        return False

def test_ntp():
    """Testa conectividade com servidores NTP"""
    print_section("4. TESTE SERVIDORES NTP")
    
    servers = ['pool.ntp.org', 'time.nist.gov', 'time.google.com']
    
    for server in servers:
        try:
            client = ntplib.NTPClient()
            response = client.request(server, version=3, timeout=5)
            ntp_time = datetime.fromtimestamp(response.tx_time)
            print_result(f"  Servidor: {server}", True, f"Hora: {ntp_time}")
            return ntp_time
        except Exception as e:
            print_result(f"  Servidor: {server}", False, str(e))
    
    return None

def compare_times(rtc_time, ntp_time):
    """Compara hora do RTC com hora NTP"""
    if not rtc_time or not ntp_time:
        return
    
    print_section("5. COMPARAÇÃO DE HORAS")
    
    diff = abs((ntp_time - rtc_time).total_seconds())
    
    print(f"Hora do RTC:  {rtc_time}")
    print(f"Hora do NTP:  {ntp_time}")
    print(f"Diferença:    {diff:.1f} segundos")
    
    if diff < 2:
        print_result("Sincronismo", True, "RTC está em sincronismo com NTP")
    elif diff < 60:
        print_result("Sincronismo", False, f"Diferença de {diff:.0f}s - recomenda-se sincronizar")
    else:
        print_result("Sincronismo", False, f"Diferença significativa de {diff:.0f}s")

def test_python_packages():
    """Testa se todos os pacotes Python estão instalados"""
    print_section("6. TESTE PACOTES PYTHON")
    
    packages = [
        'board',
        'busio',
        'adafruit_ds3231',
        'ntplib',
        'schedule',
        'requests'
    ]
    
    all_ok = True
    for pkg in packages:
        try:
            __import__(pkg)
            print_result(f"  {pkg}", True)
        except ImportError:
            print_result(f"  {pkg}", False)
            all_ok = False
    
    return all_ok

def main():
    print("\n" + "="*60)
    print("DIAGNÓSTICO RTC - RASPBERRY PI")
    print("="*60)
    print(f"Data/Hora do Sistema: {datetime.now()}\n")
    
    # Testes
    i2c_ok = test_i2c()
    rtc, rtc_time = test_rtc_connection()
    internet_ok = test_internet()
    ntp_time = test_ntp() if internet_ok else None
    i2c_ok = test_i2c()
    rtc, rtc_time = test_rtc_connection()
    internet_ok = test_internet()
    ntp_time = test_ntp() if internet_ok else None
    
    if rtc_time and ntp_time:
        compare_times(rtc_time, ntp_time)
    
    packages_ok = test_python_packages()
    
    # Resumo
    print_section("RESUMO")
    
    results = [
        ("I2C", i2c_ok),
        ("RTC", rtc is not None),
        ("Internet", internet_ok),
        ("NTP", ntp_time is not None),
        ("Pacotes Python", packages_ok)
    ]
    
    print("\nResultados:")
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ TODOS OS TESTES PASSARAM")
        print("O sistema está pronto para sincronização!")
    else:
        print("✗ ALGUNS TESTES FALHARAM")
        print("Revise os erros acima e corrija os problemas.")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
