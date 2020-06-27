# Integration of Watsor, Home Assistant and AppDaemon

## Configuration

[Home Assistant](https://www.home-assistant.io) configuration defines the camera `camera1`. For simplicity a regular Android phone is turned into the network camera using [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam) app.

[Watsor](https://github.com/asmirnou/watsor) detects a person in `camera1` video stream using deep learning-based approach. On top of the `camera1` we configure _MJPEG IP Camera_ named `camera1_detection` where the detections of a person are rendered. The still image of that camera is a snapshot with the most recent and confident detection of a person. Several sensor values are displayed at bottom of camera view to inform about the input and ouput speeds of video stream.

## Automations

The _manual alarm control panel_ represents an alarm system in Home Assistant. When the alarm control panel is armed it turns on the detection in Watsor and turns it off when disarmed.

MQTT _binary sensor_ subscribes to the Watsor publications and reports when a person or a car are detected. To avoid the flapping of state from on/off too fast (seesaw), the _template binary sensor_ `camera1_person_detected` delays switching to `off` for 5 sec.

When the alarm system is armed and a person is detected, the binary sensor triggers the alarm. The automation then executes a script that takes two snapshots from the cameras, emails about the detected threat, shows a notification on the frontend, activates stobe lights and plays a warning sound message to deter the intruder off.

[AppDaemon](https://github.com/home-assistant/appdaemon) runs automation app to record a video from the camera when the system is armed and a person is detected. 

The template binary sensor `camera1_no_detection` slows the camera down, if nothing is detected for more than 30 seconds. The camera will reach full speed by itself again as soon as something's detected.

Another template binary sensor `camera1_fps_is_low` monitors the speed of the camera and triggers the alert, emailing that the camera is broken or disconnected suddenly.

## Usage of detection details

When the camera is tuned on as the result of arming the system, HomeAssistant enables the reporting of detection details via MQTT `watsor/cameras/camera1/detection/car/details` topic, which by default are turned off, until Watsor receives the command `details = on`.

The details are published by Watsor in JSON format, where attribute `d` represents the array of all cars detected in the current video frame. Template sensor `camera1_car_count` subscribes to the topic to listen to the detection details and converts the length of array `d` into the number of cars detected. The given number then is rendered in Lovelace UI.
