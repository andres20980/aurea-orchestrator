"""OpenTelemetry configuration and utilities."""

from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize tracer provider
trace.set_tracer_provider(TracerProvider())
tracer_provider = trace.get_tracer_provider()

# Add console exporter for development
console_exporter = ConsoleSpanExporter()
span_processor = BatchSpanProcessor(console_exporter)
tracer_provider.add_span_processor(span_processor)

# Get tracer for the application
tracer = trace.get_tracer(__name__)


def get_current_trace_id() -> Optional[str]:
    """Get current trace ID from the active span context."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        trace_id = span.get_span_context().trace_id
        # Convert trace_id to hex string (32 characters)
        return format(trace_id, '032x')
    return None


def get_current_span_id() -> Optional[str]:
    """Get current span ID from the active span context."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        span_id = span.get_span_context().span_id
        # Convert span_id to hex string (16 characters)
        return format(span_id, '016x')
    return None


def instrument_app(app):
    """Instrument FastAPI app with OpenTelemetry."""
    FastAPIInstrumentor.instrument_app(app)
    return app
