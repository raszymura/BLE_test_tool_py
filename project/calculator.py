"""
Calculator
-------------
For selectiong calculator operations. Operations number:
(1)addition
(2)subtraction
(3)multiplication
(4)division
(5)equals
---------
(0)reset
()change_mode
exit
"""
import struct

""" /* struct template in C */
#pragma pack(push, 1) // Preserve current packing settings and set packing to 1 byte
struct calculator_task {		// Define a structure for calculator tasks
    uint8_t operation;			// Operation to be performed (e.g., add, subtract)
    union {						// Union for operands, allowing either float or fixed-point integer.
        loat f_operand;		// 32-bit floating-point operand
        int32_t q31_operand;	// Fixed-point (Q31) operand
    };
    bool mode;				    // Mode: floating-point (0) or fixed-point (1)
};
#pragma pack(pop) // Restore original packing settings after defining the structure
"""

FLOAT_MODE = 0
FIXED_MODE = 1

class Calculator:
    def __init__(self):
        self.mode = FIXED_MODE
        self.result = 0
        self.reset()

    def reset(self):
        self.operation = 0

    def change_mode(self, mode):
        if mode == 'float':
            self.mode = FLOAT_MODE
        elif mode == 'Q31':
            self.mode = FIXED_MODE
        else:
            print("Invalid mode. Mode unchanged.")

    # def division(self, num):
    #     """
    #     Perform division check operation.
    #     """
    #     if num == 0:
    #         print("Error: Division by zero")

    def operate(self):
        """
        Perform the specified operation on the current result and given number.
        """
        valid_operations = {'+': 1, '-': 2, '*': 3, '/': 4}
        while True:
            operation = input("Enter operation (+, -, *, / ): ")
            if operation in valid_operations:
                self.operation = valid_operations[operation]
                break
            else:
                print("Invalid operation. Try again")


    def run_calculator(self):
        """Main loop to run the calculator"""
        print("\nCurrent result:", self.result)
        print("Choose operation:")
        print("1. Calculate")
        print("2. Reset")
        print("3. Change Mode (float or int)")
        print("4. Exit")
        print("----------------------------")
        choice = input("Enter your choice: ")
        print("----------------------------")
        
        if choice == '1':
            num1 = self.get_number("Enter first number: ")
            # num2 = self.get_number("Enter second number: ")
            self.operate()
            # self.operate(operation2, num2) 
        elif choice == '2':
            self.reset()
        elif choice == '3':
            mode = input("Enter mode ('float' or 'Q31'): ")
            self.change_mode(mode)
            data = 'mode'
            return data
        elif choice == '4':
            print("Exiting calculator. Goodbye!")
            data = 'goodbye'
            return data
        else:
            print("Invalid choice. Please choose a valid option.")
        
        
        # Parsing data
        if self.mode == FLOAT_MODE:
            data = struct.pack('<BfB', self.operation, num1, self.mode)  # Convert the values to a byte array
        elif self.mode == FIXED_MODE:
            data = struct.pack('<BiB', self.operation, num1, self.mode)  # Convert the values to a byte array
        
        return data
        """ '<BIB' or '<BfB'
            This is the data format which tells the pack function how to pack the values:
            <: packed in little-endian order (the least significant byte is first).
            B: first value (operation) will be represented as a single byte.
            i: second value (q31_operand) will be represented as a 32-bit unsigned integer.
            f: second value will be represented as a 32-bit floating-point number.
            B: last value (mode) will be represented as a single byte.
        """
                
                
    def get_number(self, prompt):
        while True:
            try:
                if self.mode == FLOAT_MODE:
                    return float(input(prompt))
                elif self.mode == FIXED_MODE:
                    return int(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                