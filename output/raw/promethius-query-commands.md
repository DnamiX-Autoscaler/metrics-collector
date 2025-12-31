🖥️ NODE LEVEL METRICS

# node_cpu_usage_percent

100 - avg by (instance)(
  rate(node_cpu_seconds_total{mode="idle"}[1m])
) * 100

### node_cpu_seconds_total

# node_memory_usage_percent

(
  (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
  / node_memory_MemTotal_bytes
) * 100

### node_memory_MemTotal_bytes
### node_memory_MemAvailable_bytes
### node_memory_MemTotal_bytes

# node_memory_usage_mb

(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
/ 1024 / 1024

# node_network_rx_kbps

rate(node_network_receive_bytes_total[1m]) * 8 / 1024

### node_network_receive_bytes_total

# node_network_tx_kbps

rate(node_network_transmit_bytes_total[1m]) * 8 / 1024

### node_network_transmit_bytes_total

# node_disk_read_iops

rate(node_disk_reads_completed_total[1m])

### node_disk_reads_completed_total

# node_disk_write_iops

rate(node_disk_writes_completed_total[1m])

### node_disk_writes_completed_total


📦 POD LEVEL METRICS

# current_pod_count

count(
  kube_pod_info{namespace="<ns>", pod=~"<service>.*"}
)

# pod_cpu_usage_percent_avg

avg by (pod)(
  rate(container_cpu_usage_seconds_total{container!="", image!=""}[1m])
) * 100

### container_cpu_usage_seconds_total

# pod_cpu_usage_percent_p95

quantile_over_time(
  0.95,
  rate(container_cpu_usage_seconds_total{container!="", image!=""}[1m])[5m:]
) * 100

# pod_memory_usage_mb_avg

avg by (pod)(
  container_memory_working_set_bytes{container!="", image!=""}
) / 1024 / 1024

### container_memory_working_set_bytes

# pod_memory_usage_mb_p95

quantile_over_time(
  0.95,
  container_memory_working_set_bytes{container!="", image!=""}[5m:]
) / 1024 / 1024

# pod_restart_count

sum by (pod)(
  kube_pod_container_status_restarts_total
)

### kube_pod_container_status_restarts_total

# pod_cpu_limit_percent

(
  sum(rate(container_cpu_usage_seconds_total[1m]))
  /
  sum(kube_pod_container_resource_limits_cpu_cores)
) * 100

### kube_pod_container_resource_limits_cpu_cores

# pod_memory_limit_percent

(
  sum(container_memory_working_set_bytes)
  /
  sum(kube_pod_container_resource_limits_memory_bytes)
) * 100

### kube_pod_container_resource_limits_memory_bytes


🌐 APPLICATION LEVEL METRICS

# request_rate_rps

sum(rate(http_requests_total[1m]))

### http_requests_total

# success_rate_percent

(
  sum(rate(http_requests_total{status=~"2.."}[1m]))
  /
  sum(rate(http_requests_total[1m]))
) * 100

# error_rate_percent

(
  sum(rate(http_requests_total{status!~"2.."}[1m]))
  /
  sum(rate(http_requests_total[1m]))
) * 100

# http_4xx_rate_percent

(
  sum(rate(http_requests_total{status=~"4.."}[1m]))
  /
  sum(rate(http_requests_total[1m]))
) * 100

# http_5xx_rate_percent

(
  sum(rate(http_requests_total{status=~"5.."}[1m]))
  /
  sum(rate(http_requests_total[1m]))
) * 100

# latency_p50_ms

histogram_quantile(
  0.50,
  sum by (le)(
    rate(http_request_duration_seconds_bucket[1m])
  )
) * 1000

### http_request_duration_seconds_bucket

# latency_p95_ms

histogram_quantile(
  0.95,
  sum by (le)(
    rate(http_request_duration_seconds_bucket[1m])
  )
) * 1000

# latency_p99_ms

histogram_quantile(
  0.99,
  sum by (le)(
    rate(http_request_duration_seconds_bucket[1m])
  )
) * 1000

# queue_length

app_queue_length

### app_queue_length

# application_saturation_percent

(
  request_rate_rps
  /
  max_supported_rps
) * 100

### request_rate_rps
### max_supported_rps


🕸️ SERVICE MESH LEVEL (ISTIO)

# inbound_request_rate_rps

sum by (destination_workload)(
  rate(istio_requests_total{reporter="destination"}[1m])
)

### istio_requests_total

# outbound_request_rate_rps

sum by (source_workload)(
  rate(istio_requests_total{reporter="source"}[1m])
)

# mesh_latency_p95_ms

histogram_quantile(
  0.95,
  sum by (le, destination_workload)(
    rate(istio_request_duration_milliseconds_bucket[1m])
  )
)

### istio_request_duration_milliseconds_bucket
### destination_workload

# mesh_retry_rate_rps

sum by (destination_workload)(
  rate(istio_requests_total{response_flags=~"U.*"}[1m])
)

# mesh_tcp_open_connections

sum by (destination_workload)(
  istio_tcp_connections_opened_total
)

### istio_tcp_connections_opened_total

# mesh_tls_error_rate_percent

(
  sum(rate(istio_requests_total{response_flags="TLS"}[1m]))
  /
  sum(rate(istio_requests_total[1m]))
) * 100



🧠 GRAPH FEATURES (Derived – NOT Prometheus)

## Column	             ## Source
degree_centrality	     Service call graph
betweenness_centrality	 NetworkX / graph algo
closeness_centrality	 Graph distance
eigenvector_centrality	 Influence score

### istio_requests_total{reporter="source"}


⚠️ PRESSURE & STRESS INDICES (Derived)

# cpu_pressure_index

normalized(pod_cpu_usage_percent_p95)

# memory_pressure_index

normalized(pod_memory_limit_percent)

# io_pressure_index

normalized(node_disk_read_iops + node_disk_write_iops)

# stress_index

0.4*cpu + 0.3*memory + 0.2*latency + 0.1*restarts



