package main

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/teymurgahramanov/KubePing/exporter/modules"
	"gopkg.in/yaml.v3"
)

type configuration struct {
	Targets map[string]targetConfig `yaml:"targets"`
	Exporter exporterConfig `yaml:"exporter"`
}

type targetConfig struct {
	Address string `yaml:"address"`
	Module string `yaml:"module"`
	Interval int `yaml:"interval"`
	Timeout int `yaml:"timeout"`
}

type exporterConfig struct {
	MetricsListenPath string `yaml:"metricsListenPath"`
	MetricsListenPort int `yaml:"metricsListenPort"`
	DefaultProbeInterval int `yaml:"defaultProbeInterval"`
	DefaultProbeTimeout int `yaml:"defaultProbeTimeout"`
}

type probeRequest struct {
	Module  string `json:"module"`
	Address string `json:"address"`
	Timeout int    `json:"timeout"`
}

type probeResponse struct {
	Result bool   `json:"result"`
	Error  string `json:"error,omitempty"`
}

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	configFile := "config.yaml"

	data, err := os.ReadFile(configFile)
	if err != nil {
		logger.Error(fmt.Sprint(err))
	}

	var config configuration
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		logger.Error(fmt.Sprint(err))
	}

	if config.Exporter.MetricsListenPort == 0 {
		config.Exporter.MetricsListenPort = 8080
	}
	if config.Exporter.MetricsListenPath == "" {
		config.Exporter.MetricsListenPath = "/metrics"
	}
	if config.Exporter.DefaultProbeInterval == 0 {
		config.Exporter.DefaultProbeInterval = 22
	}
	if config.Exporter.DefaultProbeTimeout == 0 {
		config.Exporter.DefaultProbeTimeout = 5
	}

	var (
		probeResult = prometheus.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "probe_result",
				Help: "Current status of the probe (1 for success, 0 for failure)",
			},
			[]string{"target", "module","address"},
		)
	)

	promRegistry := prometheus.NewRegistry()
	prometheus.DefaultRegisterer = promRegistry
	prometheus.DefaultGatherer = promRegistry
	prometheus.MustRegister(probeResult)
	
	http.Handle(config.Exporter.MetricsListenPath, promhttp.HandlerFor(prometheus.DefaultGatherer, promhttp.HandlerOpts{}))
	http.HandleFunc("/probe", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		var request probeRequest
		err := json.NewDecoder(r.Body).Decode(&request)
		if err != nil {
			http.Error(w, "Bad request", http.StatusBadRequest)
			return
		}

		timeout := request.Timeout
		if timeout == 0 {
			timeout = config.Exporter.DefaultProbeTimeout
		}

		resultHandler := func(result bool, err error) {
			var response probeResponse
			response.Result = false
			if result {
				logger.Info("OK")
				response.Result = true
			} else {
					if err != nil {
						logger.Error(fmt.Sprint(err.Error()))
					}
					response.Error = err.Error()
			}
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(response)
		}

		switch request.Module {
		case "tcp":
				result, err := modules.ProbeTCP(request.Address, timeout)
				resultHandler(result, err)
		case "http":
				result, err := modules.ProbeHTTP(request.Address, timeout)
				resultHandler(result, err)
		case "icmp":
				result, err := modules.ProbeICMP(request.Address)
				resultHandler(result, err)
		default:
				logger.Error("Unknown module")
				http.Error(w, "Unknown module", http.StatusBadRequest)
				return
		}
	})		
	go func() {
		http.ListenAndServe(":"+fmt.Sprint(config.Exporter.MetricsListenPort), nil)
	}()

	var wg sync.WaitGroup

	for key, value := range config.Targets {
		wg.Add(1)
		go func(target string, module string, address string, interval int, timeout int) {
			defer wg.Done()
			if interval == 0 {
				interval = config.Exporter.DefaultProbeInterval
			}
			if timeout == 0 {
				timeout = config.Exporter.DefaultProbeTimeout
			}
			targetLogger := logger.With(slog.String("target",target))
			resultHandler := func(result bool, err error, interval int) {
				if result {
					targetLogger.Info("OK")
					probeResult.WithLabelValues(target, module, address).Set(1)
				} else {
						if err != nil {
							targetLogger.Error(fmt.Sprint(err.Error()))
						}
						probeResult.WithLabelValues(target, module, address).Set(0)
				}
				time.Sleep(time.Duration(interval) * time.Second)
			}
			switch module {
				case "tcp":
					for {
						result,err := modules.ProbeTCP(address,timeout)
						resultHandler(result,err,interval)
					}
				case "http":
					for {
						result,err := modules.ProbeHTTP(address,timeout)
						resultHandler(result,err,interval)
					}
				case "icmp":
					for {
						result,err := modules.ProbeICMP(address)
						resultHandler(result,err,interval)
					}
				default:
					targetLogger.Error("Unknown module")
			}
		}(key, value.Module, value.Address, value.Interval, value.Timeout)
	}
	wg.Wait()
}