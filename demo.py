import time
import heapq

MAX_SLOTS = 100
MAX_USERS = 50

class MinHeap:
    def __init__(self):
        self.slots = []

    def insert_slot(self, slot):
        if len(self.slots) < MAX_SLOTS:
            heapq.heappush(self.slots, slot)

    def get_nearest_slot(self):
        return heapq.heappop(self.slots) if self.slots else -1

    def display_slots(self):
        if not self.slots:
            print("No available parking slots.")
        else:
            print("Available slots:", ' '.join(map(str, self.slots)))

    def is_slot_available(self, slot):
        return slot in self.slots

class User:
    def __init__(self, name, user_id):
        self.name = name
        self.id = user_id
        self.parked_slot = -1
        self.parked_time = None

def register_user(users):
    if len(users) >= MAX_USERS:
        print("User limit reached!")
        return
    name = input("Enter your name: ").strip()
    user_id = len(users) + 1
    users.append(User(name, user_id))
    print(f"User registered! Your ID is: {user_id}")

def find_user(users, user_id):
    for user in users:
        if user.id == user_id:
            return user
    return None

def park_vehicle(users, parking_lot):
    user_id = int(input("Enter your User ID: "))
    user = find_user(users, user_id)

    if not user or user.parked_slot != -1:
        print("Invalid operation.")
        return

    slot = parking_lot.get_nearest_slot()
    if slot == -1:
        print("No available slots!")
    else:
        user.parked_slot = slot
        user.parked_time = time.time()
        print(f"Park in slot: {slot}")

def remove_vehicle(users, parking_lot):
    user_id = int(input("Enter your User ID: "))
    user = find_user(users, user_id)

    if not user or user.parked_slot == -1:
        print("No vehicle found.")
        return

    duration = (time.time() - user.parked_time) / 60
    fee = duration * 2.0

    print(f"Parked for {duration:.2f} minutes. Fee: ${fee:.2f}")
    parking_lot.insert_slot(user.parked_slot)
    print(f"Slot {user.parked_slot} is now available.")

    user.parked_slot = -1
    user.parked_time = None

def check_slot_availability(parking_lot):
    slot = int(input("Enter slot number to check: "))
    if parking_lot.is_slot_available(slot):
        print(f"Slot {slot} is available.")
    else:
        print(f"Slot {slot} is occupied.")

def main():
    parking_lot = MinHeap()
    users = []

    total_slots = int(input("Enter total parking slots: "))
    print("Enter slot numbers:")
    for _ in range(total_slots):
        slot = int(input())
        parking_lot.insert_slot(slot)

    while True:
        print("\n1. Register User\n2. Park Vehicle\n3. Remove Vehicle\n4. Display Available Slots\n5. Check Slot Availability\n6. Exit")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            register_user(users)
        elif choice == 2:
            park_vehicle(users, parking_lot)
        elif choice == 3:
            remove_vehicle(users, parking_lot)
        elif choice == 4:
            parking_lot.display_slots()
        elif choice == 5:
            check_slot_availability(parking_lot)
        elif choice == 6:
            break
        else:
            print("Invalid choice! Try again.")

if __name__ == "__main__":
    main()
