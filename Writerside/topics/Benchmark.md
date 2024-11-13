# Benchmark

## Description
The `BenchmarkMonitor` class is designed to measure and record the performance of the `fvg-vision-ai` application. It aggregates data over specified intervals and logs the performance metrics into an Excel file. Additionally, it generates graphs to visualize the performance data.

## Functionality

### Initialization
The class initializes with:
- **AppSettings**: Configuration settings for the application, including benchmark parameters.
- **ThreadPoolExecutor**: Manages the execution of benchmark tasks in separate threads.
- **Excel Workbook**: Creates or loads an Excel workbook to store benchmark results.

### Performance Measurement
The core functionality of the class revolves around measuring and recording performance metrics. For each measurement, the following steps are performed:
1. **Data Aggregation**: Aggregates data over a specified time interval.
2. **Message Building**: Builds the message payload with the aggregated data.
3. **Data Logging**: Logs the data into the Excel workbook.
4. **Graph Generation**: Generates graphs to visualize the performance data.

### Example Usage

```python
import threading
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.benchmark.benchmark_monitor import BenchmarkMonitor
from fvgvisionai.processor.data_aggregator import DataAggregator

app_settings = AppSettings(...)
exit_signal = threading.Event()

benchmark_monitor = BenchmarkMonitor(
    enabled=True,
    app_settings=app_settings,
    measures_aggregation_time_ms=10000,
    exit_signal=exit_signal
)

benchmark_monitor.start()

# Example of measuring performance
data_aggregator = DataAggregator()
frame_index = 0
source_frame = ...  # Obtain the source frame from the video stream
benchmark_monitor.measure_performance(frame_index, source_frame, data_aggregator)

# Close the benchmark monitor and save results
benchmark_monitor.close()
```

## Notes
- Ensure the input data is correctly populated with performance metrics.
- Properly configure the `AppSettings` class with necessary settings before initializing the `BenchmarkMonitor`.