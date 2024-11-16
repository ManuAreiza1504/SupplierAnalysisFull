import datetime
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapy import Selector
from selenium.webdriver.support.ui import Select
import time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import psycopg2

class EmpresasSpider(scrapy.Spider):
    name = "empresas"
    # allowed_domains = ["siis.ia.supersociedades.gov.co"]
    # start_urls = ["https://siis.ia.supersociedades.gov.co"]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    def __init__(self, *args, **kwargs):
        super(EmpresasSpider, self).__init__(*args, **kwargs)
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)

        self.dsn = "postgresql://eh5b17:xau_h6oA2zsTsNzOhau4F6OIMc1zm5iIbRsT1@us-east-1.sql.xata.sh/hackathon:main?sslmode=require"

        self.conn = psycopg2.connect(self.dsn)
        self.cur = self.conn.cursor()

        tableCreationQuery = """
        CREATE TABLE IF NOT EXISTS supersociedades (
            nit VARCHAR(9),
            razon VARCHAR(70),
            actividad VARCHAR(5),
            ubicacion VARCHAR(30),
            fecha_constitucion DATE,
            estado VARCHAR(20),
            corte DATE,

            activos BIGINT,
            pasivos BIGINT,
            patrimonio BIGINT,

            ingreso BIGINT,
            ganancia BIGINT,

            prueba FLOAT,
            endeudamiento FLOAT,
            roa FLOAT,
            roe FLOAT,

            act_operacion BIGINT,
            act_inversion BIGINT,
            act_financiacion BIGINT,

            integral_ganancia BIGINT,
            resultado_integral BIGINT,

            pro_activos BIGINT,
            pro_cerrados BIGINT
        );
        """
        self.cur.execute(tableCreationQuery)
        self.conn.commit()

    def start_requests(self):
        # Define aquí tu URL inicial de la SPA
        url = "https://siis.ia.supersociedades.gov.co"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)

        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

        submit_button = WebDriverWait(self.driver, 200, ignored_exceptions=ignored_exceptions).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        submit_button.click()

        time.sleep(2)

        select_element2 = WebDriverWait(self.driver, 200, ignored_exceptions=ignored_exceptions).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[id='selectorder-params']"))
        )
        select = Select(select_element2)
        select.select_by_value("0")

        time.sleep(2)

        select_element3 = WebDriverWait(self.driver, 200, ignored_exceptions=ignored_exceptions).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[name='macroSector']"))
        )
        select = Select(select_element3)
        select.select_by_value("CONSTRUCCION")

        time.sleep(2)

        select_element4 = WebDriverWait(self.driver, 200, ignored_exceptions=ignored_exceptions).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[name='fechaCorte']"))
        )
        select = Select(select_element4)
        select.select_by_value("2021")

        time.sleep(2)

        select_element = WebDriverWait(self.driver, 200, ignored_exceptions=ignored_exceptions).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[name='orderParams'].custom-select.ml-3"))
        )
        select = Select(select_element)
        select.select_by_value("500")

        time.sleep(2)

        WebDriverWait(self.driver, 200, ignored_exceptions=ignored_exceptions).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card"))
            )
        
        button_xpath = ".//li[@class='list-group-item v-middle item-btn btn-v360']//button"
        total_buttons = len(self.driver.find_elements(By.XPATH, button_xpath))

        for index in range(total_buttons):
            try:

                buttons = self.driver.find_elements(By.XPATH, button_xpath)
                button = buttons[index]

                WebDriverWait(self.driver, 200, ignored_exceptions=ignored_exceptions).until(EC.visibility_of(button))
                WebDriverWait(self.driver, 200, ignored_exceptions=ignored_exceptions).until(EC.element_to_be_clickable(button))

                time.sleep(2)

                button.click()
                
                time.sleep(2)

                vista360_title = WebDriverWait(self.driver, 200, ignored_exceptions=ignored_exceptions).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h2.titles"))
                    )

                time.sleep(2)

                if vista360_title.text == "Vista 360":
                    html = self.driver.page_source
                    response = Selector(text=html)

                    self.parse_empresas(response)

                    self.driver.back()

                    time.sleep(5)

            except Exception as e:
                self.logger.error(f"Hola{e}")
                break


    def parse_empresas(self, response):
        razon = response.css("div.item-detail.subtitles::text").get()
        if razon:
            razon = razon.lower()
        nit = response.xpath("//div[@class='basic-info']//li[label[contains(text(), 'NIT')]]/div[@class='item-detail']/text()").get()
        if nit:
            nit = nit.replace('.', '')
        actividad = response.xpath("//div[@class='economy-info--full']//li[label[contains(text(), 'Actividad Económica')]]/div[@class='item-detail']/p[@class='text-left']/text()").get()
        if actividad:
            actividad = actividad[:5]
        ubicacion = response.xpath("//div[@class='economy-info--full']//li[label[contains(text(), 'Ubicación')]]/div[@class='item-detail']/text()").get()
        if ubicacion:
            ubicacion = ubicacion.lower()
        fecha_constitucion = response.xpath("//div[@class='economy-info--full']//li[label[contains(text(), 'Constitución')]]/div[@class='item-detail']/text()").get()
        if fecha_constitucion:
            fecha_constitucion = datetime.datetime.strptime(fecha_constitucion.strip(), '%Y-%m-%d').date()
        estado = response.css("div.economy-info--full li.item-badge div.item-detail span.badge::text").get()
        if estado:
            estado = estado.lower()
        corte = response.xpath("//div[@class='desktop-visible label-date-corte']/label[contains(@class, 'subtitles')]/text()").get()
        if corte:
            corte = datetime.datetime.strptime(corte[5:].strip(), '%Y-%m-%d').date()
        
        activos = response.xpath(".//div[@class='widget-heading' and text()='ACTIVOS']/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if activos:
            activos = activos.replace('.', '').replace(' M', '').replace('$', '')
        pasivos = response.xpath(".//div[@class='widget-heading' and text()='PASIVOS']/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if pasivos:
            pasivos = pasivos.replace('.', '').replace(' M', '').replace('$', '')
        patrimonio = response.xpath(".//div[@class='widget-heading' and text()='PATRIMONIO']/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if patrimonio:
            patrimonio = patrimonio.replace('.', '').replace(' M', '').replace('$', '')

        
        ingreso = response.xpath(".//div[@class='widget-heading' and text()='INGRESO']/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if ingreso:
            ingreso = ingreso.replace('.', '').replace(' M', '').replace('$', '')
        ganancia = response.xpath(".//div[@class='widget-heading' and text()='GANANCIA .']/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if ganancia:
            ganancia = ganancia.replace('.', '').replace(' M', '').replace('$', '')

        
        prueba = response.xpath(".//div[@class='widget-heading' and contains(text(), 'PRUEBA ÁCIDA')]/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if prueba:
            prueba = prueba.replace(' Veces', '')
        endeudamiento = response.xpath(".//div[@class='widget-heading' and text()='ENDEUDAMIENTO']/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if endeudamiento:
            endeudamiento = endeudamiento.replace('%', '')
        roa = response.xpath(".//div[@class='widget-heading' and text()='ROA']/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if roa:
            roa = roa.replace('%', '')
        roe = response.xpath(".//div[@class='widget-heading' and text()='ROE']/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if roe:
            roe = roe.replace('%', '')

        
        act_operacion = response.xpath(".//div[@class='widget-heading' and contains(text(), 'ACT. OPERACIÓN')]/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if act_operacion:
            act_operacion = act_operacion.replace('$', '').replace('.', '').replace(' M', '')
        act_inversion = response.xpath(".//div[@class='widget-heading' and contains(text(), 'ACT. INVERSIÓN')]/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if act_inversion:
            act_inversion = act_inversion.replace('$', '').replace('.', '').replace(' M', '')
        act_financiacion = response.xpath(".//div[@class='widget-heading' and contains(text(), 'ACT. FINANCIANCIÓN')]/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if act_financiacion:
            act_financiacion = act_financiacion.replace('$', '').replace('.', '').replace(' M', '')


        integral_ganancia = response.xpath(
            ".//div[contains(@class, 'subtitle-light-govco') and text()='Otro resultado integral']"
            "//following-sibling::div//div[@class='widget-heading' and contains(text(), 'GANANCIA')]"
            "/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()"
        ).get()
        if integral_ganancia:
            integral_ganancia = integral_ganancia.replace('$', '').replace('.', '').replace(' M', '')
        resultado_integral = response.xpath(".//div[@class='widget-heading' and contains(text(), 'RESULTADO INTEGRAL')]/following-sibling::div[@class='widget-subheading']/following::div[contains(@class, 'widget-numbers')]/span[@class='widget-numbers--formattedValue']/text()").get()
        if resultado_integral:
            resultado_integral = resultado_integral.replace('$', '').replace('.', '').replace(' M', '')


        pro_activos = response.xpath(".//div[contains(@class, 'subtitle-light-govco') and contains(text(), 'Procesos en superintendencia')]/following-sibling::div//div[@class='widget-heading' and contains(text(), 'ACTIVOS')]/following::span[@class='widget-numbers--formattedValue']/text()").get()
        if pro_activos:
            pro_activos = pro_activos.strip()
        pro_cerrados = response.xpath(".//div[contains(@class, 'subtitle-light-govco') and contains(text(), 'Procesos en superintendencia')]/following-sibling::div//div[@class='widget-heading' and contains(text(), 'CERRADOS')]/following::span[@class='widget-numbers--formattedValue']/text()").get()
        if pro_cerrados:
            pro_cerrados = pro_cerrados.strip()
        
        try:
            insertQuery = """
                INSERT INTO supersociedades (
                    nit, razon, actividad, ubicacion, fecha_constitucion, estado, corte,
                    activos, pasivos, patrimonio,
                    ingreso, ganancia,
                    prueba, endeudamiento, roa, roe,
                    act_operacion, act_inversion, act_financiacion,
                    integral_ganancia, resultado_integral,
                    pro_activos, pro_cerrados
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, 
                    %s, %s, 
                    %s, %s, %s, %s, 
                    %s, %s, %s, 
                    %s, %s, 
                    %s, %s
                );
            """

            data = (
                nit, razon, actividad, ubicacion, fecha_constitucion, estado, corte,
                int(activos) if activos else 0,
                int(pasivos) if pasivos else 0,
                int(patrimonio) if patrimonio else 0,
                int(ingreso) if ingreso else 0,
                int(ganancia) if ganancia else 0,
                float(prueba) if prueba else 0.0,
                float(endeudamiento) if endeudamiento else 0.0,
                float(roa) if roa else 0.0,
                float(roe) if roe else 0.0,
                int(act_operacion) if act_operacion else 0,
                int(act_inversion) if act_inversion else 0,
                int(act_financiacion) if act_financiacion else 0,
                int(integral_ganancia) if integral_ganancia else 0,
                int(resultado_integral) if resultado_integral else 0,
                int(pro_activos) if pro_activos else 0,
                int(pro_cerrados) if pro_cerrados else 0
            )

            print(len(data))
            print(data)

            self.cur.execute(insertQuery, data)
            self.conn.commit()
            self.logger.info(f"Datos insertados correctamente para la empresa con NIT {nit}")
            # return []

        except Exception as e:
            self.logger.error(f"Error al insertar datos: {e}")
            # return []

    def close(self, reason):
        self.driver.quit()
        self.cur.close()
        self.conn.close()