#!/usr/bin/env python3
"""
Test script to launch the GUI and take a screenshot
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from main import CryptoPredictionApp

def test_gui():
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create main window
    window = CryptoPredictionApp()
    window.show()
    
    # Take screenshot after a short delay
    def take_screenshot():
        try:
            # Take screenshot
            screen = app.primaryScreen()
            screenshot = screen.grabWindow(window.winId())
            screenshot.save('cryptocurrency_app_screenshot.png')
            print("Screenshot saved as cryptocurrency_app_screenshot.png")
            
            # Populate some demo data
            window.coin_combo.setCurrentText('bitcoin')
            window.days_spinbox.setValue(30)
            
            # Close the application
            app.quit()
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            app.quit()
    
    # Schedule screenshot after 2 seconds
    QTimer.singleShot(2000, take_screenshot)
    
    # Run application briefly
    app.exec_()

if __name__ == "__main__":
    test_gui()