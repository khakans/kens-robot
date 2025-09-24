# src/control/drive.py
try:
    from gpiozero import Motor
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    # Fallback dummy class kalau dijalankan di PC / tanpa GPIO
    GPIO_AVAILABLE = False

    class Motor:
        def __init__(self, forward=None, backward=None):
            self.forward_pin = forward
            self.backward_pin = backward

        def forward(self, speed=1.0):
            print(f"[DummyMotor] Forward (pin {self.forward_pin}) speed={speed}")

        def backward(self, speed=1.0):
            print(f"[DummyMotor] Backward (pin {self.backward_pin}) speed={speed}")

        def stop(self):
            print(f"[DummyMotor] Stop (pins {self.forward_pin}, {self.backward_pin})")


from time import sleep


class DifferentialDrive:
    """
    Simple wrapper for two motors using gpiozero.Motor
    left_pins and right_pins are tuples: (forward_pin, backward_pin)
    """

    def __init__(self, left_pins=(17, 18), right_pins=(22, 23)):
        self.left = Motor(forward=left_pins[0], backward=left_pins[1])
        self.right = Motor(forward=right_pins[0], backward=right_pins[1])

    def forward(self, speed=0.6, duration=None):
        self.left.forward(speed)
        self.right.forward(speed)
        if duration:
            sleep(duration)
            self.stop()

    def backward(self, speed=0.6, duration=None):
        self.left.backward(speed)
        self.right.backward(speed)
        if duration:
            sleep(duration)
            self.stop()

    def stop(self):
        self.left.stop()
        self.right.stop()

    def turn_left(self, speed=0.5, duration=None):
        self.left.backward(speed)
        self.right.forward(speed)
        if duration:
            sleep(duration)
            self.stop()

    def turn_right(self, speed=0.5, duration=None):
        self.left.forward(speed)
        self.right.backward(speed)
        if duration:
            sleep(duration)
            self.stop()
