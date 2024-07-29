import logging
import pandas as pd

class SalvarInfoExcel:
    def save_to_excel(data):
        logging.info("Salvando dados no Excel")
        df = pd.DataFrame(data, columns=['Nome', 'Endereço', 'Telefone', 'Website', 'Instagram'])
        df.to_excel('company_data.xlsx', index=False)
