# NODE_LEVEL -------------

### node_cpu_seconds_total
curl.exe "http://localhost:9090/api/v1/query?query=node_cpu_seconds_total" -o node_cpu.json
type node_cpu.json

### node_memory_MemAvailable_bytes
curl.exe "http://localhost:9090/api/v1/query?query=node_memory_MemAvailable_bytes" -o node_mem.json
type node_mem.json

### node_network_receive_bytes_total
curl.exe "http://localhost:9090/api/v1/query?query=node_network_receive_bytes_total" -o node_net_rx.json
type node_net_rx.json

### cpu_utilization
curl.exe "http://localhost:9090/api/v1/query?query=100%20-%20(avg%20by%20(instance)%20(irate(node_cpu_seconds_total%7Bmode%3D%22idle%22%7D%5B1m%5D))%20*%20100)" --output cpu_utilization.json
type cpu_utilization.json

### memory_usage_&_availability
curl.exe "http://localhost:9090/api/v1/query?query=((node_memory_MemTotal_bytes%20-%20node_memory_MemAvailable_bytes)%20%2F%20node_memory_MemTotal_bytes)%20*%20100" --output memory_usage.json
type memory_usage.json

### disk_I/O_throughput_(read/write MB/s)
curl.exe "http://localhost:9090/api/v1/query?query=irate(node_disk_read_bytes_total%5B1m%5D)%20%2F%201024%20%2F%201024" --output disk_read.json
type disk_read.json

curl.exe "http://localhost:9090/api/v1/query?query=irate(node_disk_written_bytes_total%5B1m%5D)%20%2F%201024%20%2F%201024" --output disk_write.json
type disk_write.json

### network_throughput_(incoming/outgoing_rate MB/s)
curl.exe "http://localhost:9090/api/v1/query?query=irate(node_network_receive_bytes_total%5B1m%5D)%20%2F%201024%20%2F%201024" --output net_in.json
type net_in.json

curl.exe "http://localhost:9090/api/v1/query?query=irate(node_network_transmit_bytes_total%5B1m%5D)%20%2F%201024%20%2F%201024" --output net_out.json
type 

### cpu_load_average_(1m, 5m, 15m)
curl.exe "http://localhost:9090/api/v1/query?query=node_load1" --output load1.json
type load1.json

curl.exe "http://localhost:9090/api/v1/query?query=node_load5" --output load5.json
type load5.json

curl.exe "http://localhost:9090/api/v1/query?query=node_load15" --output load15.json\
type load15.json


# POD_LEVEL -------------

### container_cpu_usage_seconds_total
curl.exe "http://localhost:9090/api/v1/query?query=container_cpu_usage_seconds_total" -o cadvisor_cpu.json
type cadvisor_cpu.json

### container_memory_usage_bytes
curl.exe "http://localhost:9090/api/v1/query?query=container_memory_usage_bytes" -o cadvisor_mem.json
type cadvisor_mem.json

### container_fs_usage_bytes
curl.exe "http://localhost:9090/api/v1/query?query=container_fs_usage_bytes" -o cadvisor_fs.json
type cadvisor_fs.json

### pod_cpu_usage (%)
curl.exe "http://localhost:9090/api/v1/query?query=sum%20by%20(pod%2C%20namespace)%20(irate(container_cpu_usage_seconds_total%7Bimage!%3D%22%22%2C%20container!%3D%22%22%7D%5B1m%5D))%20*%20100" --output pod_cpu.json
type pod_cpu.json

### pod_memory_usage (MB)
curl.exe "http://localhost:9090/api/v1/query?query=sum%20by%20(pod%2C%20namespace)%20(container_memory_working_set_bytes%7Bimage!%3D%22%22%2C%20container!%3D%22%22%7D)%20%2F%201024%20%2F%201024" --output pod_memory.json
type pod_memory.json

### pod_restart_count_(stability_measure)
curl.exe "http://localhost:9090/api/v1/query?query=sum%20by%20(pod%2C%20namespace)%20(kube_pod_container_status_restarts_total)" --output pod_restarts.json
type pod_restarts.json

### pod_network_I/O_(incoming/outgoing MB/s)
curl.exe "http://localhost:9090/api/v1/query?query=sum%20by%20(pod%2C%20namespace)%20(irate(container_network_receive_bytes_total%5B1m%5D))%20%2F%201024%20%2F%201024" --output pod_net_in.json
type pod_net_in.json

curl.exe "http://localhost:9090/api/v1/query?query=sum%20by%20(pod%2C%20namespace)%20(irate(container_network_transmit_bytes_total%5B1m%5D))%20%2F%201024%20%2F%201024" --output pod_net_out.json
type pod_net_out.json


# APPLICATION_LEVEL -------------

### queue_length
curl.exe http://127.0.0.1:3000/metrics | findstr app_queue_length

### request_count (RPS)
curl.exe http://127.0.0.1:3000/metrics | findstr http_requests_total

### latency_histogram
curl.exe http://127.0.0.1:3000/metrics | findstr http_request_duration

### errors_(status != 200)_find
curl.exe http://127.0.0.1:3000/metrics | findstr 404



# SERVICE_MESH_LEVEL -------------

### inbound_request_rate_rps
Invoke-WebRequest "http://localhost:9090/api/v1/query?query=sum%20by%20(destination_workload)%20(rate(istio_requests_total%7Breporter%3D%22destination%22%7D%5B1m%5D))" | Select-Object -Expand Content


### outbound_request_rate_rps -
Invoke-WebRequest "http://localhost:9090/api/v1/query?query=sum%20by%20(source_workload)%20(rate(istio_requests_total%7Breporter%3D%22source%22%7D%5B1m%5D))" | Select-Object -Expand Content


### mesh_latency_p95_ms
Invoke-WebRequest "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95%2C%20sum%20by%20(le%2C%20destination_workload)%20(rate(istio_request_duration_milliseconds_bucket%5B1m%5D)))" | Select-Object -Expand Content


### mesh_retry_rate_rps -
Invoke-WebRequest "http://localhost:9090/api/v1/query?query=sum%20by%20(destination_workload)%20(rate(istio_requests_total%7Bresponse_flags%3D~%22U.%22%7D%5B1m%5D))" | Select-Object -Expand Content


### mesh_tls_error_rate_percent
Invoke-WebRequest "http://localhost:9090/api/v1/query?query=sum%20by%20(destination_workload)%20(rate(istio_requests_total%7Bresponse_flags%3D%22TLS%22%7D%5B1m%5D))" | Select-Object -Expand Content



#### ------------------------------------------------------------------------

# check_prometheus_API_is_alive
curl.exe "http://localhost:9090/api/v1/query?query=up"
