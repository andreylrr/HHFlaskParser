from web_app import app, connect_db, login_manager
from parser_app import process_request as pr
import multiprocessing as ml

if __name__ == "__main__":

    par_service = ml.Process(name="HH API Parser", target=pr.main)
    par_service.start()

    app.run()