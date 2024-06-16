"""
calculator.py
-------------
For selecting calculator operations:
1. Calculate
2. Use previous result
3. Reset
4. Change Mode (float or fixed)
5. Exit
Calculate operations number:
(1) addition
(2) subtraction
(3) multiplication
(4) division
---------
"""
import struct

""" /* struct template in C */
#pragma pack(push, 1) // Preserve current packing settings and set packing to 1 byte
struct calculator_task {		// Define a structure for calculator tasks
	uint8_t operation;			// Operation to be performed (e.g., add, subtract)
	union {						// Union for 1 argument, allowing either float or fixed-point integer.
		float f_operand_1;		// 32-bit floating-point operand
        int32_t q31_operand_1;	// Fixed-point (Q31) operand
	};
	union {						// Union for 2 argument, allowing either float or fixed-point integer.
		float f_operand_2;		// 32-bit floating-point operand
		int32_t q31_operand_2;	// Fixed-point (Q31) operand
	};
	bool mode;					// Mode: floating-point (0) or fixed-point (1)
};
#pragma pack(pop) // Restore original packing
"""

FLOAT_MODE = 0
FIXED_MODE = 1

epsilon = 1e-10  # Division by zero

class Calculator:
    def __init__(self):
        self.mode = FLOAT_MODE  # Default FLOAT_MODE
        self.result = 0
        self.use_previous_result = False  # Flag to use previous result  in calculations
        self.reset()

    def reset(self):
        self.num1 = 0
        self.num2 = 0
        self.operation = 0
        self.use_previous_result = False 

    def change_mode(self):
        if self.mode == FIXED_MODE:
            self.mode = FLOAT_MODE
        elif self.mode == FLOAT_MODE:
            self.mode = FIXED_MODE
        else:
            print("Invalid mode. Mode unchanged.")      
        
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
       
    def get_number(self, prompt):
        while True:
            try:
                if self.use_previous_result:
                    self.use_previous_result = False
                    if self.result >= 1.0 or self.result < -1.0:
                        print("Out of range. Please enter a valid number in range <-1, 1)")
                        continue
                    return self.result
                else:  # Calculate mode
                    if self.mode == FLOAT_MODE:
                        return float(input(prompt))
                    elif self.mode == FIXED_MODE:
                        prompt = float(input(prompt))
                        if prompt >= 1.0 or prompt < -1.0:
                            print("Out of range. Please enter a valid number in range <-1, 1)")
                            prompt = ''
                            continue
                        return prompt
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                
    def float_to_q31(self, value):
            """
            Convert a floating-point number to Q31 fixed-point format. Q31 format represents numbers as a 32-bit signed integer.
            """
            return int(value * (1 << 31))

    def run_calculator(self):
        """Main loop to run the calculator"""
        print("\nChoose operation in mode: ----------------------------")
        if self.mode == FLOAT_MODE:
            print("--> FLOAT <--")
        elif self.mode == FIXED_MODE:
            print("--> FIXED <--")
            
        print("1. Calculate")
        print("2. Use previous result =", self.result)
        print("3. Reset")
        print("4. Change Mode (float or fixed)")
        print("5. Exit")
        print("----------------------------")
        choice = input("Enter your choice: ")
        print("----------------------------")
        
        if choice == '1':  # Calculate
            self.num1 = self.get_number("Enter first number: ")
            self.operate()
            self.num2 = self.get_number("Enter second number: ")
        elif choice == '2':  # Use previous result
            self.use_previous_result = True
            print("Using previous result: ", self.result)
            self.num1 = self.get_number("First number: ")
            self.operate()
            self.num2 = self.get_number("Enter second number: ")
        elif choice == '3':  # Reset
            self.reset()
        elif choice == '4':  # Change Mode
            print("The mode has been changed!")
            self.change_mode()
            return 'go_again'
        elif choice == '5':  # Exit
            print("Exiting calculator. Goodbye!")
            return 'goodbye'
        else:
            print("Invalid choice. Please choose a valid option.")
            return 'go_again'
            
        if self.operation == 4 and abs(self.num2) < epsilon:  # Perform division check operation.
            print("Error: Division by zero. Please choose a valid operation.")
            return 'go_again'
        
        # Parsing data
        if self.mode == FLOAT_MODE:
            data = struct.pack('<BffB', self.operation, self.num1, self.num2, self.mode)  # Convert the values to a byte array
        elif self.mode == FIXED_MODE:
            q31_num1 = self.float_to_q31(self.num1)
            q31_num2 = self.float_to_q31(self.num2)
            data = struct.pack('<BiiB', self.operation, q31_num1, q31_num2, self.mode)  # Convert the values to a byte array
        
        return data
        """ '<BiiB' or '<BffB'
        This is the data format which tells the pack function how to pack the values:
        <: packed in little-endian order (the least significant byte is first).
        B: first value (operation) will be represented as a single byte.
        i: value (q31_operand) will be represented as a 32-bit unsigned integer.
        f: value will be represented as a 32-bit floating-point number.
        B: last value (mode) will be represented as a single byte.
        """
        

# Guard condition to check if the module is being run directly
if __name__ == "__main__":
    print("** testing TUI: calculator.py **")
    calc = Calculator()
    data = calc.run_calculator()