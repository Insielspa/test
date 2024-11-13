# Notification

## Description
The `NotificationClient` class is designed to handle notifications and alerts for the `fvg-vision-ai` application. It integrates with Azure IoT Hub to send messages and alerts based on the analysis of video frames.

## Functionality

### Initialization
The class initializes with:
- **Azure IoT Hub Client**: Connects to Azure IoT Hub using the provided connection string.
- **AppSettings**: Configuration settings for the application, including device and camera IDs, and aggregation time for measures.
- **ThreadPoolExecutor**: Manages the execution of notification tasks in separate threads.

### Notification Handling
The core functionality of the class revolves around handling notifications and alerts. For each notification, the following steps are performed:
1. **Data Aggregation**: Aggregates data over a specified time interval.
2. **Message Building**: Builds the message payload with the aggregated data.
3. **Message Sending**: Sends the message to Azure IoT Hub.

### Alert Handling
The class also handles specific alerts, such as people in a zone or raised hands. For each alert, the following steps are performed:
1. **Alert Building**: Builds the alert payload with the alert details.
2. **Alert Sending**: Sends the alert to Azure IoT Hub.

### Example Usage

```python
import threading
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.notify.notification_client import NotificationClient
from fvgvisionai.processor.data_aggregator import DataAggregator

app_settings = AppSettings(...)
notification_client = NotificationClient(
    enabled=True,
    azure_connection_string="your_connection_string",
    device_id="your_device_id",
    camera_id="your_camera_id",
    model_id="your_model_id",
    measures_aggregation_time_ms=10000
)

notification_client.start()

# Example of handling notifications
data_aggregator = DataAggregator()
data_aggregation_datetime_start = datetime.now()
notification_client.handle_notification(data_aggregation_datetime_start, data_aggregator)

# Example of handling alerts
notification_client.handle_alarms(AlarmStatus.ALARM_WITH_NOTIFICATION, AlarmStatus.ALARM_WITH_NOTIFICATION)
```

## Notes
- Ensure the Azure IoT Hub connection string is correct and accessible.
- Properly configure the `AppSettings` class with necessary settings before initializing the `NotificationClient`.