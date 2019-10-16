# with is like your try .. finally block in this case
with open('vid/settings.py', 'r') as file:
    # read a list of lines into data
    data = file.readlines()

#print(data)
print("Your name: " + data[12])

# now change the 2nd line, note that you have to add a newline
data[12] = 'Magdddde\n'

# and write everything back
with open('vid/settings.py', 'w') as file:
    file.writelines( data )
	