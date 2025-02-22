# From-node exporter

The From-node Exporter for Prometheus is designed to probe the accessibility of external endpoints from each node of the Kubernetes cluster over TCP, HTTP, and ICMP.

## How will it be useful?

While there are other tools like the Blackbox Exporter, the From-node Exporter focuses specifically on simplicity and efficiency for Kubernetes node-level probing. It's designed to serve a specific use case - ensuring all required endpoints are accessible from every node of your cluster.


### Use case
Consider a scenario where your pods were evicted due to a node failure. The pods were then moved to new nodes that were recently added to the cluster. However, this resulted in errors and service unavailability due to a lack of access to essential external endpoints. Later, it was discovered that the security department failed to apply access rules to the new cluster nodes. 

This is just one example of how node-level probes can help you identify potential issues before they become major problems.

## Run

### Kubernetes

Install Helm [chart](./chart/).

### Docker

1. Create config.yaml
2. Run

    ```
    docker run --rm -v $(pwd)/config.yaml:/config.yaml teymurgahramanov/from-node-exporter:latest
    ```

### Binary

1. Download binary from [the releases tab](https://github.com/teymurgahramanov/from-node-exporter/releases)
2. Create config.yaml
3. Run ```./from-node-exporter```

## config.yaml

| Field | Description  | Type  | Default
|:-:|:-:|:-:|:-:
| exporter.metricsListenPort  | | Integer | 8080
| exporter.metricsListenPath  |   | String  | /metrics
| exporter.defaultProbeInterval  | Default interval between probes in seconds | Integer   | 22
| exporter.defaultProbeTimeout  | Default timeout for probes in seconds | Integer   | 22
| targets  | KVs of targets to probe | List |
| targets."target".address  | Target address. Can be URL, IP, or IP:PORT depending on chosen module | String |
| targets."target".module  | Module to probe the target (tcp, http, icmp) | String |
| targets."target".interval  | Probe interval for the target | Integer | exporter.defaultProbeInterval
| targets."target".timeout  | Probe timeout for the target | Integer | exporter.defaultProbeTimeout

Example:
```
exporter:
  metricsListenPort: 3333
  metricsListenPath: /metricz
  defaultProbeInterval: 31
  defaultProbeTimeout: 13
targets:
  target1:
    address: api.example.com:8080
    module: tcp
    timeout: 15
  target2:
    address: https://example.com
    module: http
    interval: 60
  target3:
    address: 192.168.0.1
    module: icmp
```

## Instant probes
Useful to check the availability of individual targets besides configured ones instantly. It's performed by making a POST request to `/probe`.

In the case of Kubernetes, it can be leveraged to perform instant probes from all nodes at once instead of doing it one by one. For better experience try [KubePing](https://github.com/teymurgahramanov/KubePing).

### Example
Here is the example of probe using `http` module.

Request body
```
{
    "module": "http", 
    "address": "http://192.168.0.107:5000",
    "timeout": 1 # Optional
}
```
Response body
```
{
    "result": true # or false
}
```

## Metrics

By default metrics and their descriptions are available on ```:8080/metrics```.

Prometheus job example:
```
- job_name: from-node-exporter
  kubernetes_sd_configs:
    - role: endpoints
  relabel_configs:
    - source_labels: [__meta_kubernetes_endpoints_name]
      regex: from-node-exporter
      action: keep
    - source_labels: [__meta_kubernetes_endpoint_node_name]
      action: replace
      target_label: instance
```

## Note

- __The ICMP probe requires elevated privileges to function__ \
Refer to https://github.com/prometheus-community/pro-bing?tab=readme-ov-file#supported-operating-systems

## Contributing

Contributions to enhance or fix issues are welcome. Feel free to submit pull requests.
