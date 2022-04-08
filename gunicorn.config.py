import multiprocessing

wsgi_app = "wsgi:app"
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
workers = 1
threads = 3
bind = "127.0.0.1:8888"
