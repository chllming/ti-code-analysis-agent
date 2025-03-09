# Monitoring, Logging, and Scaling Guide for MCP Server

This guide provides information on how to configure monitoring, logging, and scaling for the MCP server deployed on Railway.

## Monitoring

The MCP server includes built-in endpoints and metrics collection to help you monitor its health and performance.

### Health Check Endpoint

The server exposes a `/health` endpoint that returns basic health information:

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600
}
```

Railway automatically uses this endpoint to determine if your service is healthy.

### Metrics Endpoint

The server exposes a `/metrics` endpoint that returns detailed metrics about the server's performance:

```json
{
  "uptime_seconds": 3600,
  "total_requests": 1000,
  "active_requests": 5,
  "successful_requests": 980,
  "failed_requests": 20,
  "error_rate_percent": 2.0,
  "avg_response_time_ms": 45.8,
  "request_methods": {
    "initialize": 10,
    "tools/list": 20,
    "tools/call": 970
  },
  "status_codes": {
    "200": 980,
    "400": 15,
    "500": 5
  }
}
```

### Railway Monitoring Dashboard

Railway provides built-in monitoring capabilities. To set up monitoring:

1. Go to your Railway project dashboard
2. Click on the "Monitoring" tab
3. View CPU, memory, and network usage

### Setting Up Alerts

Railway supports alerts based on various metrics. To set up alerts:

1. Go to your Railway project
2. Click on "Settings" > "Alerts"
3. Configure alerts for:
   - High CPU usage (e.g., >80% for 5 minutes)
   - High memory usage (e.g., >80% for 5 minutes)
   - Service downtime (health check fails)
   - Error rate threshold (e.g., >5% error rate)

### External Monitoring

For more advanced monitoring, consider setting up:

1. **Datadog Integration**:
   - Configure the Railway integration with Datadog
   - Set up custom dashboards for MCP server metrics

2. **Grafana/Prometheus**:
   - Expose metrics endpoint to Prometheus
   - Create Grafana dashboards for visualization

## Logging

The MCP server is configured with structured JSON logging for easier log analysis and integration with log management systems.

### Log Configuration

The following environment variables control the logging behavior:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `ENABLE_JSON_LOGS` | Whether to use structured JSON logging | true |

### Log Format

When `ENABLE_JSON_LOGS` is enabled, logs are formatted as JSON with the following structure:

```json
{
  "timestamp": "2025-03-09T10:15:30.123456",
  "level": "INFO",
  "message": "Request started",
  "logger": "mcp_server",
  "module": "mcp_server",
  "function": "mcp_endpoint",
  "line": 150,
  "request_id": "3f7c9e6b-8f5a-4d6c-9c5b-6a7b8c9d0e1f",
  "method": "POST",
  "path": "/mcp",
  "remote_addr": "192.168.1.1"
}
```

### Viewing Logs in Railway

To view logs in Railway:

1. Go to your Railway project dashboard
2. Click on your service
3. Select the "Logs" tab
4. Optionally filter logs by severity or search for specific terms

### Log Retention and Analysis

Railway retains logs for a limited period. For long-term log retention and analysis:

1. **Configure Log Forwarding**:
   - Set up a log drain in Railway to forward logs to an external service
   - Supported destinations include Datadog, Papertrail, and custom HTTP endpoints

2. **Log Analysis Tools**:
   - Use tools like ELK Stack (Elasticsearch, Logstash, Kibana) for log analysis
   - Set up log-based alerts for error patterns

## Scaling

The MCP server can be scaled both vertically and horizontally to handle increased load.

### Vertical Scaling

Railway provides easy vertical scaling of resources:

1. Go to your service in the Railway dashboard
2. Click on "Settings" > "Resources"
3. Adjust the resource sliders for:
   - Memory (RAM)
   - CPU
   - Disk space

Recommended starting configuration:
- 512MB RAM
- 0.5 vCPU
- 1GB Disk

### Horizontal Scaling

For horizontal scaling (running multiple instances):

1. Go to your service in the Railway dashboard
2. Click on "Settings" > "Replicas"
3. Increase the number of replicas

Notes on horizontal scaling:
- The MCP server is stateless and can be safely replicated
- Railway automatically load balances between replicas
- File system is not shared between replicas

### Auto-Scaling Configuration

Railway currently doesn't support automatic scaling based on metrics, but you can:

1. Monitor your application's performance using the metrics endpoint
2. Set up alerts for high resource usage
3. Manually adjust scaling when needed

### Performance Tuning

The MCP server uses Gunicorn as the WSGI server with the following tuning options:

1. **Worker Processes**:
   - The server is configured to use 4 worker processes by default
   - Modify the `--workers` parameter in the Dockerfile CMD to adjust

2. **Worker Type**:
   - Default worker type is synchronous
   - For high-concurrency workloads, consider using the `--worker-class eventlet` option

3. **Timeouts**:
   - Default timeout is 30 seconds
   - For long-running analyses, increase with `--timeout 120`

## Performance Monitoring

To monitor the performance of your MCP server:

1. **Response Time Tracking**:
   - Monitor the `avg_response_time_ms` metric
   - Set up alerts if it exceeds acceptable thresholds (e.g., >500ms)

2. **Error Rate Monitoring**:
   - Monitor the `error_rate_percent` metric
   - Investigate if error rates exceed 1%

3. **Resource Utilization**:
   - Monitor CPU and memory usage in Railway dashboard
   - Scale up if consistently above 70%

## Best Practices

1. **Staged Rollouts**:
   - Use Railway environments for staging before production
   - Test new versions in staging before deploying to production

2. **Regular Backup**:
   - The MCP server is stateless, but consider backing up any configuration

3. **Regular Load Testing**:
   - Perform periodic load tests to ensure capacity meets demand
   - Use tools like Apache JMeter or locust.io 