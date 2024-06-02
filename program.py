import sys
from typing import Optional

from injector import Injector
import asyncio
from app_module import AppModule
from main import Main
import getopt
import logging


def main(argv):
    skills_source_path: Optional[str] = None
    packages_source_path: Optional[str] = None
    output_path: Optional[str] = None
    config_path: Optional[str] = None
    log_level: int = logging.INFO

    try:
        opts, args = getopt.getopt(argv, "hvs:p:o:c:", ["skills=", "packages=", "output=", "config="])
    except getopt.GetoptError:
        print('program.py -s <skillsfile> -p <packagesfile> -o <outputfile> -c <configfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('program.py -s <skillsfile> -p <packagesfile> -o <outputfile> -c <configfile>')
            sys.exit()
        elif opt in ("-s", "--skills"):
            skills_source_path = arg
        elif opt in ("-p", "--packages"):
            packages_source_path = arg
        elif opt in ("-o", "--output"):
            output_path = arg
        elif opt in ("-c", "--config"):
            config_path = arg
        elif opt in "-v":
            log_level = logging.DEBUG

    if not skills_source_path or not packages_source_path or not output_path or not config_path:
        print('program.py -s <skillsfile> -p <packagesfile> -o <outputfile> -c <configfile>')
        sys.exit(2)

    app_module = AppModule(skills_source_path, packages_source_path, output_path, config_path, log_level)
    injector = Injector(app_module)
    logger = injector.get(logging.Logger)
    logger.info("Starting the program")
    logger.info(f"Skills source path: %s", skills_source_path)
    logger.info(f"Packages source path: %s", packages_source_path)
    logger.info(f"Output path: %s", output_path)
    logger.info(f"Config path: %s", config_path)

    asyncio.run(injector.get(Main).run())


if __name__ == "__main__":
    main(sys.argv[1:])
