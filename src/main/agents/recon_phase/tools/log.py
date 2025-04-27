import os
from typing import Optional, Literal, TypedDict
import logging
import mylib
logger = logging.getLogger(__name__)


class Log(TypedDict):
    id: str
    log_content: str




def main():
    logging.basicConfig(filename-'logger', level=logging.INFO)
    logger.info('Started')



if __name__ == '__main__':
    main()
