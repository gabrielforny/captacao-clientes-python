import logging
import pywhatkit
import os

class EnviarMenssagemWhtsapp:
    def send_whatsapp_messages(data):
        logging.info("Enviando mensagens pelo WhatsApp")
        
        # Obter o diretório atual e construir o caminho para o arquivo
        file_path = "Templates\mensagem-wpp.txt"
        
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

