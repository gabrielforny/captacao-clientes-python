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

logging.basicConfig(filename='robot_log.txt', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Configurar webdriver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
# Remova a linha abaixo se quiser ver o navegador em ação
# options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()  

def search_google_maps(niche):
    logging.info("Iniciando busca no Google Maps")
    url = 'https://www.google.com/maps'
    driver.get(url)
    search_box = driver.find_element(By.XPATH, '//input[@id="searchboxinput"]')
    search_box.send_keys(niche)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

def is_valid_phone(phone):
    pattern = r"\(\d{2}\) \d{4,5}-\d{4}"
    return re.match(pattern, phone) is not None

def is_valid_website(url):
    pattern = r".*\.(com|br)$"
    if re.match(pattern, url) and "whatsapp.com" not in url.lower():
        return True
    return False

def clean_text(text):
    return re.sub(r'\s+', ' ', text.replace('\ue80b', '').replace('\ue878', '').strip())

def extract_company_data():
    logging.info("Extraindo dados das empresas")
    company_data = []

    time.sleep(5)

    numberDiv = 3
    for companies in range(2):
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
                website = ''
                website_elements = driver.find_elements(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div')
                for element in website_elements:
                    url_text = clean_text(element.text)
                    if is_valid_website(url_text):
                        website = url_text
                        break
                # Se website estiver vazio e phone contém 'whatsapp', use phone como website
                if not website and 'whatsapp' in phone.lower():
                    website = phone
            except Exception as e:
                website = ''
                logging.error(f"Erro ao processar o website: {e}")
                print(f"Erro ao processar o website: {e}")
            
            try:
                instagram = ''
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

import os

def send_whatsapp_messages(data):
    logging.info("Enviando mensagens pelo WhatsApp")
    
    # Obter o diretório atual e construir o caminho para o arquivo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'mensagem-wpp.txt')
    
    # Ler o conteúdo do arquivo de texto
    with open(file_path, 'r', encoding='utf-8') as file:
        message_template = file.read()

    for entry in data:
        phone = entry[2]
        name = entry[0]

        # Verificar e formatar o número de telefone
        if phone:
            phone_number = phone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            phone_number = '+55' + phone_number

            # Substituir o placeholder pelo nome da empresa
            message = message_template.replace('$nomeEmpresa$', name)
            
            try:
                pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=10)
            except Exception as e:
                logging.error(f"Erro ao enviar mensagem para {phone_number}: {e}")
                print(f"Erro ao enviar mensagem para {phone_number}: {e}")


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
