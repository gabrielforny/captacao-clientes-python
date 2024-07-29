import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import tkinter as tk
from tkinter import simpledialog, messagebox
import logging
import re
from servicos.enviarMenssagemWhatsapp import EnviarMenssagemWhtsapp
from servicos.salvarInfoExcel import SalvarInfoExcel
from servicos.validarTelefone import ValidarTelefone
from servicos.validarWebSite import ValidarWebSite
import os
logging.basicConfig(filename='robot_log.txt', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Configurar webdriver
options = webdriver.ChromeOptions()
# Remova a linha abaixo se quiser ver o navegador em ação
# options.add_argument('--headless')
service = Service(executable_path="C:\chromeDriver\chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()  

def search_google_maps(niche):
    logging.info("Iniciando busca no Google Maps")
    url = 'https://www.google.com/maps'
    driver.get(url)
    search_box = driver.find_element(By.XPATH, '//input[@id="searchboxinput"]')
    search_box.send_keys(niche)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

def clean_text(text):
    return re.sub(r'\s+', ' ', text.replace('\ue80b', '').replace('\ue878', '').strip())

def extract_company_data():
    logging.info("Extraindo dados das empresas")
    company_data = []

    time.sleep(5)

    numberDiv = 3
    for companies in range(15):
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
                    if ValidarTelefone.is_valid_phone(phone_text):
                        phone = phone_text
                        break
            except:
                phone = ''
            
            try:
                website = ''
                website_elements = driver.find_elements(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[7]/div')
                for element in website_elements:
                    url_text = clean_text(element.text)
                    if ValidarWebSite.is_valid_website(url_text):
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

# Função principal da automação
def start_automation():
    niche = simpledialog.askstring("Input", "Digite o nicho de pesquisa:")
    if niche:
        search_google_maps(niche)
        company_data = extract_company_data()
        SalvarInfoExcel.save_to_excel(company_data)
        messagebox.showinfo("Info", "Extração concluída. Dados salvos no arquivo 'company_data.xlsx'.")
        if messagebox.askyesno("Enviar mensagens", "Deseja enviar mensagens pelo WhatsApp?"):
            EnviarMenssagemWhtsapp.send_whatsapp_messages(company_data)
        driver.quit()

# Interface gráfica
root = tk.Tk()
root.geometry('300x200')
root.title('Automação Google Maps')

start_button = tk.Button(root, text="Iniciar Automação", command=start_automation)
start_button.pack(pady=20)

root.mainloop()
