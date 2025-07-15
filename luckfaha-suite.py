######################################################
#                   By SecBras                       #
################### Suite 1.2 ########################

import random
import socket
import threading
import time
import requests
import pycountry  # type: ignore
from colorama import Fore, Style, init

print(f"\n\n{Fore.YELLOW}                                           _L/L")
print(f"                                         _LT/l_L_")
print(f"                          {Fore.GREEN}LuckFaha{Style.RESET_ALL}{Fore.YELLOW}     _LLl/L_T_lL_")
print(f"                   _T/L   {Fore.GREEN}Suite 1.2{Style.RESET_ALL}{Fore.YELLOW}  _LT|L/_|__L_|_L_")
print(f"                 _Ll/l_L_          _TL|_T/_L_|__T__|_l_")
print(f"               _TLl/T_l|_L_      _LL|_Tl/_|__l___L__L_|L_")
print(f"             _LT_L/L_|_L_l_L_  _'|_|_|T/_L_l__T _ l__|__|L_")
print(f"           _Tl_L|/_|__|_|__T _LlT_|_Ll/_{Fore.GREEN}SecBras Research{Style.RESET_ALL}{Fore.YELLOW}l__|")
print(f"    ______LT_l_l/|__|__l_T _T_L|_|_|l/___|__ | _l__|_ |__|_T_L_____{Style.RESET_ALL}")

# Inicializa o colorama
init()

# Cria um lock para sincronizar as impressões
print_lock = threading.Lock()

# Faixas de IPs públicos conhecidos
faixas_ip_publicos = [
    (1, 126, 0, 0, 0, 255),   # Classe A: 1.0.0.0 - 126.255.255.255
    (128, 191, 0, 0, 0, 255), # Classe B: 128.0.0.0 - 191.255.255.255
    (192, 223, 0, 0, 0, 255), # Classe C: 192.0.0.0 - 223.255.255.255
]

def gerar_ip_aleatorio():
    """Gera um endereço IP aleatório dentro de faixas de IPs públicos conhecidos."""
    faixa = random.choice(faixas_ip_publicos)
    return f"{random.randint(faixa[0], faixa[1])}.{random.randint(faixa[2], faixa[3])}.{random.randint(faixa[4], faixa[5])}.{random.randint(0, 255)}"

def testar_porta(ip, porta):
    """Testa se a porta está aberta no IP fornecido."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((ip, porta))
            return True
    except (socket.timeout, socket.error):
        return False

def obter_banner(ip, porta):
    """Obtém o banner de um serviço na porta fornecida."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((ip, porta))
            s.send(b'HEAD / HTTP/1.0\r\n\r\n')  # Envia uma requisição HTTP simples
            banner = s.recv(4096).decode()  # Recebe e decodifica o banner
            return banner
    except (socket.timeout, socket.error):
        return None

def verificar_servico(ip, porta, servico, versao=None):
    """Verifica se um serviço específico está rodando na porta fornecida, com ou sem versão."""
    banner = obter_banner(ip, porta)
    if banner:
        banner_upper = banner.upper()
        servico_upper = servico.upper()

        # Verifica se o serviço está presente no banner com uma correspondência parcial
        if servico_upper in banner_upper:
            if versao:
                versao_upper = versao.upper()
                # Verifica se a versão fornecida está presente no banner
                if versao_upper in banner_upper:
                    return True, banner
            else:
                return True, banner
    return False, banner

def obter_localizacao_completa(ip):
    """Obtém informações completas de localização do IP usando a API ipinfo.io."""
    url = f"http://ipinfo.io/{ip}/json"
    try:
        response = requests.get(url)
        data = response.json()
        
        # Padroniza os dados de localização
        localizacao = {
            'ip': ip,
            'pais': data.get('country', 'Desconhecido'),
            'nome_pais': codigo_para_nome_pais(data.get('country', '')),
            'regiao': data.get('region', 'Desconhecido'),
            'cidade': data.get('city', 'Desconhecido'),
            'localizacao': data.get('loc', 'Desconhecido'),
            'org': data.get('org', 'Desconhecido'),
            'timezone': data.get('timezone', 'Desconhecido')
        }
        
        # Se não tiver nome do país, tenta obter do código
        if localizacao['nome_pais'] == 'Desconhecido' and localizacao['pais'] != 'Desconhecido':
            localizacao['nome_pais'] = codigo_para_nome_pais(localizacao['pais'])
            
        return localizacao
    except requests.RequestException:
        return {
            'ip': ip,
            'pais': 'Desconhecido',
            'nome_pais': 'Desconhecido',
            'regiao': 'Desconhecido',
            'cidade': 'Desconhecido',
            'localizacao': 'Desconhecido',
            'org': 'Desconhecido',
            'timezone': 'Desconhecido'
        }

def codigo_para_nome_pais(codigo_iso):
    """Converte o código ISO do país para o nome completo do país."""
    try:
        pais = pycountry.countries.get(alpha_2=codigo_iso)
        return pais.name if pais else "Desconhecido"
    except LookupError:
        return "Desconhecido"

def formatar_localizacao(localizacao):
    """Formata as informações de localização para exibição."""
    return (
        f"País: {Fore.GREEN}{localizacao['nome_pais']} ({localizacao['pais']}){Style.RESET_ALL}\n"
        f"Região/Estado: {Fore.GREEN}{localizacao['regiao']}{Style.RESET_ALL}\n"
        f"Cidade: {Fore.GREEN}{localizacao['cidade']}{Style.RESET_ALL}\n"
        f"Coordenadas: {Fore.GREEN}{localizacao['localizacao']}{Style.RESET_ALL}\n"
        f"Provedor: {Fore.GREEN}{localizacao['org']}{Style.RESET_ALL}\n"
        f"Timezone: {Fore.GREEN}{localizacao['timezone']}{Style.RESET_ALL}"
    )

def tarefa_por_porta(ip, porta, resultados, ips_testados):
    """Executa a tarefa de testar portas e coleta informações do banner."""
    ips_testados.append(ip)
    if testar_porta(ip, porta):
        localizacao = obter_localizacao_completa(ip)
        with print_lock:
            print(f"\nIP: {Fore.GREEN}{ip}{Style.RESET_ALL}")
            print(formatar_localizacao(localizacao))
            resultados.append((ip, localizacao))
    else:
        with print_lock:
            print(f"Porta: {Fore.RED}{porta} NÃO está aberta em {ip}{Style.RESET_ALL}")

def tarefa_por_servico(ip, porta, servico, versao, resultados, ips_testados):
    """Executa a tarefa de testar serviços e coleta informações do banner."""
    ips_testados.append(ip)
    if testar_porta(ip, porta):
        localizacao = obter_localizacao_completa(ip)
        banner = obter_banner(ip, porta)
        encontrado, banner = verificar_servico(ip, porta, servico, versao)

        with print_lock:
            print(f"\nIP: {Fore.GREEN}{ip}{Style.RESET_ALL}")
            print(formatar_localizacao(localizacao))
            
            if encontrado:
                print(f"Serviço encontrado: {Fore.GREEN}{servico} {versao if versao else ''}{Style.RESET_ALL}")
                print(f"Banner:\n{Fore.YELLOW}{banner}{Style.RESET_ALL}")
                resultados.append((ip, localizacao, banner))
            else:
                print(f"Serviço: {Fore.RED}{servico} {versao if versao else ''} NÃO foi encontrado.{Style.RESET_ALL}")
                if banner:
                    print(f"Banner:\n{Fore.YELLOW}{banner}{Style.RESET_ALL}")
                else:
                    print(f"Banner: {Fore.YELLOW}não obtido.{Style.RESET_ALL}")
    else:
        with print_lock:
            print(f"Porta: {Fore.RED}{porta} NÃO está aberta em {ip}{Style.RESET_ALL}")

def tarefa_por_servico_e_pais(ip, porta, servico, versao, pais, resultados, ips_testados):
    """Executa a tarefa de testar serviços e filtra por país."""
    ips_testados.append(ip)
    if testar_porta(ip, porta):
        localizacao = obter_localizacao_completa(ip)
        banner = obter_banner(ip, porta)
        encontrado, banner = verificar_servico(ip, porta, servico, versao)
        
        pais_solicitado_upper = pais.upper()
        pais_encontrado_upper = localizacao['nome_pais'].upper()
        codigo_pais_upper = localizacao['pais'].upper()

        with print_lock:
            print(f"\nIP: {Fore.GREEN}{ip}{Style.RESET_ALL}")
            print(formatar_localizacao(localizacao))

        # Verifica se o país no IP corresponde ao país solicitado
        if (pais_encontrado_upper == pais_solicitado_upper or 
            codigo_pais_upper == pais_solicitado_upper or 
            pais_solicitado_upper == "BR" and codigo_pais_upper == "BR"):
            
            if encontrado:
                with print_lock:
                    print(f"Serviço encontrado: {Fore.GREEN}{servico} {versao if versao else ''}{Style.RESET_ALL}")
                    print(f"Banner:\n{Fore.YELLOW}{banner}{Style.RESET_ALL}")
                resultados.append((ip, localizacao, banner))
            else:
                with print_lock:
                    print(f"Serviço: {Fore.RED}{servico} {versao if versao else ''} NÃO foi encontrado.{Style.RESET_ALL}")
                    if banner:
                        print(f"Banner:\n{Fore.YELLOW}{banner}{Style.RESET_ALL}")
                    else:
                        print(f"Banner: {Fore.YELLOW}não obtido.{Style.RESET_ALL}")
        else:
            with print_lock:
                print(f"País: {Fore.YELLOW}O IP não está no país solicitado ({pais}).{Style.RESET_ALL}")
    else:
        with print_lock:
            print(f"Porta: {Fore.RED}{porta} NÃO está aberta em {ip}{Style.RESET_ALL}")

