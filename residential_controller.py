#Defining the column class
class Column:
    def __init__(self, id, status, amountOfElevators, amountOfFloors):
        self.ID = id
        self.status = status
        self.amountOfElevators = amountOfElevators
        self.amountOfFloors = amountOfFloors
        self.elevatorsList = []
        self.callButtonsList = []
        
        self.makeElevator(amountOfElevators, amountOfFloors) #Calling the method to create elevators
        self.makeCallButtons(amountOfFloors) #Calling the method to create call buttons

    #Method to create elevators
    def makeElevator(self, amountOfElevators, amountOfFloors):
        elevatorID = 1
        for i in range(amountOfElevators):
            elevator = Elevator(elevatorID, 'idle', amountOfFloors, 1)
            self.elevatorsList.append(elevator)
            elevatorID += 1

    #Method to create call buttons
    def makeCallButtons(self, amountOfFloors):
        callButtonId = 1
        callButtonFloor = 1
        for callButtonCounter in range(amountOfFloors):
            #If not first floor
            if callButtonCounter >= 1:
                callButton = CallButton(callButtonId, 'off', callButtonFloor, 'down')
                self.callButtonsList.append(callButton)
                callButtonId += 1
            #If not last floor
            if callButtonCounter < amountOfFloors:
                callButton = CallButton(callButtonId, 'off', callButtonFloor, 'up')
                self.callButtonsList.append(callButton)
                callButtonId += 1
            callButtonFloor += 1

    #User calls an elevator
    def requestElevator(self, floor, direction):
        print(f'A request for an elevator is made from floor {floor}, going {direction}.')
        elevator = self.findBestElevator(floor, direction)
        print(f'Elevator {elevator.ID} is the best elevator, so it is sent.')
        elevator.floorRequestList.append(floor)
        elevator.sortFloorList()
        print('Elevator is moving.')
        elevator.moveElevator()
        print(f'Elevator is {elevator.status}.')
        elevator.doorController()
        return elevator
    
    #Find best elevator
    def findBestElevator(self, floor, direction):
        requestedFloor = floor
        requestedDirection = direction
        bestElevator = None
        bestScore = 5
        referenceGap = 1000000
        bestElevatorInfo = [bestElevator, bestScore, referenceGap]

        for elevator in self.elevatorsList:
            #Elevator is at floor going in correct direction
            if requestedFloor == elevator.currentFloor and elevator.status == 'stopped' and requestedDirection == elevator.direction:
                bestElevatorInfo = self.checkBestElevator(1, elevator, bestElevatorInfo, requestedFloor)
            #Elevator is lower than user and moving through them to destination
            elif requestedFloor > elevator.currentFloor and elevator.direction == 'up' and requestedDirection == elevator.direction:
                bestElevatorInfo = self.checkBestElevator(2, elevator, bestElevatorInfo, requestedFloor)
            #Elevator is higher than user and moving through them to destination
            elif requestedFloor < elevator.currentFloor and elevator.direction == 'down' and requestedDirection == elevator.direction:
                bestElevatorInfo = self.checkBestElevator(2, elevator, bestElevatorInfo, requestedFloor)
            #Elevator is idle
            elif elevator.status == 'idle':
                bestElevatorInfo = self.checkBestElevator(3, elevator, bestElevatorInfo, requestedFloor)
            #Elevator is last resort
            else:
                bestElevatorInfo = self.checkBestElevator(4, elevator, bestElevatorInfo, requestedFloor)
        return bestElevatorInfo[0]
    
    #Comparing elevator to previous best
    def checkBestElevator(self, scoreToCheck, newElevator, bestElevatorInfo, floor):
        #If elevators situation is more favourable, set to best elevator
        if scoreToCheck < bestElevatorInfo[1]:
            bestElevatorInfo[1] = scoreToCheck
            bestElevatorInfo[0] = newElevator
            bestElevatorInfo[2] = abs(newElevator.currentFloor - floor)
        #If elevators are in a similar situation, set the closest one to the best elevator
        elif (bestElevatorInfo[1] == scoreToCheck):
            gap = abs(newElevator.currentFloor - floor)
            if bestElevatorInfo[2] > gap:
                bestElevatorInfo[1] = scoreToCheck
                bestElevatorInfo[0] = newElevator
                bestElevatorInfo[2] = gap
        return bestElevatorInfo


