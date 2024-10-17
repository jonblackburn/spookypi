# logservice.py
import logging, logging.config
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry._logs import set_logger_provider

from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

class LogService:
    def __init__(self, config):
        self.config = config
        
        # throttle noisy loggers
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").removeHandler(logging.StreamHandler)
        logging.getLogger("azure").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        
        self._configure_logging()


    def _configure_logging(self):
        logging.config.dictConfig(self.config["Logging"])
        self.logger = logging.getLogger(__name__)

        # OpenTelemetry setup
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        span_processor = BatchSpanProcessor(ConsoleSpanExporter())
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Azure App Insights setup
        azure_connection_string = self.config["Azure"]["MonitorConnectionString"]
        configure_azure_monitor(
           connection_string=azure_connection_string,
        )

        logger_provider = LoggerProvider()
        set_logger_provider(logger_provider)
        exporter = AzureMonitorLogExporter(
            connection_string=azure_connection_string
        )
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        handler = LoggingHandler()
        logging.getLogger().addHandler(handler)                                                                                                                     

    def get_logger(self, name):
        return logging.getLogger(name)