def imprimir_resultados(resultados, ips_testados):
    """Imprime todos os resultados coletados no final dos testes."""
    print(f"\n{'='*50} RESUMO DOS RESULTADOS {'='*50}")
    
    # Remove duplicatas mantendo a ordem original
    resultados_unicos = []
    ips_vistos = set()
    
    for resultado in resultados:
        ip = resultado[0]
        if ip not in ips_vistos:
            ips_vistos.add(ip)
            resultados_unicos.append(resultado)
    
    for resultado in resultados_unicos:
        if len(resultado) == 2:  # Apenas porta aberta
            ip, localizacao = resultado
            print(f"\nIP: {Fore.GREEN}{ip}{Style.RESET_ALL}")
            print(formatar_localizacao(localizacao))
        elif len(resultado) >= 3:  # Serviço encontrado
            ip, localizacao, banner = resultado[:3]
            print(f"\nIP: {Fore.GREEN}{ip}{Style.RESET_ALL}")
            print(formatar_localizacao(localizacao))
            print(f"Banner:\n{Fore.YELLOW}{banner}{Style.RESET_ALL}")
    
    print(f"\nTotal de IPs testados: {Fore.GREEN}{len(ips_testados)}{Style.RESET_ALL}")
    print(f"Total de IPs coletados: {Fore.GREEN}{len(resultados_unicos)}{Style.RESET_ALL}")
    print(f"{'='*120}")

def main():
    print("\n\nEscolha uma opção:")
    print("\n1 - Buscar apenas portas abertas")
    print("2 - Buscar por serviços específicos")
    print("3 - Buscar por serviços e filtrar por país")

    opcao = input("\nDigite o número da opção: ")

    if opcao == "1":
        porta = int(input("\nDigite o número da porta: "))
        numero_de_ips = int(input("Digite o número de IPs: "))
        print("\n")

        resultados = []
        ips_testados = []

        start_time = time.time()  # Início do tempo

        def buscar_por_porta():
            while len(resultados) < numero_de_ips:
                ip = gerar_ip_aleatorio()
                tarefa_por_porta(ip, porta, resultados, ips_testados)

        threads = []
        for _ in range(500):
            thread = threading.Thread(target=buscar_por_porta)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        end_time = time.time()  # Fim do tempo
        tempo_total = end_time - start_time
        print(f"\nTempo total: {Fore.GREEN}{tempo_total:.2f} segundos{Style.RESET_ALL}")

        # Imprime o resumo dos resultados
        imprimir_resultados(resultados, ips_testados)

    elif opcao == "2":
        servico = input("\nDigite o serviço a ser verificado (por exemplo, 'apache'): ")
        versao = input("Versão (opcional, pressione Enter para pular): ")
        porta = int(input("Digite o número da porta: "))
        numero_de_ips = int(input("Digite o número de IPs: "))
        print("\n")

        resultados = []
        ips_testados = []

        start_time = time.time()  # Início do tempo

        def buscar_por_servico():
            while len(resultados) < numero_de_ips:
                ip = gerar_ip_aleatorio()
                tarefa_por_servico(ip, porta, servico, versao, resultados, ips_testados)

        threads = []
        for _ in range(500):
            thread = threading.Thread(target=buscar_por_servico)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        end_time = time.time()  # Fim do tempo
        tempo_total = end_time - start_time
        print(f"\nTempo total: {Fore.GREEN}{tempo_total:.2f} segundos{Style.RESET_ALL}")

        # Imprime o resumo dos resultados
        imprimir_resultados(resultados, ips_testados)

    elif opcao == "3":
        servico = input("\nDigite o serviço a ser verificado (por exemplo, 'apache'): ")
        versao = input("Versão (opcional, pressione Enter para pular): ")
        porta = int(input("Digite o número da porta: "))
        numero_de_ips = int(input("Digite o número de IPs: "))
        pais = input("País (nome completo ou código ISO, exemplo: Brazil ou BR): ")
        print("\n")

        resultados = []
        ips_testados = []

        start_time = time.time()  # Início do tempo

        def buscar_por_servico_e_pais():
            while len(resultados) < numero_de_ips:
                ip = gerar_ip_aleatorio()
                tarefa_por_servico_e_pais(ip, porta, servico, versao, pais, resultados, ips_testados)

        threads = []
        for _ in range(500):
            thread = threading.Thread(target=buscar_por_servico_e_pais)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        end_time = time.time()  # Fim do tempo
        tempo_total = end_time - start_time
        print(f"\nTempo total: {Fore.GREEN}{tempo_total:.2f} segundos{Style.RESET_ALL}")

        # Imprime o resumo dos resultados
        imprimir_resultados(resultados, ips_testados)

    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()