#Defining the elevator class
class Elevator:
    def __init__(self, id, status, amountOfFloors, currentFloor):
        self.ID = id
        self.status = status
        self.amountOfFloors = amountOfFloors
        self.currentFloor = currentFloor
        self.direction = None
        self.door = Door(id, 'closed')
        self.overweight = False
        self.obstruction = False
        self.floorRequestButtonsList = []
        self.floorRequestList = []
        self.makeFloorRequestButton(amountOfFloors) #Calling the method to create the floor request buttons

    #Method to create floor request buttons
    def makeFloorRequestButton(self, amountOfFloors):
        floorRequestButtonFloor = 1
        for i in range(amountOfFloors):
            floorRequestButton = FloorRequestButton(i, 'off', floorRequestButtonFloor)
            self.floorRequestButtonsList.append(floorRequestButton)
            floorRequestButtonFloor += 1
        
    #User requesting floor inside elevator
    def requestFloor(self, floor):
        print(f'The elevator is requested to move to floor {floor}.')
        self.floorRequestList.append(floor)
        self.sortFloorList()
        print('Elevator is moving.')
        self.moveElevator()
        print(f'Elevator is {self.status}.')
        self.doorController()
        if len(self.floorRequestList) == 0:
            self.direction = None
            self.status = 'idle'
        print(f'Elevator is {self.status}.')

    #Moving elevator
    def moveElevator(self):
        while len(self.floorRequestList) != 0:
            destination = self.floorRequestList[0]
            self.status = 'moving'
            if self.currentFloor < destination:
                self.direction = 'up'
                while self.currentFloor < destination:
                    self.currentFloor += 1
                    print(f'Elevator is at floor: {self.currentFloor}')
            elif self.currentFloor > destination:
                self.direction = 'down'
                while self.currentFloor > destination:
                    self.currentFloor -= 1
                    print(f'Elevator is at floor: {self.currentFloor}')
            self.status = 'stopped'
            self.floorRequestList.pop()

    #Sorting floor request list
    def sortFloorList(self):
        if self.direction == 'up':
            self.floorRequestList.sort()
        elif self.direction == 'down':
            self.floorRequestList.sort(reverse=True)

    #Door operation controller
    def doorController(self):
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
                self.doorController()
        else:
            while self.overweight is True:
                #Ring alarm and wait until not overweight
                self.overweight = False
            self.doorController()

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

#Defining scenario 1
def scenario1():
    #In scenario 1, an individual is on floor 3, going up to floor 7.
    #Elevator 1 is at floor 2, and Elevator 2 is at floor 6.
    #Elevator 1 will be sent.
    column = Column(1, 'online', 2, 10)

    column.elevatorsList[0].currentFloor = 2
    column.elevatorsList[1].currentFloor = 6

    elevator = column.requestElevator(3, 'up')
    elevator.requestFloor(7)

#Defining scenario 2
def scenario2():
    #In scenario 2, an individual is on floor 1, going up to floor 6.
    #Elevator 1 is at floor 10, and Elevator 2 is at floor 3.
    #Elevator 2 will be sent.
    #An individial is on floor 3, going up to floor 5.
    #Elevator 1 is at floor 10, and Elevator 2 is at floor 6.
    #Elevator 2 will be sent.
    #An individial is on floor 9, going down to floor 2.
    #Elevator 1 is at floor 10, and Elevator 2 is at floor 5.
    #Elevator 1 will be sent.
    column = Column(1, 'online', 2, 10)

    column.elevatorsList[0].currentFloor = 10
    column.elevatorsList[1].currentFloor = 3

    elevator = column.requestElevator(1, 'up')
    elevator.requestFloor(6)

    print('')
    print('')

    elevator = column.requestElevator(3, 'up')
    elevator.requestFloor(5)

    print('')
    print('')
    
    elevator = column.requestElevator(9, 'down')
    elevator.requestFloor(2)

#Defining scenario 3
def scenario3():
    #In scenario 2, an individual is on floor 3, going down to floor 2.
    #Elevator 1 is at floor 10, and Elevator 2 is moving from floor 3 to 6.
    #Elevator 1 will be sent.
    #An individial is on floor 10, going down to floor 3.
    #Elevator 1 is at floor 10, and Elevator 2 is at floor 6.
    #Elevator 2 will be sent.
    column = Column(1, 'online', 2, 10)

    column.elevatorsList[0].currentFloor = 10
    column.elevatorsList[1].currentFloor = 3
    column.elevatorsList[1].status = 'moving'
    column.elevatorsList[1].direction = 'up'

    elevator = column.requestElevator(3, 'down')
    elevator.requestFloor(2)

    print('')
    print('')
    
    column.elevatorsList[1].currentFloor = 6
    column.elevatorsList[1].status = 'idle'
    column.elevatorsList[1].direction = None

    elevator = column.requestElevator(10, 'down')
    elevator.requestFloor(3)  

#Uncomment to run scenario 1
#scenario1()

#Uncomment to run scenario 2
#scenario2()

#Uncomment to run scenario 3
#scenario3()