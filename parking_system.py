import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta

class ParkingSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Parking System")
        self.geometry("300x200")

        # Initialize data structures
        self.parking_slots = [None] * 100  # Array to represent parking slots
        self.parking_rate = 2.5  # Per hour parking rate
        self.entry_times = [None] * 100  # Array to store entry times
        self.exit_times = [None] * 100  # Array to store exit times
        self.car_details = {}  # Dictionary to store car details

        self.entry_frame = None
        self.payment_frame = None
        self.login_frame = None

        self.user_password = "user123"  # Default user password
        self.admin_password = "admin123"  # Default admin password

        self.setup_login_panel()

    def setup_login_panel(self):
        self.login_frame = tk.Frame(self)
        self.login_frame.pack(pady=10)

        # Add heading
        heading_label = tk.Label(self.login_frame, text="Welcome to Parking System", font=("Helvetica", 16))
        heading_label.grid(row=0, column=0, columnspan=2, pady=10)
        heading_label = tk.Label(self.login_frame, text="Use Username:\tuser\nPassword:\tuser123", font=("Helvetica", 8))
        heading_label.grid(row=1, column=0, columnspan=2, pady=10)

        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=2, column=0, padx=15, pady=15, sticky="e")
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=2, column=1, padx=15, pady=15)

        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.grid(row=3, column=0, padx=15, pady=15, sticky="e")
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=3, column=1, padx=15, pady=15)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=4, columnspan=2, pady=10)


    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "user" and password == self.user_password:
            self.setup_user_panel()
            self.login_frame.destroy()
        elif username == "admin" and password == self.admin_password:
            self.setup_admin_panel()
            self.login_frame.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def setup_user_panel(self):
        self.entry_button = tk.Button(self, text="Entry", command=self.entry)
        self.entry_button.pack(pady=5)

    def setup_admin_panel(self):
        self.admin_button = tk.Button(self, text="Admin", command=self.admin)
        self.admin_button.pack(pady=5)

    def entry(self):
        if self.entry_frame is None:
            self.entry_frame = tk.Frame(self)
            self.entry_frame.pack(pady=10)

            self.car_number_label = tk.Label(self.entry_frame, text="Car Number:")
            self.car_number_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.car_number_entry = tk.Entry(self.entry_frame)
            self.car_number_entry.grid(row=0, column=1, padx=10, pady=5)

            self.park_button = tk.Button(self.entry_frame, text="Park", command=self.park)
            self.park_button.grid(row=1, column=1, pady=10)

    def park(self):
        car_number = self.car_number_entry.get()
        available_slot = self.find_available_slot()

        if available_slot != -1:
            self.parking_slots[available_slot] = car_number
            self.entry_times[available_slot] = datetime.now()
            self.car_details[car_number] = {'entry_time': self.entry_times[available_slot], 'slot': available_slot}
            self.write_to_file("Entry", car_number, available_slot)
            messagebox.showinfo("Parking Successful", f"Parked at slot {available_slot} at {self.entry_times[available_slot]}")
            self.setup_payment_frame(available_slot)
        else:
            messagebox.showinfo("Parking Full", "Sorry, all slots are filled.")

    def setup_payment_frame(self, slot):
        if self.payment_frame is None:
            self.payment_frame = tk.Frame(self)
            self.payment_frame.pack(pady=10)

            self.duration_label = tk.Label(self.payment_frame, text="Parking Duration (hours):")
            self.duration_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.duration_entry = tk.Entry(self.payment_frame)
            self.duration_entry.grid(row=0, column=1, padx=10, pady=5)

            self.pay_button = tk.Button(self.payment_frame, text="Pay", command=lambda: self.pay(slot))
            self.pay_button.grid(row=1, column=1, pady=10)

    def pay(self, slot):
        duration = float(self.duration_entry.get())
        total_cost = duration * self.parking_rate
        exit_time = self.entry_times[slot] + timedelta(hours=duration)
        self.exit_times[slot] = exit_time
        self.write_to_file("Exit", self.parking_slots[slot], slot)
        messagebox.showinfo("Payment Successful", f"Total Cost: ${total_cost}\nExit Time: {exit_time}")

        extend = messagebox.askyesno("Extend Parking Slot", "Do you want to extend the parking slot?")
        if extend:
            self.extend(slot)
        else:
            self.exit(slot)

    def extend(self, slot):
        duration_to_extend = simpledialog.askfloat("Extend Parking Slot", "Enter duration to extend (hours):")
        if duration_to_extend is not None:
            self.exit_times[slot] += timedelta(hours=duration_to_extend)
            self.write_to_file("Extend", self.parking_slots[slot], slot)
            messagebox.showinfo("Extension Successful", f"Parking slot extended by {duration_to_extend} hours.")
            self.exit(slot)

    def exit(self, slot):
        car_number = self.parking_slots[slot]
        entry_time = self.entry_times[slot]
        exit_time = self.exit_times[slot] if self.exit_times[slot] else datetime.now()
        parking_duration = exit_time - entry_time
        messagebox.showinfo("Exit", f"Thank you for using our parking service.\nCar Number: {car_number}\nSlot: {slot}\nEntry Time: {entry_time}\nExit Time: {exit_time}\nDuration: {parking_duration}")
        self.parking_slots[slot] = None
        self.entry_times[slot] = None
        self.exit_times[slot] = None
        self.entry_frame.destroy()
        self.payment_frame.destroy()
        self.entry_frame = None
        self.payment_frame = None

    def find_available_slot(self):
        for i, slot in enumerate(self.parking_slots):
            if slot is None:
                return i
        return -1

    def admin(self):
        admin_window = tk.Toplevel(self)
        admin_window.title("Admin Panel")
        admin_window.geometry("400x300")

        slots_label = tk.Label(admin_window, text="Parking Details:")
        slots_label.pack()

        slots_text = tk.Text(admin_window, height=25, width=100)
        slots_text.pack()

        slots_text.insert(tk.END, "\n")
        with open("parking_data.txt", "r") as file:
            for line in file:
                slots_text.insert(tk.END, line)


    def write_to_file(self, action, car_number, slot):
        with open("parking_data.txt", "a") as file:
            file.write(f"{action}: Car Number: {car_number} - Slot: {slot} - Time: {datetime.now()}\n")

if __name__ == "__main__":
    app = ParkingSystem()
    app.mainloop()



