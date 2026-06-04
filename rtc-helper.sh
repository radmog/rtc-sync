#!/bin/bash

# Helper script para gerenciar o RTC Sync
# Torna fácil ativar o venv e executar comandos

INSTALL_DIR="/bin/rtcsync"
VENV_DIR="$INSTALL_DIR/venv"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo -e "${BLUE}RTC Sync Helper - Gerenciador de Serviço${NC}"
    echo ""
    echo "Uso: $0 <comando> [opções]"
    echo ""
    echo "Comandos:"
    echo "  status          Ver status do serviço"
    echo "  start           Iniciar serviço"
    echo "  stop            Parar serviço"
    echo "  restart         Reiniciar serviço"
    echo "  logs            Ver logs em tempo real"
    echo "  test            Executar teste de diagnóstico"
    echo "  manual          Executar script manualmente"
    echo "  shell           Ativar venv (shell interativo)"
    echo "  pip <args>      Executar pip dentro do venv"
    echo "  python <args>   Executar python dentro do venv"
    echo "  install         Ver instruções de instalação"
    echo "  update          Atualizar pip e dependências"
    echo ""
}

# Verifica se comando existe
if [ $# -eq 0 ]; then
    print_usage
    exit 1
fi

case "$1" in
    status)
        echo -e "${BLUE}Status do Serviço RTC Sync:${NC}"
        sudo systemctl status rtc_sync.service
        ;;
    
    start)
        echo -e "${YELLOW}Iniciando serviço...${NC}"
        sudo systemctl start rtc_sync.service
        echo -e "${GREEN}✓ Serviço iniciado${NC}"
        ;;
    
    stop)
        echo -e "${YELLOW}Parando serviço...${NC}"
        sudo systemctl stop rtc_sync.service
        echo -e "${GREEN}✓ Serviço parado${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}Reiniciando serviço...${NC}"
        sudo systemctl restart rtc_sync.service
        sleep 2
        echo -e "${GREEN}✓ Serviço reiniciado${NC}"
        sudo systemctl status rtc_sync.service
        ;;
    
    logs)
        echo -e "${BLUE}Logs em tempo real (Ctrl+C para sair):${NC}"
        sudo tail -f /var/log/rtcsync/rtc_sync.log
        ;;
    
    test)
        echo -e "${BLUE}Executando diagnóstico...${NC}"
        source "$VENV_DIR/bin/activate"
        sudo python3 "$INSTALL_DIR/test_rtc.py"
        ;;
    
    manual)
        echo -e "${BLUE}Executando script manualmente...${NC}"
        echo -e "${YELLOW}(Pressione Ctrl+C para parar)${NC}"
        source "$VENV_DIR/bin/activate"
        sudo python3 "$INSTALL_DIR/rtc_sync.py"
        ;;
    
    shell)
        echo -e "${BLUE}Ativando ambiente virtual...${NC}"
        echo -e "${YELLOW}Execute 'deactivate' para sair${NC}"
        source "$VENV_DIR/bin/activate"
        echo -e "${GREEN}✓ Venv ativo!${NC}"
        bash
        ;;
    
    pip)
        shift
        echo -e "${BLUE}Executando pip dentro do venv...${NC}"
        source "$VENV_DIR/bin/activate"
        pip "$@"
        ;;
    
    python)
        shift
        source "$VENV_DIR/bin/activate"
        python3 "$@"
        ;;
    
    install)
        echo -e "${BLUE}Instruções de Instalação${NC}"
        echo ""
        echo "Se ainda não instalou:"
        echo "  cd /caminho/para/rtc-sync"
        echo "  sudo bash install.sh"
        echo ""
        echo "Depois:"
        echo "  $0 test       # Testar"
        echo "  $0 status     # Ver status"
        echo "  $0 logs       # Ver logs"
        echo ""
        ;;
    
    update)
        echo -e "${YELLOW}Atualizando pip e dependências...${NC}"
        source "$VENV_DIR/bin/activate"
        pip install --upgrade pip setuptools wheel
        pip install --upgrade -r "$INSTALL_DIR/requirements.txt"
        echo -e "${GREEN}✓ Atualização concluída${NC}"
        ;;
    
    *)
        echo -e "${RED}Comando desconhecido: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac
