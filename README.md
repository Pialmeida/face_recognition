# face_recognition

### ORGANIZATION:
##audio
- Saves audio files for reproduction
	- Confirmation sound
	- Rejection sound

##Data
- Temporary place to store database
- Will eventually be relocated to designated place in cloud

##known_people
- Temporary place to store registered faces
- Automatically created by managementUI.py
- Number of underlines show if email is wanted or not
	- 1 Underline separating name and number means no
	- 2 underline separating  name and number means yes
- Will eventually be relocated to designated place in cloud

##mylib
#camera.py
- Class with all recognition features in the program
- Main method to recognize faces in still frame
- Can check if pictures during registration are valid

#data.py
- Class to manage modification of database
- Contains all methods in relation to retrieving and storing data

#extendedCombo.py
- Class with extended Combo Box Model for PyQt5 Window
- Differes my showing auto-complete options during writing

#table.py
- Contains two definitions for table and table models widget for PyQt5 Windows
	- Table and MyTable are for recent log in main window where no editing is allowed
	- ModifyTable and ModifyMyTable are for editing entries where editing is allowed

#thread.py
- Contains definition for Thread Elements for Webcam reading
	- Creates and automanages thread to read webcam data and store in Queue

##Report
- Contains all generated reports by main window
- Auto named by date of creation and date of containing data

##UI_elements
#modifyWindow.py
- PyQt5 Class for window to edit database
	- Allows variety of filter options
	-  Auto checks if data modification is valid

#nameDeregistration.py
- PyQt5 Class for window to deregister names from known_people
	- Auto deletes pictures of unregistered individuals
	- Requires confirmation before deletion.

#nameRegistration.py
- PyQt5 Class for window to register names to known_people
	- Auto labels pictures once complete
	- Can distinguish naming based on choice of emails vs. no emails

#registerWindow.py
- PyQt5 Class for window to take pictures of new registers
	- Creates nameRegistration once specified number of images have been taken
	- Provide some outline as to where faces should be on frame

#threadUI.py
- PyQt5 Class to display webcam readings to RaspberryUI.py in realtime
- Can enable/disable recognition for faster readings
- Prompts database modification if recognized

##config.json
- Contains all relevant configurations used in library
- Used to customize different UI and data management configurations without searching python scripts

##logoAKAER.jpg
- Logo of AKAER for display in UI

##managementUI.py
- Contains all UI elements for main Management Window belonging to "RH"
- Detailed methods all with descriptions

##raspberryUI.py
- Contains all UI elements for raspberry Pi located around AKAER
- Recognizes and records entries in database
- Can rollback previous entry if mis-recognized
- Interfaces with sensor components

##recognise_face.py
- Sample model of all face_recognition module usage

##requirements.txt
- Contains all required modules for use

##test.py
- Python script for testing features prior to implementation
- Contains sample code usage for external sensors

##__pychache__ & LICENSE & .gitignore
- Standard features of github repos.


### TO DO:
- Create Raspberry Pi front-end UI
	- ~~Add camera thread to UI~~
	- ~~Add background data management~~
		- ~~Add SQL management of database~~
		- ~~Add path locations to *config.json*~~
	- ~~Add rollback feature for misidentification~~
	- ~~Add sidebar display with user details once recognized~~
	- ~~Add prevention to double registers of the same name~~
	- ~~Add calculation of hours worked at end of the day~~
	- ~~Add sound effects for confirmation of entries~~
	- ~~Add sensor to replace clickable button~~
	- ~~Add multi-entry system compatibility~~
	- Add auto-sender for individuals missing entries
		- ~~Add recognition for users missing entries~~
		- Add auto-sender for recognized users
	- Add ability to register night-time shifts

- Create front-end UI for Computer Access
	- Add registering functionality
		- ~~Add mechanism to prevent repetition~~
		- ~~Add deletion of pictures if operation is closed~~
		- ~~Add confirmation of model acceptance of pictures~~
		- Add confirmation of names in database
	- ~~Add removal functionality~~
		- ~~Add lookup of user~~
		- ~~Add prevention of invalid name~~
	- ~~Add auto-updating log of entry~~
		- ~~Add data update~~
		- ~~Add to excel button~~
		- ~~Add generate report button~~
			- Add overtime feature (Horas Extras)
			- Add overtime on holidays (Horas Extras Diferenciado 100%)
			- Add column with late days
			- Add classification of night-time shift
	- ~~Add filter mechanism for data lookup~~
		- ~~Add name filter~~
		- ~~Add date filter~~
			- ~~Add check for valid date range~~
		- ~~Add status filter~~
		- ~~Add filter for hours worked~~
	- ~~Add data modifying functionality~~
		- ~~Add entry modification~~
		- ~~Add deletion of rows~~
		- Add change to overtime functionality
			- Allow change to "Horas Extras"
			- Allow change to "Horas Extras Diferenciado 100%"
	- Add automatic classification of late entries
		- Add differentiation between late entries and different shifts


Extras Horas 
Horas Extras Diferenciado 100%
Atrasos
Adicional Noturno
