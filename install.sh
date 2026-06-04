#!/bin/bash

# Script de instalação do RTC Sync para Raspberry Pi com venv
# Instala em /bin/rtcsync/ com ambiente virtual Python

INSTALL_DIR="/bin/rtcsync"
VENV_DIR="$INSTALL_DIR/venv"
LOG_DIR="/var/log/rtcsync"

echo "================================================"
echo "Instalação - RTC Sync para Raspberry Pi"
echo "Instalação: $INSTALL_DIR"
echo "================================================"
echo ""

# Verifica se está rodando como root
if [[ $EUID -ne 0 ]]; then
   echo "Este script deve ser executado como root:"
   echo "sudo bash install.sh"
   exit 1
fi

echo "1. Atualizando pacotes..."
apt-get update
apt-get upgrade -y

echo ""
echo "2. Instalando dependências de sistema..."
apt-get install -y python3 python3-venv python3-pip python3-dev i2c-tools

echo ""
echo "3. Habilitando I2C (se não estiver habilitado)..."
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" >> /boot/config.txt
    echo "   ⚠ I2C habilitado. Será necessário reiniciar o Pi."
fi

echo ""
echo "4. Criando diretório de instalação..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"

echo ""
echo "5. Criando ambiente virtual Python..."
if [ -d "$VENV_DIR" ]; then
    echo "   ⚠ Ambiente virtual já existe. Removendo..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo ""
echo "6. Instalando dependências Python no venv..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo ""
echo "7. Copiando scripts para $INSTALL_DIR..."
cp rtc_sync.py "$INSTALL_DIR/"
cp test_rtc.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/rtc_sync.py"
chmod +x "$INSTALL_DIR/test_rtc.py"

echo ""
echo "8. Copiando documentação e scripts helpers..."
cp README.md "$INSTALL_DIR/"
cp QUICK_START.md "$INSTALL_DIR/"
cp TROUBLESHOOTING.md "$INSTALL_DIR/"
cp PROJETO.md "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"
cp rtc-helper.sh "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/rtc-helper.sh"
ln -sf "$INSTALL_DIR/rtc-helper.sh" /usr/local/bin/rtc-helper || true

echo ""
echo "9. Configurando serviço systemd..."
cp rtc_sync.service /etc/systemd/system/
systemctl daemon-reload

echo ""
echo "10. Configurando permissões..."
chmod 755 "$INSTALL_DIR"
chmod 755 "$LOG_DIR"
chown -R $(logname):$(logname) "$LOG_DIR"

echo ""
echo "================================================"
echo "Instalação concluída com sucesso!"
echo "================================================"
echo ""
echo "Local de instalação: $INSTALL_DIR"
echo "Ambiente virtual:    $VENV_DIR"
echo "Diretório de logs:   $LOG_DIR"
echo ""
echo "Próximos passos:"
echo ""
echo "1. Verifique se o RTC está conectado:"
echo "   i2cdetect -y 1"
echo "   (Procure por um endereço i2c, geralmente 0x68)"
echo ""
echo "2. Teste o script:"
echo "   rtc-helper test"
echo ""
echo "3. Ative como serviço (executa no boot):"
echo "   sudo systemctl enable rtc_sync.service"
echo "   sudo systemctl start rtc_sync.service"
echo ""
echo "4. Veja o status:"
echo "   rtc-helper status"
echo ""
echo "5. Acompanhe os logs:"
echo "   rtc-helper logs"
echo ""
echo "Comandos úteis:"
echo "   rtc-helper test      - Diagnosticar"
echo "   rtc-helper manual    - Executar manualmente"
echo "   rtc-helper logs      - Ver logs"
echo "   rtc-helper status    - Ver status"
echo "   rtc-helper restart   - Reiniciar"
echo "   rtc-helper update    - Atualizar dependências"
echo "   rtc-helper shell     - Shell interativo com venv"
echo ""
echo "Ver mais:"
echo "   rtc-helper           - Listar todos os comandos"
echo ""
echo "7. Se reiniciou o Pi para habilitar I2C, reinicie agora:"
echo "   sudo reboot"
echo ""
