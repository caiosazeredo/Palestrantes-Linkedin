import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from flask import current_app
import re

logger = logging.getLogger(__name__)

class LinkedInCrawler:
    """
    Classe para realizar crawler no LinkedIn para buscar perfis de profissionais.
    Nota: O uso de crawlers pode violar os termos de serviço do LinkedIn.
    Em um ambiente de produção, seria recomendável utilizar a API oficial.
    """
    
    def __init__(self):
        """Inicializa o crawler do LinkedIn"""
        # Configurações do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executar em modo headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        # Inicializar o driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Verificar se as credenciais estão disponíveis
        self.username = current_app.config.get('LINKEDIN_USERNAME')
        self.password = current_app.config.get('LINKEDIN_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("Credenciais do LinkedIn não configuradas. Configure LINKEDIN_USERNAME e LINKEDIN_PASSWORD.")
        
        # Realizar login no LinkedIn
        self._login()
    
    def _login(self):
        """Realiza login no LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Preencher credenciais
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            email_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            # Clicar no botão de login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Aguardar login completo (verificando se a página inicial carregou)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            
            logger.info("Login no LinkedIn realizado com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao fazer login no LinkedIn: {e}")
            raise
    
    def buscar_profissionais(self, palavras_chave, min_seguidores=0, localizacao=None, max_resultados=10):
        """
        Busca profissionais no LinkedIn com base em palavras-chave
        
        Args:
            palavras_chave (list): Lista de palavras-chave para buscar
            min_seguidores (int): Número mínimo de seguidores
            localizacao (str): Localização para filtrar (opcional)
            max_resultados (int): Número máximo de resultados a retornar
            
        Returns:
            list: Lista de dicionários com informações dos perfis encontrados
        """
        resultados = []
        
        # Montar a consulta de busca
        query = " ".join(palavras_chave)
        if isinstance(palavras_chave, str):
            query = palavras_chave
            
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={query}&origin=GLOBAL_SEARCH_HEADER"
        
        if localizacao:
            search_url += f"&locationId={localizacao}"
        
        try:
            self.driver.get(search_url)
            
            # Aguardar carregamento dos resultados
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".search-result__info, .reusable-search__result-container"))
            )
            
            # Scroll para carregar mais resultados
            for _ in range(3):  # Ajuste conforme necessário
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Adaptar seletores baseado na versão atual do LinkedIn
            resultados_elementos = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".search-result__info, .reusable-search__result-container"
            )
            
            for i, elemento in enumerate(resultados_elementos):
                if i >= max_resultados:
                    break
                
                try:
                    # Extrair link do perfil
                    link_element = elemento.find_element(By.CSS_SELECTOR, "a.app-aware-link")
                    perfil_url = link_element.get_attribute("href").split("?")[0]
                    
                    # Obter mais informações do perfil
                    info_perfil = self.obter_info_perfil(perfil_url)
                    
                    # Verificar número de seguidores
                    seguidores = info_perfil.get('seguidores', 0)
                    if seguidores >= min_seguidores:
                        resultados.append(info_perfil)
                
                except Exception as e:
                    logger.warning(f"Erro ao processar perfil: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Erro na busca de profissionais: {e}")
        
        return resultados
    
    def obter_info_perfil(self, perfil_url):
        """
        Obtém informações detalhadas de um perfil do LinkedIn
        
        Args:
            perfil_url (str): URL do perfil do LinkedIn
            
        Returns:
            dict: Dicionário com informações do perfil
        """
        info = {
            'nome': '',
            'cargo_atual': '',
            'empresa_atual': '',
            'bio': '',
            'seguidores': 0,
            'habilidades': [],
            'perfil_url': perfil_url,
            'foto_url': '',
            'email': ''  # Pode ser vazio, pois nem sempre está disponível
        }
        
        try:
            # Acessar a página do perfil
            self.driver.get(perfil_url)
            
            # Aguardar carregamento do perfil
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pv-top-card, .profile-background-image"))
            )
            
            # Nome
            try:
                nome_element = self.driver.find_element(By.CSS_SELECTOR, ".text-heading-xlarge, .pv-top-card--list-bullet > li:first-child")
                info['nome'] = nome_element.text.strip()
            except NoSuchElementException:
                try:
                    # Alternativa para o layout mais recente
                    nome_element = self.driver.find_element(By.CSS_SELECTOR, "h1.text-heading-xlarge")
                    info['nome'] = nome_element.text.strip()
                except:
                    pass
            
            # Cargo atual
            try:
                cargo_element = self.driver.find_element(By.CSS_SELECTOR, ".text-body-medium, .pv-top-card--experience-list-item")
                info['cargo_atual'] = cargo_element.text.strip()
            except:
                pass
            
            # Empresa atual
            try:
                empresa_elements = self.driver.find_elements(By.CSS_SELECTOR, ".pv-top-card--experience-list-item, .inline-show-more-text")
                if len(empresa_elements) > 1:
                    info['empresa_atual'] = empresa_elements[1].text.strip()
            except:
                pass
            
            # Bio/Sobre
            try:
                # Tentar expandir seção "sobre"
                try:
                    ver_mais = self.driver.find_element(By.CSS_SELECTOR, ".lt-line-clamp__more, .inline-show-more-button")
                    ver_mais.click()
                    time.sleep(1)
                except:
                    pass
                
                bio_element = self.driver.find_element(By.CSS_SELECTOR, ".pv-about-section, .display-flex.ph5.pv3")
                info['bio'] = bio_element.text.strip()
            except:
                pass
            
            # Extrair número de seguidores
            try:
                seguidores_text = self.driver.find_element(By.CSS_SELECTOR, ".pv-recent-activity-section__follower-count, .text-body-small").text
                # Extrair apenas os números usando regex
                seguidores_match = re.search(r'(\d+(?:,\d+)?)', seguidores_text)
                if seguidores_match:
                    seguidores_str = seguidores_match.group(1).replace(',', '')
                    info['seguidores'] = int(seguidores_str)
            except:
                pass
            
            # URL da foto de perfil
            try:
                foto_element = self.driver.find_element(By.CSS_SELECTOR, ".pv-top-card__photo img, .profile-photo-edit__preview")
                info['foto_url'] = foto_element.get_attribute("src")
            except:
                pass
            
            # Scroll para ver habilidades
            self.driver.execute_script("window.scrollTo(0, 2000);")
            time.sleep(2)
            
            # Tentar clicar no botão "Ver mais" nas habilidades
            try:
                ver_mais_skills = self.driver.find_element(By.CSS_SELECTOR, ".pv-skills-section__additional-skills, .inline-show-more-button")
                ver_mais_skills.click()
                time.sleep(1)
            except:
                pass
            
            # Habilidades (Skills)
            try:
                habilidades_elements = self.driver.find_elements(By.CSS_SELECTOR, ".pv-skill-category-entity__name-text, .display-flex.align-items-center.mr1.hoverable-link-text")
                info['habilidades'] = [elem.text.strip() for elem in habilidades_elements if elem.text.strip()]
            except:
                pass
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do perfil {perfil_url}: {e}")
        
        return info
    
    def __del__(self):
        """Fechar o driver ao destruir o objeto"""
        if hasattr(self, 'driver'):
            self.driver.quit()