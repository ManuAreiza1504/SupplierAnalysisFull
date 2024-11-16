import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from scrapy import Selector
from selenium.webdriver.support.ui import Select
import time

def wait_for(driver, xpath):
    while True:
        try:
            # Espera hasta encontrar el elemento
            driver.find_elements(By.XPATH, xpath)
            return True
        except NoSuchElementException:
            continue  # Si no lo encuentra, espera y vuelve a intentarlo

class PruebasSpider(scrapy.Spider):
    name = "pruebas"
    allowed_domains = ["siis.ia.supersociedades.gov.co"]
    start_urls = ["https://siis.ia.supersociedades.gov.co"]

    def __init__(self, *args, **kwargs):
        super(PruebasSpider, self).__init__(*args, **kwargs)
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response):
        self.driver.get(response.url)

        # Espera hasta que el botón de submit esté disponible
        wait_for(self.driver, "//button[@type='submit']")
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # # Espera hasta que el select esté disponible
        # wait_for(self.driver, "//select[@name='orderParams']")
        # select_element = self.driver.find_element(By.XPATH, "//select[@name='orderParams']")
        # select = Select(select_element)
        # select.select_by_value("500")

        # Espera hasta que los elementos 'div.card' estén presentes
        wait_for(self.driver, "//div[@class='card']")
        
        # Xpath para los botones
        button_xpath = "//li[contains(@class,'list-group-item')]/button"
        total_buttons = len(self.driver.find_elements(By.XPATH, button_xpath))
        
        for index in range(total_buttons):
            try:
                buttons = self.driver.find_elements(By.XPATH, button_xpath)
                button = buttons[index]

                # Espera a que el botón sea visible y clickeable
                wait_for(self.driver, button_xpath)  # Usamos wait_for para esperar al botón
                
                # Clic en el botón
                button.click()
                
                # Espera a que el título "Vista 360" aparezca
                wait_for(self.driver, "//h2[contains(@class, 'titles')]")
                vista360_title = self.driver.find_element(By.XPATH, "//h2[contains(@class, 'titles')]")

                if vista360_title.text == "Vista 360":
                    html = self.driver.page_source
                    response = Selector(text=html)

                    yield from self.parse_empresas(response)

                    # Regresar a la página anterior
                    self.driver.back()

                    # Espera de nuevo hasta que todos los elementos 'div.card' estén disponibles
                    wait_for(self.driver, "//div[@class='card']")

            except Exception as e:
                self.logger.error(f"Error al procesar el botón: {e}")
                break

    def parse_empresas(self, response):
        razon = response.css("div.item-detail.subtitles::text").get().lower()
        yield {
            'razon': razon,
        }

    def close(self, reason):
        self.driver.quit()