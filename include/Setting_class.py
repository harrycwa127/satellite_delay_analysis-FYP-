import tkinter as tk
import math
from include.SimParameter_class import SimParameter

class Setting:
    inclination = -1
    argument_of_perigee = -1
    motion = -1
    orbit_size = -1
    sat_size = -1

    @classmethod
    def display(cls):
        cls.window = tk.Tk()
        cls.window.geometry("420x350")
        cls.window.title("Setting")

        # Blank
        cls.blank_label1 = tk.Label(cls.window, text=" ", anchor='e')
        cls.blank_label1.grid(row=0, column=0)
        
        # Create input fields for setting parameters
        cls.inclination_label = tk.Label(cls.window, text="Satellite Inclination (degree): ", anchor='e')
        cls.inclination_label.grid(row=1, column=0)
        cls.inclination_input = tk.Entry(cls.window)
        cls.inclination_input.insert(0, "97")
        cls.inclination_input.grid(row=1, column=1)
        
        cls.argument_of_perigee_label = tk.Label(cls.window, text="Satellite Argument Of_Perigee (degree): ", anchor='e')
        cls.argument_of_perigee_label.grid(row=2, column=0)
        cls.argument_of_perigee_input = tk.Entry(cls.window)
        cls.argument_of_perigee_input.insert(0, "0")
        cls.argument_of_perigee_input.grid(row=2, column=1)

        cls.motion_label = tk.Label(cls.window, text="Satellite Motion (Revolutions/Day): ", anchor='e')
        cls.motion_label.grid(row=3, column=0)
        cls.motion_input = tk.Entry(cls.window)
        cls.motion_input.insert(0, "14")
        cls.motion_input.grid(row=3, column=1)

        cls.off_nadir_label = tk.Label(cls.window, text="Satellite Off Nadir Angle (degree): ", anchor='e')
        cls.off_nadir_label.grid(row=4, column=0)
        cls.off_nadir_input = tk.Entry(cls.window)
        cls.off_nadir_input.insert(0, "45")
        cls.off_nadir_input.grid(row=4, column=1)

        cls.orbit_size_label = tk.Label(cls.window, text="Total Number of Orbit: ", anchor='e')
        cls.orbit_size_label.grid(row=5, column=0)
        cls.orbit_size_input = tk.Entry(cls.window)
        cls.orbit_size_input.insert(0, "9")
        cls.orbit_size_input.grid(row=5, column=1)

        cls.sat_size_label = tk.Label(cls.window, text="Number of Satellite in Orbit: ", anchor='e')
        cls.sat_size_label.grid(row=6, column=0)
        cls.sat_size_input = tk.Entry(cls.window)
        cls.sat_size_input.insert(0, "25")
        cls.sat_size_input.grid(row=6, column=1)
        
        cls.package_size_label = tk.Label(cls.window, text="Package Size (Bytes): ", anchor='e')
        cls.package_size_label.grid(row=7, column=0)
        cls.package_size_input = tk.Entry(cls.window)
        cls.package_size_input.insert(0, "56623104")
        cls.package_size_input.grid(row=7, column=1)
        
        cls.data_rate_label = tk.Label(cls.window, text="Data Rate (Bytes/s): ", anchor='e')
        cls.data_rate_label.grid(row=8, column=0)
        cls.data_rate_input = tk.Entry(cls.window)
        cls.data_rate_input.insert(0, "530579456")
        cls.data_rate_input.grid(row=8, column=1)

        cls.signal_speed_label = tk.Label(cls.window, text="Signal Speed (m/s): ", anchor='e')
        cls.signal_speed_label.grid(row=9, column=0)
        cls.signal_speed_input = tk.Entry(cls.window)
        cls.signal_speed_input.insert(0, "299792458")
        cls.signal_speed_input.grid(row=9, column=1)

        cls.process_delay_label = tk.Label(cls.window, text="Process Delay (sec): ", anchor='e')
        cls.process_delay_label.grid(row=10, column=0)
        cls.process_delay_input = tk.Entry(cls.window)
        cls.process_delay_input.insert(0, "0.01")
        cls.process_delay_input.grid(row=10, column=1)

        cls.buffer_delay_label = tk.Label(cls.window, text="Buffer Delay (sec): ", anchor='e')
        cls.buffer_delay_label.grid(row=11, column=0)
        cls.buffer_delay_input = tk.Entry(cls.window)
        cls.buffer_delay_input.insert(0, "0.05")
        cls.buffer_delay_input.grid(row=11, column=1)

        # Blank
        cls.blank_label2 = tk.Label(cls.window, text=" ", anchor='e')
        cls.blank_label2.grid(row=12, column=0)
        
        # Add a button for submitting the parameters
        cls.submit_button = tk.Button(cls.window, text="Submit", command=cls.submit)
        cls.submit_button.grid(row=13, column=0, columnspan=2)
        
        cls.window.mainloop()
        
    @classmethod
    def submit(cls):
        # Retrieve the parameter values from the input fields
        SimParameter.set_off_nadir(math.radians(int(cls.off_nadir_input.get())))
        SimParameter.set_package_size(int(cls.package_size_input.get()))
        SimParameter.set_data_rate(int(cls.data_rate_input.get()))
        SimParameter.set_signal_speed(int(cls.signal_speed_input.get()))
        SimParameter.set_process_delay(float(cls.process_delay_input.get()))
        SimParameter.set_buffer_delay(float(cls.buffer_delay_input.get()))
        
        cls.inclination = math.radians(int(cls.inclination_input.get()))
        cls.argument_of_perigee = math.radians(int(cls.argument_of_perigee_input.get()))
        cls.motion = int(cls.motion_input.get())
        cls.orbit_size = int(cls.orbit_size_input.get())
        cls.sat_size = int(cls.sat_size_input.get())
        cls.window.destroy()

# input_ui = SettingUI()