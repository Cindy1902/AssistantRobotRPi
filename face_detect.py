from picamera2 import Picamera2, Preview
import time

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": "XRGB8888", "size": (800, 600)}
))
picam2.start_preview(Preview.QTGL)
picam2.start()
time.sleep(5)
picam2.capture_file("test.jpg")
