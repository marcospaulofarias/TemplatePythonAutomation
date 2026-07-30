from loguru import logger
from resources.UiAutomationClass import UiAutomationClass

if __name__ == '__main__':
    uiautomationclass = UiAutomationClass()

    # uiautomationclass.find_element("Window")

    window = uiautomationclass.find_element(element_type="Window", params={"name": "Calculador"})
    logger.info(f'WINDOW: {window}')
    window = uiautomationclass.find_element(element_type="Window", params={"name": "Calculadora"})
    logger.info(f'WINDOW: {window}')
