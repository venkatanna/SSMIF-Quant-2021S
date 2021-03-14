def divisible(s, x):
	"""
	Args:
	    s (str): the inputted string
	    x (int): non-negative integer (divisor)
	
	Returns:
	    list: all the unique numbers contained in the string that are divisible by x but do not include x 
	    within the number itself
	"""
	# Dividing by 0 is undefined, return an empty list
	if x < 1:
		return []

	# If the string is empty, return an empty list
	if not s:
		return []

	workingNumbers = []
	finalResult = []

	# Iterate through the characters in the string
	for character in s:
		# Check if the character is an integer
		if character.isnumeric():
			# If it is, make it an integer
			intCharacter = int(character)
			# Append all the possible number substrings to the working list
			for i in range(0, len(workingNumbers)):
				workingNumbers[i] = workingNumbers[i]*10 + intCharacter
			# Append the number itself 
			workingNumbers.append(intCharacter)
			# Call the helper function to filter through the list of numbers in the working list
			# Append the values (divisible by x but do not include x within the number itself) that are returned from the helper function to the final list
			finalResult = finalResult + divisibleHelper(workingNumbers, x)
		else:
			# Reset the working list when you see a non-numeric number when iterating through the string
			workingNumbers = []

	return list(set(finalResult))

def divisibleHelper(l, divisor):
	helper = []
	# Iterate through the list
	for i in l:
		# Check if the number is divisible by x and that it does not include x within itself
		if i%divisor == 0 and str(divisor) not in str(i):
			helper.append(i)
	return helper

print(divisible("tothemoon", 1))
print(divisible("a465839485739b102988c30jklol4", 7))
print(divisible("a1234567890ef", 5))
print(divisible("1782931", 1894792))
print(divisible("Jennychangeyournumber8675309", 0))
print(divisible("JS29104902fjkdalj91489282ss", 13))
print(divisible("13", 13))
print(divisible("a465839485739-102988c30jklol4", 7))
print(divisible("111211", 111))