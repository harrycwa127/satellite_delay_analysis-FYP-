import tkinter as tk
import math
from include import read_data

class Setting:
    # sat parameter
    inclination: float = math.radians(97)
    argument_of_perigee: float = 0
    motion: float = 14
    orbit_size: float = 9
    sat_size: float = 25

    off_nadir: float = math.radians(45)
    package_size: float = 56623104
    data_rate: float = 530579456
    signal_speed: float = 299792458
    buffer_delay: float = 0.01
    process_delay: float = 0.05
    start_time_julian, start_greenwich = read_data.get_start_julian_time()

    

    @classmethod
    def display(cls):
        cls.window = tk.Tk()
        cls.window.geometry("570x390")
        cls.window.title("Parameter Setting")
        font = ("Helvetica", 11)

        # Blank
        cls.blank_label1 = tk.Label(cls.window, text=" ", anchor=tk.E, font=font)
        cls.blank_label1.grid(row=0, column=0)
        
        # Create input fields for setting parameters
        cls.inclination_label = tk.Label(cls.window, text="Satellite Inclination (degree): ", anchor=tk.E, font=font, width=32, pady=3)
        cls.inclination_label.grid(row=1, column=0)
        cls.inclination_input = tk.Entry(cls.window, font=font, width=32)
        cls.inclination_input.insert(0, "97")
        cls.inclination_input.grid(row=1, column=1)
        
        cls.argument_of_perigee_label = tk.Label(cls.window, text="Satellite Argument Of Perigee (degree): ", anchor=tk.E, font=font, width=32, pady=3)
        cls.argument_of_perigee_label.grid(row=2, column=0)
        cls.argument_of_perigee_input = tk.Entry(cls.window, font=font, width=32)
        cls.argument_of_perigee_input.insert(0, "0")
        cls.argument_of_perigee_input.grid(row=2, column=1)

        cls.motion_label = tk.Label(cls.window, text="Satellite Motion (Revolutions/Day): ", anchor=tk.E, font=font, width=32, pady=3)
        cls.motion_label.grid(row=3, column=0)
        cls.motion_input = tk.Entry(cls.window, font=font, width=32)
        cls.motion_input.insert(0, "14")
        cls.motion_input.grid(row=3, column=1)

        cls.off_nadir_label = tk.Label(cls.window, text="Satellite Off Nadir Angle (degree): ", anchor=tk.E, font=font, width=32, pady=3)
        cls.off_nadir_label.grid(row=4, column=0)
        cls.off_nadir_input = tk.Entry(cls.window, font=font, width=32)
        cls.off_nadir_input.insert(0, "45")
        cls.off_nadir_input.grid(row=4, column=1)

        cls.orbit_size_label = tk.Label(cls.window, text="Total Number of Orbit: ", anchor=tk.E, font=font, width=32, pady=3)
        cls.orbit_size_label.grid(row=5, column=0)
        cls.orbit_size_input = tk.Entry(cls.window, font=font, width=32)
        cls.orbit_size_input.insert(0, "9")
        cls.orbit_size_input.grid(row=5, column=1)

        cls.sat_size_label = tk.Label(cls.window, text="Number of Satellite in Orbit: ", anchor=tk.E, font=font, width=32, pady=3)
        cls.sat_size_label.grid(row=6, column=0)
        cls.sat_size_input = tk.Entry(cls.window, font=font, width=32)
        cls.sat_size_input.insert(0, "25")
        cls.sat_size_input.grid(row=6, column=1)
        
        cls.package_size_label = tk.Label(cls.window, text="Package Size (Bytes): ", anchor=tk.E, font=font, width=32, pady=3)
        cls.package_size_label.grid(row=7, column=0)
        cls.package_size_input = tk.Entry(cls.window, font=font, width=32)
        cls.package_size_input.insert(0, "56623104")
        cls.package_size_input.grid(row=7, column=1)
        
        cls.data_rate_label = tk.Label(cls.window, text="Data Rate (Bytes/s): ", anchor=tk.E, font=font, width=32, pady=3)
        cls.data_rate_label.grid(row=8, column=0)
        cls.data_rate_input = tk.Entry(cls.window, font=font, width=32)
        cls.data_rate_input.insert(0, "530579456")
        cls.data_rate_input.grid(row=8, column=1)

        cls.signal_speed_label = tk.Label(cls.window, text="Signal Speed (m/s): ", anchor=tk.E, font=font, width=32, pady=3)
        cls.signal_speed_label.grid(row=9, column=0)
        cls.signal_speed_input = tk.Entry(cls.window, font=font, width=32)
        cls.signal_speed_input.insert(0, "299792458")
        cls.signal_speed_input.grid(row=9, column=1)

        cls.process_delay_label = tk.Label(cls.window, text="Process Delay (sec): ", anchor=tk.E, font=font, width=32, pady=3)
        cls.process_delay_label.grid(row=10, column=0)
        cls.process_delay_input = tk.Entry(cls.window, font=font, width=32)
        cls.process_delay_input.insert(0, "0.01")
        cls.process_delay_input.grid(row=10, column=1)

        cls.buffer_delay_label = tk.Label(cls.window, text="Buffer Delay (sec): ", anchor=tk.E, font=font, width=32, pady=3)
        cls.buffer_delay_label.grid(row=11, column=0)
        cls.buffer_delay_input = tk.Entry(cls.window, font=font, width=32)
        cls.buffer_delay_input.insert(0, "0.05")
        cls.buffer_delay_input.grid(row=11, column=1)

        # Blank
        cls.blank_label2 = tk.Label(cls.window, text=" ", anchor=tk.E, font=font)
        cls.blank_label2.grid(row=12, column=0)
        
        # Add a button for submitting the parameters
        cls.submit_button = tk.Button(cls.window, text="Submit", command=cls.submit, font=font)
        cls.submit_button.grid(row=13, column=0, columnspan=2)
        
        cls.window.mainloop()
        
    @classmethod
    def submit(cls):
        # Retrieve the parameter values from the input fields
        cls.off_nadir = math.radians(int(cls.off_nadir_input.get()))
        cls.package_size = int(cls.package_size_input.get())
        cls.data_rate = int(cls.data_rate_input.get())
        cls.signal_speed = int(cls.signal_speed_input.get())
        cls.process_delay = float(cls.process_delay_input.get())
        cls.buffer_delay = float(cls.buffer_delay_input.get())
        
        cls.inclination = math.radians(int(cls.inclination_input.get()))
        cls.argument_of_perigee = math.radians(int(cls.argument_of_perigee_input.get()))
        cls.motion = int(cls.motion_input.get())
        cls.orbit_size = int(cls.orbit_size_input.get())
        cls.sat_size = int(cls.sat_size_input.get())
        cls.window.destroy()