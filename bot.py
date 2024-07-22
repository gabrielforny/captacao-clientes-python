import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import simpledialog, messagebox
import pywhatkit
import logging
import re

# Configurar o logger
logging.basicConfig(filename='robot_log.txt', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Configurar webdriver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
# Remova a linha abaixo se quiser ver o navegador em ação
# options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()  # Maximiza o navegador após a inicialização

# Função para buscar empresas no Google Maps
def search_google_maps(niche):
    logging.info("Iniciando busca no Google Maps")
    url = 'https://www.google.com/maps'
    driver.get(url)
    search_box = driver.find_element(By.XPATH, '//input[@id="searchboxinput"]')
    search_box.send_keys(niche)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

def is_valid_phone(phone):
    # Regex para validar um número de telefone no formato (xx) xxxxx-xxxx
    pattern = r"\(\d{2}\) \d{4,5}-\d{4}"
    return re.match(pattern, phone) is not None

# Função para extrair dados das empresas
def extract_company_data():
    logging.info("Extraindo dados das empresas")
    company_data = []

    # Esperar os resultados carregarem
    time.sleep(5)

    # Encontrar os elementos que correspondem aos resultados da pesquisa
    numberDiv = 3
    for companies in range(5):
        print(f"Acessando empresa {companies}")
        try:
            company = driver.find_element(By.XPATH, f'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[{numberDiv}]')
            company.click()
            time.sleep(3)
            
            try:
                name = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1').text
            except:
                name = ''
            
            try:
                address = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[3]/button/div/div[2]/div[1]').text
            except:
                address = ''
            
            try:
                phone_elements = driver.find_elements(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]//button/div/div[2]/div[1]')
                phone = ''
                for element in phone_elements:
                    phone_text = element.text
                    if is_valid_phone(phone_text):
                        phone = phone_text
                        break
            except:
                phone = ''
            
            try:
                # Localize o contêiner que contém o ícone do globo e o texto do URL
                container = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div[7]')
                if container:
                    try:
                        # Verifique se o ícone do globo está presente dentro do contêiner
                        globe_icon = container.find_element(By.XPATH, './/span[contains(@class, "google-symbols PHazN")]')
                        if globe_icon:
                            # Capture o texto do URL ao lado do ícone do globo
                            website = container.find_element(By.XPATH, './/div[contains(@class, "Io6YTe fontBodyMedium kR99db")]').text
                        else:
                            website = ''
                    except Exception as inner_e:
                        website = ''
                        logging.error(f"Erro ao processar o website (ícone encontrado, mas erro ao capturar texto): {inner_e}")
                        print(f"Erro ao processar o website (ícone encontrado, mas erro ao capturar texto): {inner_e}")
                else:
                    website = ''
            except Exception as e:
                website = ''
                logging.error(f"Erro ao processar o website (contêiner não encontrado): {e}")
                print(f"Erro ao processar o website (contêiner não encontrado): {e}")
            
            try:
                instagram = ''
                # Implementar lógica para buscar Instagram se disponível
            except:
                instagram = ''
            
            numberDiv = numberDiv + 2
            company_data.append([name, address, phone, website, instagram])
            driver.back()
            time.sleep(3)
        
        except Exception as e:
            logging.error(f"Erro ao processar empresa: {e}")
    
    return company_data

# Função para salvar os dados em um Excel
def save_to_excel(data):
    logging.info("Salvando dados no Excel")
    df = pd.DataFrame(data, columns=['Nome', 'Endereço', 'Telefone', 'Website', 'Instagram'])
    df.to_excel('company_data.xlsx', index=False)

# Função para enviar mensagens via WhatsApp
def send_whatsapp_messages(data):
    logging.info("Enviando mensagens pelo WhatsApp")
    for entry in data:
        phone = entry[2]
        if 'whatsapp' in phone.lower():
            message = f"Olá {entry[0]}, estamos entrando em contato para..."
            phone_number = '+55' + phone.replace('whatsapp', '').replace(' ', '')
            pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=10)

# Função principal da automação
def start_automation():
    niche = simpledialog.askstring("Input", "Digite o nicho de pesquisa:")
    if niche:
        search_google_maps(niche)
        company_data = extract_company_data()
        save_to_excel(company_data)
        messagebox.showinfo("Info", "Extração concluída. Dados salvos no arquivo 'company_data.xlsx'.")
        if messagebox.askyesno("Enviar mensagens", "Deseja enviar mensagens pelo WhatsApp?"):
            send_whatsapp_messages(company_data)
        driver.quit()

# Interface gráfica
root = tk.Tk()
root.geometry('300x200')
root.title('Automação Google Maps')

start_button = tk.Button(root, text="Iniciar Automação", command=start_automation)
start_button.pack(pady=20)

root.mainloop()
