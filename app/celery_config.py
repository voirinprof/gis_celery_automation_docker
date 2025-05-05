broker_url = 'amqp://guest:guest@rabbitmq:5672//'
result_backend = 'redis://redis:6379/0'

task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True
task_default_retry_delay = 300
task_max_retries = 3