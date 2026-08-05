from loguru import logger
from resources.EnvManager import EnvManager

if __name__ == '__main__':
    envmanager = EnvManager()

    logger.debug(envmanager.paths)
    