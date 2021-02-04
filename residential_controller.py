#Defining the column class
class Column:
    def __init__(self, id, status, amount_of_elevators, amount_of_floors):
        self.ID = id
        self.status = status
        self.amount_of_elevators = amount_of_elevators
        self.amount_of_floors = amount_of_floors
        self.elevators_list = []
        self.call_buttons_list = []
        self.make_elevator(amount_of_elevators, amount_of_floors) #Calling the method to create elevators
        self.make_call_buttons(amount_of_floors) #Calling the method to create call buttons

    #Method to create elevators
    def make_elevator(self, amount_of_elevators, amount_of_floors):
        for elevator_id in range(amount_of_elevators):
            elevator = Elevator(elevator_id, 'idle', amount_of_floors, 1)
            self.elevators_list.append(elevator)

    def make_call_buttons(self, amount_of_floors):
        call_button_id = 1
        call_button_floor = 1
        for call_button_counter in range(amount_of_floors):
            #If not first floor
            if call_button_counter >= 1:
                call_button = CallButton(call_button_id, 'off', call_button_floor, 'down')
                self.call_buttons_list.append(call_button)
                call_button_id += 1
            #If not last floor
            if call_button_counter < amount_of_floors:
                call_button = CallButton(call_button_id, 'off', call_button_floor, 'up')
                self.call_buttons_list.append(call_button)
                call_button_id += 1
            call_button_floor += 1

    #User calls an elevator
    def request_elevator(self, floor, direction):
        print(f'A request for an elevator is made from floor {floor}, going {direction}.')
        elevator = self.find_best_elevator(floor, direction)
        print(f'Elevator {elevator.ID} is the best elevator, so it is sent.')
        elevator.floor_request_list.append(floor)
        elevator.sort_floor_list()
        print('Elevator is moving.')
        elevator.move_elevator()
        print(f'Elevator is {elevator.status}.')
        elevator.door_controller()
        return elevator
    
    #Find best elevator
    def find_best_elevator(self, floor, direction):
        requested_floor = floor
        requested_direction = direction
        best_elevator = None
        best_score = 5
        reference_gap = 1000000
        best_elevator_info = [best_elevator, best_score, reference_gap]

        for elevator in self.elevators_list:
            #Elevator is at floor going in correct direction
            if (requested_floor == elevator.current_floor and elevator.status == 'stopped' and requested_direction == elevator.direction):
                best_elevator_info = self.check_best_elevator(1, elevator, best_elevator_info, requested_floor)
            #Elevator is lower than user and moving through them to destination
            elif (requested_floor > elevator.current_floor and elevator.direction == 'up' and requested_direction == elevator.direction):
                best_elevator_info = self.check_best_elevator(2, elevator, best_elevator_info, requested_floor)
            #Elevator is higher than user and moving through them to destination
            elif (requested_floor < elevator.current_floor and elevator.direction == 'down' and requested_direction == elevator.direction):
                best_elevator_info = self.check_best_elevator(2, elevator, best_elevator_info, requested_floor)
            #Elevator is idle
            elif (elevator.status == 'idle'):
                best_elevator_info = self.check_best_elevator(3, elevator, best_elevator_info, requested_floor)
            #Elevator is last resort
            else:
                best_elevator_info = self.check_best_elevator(4, elevator, best_elevator_info, requested_floor)
        return best_elevator_info[0]
    
    #Comparing elevator to previous best
    def check_best_elevator(self, score_to_check, new_elevator, best_elevator_info, floor):
        #If elevators situation is more favourable, set to best elevator
        if (score_to_check < best_elevator_info[1]):
            best_elevator_info[1] = score_to_check
            best_elevator_info[0] = new_elevator
            best_elevator_info[2] = abs(new_elevator.current_floor - floor)
        elif (best_elevator_info[1] == score_to_check):
            gap = abs(new_elevator.current_floor - floor)
            if (best_elevator_info[2] > gap):
                best_elevator_info[1] = score_to_check
                best_elevator_info[0] = new_elevator
                best_elevator_info[2] = gap
        return best_elevator_info


