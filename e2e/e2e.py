from selenium import webdriver


try:
  driver = webdriver.Firefox()
  driver.implicitly_wait(2) # segundos
  driver.get('http://localhost:3000')

  # se o elemento não for encontrado vai dar exceção
  driver.find_element_by_xpath('//li[contains(text(), "Bala")]')

finally:
  driver.close()
