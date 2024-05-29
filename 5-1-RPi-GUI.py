from PyQt5 import QtWidgets, QtCore, QtTest
import sys
import RPi.GPIO as GPIO

class TrafficWindow(QtWidgets.QMainWindow):
    def __init__(self, app: QtWidgets.QApplication):
        super(TrafficWindow, self).__init__()
        self.initConstants()
        self.initGPIO()
        self.app = app
        # Connect our custom logic to the normal quit functionality
        # in order to include GPIO.cleanup()
        self.app.aboutToQuit.connect(self.cleanup)
        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.initUI()
    
    def initConstants(self):
        # For legibility in the GPIO section, these are the pins the LEDs are connected to
        self.GREEN = 18
        self.AMBER = 16
        self.RED   = 13
        self.OFF   = 0
    
    def initGPIO(self):
        self.currentLed = self.OFF
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(13, GPIO.OUT)
        GPIO.setup(16, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)
        
        
    def initUI(self):
        self.vBtnBox = QtWidgets.QVBoxLayout(self.main_widget)
        self.initRadioGroup()
        self.initButtons()
        
    def initRadioGroup(self):
        self.trafficGroup = QtWidgets.QGroupBox("Traffic Lights", self.main_widget)
        #Initialise radios and connect their onClick functions
        self.green = QtWidgets.QRadioButton("Green", self)
        self.green.toggled.connect(self.greenOnClick)
        self.amber = QtWidgets.QRadioButton("Amber", self)
        self.amber.toggled.connect(self.amberOnClick)
        self.red = QtWidgets.QRadioButton("Red", self)
        self.red.toggled.connect(self.redOnClick)
        self.off = QtWidgets.QRadioButton("Off", self)
        self.off.toggled.connect(self.offOnClick)
        #By default, no LEDs are lit
        self.off.setChecked(True)
        #Group radios into a common layout
        self.vRadioBox = QtWidgets.QVBoxLayout(self.trafficGroup)
        self.vRadioBox.addWidget(self.green, 0)
        self.vRadioBox.addWidget(self.amber, 1)
        self.vRadioBox.addWidget(self.red, 2)
        self.vRadioBox.addWidget(self.off, 3)
        self.vRadioBox.addStretch(1)
    
    def initButtons(self):
        #Initialise buttons and connect their onClick functions
        self.cycleLights = QtWidgets.QPushButton("Cycle", self)
        self.cycleLights.clicked.connect(self.cycleOnClick)
        self.quitApp = QtWidgets.QPushButton("Exit", self)
        self.quitApp.clicked.connect(self.exitOnClick)
        # Group radio group and buttons together
        self.vBtnBox.addWidget(self.trafficGroup)
        self.vBtnBox.addWidget(self.cycleLights)
        self.vBtnBox.addWidget(self.quitApp)
        self.vBtnBox.addStretch(1)
    
    def exitOnClick(self):
        self.app.quit()
    
    def cleanup(self):
        self.switchLed(self.OFF)
        GPIO.cleanup()

    #disable all LED-related widgets and cycle through all colours
    def cycleOnClick(self):
        #take a copy of the currently-lit LED, if one is
        state = self.currentLed
        self.cycleLights.setText("Cycling...")
        self.cycleLights.setDisabled(True)
        self.trafficGroup.setDisabled(True)
        self.switchLed(self.GREEN)
        #qWait is an alternative to time.sleep that allows the UI to update
        #while this thread waits for the specified time period
        #if this wasn't used, the radios/cycle button wouldn't update their state to disabled
        #and the program would hang while the LEDs cycled
        #but in general this kind of behaviour should be implemented with signals
        QtTest.QTest.qWait(2000)
        self.switchLed(self.AMBER)
        QtTest.QTest.qWait(1000)
        self.switchLed(self.RED)
        QtTest.QTest.qWait(2000)
        self.switchLed(self.OFF)
        #Restore previous widget state
        self.cycleLights.setText("Cycle")
        self.cycleLights.setDisabled(False)
        self.trafficGroup.setDisabled(False)
        #Restore LEDs to their previous state   
        self.switchLed(state)  
        
    def greenOnClick(self):
        self.switchLed(self.GREEN)
        
    def amberOnClick(self):
        self.switchLed(self.AMBER)
        
    def redOnClick(self):
        self.switchLed(self.RED)
    
    def offOnClick(self):
        self.switchLed(self.OFF)
    
    #Switch the specified LED on and all others off (or all off)
    def switchLed(self, led):
        match led:
            case self.GREEN:
                GPIO.output(self.GREEN, GPIO.HIGH)
                GPIO.output(self.AMBER, GPIO.LOW)
                GPIO.output(self.RED, GPIO.LOW)
            case self.AMBER:
                GPIO.output(self.GREEN, GPIO.LOW)
                GPIO.output(self.AMBER, GPIO.HIGH)
                GPIO.output(self.RED, GPIO.LOW)
            case self.RED:
                GPIO.output(self.GREEN, GPIO.LOW)
                GPIO.output(self.AMBER, GPIO.LOW)
                GPIO.output(self.RED, GPIO.HIGH)
            case self.OFF:
                GPIO.output(self.GREEN, GPIO.LOW)
                GPIO.output(self.AMBER, GPIO.LOW)
                GPIO.output(self.RED, GPIO.LOW)
        self.currentLed = led
        
        
def window():
    app = QtWidgets.QApplication(sys.argv)
    win = TrafficWindow(app)
    win.setGeometry(200, 200, 300, 300)
    win.setWindowTitle("Task 5.1 Traffic LED Selector")
    win.show()
    sys.exit(app.exec_())

window()
GPIO.cleanup()
        