#Defining the elevator class
class Elevator:
    def __init__(self, id, status, amount_of_floors, current_floor):
        self.ID = id
        self.status = status
        self.amount_of_floors = amount_of_floors
        self.current_floor = current_floor
        self.direction = None
        self.door = Door(id, 'closed')
        self.overweight = False
        self.obstruction = False
        self.floor_request_buttons_list = []
        self.floor_request_list = []
        self.make_floor_request_button(amount_of_floors) #Calling the method to create the floor request buttons

    def make_floor_request_button(self, amount_of_floors):
        floor_request_button_floor = 1
        for i in range(amount_of_floors):
            floor_request_button = FloorRequestButton(i, 'off', floor_request_button_floor)
            self.floor_request_buttons_list.append(floor_request_button)
            floor_request_button_floor += 1
        
    #User requesting floor inside elevator
    def request_floor(self, floor):
        print(f'The elevator is requested to move to floor {floor}.')
        self.floor_request_list.append(floor)
        self.sort_floor_list()
        print('Elevator is moving.')
        self.move_elevator()
        print(f'Elevator is {self.status}.')
        self.door_controller()
        if (len(self.floor_request_list) == 0):
            self.direction = None
            self.status = 'idle'
        print(f'Elevator is {self.status}.')

    #Moving elevator
    def move_elevator(self):
        while len(self.floor_request_list) != 0:
            destination = self.floor_request_list[0]
            self.status = 'moving'
            if self.current_floor < destination:
                self.direction = 'up'
                while self.current_floor < destination:
                    self.current_floor += 1
                    print(f'Elevator is at floor: {self.current_floor}')
            elif self.current_floor > destination:
                self.direction = 'down'
                while self.current_floor > destination:
                    self.current_floor -= 1
                    print(f'Elevator is at floor: {self.current_floor}')
            self.status = 'stopped'
            self.floor_request_list.pop()

    #Sorting floor request list
    def sort_floor_list(self):
        if self.direction == 'up':
            self.floor_request_list.sort()
        elif self.direction == 'down':
            self.floor_request_list.sort(reverse=True)

    #Door operation controller
    def door_controller(self):
        self.door = 'opened'
        print(f'Elevator doors are {self.door}.')
        print('Waiting for occupant(s) to transition.')
        #Wait 5 seconds
        if self.overweight is False:
            self.door = 'closing'
            if self.obstruction is False:
                self.door = 'closed'
                print(f'Elevator doors are {self.door}.')
            else:
                #Wait for obstruction to clear
                self.obstruction = False
                self.door_controller()
        else:
            while self.overweight is True:
                #Ring alarm and wait until not overweight
                self.overweight = False
            self.door_controller()

#Defining call button class
class CallButton:
    def __init__(self, id, status, floor, direction):
        self.ID = id
        self.status = status
        self.floor = floor
        self.direction = direction

#Defining floor request button class
class FloorRequestButton:
    def __init__(self, id, status, floor):
        self.ID = id
        self.status = status
        self.floor = floor

#Defining door class
class Door:
    def __init__(self, id, status):
        self.ID = id
        self.status = status

def scenario1():
    column = Column(1, 'online', 2, 10)

    column.elevators_list[0].current_floor = 2
    column.elevators_list[1].current_floor = 6

    elevator = column.request_elevator(3, 'up')
    elevator.request_floor(7)

def scenario2():
    column = Column(1, 'online', 2, 10)

    column.elevators_list[0].current_floor = 10
    column.elevators_list[1].current_floor = 3

    elevator = column.request_elevator(1, 'up')
    elevator.request_floor(6)

    print('')
    print('')

    elevator = column.request_elevator(3, 'up')
    elevator.request_floor(5)

    print('')
    print('')
    
    elevator = column.request_elevator(9, 'down')
    elevator.request_floor(2)

def scenario3():
    column = Column(1, 'online', 2, 10)

    column.elevators_list[0].current_floor = 10
    column.elevators_list[1].current_floor = 3
    column.elevators_list[1].status = 'moving'
    column.elevators_list[1].direction = 'up'

    elevator = column.request_elevator(3, 'down')
    elevator.request_floor(2)

    print('')
    print('')
    
    column.elevators_list[1].current_floor = 6
    column.elevators_list[1].status = 'idle'
    column.elevators_list[1].direction = None

    elevator = column.request_elevator(10, 'down')
    elevator.request_floor(3)  

#Uncomment to run scenario 1
#scenario1()

#Uncomment to run scenario 2
#scenario2()

#Uncomment to run scenario 3
#scenario3()