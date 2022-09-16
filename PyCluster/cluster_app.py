from pathlib import Path 
#imports for gaia API
from astroquery.gaia import Gaia
from astropy.coordinates import SkyCoord
from astropy import units as u
#from matplotlib import use
import csv
import matplotlib
import numpy as np
import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image


#--------------------------------------#
#         Utility functions            #
#--------------------------------------#
def valid_path(filepath):
	'''
	Checks if the given path exists
	'''
	if filepath and Path(filepath).exists():
		return True
	sg.popup_error("Problem with the file(s) path(s)!")
	return False

def display_excel(filepath, sheet_name):
	'''
	Function that enables the inspection of the excel file created
	'''
	df = pd.read_excel(filepath, sheet_name)
	filename = Path(filepath).name
	sg.popup_scrolled(df, title=filename)

def display_csv(filepath):
	'''
	Function that enables the inspection of the excel file created
	'''
	df = pd.read_csv(filepath, header=None)
	filename = Path(filepath).name
	sg.popup_scrolled(df, title=filename)

def convert_to_csv(filepath, output_folder, sheet_name, decimal):
	'''
	Converts the given Excel file to .csv file
	'''
	df = pd.read_excel(filepath, sheet_name)
	filename = Path(filepath).stem
	outputfile = Path(output_folder) / f"{filename}.csv"
	df.to_csv(outputfile, decimal=decimal, index=False)
	sg.popup_no_titlebar('Completed')


def draw_plots(pymoviepath, platesolvepath, maxaperture):
	pymovie_data = pd.read_csv(pymoviepath)
	platesolve_data = pd.read_csv(platesolvepath, header=None)
	max_aperture = maxaperture
	# print(max_aperture)
	# LOAD THE SIGNAL COLUMNS TO ARRAYS
	signals_known = pymovie_data.iloc[:,2:max_aperture+2:2].values # use odds as known
	signals_unknown = pymovie_data.iloc[:,3:max_aperture+2:2].values # use even as unknown

	# LOAD THE MAGNITUDE DATA FROM THE MODIFIED CSV FILE
	mags_known = platesolve_data.iloc[0:max_aperture+1:2,0].values # use odds as known | last digit is the column
	mags_unknown = platesolve_data.iloc[1:max_aperture+1:2,0].values # use even as unknown | last digit is the column
	print(mags_known)
	print(mags_unknown)

	counts = np.round(np.sum(signals_known, axis=0)/15) # calculate the average signal of each known aperture
	counts2 = np.round(np.sum(signals_unknown, axis=0)/15) # calculate the average signal of each unknown aperture
	# print(counts.shape)
	# instrum_mag = -2.5 * np.log10(counts/(5*3600))
	# instrum_mag2 = -2.5 * np.log10(counts2/(5*3600))
	instrum_mag = -2.5 * np.log10(counts/2)
	instrum_mag2 = -2.5 * np.log10(counts2/2)
	# print(instrum_mag) ---
	P = np.polyfit(instrum_mag,mags_known,1)
	Yfit = np.polyval(P,instrum_mag)
	Ycal = np.polyval(P,instrum_mag2) # predicted Y
	res = Ycal - mags_unknown  # residual = observed value – predicted value
	rmse = np.sqrt(np.mean(res)**2)

	# print("instrumental magnitude of known")
	# print(instrum_mag)
	# print("instrumental magnitude of unknown")
	# print(instrum_mag2)
	# print("Yfit")
	# print(Yfit)
	# print("Ycal")
	# print(Ycal)
	# print("res")
	# print(res)
	# print("mags_unknown")
	# print(mags_unknown)


	# PLOTS
	# this plots the gaia magnitudes of half the stars we considered known and their instrumental magnitude as calculated by the code
	plt.figure('Calculated magnitudes - Instrumental magnitudes')
	plt.scatter(instrum_mag,mags_known)
	plt.plot(instrum_mag,Yfit,'r',label=np.poly1d(P))
	plt.xlabel('x - Instrumental magnitude')
	plt.ylabel('y - Calculated magnitude')
	plt.title('Calculated magnitudes - Instrumental magnitudes')
	plt.legend()

	plt.figure('fit diagram 2??? might not be needed')
	plt.scatter(instrum_mag,Yfit)
	plt.plot(instrum_mag,Yfit,'r',label=np.poly1d(P))
	plt.xlabel('x - instrum_mag')
	plt.ylabel('y - Yfit')
	plt.title('Plot instrum_mag as x and Yfit as y')
	plt.legend()

	plt.figure('Residuals')
	plt.axhline(y=0, color='r', linestyle='-')
	plt.title('Residuals - RMSE={}'.format(rmse))
	plt.scatter(instrum_mag2,res)


	plt.show()

def save_file(filepath, output_folder, rows):
	filename = Path(filepath).stem
	rows = np.array(rows)
	outputfile = Path(output_folder) / f"{filename}-edited.csv"
	# print(filename)
	# print(outputpath)
	sg.popup_no_titlebar('Completed')

def singleGaiaSearch(ra,dec):
	'''
	SEARCH FOR A MAGNITUDE USING A SINGLE SOURCE-STAR (RA, DEC)
	'''
	dfGaia = pd.DataFrame()
	coord = SkyCoord(ra=ra, dec=dec,unit=(u.hourangle, u.deg))
	# print(coord.ra.value)
	# print(coord)
	# qry = "SELECT TOP 2000 gaia_source.source_id,gaia_source.ra,gaia_source.dec,gaia_source.phot_g_mean_mag FROM gaiadr3.gaia_source WHERE CONTAINS(POINT('ICRS',gaiadr3.gaia_source.ra,gaiadr3.gaia_source.dec), CIRCLE('ICRS',268.38785,-34.75018055555555,0.0005555555555555556))=1  AND  (gaiadr3.gaia_source.phot_g_mean_mag<=15)"
	# job = Gaia.launch_job_async(qry, dump_to_file=True, output_format='csv')
	job = Gaia.launch_job_async("SELECT TOP 2000 gaia_source.source_id,gaia_source.ra,gaia_source.dec,gaia_source.phot_g_mean_mag "+
			"FROM gaiadr3.gaia_source WHERE CONTAINS(POINT('ICRS',gaiadr3.gaia_source.ra,gaiadr3.gaia_source.dec),"+
			"CIRCLE('ICRS',"+str(coord.ra.value)+','+str(coord.dec.value)+','+str(0.0005555555555555556)+"))=1"+
			"  AND  (gaiadr3.gaia_source.phot_g_mean_mag<=15)",dump_to_file=False, output_format='csv')

	tblGaia = job.get_results()
	# print(tblGaia['phot_g_mean_mag'])
	# print(tblGaia)
	dfGaia = tblGaia.to_pandas()
	array = dfGaia.to_numpy()
	# print(array.shape)

	# print('-----------------')
	# if len(array)>1:
	for i in array:
		value = round(i[3],2)
	return value

def GaiaFileSearch(filepath, output):
	'''
	USES A CSV FILE CONTAINING 2 COLUMNS (RA,DEC) AND SEARCHES FOR THE MAGNITUDES. RESULT IS SAVED IN A NEW CSV FILE.
	'''
	# filepath = 'C:/Users/PC-CP/Documents/Projects/Cluster application/Gaia_mags.csv'
	outputfile = Path(output) / "Gmags.csv"
	gaia_coord = pd.read_csv(filepath)
	RA = gaia_coord["RA"]
	Dec = gaia_coord["Dec"]
	radius = 0.0005555555555555556
	ra=np.zeros_like(RA)
	dec=np.zeros_like(RA)
	result=np.zeros_like(RA)
	dfGaia = pd.DataFrame(columns=['num','Gmag'])

	for i in range(len(RA)):
		c = SkyCoord(ra=RA[i], dec=Dec[i],unit=(u.hourangle, u.deg))
		ra[i] = c.ra.deg
		dec[i] = c.dec.deg
		job = Gaia.launch_job_async("SELECT TOP 2000 gaia_source.source_id,gaia_source.ra,gaia_source.dec,gaia_source.phot_g_mean_mag "+
			"FROM gaiadr3.gaia_source WHERE CONTAINS(POINT('ICRS',gaiadr3.gaia_source.ra,gaiadr3.gaia_source.dec),"+
			"CIRCLE('ICRS',"+str(ra[i])+','+str(dec[i])+','+str(0.0005555555555555556)+"))=1"+
			"  AND  (gaiadr3.gaia_source.phot_g_mean_mag<=15)",dump_to_file=False, output_format='csv')
		table = job.get_results()
		dfGaia = table.to_pandas()
		array = dfGaia.to_numpy()
		# result[i]=table['phot_g_mean_mag']
		result[i]=round(array[0,3],2)
		
	np.savetxt(outputfile,result,fmt='%1.2f')

	
#--------------------------------------#
#           Various Windows            #
#--------------------------------------#


# -------- GAIA API Window -------- #
def Gaia_window():

	layout_single_search = [	
							[sg.Text("Use this feature to search the magnitude of a single star.",font=('Arial',12,'bold'), justification="l")],
							[sg.Text("Enter the star's RA:", size=(15,None),justification="l"), sg.Input(s=15, key="-STAR-RA-",default_text='00:00:00.00'), sg.Text("Format: 00h00m00.00s")],
							[sg.Text("Enter the star's Dec:", size=(15,None), justification="l"), sg.Input(s=15, key="-STAR-DEC-",default_text='00:00:00.00'), sg.Text("Format: 00deg00m00.00s")],
							[sg.HSeparator()],
							[sg.Text("GAIA star magnitude:", size=(15,None), justification="l"), sg.Input(s=15, key="-STAR-RESULT-"), sg.Text("You can copy-paste this to your magnitude .csv file.",font=('Arial',12,'bold'),size=(40,None))],
							[sg.Button("Search",s=10),]
						]

	layout_multi_search = [	
							[sg.Text("Use this feature to search the magnitude of multiple stars using their coordinates RA & Dec (See instrucions for the format).",font=('Arial',12,'bold'), justification="l",size=(70,None))],
							[sg.Text("This step may take several minutes. Don't worry if the app becomes unresponsive.",font=('Arial',12,'bold'),text_color='red')],
							[sg.Text("Select coordinates csv file:",size=(20,None), justification="l"),sg.Input(key='-magin-'), sg.FileBrowse(file_types=("csv Files", "*.csv*"))],
							[sg.Text("Select destination:",size=(20,None),justification="l"),sg.Input(key='-magout-'), sg.FolderBrowse()],
							[sg.Button("Get magnitudes file")]
						]
	layout_gaia= [
				[sg.Frame('Single magnitude search',layout_single_search)],
				[sg.Frame('Multi magnitude search through a csv file',layout_multi_search)]

			]

	window_gaia = sg.Window('GAIA API', layout_gaia, modal=True)
	while True:
		event, values = window_gaia.read()
		if event == sg.WINDOW_CLOSED:
			break
		elif event== "Search":
			single_search = singleGaiaSearch(values["-STAR-RA-"], values["-STAR-DEC-"])
			window_gaia.Element("-STAR-RESULT-").update(single_search)
		elif event == "Get magnitudes file":
			GaiaFileSearch(filepath=values["-magin-"], output=values["-magout-"])


# -------- Settings Main Window -------- #
def settings_window(settings):
	# sg.popup_scrolled(settings, title="Settings Window")
	layout2 = [
			   [sg.Text("* !!!You MUST provide the number of apertures used in PyMovie or the program will crash!!!",font=('Arial',12,'bold'))],
			   [sg.Text("* Decimal input should NOT be changed for the current version of the program")],
			   [sg.Text("* You must restart the program in order for a new theme to take effect")],
			   [sg.HSeparator()],
			   [sg.Text("Excel's Sheet Name:", size=(19,None),justification='l'), sg.Input(settings["EXCEL"]["sheet_name"], s=10, key="-SHEET_NAME-")],
			   [sg.Text("Max apertures:", size=(19,None), justification='l'), sg.Input(settings["PYMOVIE"]["max_aperture"], s=3, key="-MAX_APERTURE-")],
			   [sg.Text("Decimal:", size=(19,None), justification='l'), sg.Input(settings["CSV"]["decimal"], s=2, key="-DECIMAL-")],
			   [sg.Text("Select Theme:", size=(19,None), justification="l"), sg.Combo(settings["GUI"]["theme"].split("/"), default_value=settings["GUI"]["default_theme"], key="-THEME-")],
			   [sg.Button("Save Settings", s=20, button_color="dark green")]
			  ] 
	window = sg.Window("Settings Window", layout2, modal=True, element_justification='l')
	while True:
		event, values = window.read()
		if event == sg.WINDOW_CLOSED:
			break
		if event == "Save Settings":
			settings["PYMOVIE"]["max_aperture"] = values["-MAX_APERTURE-"]
			settings["EXCEL"]["sheet_name"] = values["-SHEET_NAME-"]
			settings["GUI"]["default_theme"] = values["-THEME-"]

			sg.popup_no_titlebar("Settings Saved")
			break
	window.close()

# -------- About Window -------- #
def about_window():
	layout3 = [

		[sg.Text("Grivas Grigoris - 2022",font=('Arial',12,'bold'))],
		[sg.Text("For any questions e-mail me! -", font=('Arial',12,'bold')), sg.Input("grivas.grigoris@gmail.com", use_readonly_for_disable=True, disabled=True)],
		[sg.Text("Code available at:", font=('Arial',12,'bold')), 
		sg.Input("https://github.com/greggrivas/ClusterApp", use_readonly_for_disable=True, disabled=True,expand_x = True)]
	]
	window = sg.Window("About", layout3, modal=True, size=(550,110))
	while True:
		event, values = window.read()
		if event == sg.WINDOW_CLOSED:
			break
	window.close()

# -------- Editor Window -------- #
def editor(filepath, output_folder):
	filepath = filepath
	outpath = output_folder
	with open(filepath,encoding="utf-8") as file:
		# reader = csv.reader(file)
		reader = pd.read_csv(file,header=None)
		# rows = list(reader)

		
	menu_layout = [['File', ["Save File"]]]

	layout = [
			  [sg.MenubarCustom(menu_layout)],
			  [sg.Multiline(reader,font=('Arial', 10), size=(100,40) , key='-Editorline-', auto_refresh=True, horizontal_scroll=True)] #65 40
			 ]
	window = sg.Window('Editor', layout, margins=(0,0), resizable=True)

	while True:
		event, values = window.read()
		if event == sg.WINDOW_CLOSED:
			break
		elif event == "Save File":
			# testerino = values['-Editorline-']
			save_file(filepath=filepath, output_folder=outpath, rows=values["-Editorline-"])
	window.close()

# -------- Instructions Window -------- #
def instructions_window():
	filepath = Path.cwd()
	path = filepath/"instructions.txt"
	with open(path,mode='rt',encoding="utf-8") as file:
		instructions = file.read()
	
	layout = [
			  [sg.Multiline(default_text=instructions,size=(100,40),auto_size_text=False,disabled=True,font=('Consolas', 12),background_color='#bdc1c7')]
			 ]
	window_instructions = sg.Window('Instructions', layout, margins=(0,0), resizable=True)
	while True:
		event, values = window_instructions.read()
		if event == sg.WINDOW_CLOSED:
			break

	window_instructions.close()

# --------Application Main Window-------- #
def mainwindow():

	# menu = [["About"]]
	layout_1 = [
		      # [sg.Menubar(menu, tearoff=True)],
		      [sg.Text("Feature to easily convert an Excel file to csv (e.g. for GAIA magnitudes to use below)",size=(93,None), font=('Arial',12,'bold'))],
			  [sg.Push(), sg.Text("Select Excel File:"), sg.Input(key = "-INPUT-"), sg.FileBrowse(file_types=(("Excel Files", "*.xls*"),))],
			  [sg.Push(), sg.Text("Output Directory:"), sg.Input(key = "-OUTPUT-"), sg.FolderBrowse()],
			  [sg.Push(),sg.Button("Show Excel"),sg.Button("Convert to .csv")]
			  ]
			  # [sg.HSeparator()],
			  # [sg.Text("Load the two csv files here to get the plots", font=('Consolas',12,'bold'))],
			  # [sg.Push(), sg.Text("Select PyMovie csv"), sg.Input(key = "-Pcsv-"), sg.FileBrowse(file_types=(("csv Files", "*.csv*"),))],
			  # [sg.Push(), sg.Text("Select PlateSolve3 csv"), sg.Input(key = "-PScsv-"), sg.FileBrowse(file_types=(("csv Files", "*.csv*"),))],
			  # [sg.HSeparator()],
			  # [sg.Text("**You MUST visit the settings tab below and enter a max_apertures value as used in PyMovie before ploting the data**",
			  #  text_color="red2", size=(70,None), font=('Consolas',14,'bold'))],
			  # [sg.Exit(button_color="dark red"), sg.Button("About", button_color='orange red'), sg.Push(), sg.Button("Settings"), 
			  # sg.Button("Show Excel"), 
			  # sg.Button("Convert to .csv"), sg.Button("Plot")]

	layout_2 = [
				# [sg.Text("Select file to edit:"), sg.Input(key="-EDIT-", size=(60,None)), sg.FileBrowse(file_types=(("csv Files", "*.csv*"),)), sg.Button("Edit")]
				[sg.Text("This feature can be used to edit the csv file produced by PyMovie to remove the comments (editing does not work yet)",size=(93,None),font=('Arial',12,'bold'))],
				[sg.Push(),sg.Text("Select file to edit:"), sg.Input(key="-CSVtoEdit-", size=(50,None)), sg.FileBrowse(file_types=(("csv Files", "*.csv*"),))],
				[sg.Push(), sg.Text("Output Directory:"), sg.Input(key="-CSVtoSave-", size=(50,None)), sg.FolderBrowse()],
				[sg.Button("Editor (only for inspection)", size=(20,None))]
			   ]
			   

	layout_3 = [
				[sg.Text("Load the two csv files here to get the plots:", font=('Aral',12,'bold'))],
			    [sg.Push(), sg.Text("Select PyMovie csv | (counts)"), sg.Input(key="-Pcsv-"), sg.FileBrowse(file_types=(("csv Files", "*.csv*"),)),sg.Button("Inspect", key='-inspect1-')],
			    [sg.Push(), sg.Text("Select Gaia-mags.csv file | (magnitudes)"), sg.Input(key="-PScsv-"), sg.FileBrowse(file_types=(("csv Files", "*.csv*"),)),sg.Button("Inspect",key='-inspect2-')],
				[sg.Push(),sg.Button("Plot", s=14)],
				[sg.Text("!!You MUST visit the settings tab and enter a max_apertures value as used in PyMovie before plotting the data!!",
			   text_color="orange2", size=(77,None), font=('Arial',14,'bold'), justification='c')]

			   ]


	layout_csv_instr = [
						[sg.Text("Click the button to read the instructions for the Cluster exercise.",font=('Arial',12,'bold')),sg.Push(),sg.Button("Instructions",size=(15,1),font=('Arial',14,'bold'),button_color='orange red')]
# 						[sg.Text('''In order for the analysis below to work you must edit the .csv file provided by PyMovie and erase the comment lines it includes.
# To do this open the PyMovie .csv file in an empty Excel Sheet. Then delete all the lines from Column A that contain a # sumbol and 
# only keep the table containing the data (First column's name is FrameNum). Then save the new csv file and load it to the analysis below.''', 
							# font=('Arial',11,'bold'), size=(103,None))],
					   ]
	layout_gaia = [
					[sg.Text('''This is the GAIA API used to acquire the stars' magnitudes using the RA and Dec the from the .csv file PlateSolve3 provides. Enter the respective RA and Dec and then replace the UC4 magnitude with the one provided by the GAIA API. Multiple star search with a coordinate csv file is also supported''',
						font=('Arial',11,'bold'), size=(103,None))],
					[sg.Button('Gaia API',s=10,font=('Arial',13,'bold'))]
				  ]				   


	layout = [
				[sg.Frame('Convertion', layout_1)],
				[sg.Frame('Edit File (Use only to inspect content)',layout_2, element_justification='c')],
				[sg.Frame('Instructions', layout_csv_instr,size=(945,70))],
				[sg.Frame('GAIA API', layout_gaia, element_justification='c')],
				[sg.Frame('Plotting',layout_3,size=(945,205))],
				[sg.Push(), sg.Button("Settings",s=15), sg.Button("About", button_color='orange red', s=7), sg.Exit(button_color="dark red", s=7)]
			  	]


	window_title = settings["GUI"]["title"]
	window = sg.Window(window_title, layout, finalize=True)

	while True:
		event, values = window.read()
		if event in (sg.WINDOW_CLOSED, "Exit"):
			break
		elif event == "Show Excel":
			if valid_path(values["-INPUT-"]):
				display_excel(filepath=values["-INPUT-"], sheet_name=settings["EXCEL"]["sheet_name"])
		elif event == "Settings":
			settings_window(settings)
		elif event == "About":
			about_window()
		elif event == "Convert to .csv":
			if (valid_path(values["-INPUT-"])) and valid_path(values["-OUTPUT-"]):
				convert_to_csv(filepath=values["-INPUT-"], output_folder=values["-OUTPUT-"], sheet_name=settings["EXCEL"]["sheet_name"], decimal=settings["CSV"]["decimal"])
		elif event == "Editor (only for inspection)":
			if (valid_path(values["-CSVtoEdit-"])) and valid_path(values["-CSVtoSave-"]):
				editor(filepath=values["-CSVtoEdit-"], output_folder=values["-CSVtoSave-"])
		elif event == "Plot":
			#to add valid path method here
			if (valid_path(values["-Pcsv-"])) and valid_path(values["-PScsv-"]):
				draw_plots(pymoviepath=values["-Pcsv-"], platesolvepath=values["-PScsv-"], maxaperture=int(settings["PYMOVIE"]["max_aperture"]))
		elif event == "-inspect1-":
			if (valid_path(values["-Pcsv-"])):
				display_csv(filepath=values["-Pcsv-"])
		elif event == "-inspect2-":
			if (valid_path(values["-PScsv-"])):
				display_csv(filepath=values["-PScsv-"])
		elif event == "Gaia API":
			Gaia_window()
		elif event == 'Instructions':
			instructions_window()
			
	window.close()

if __name__ == "__main__":
	settings_path = Path.cwd() # Take the current directory as the settings file path
	settings = sg.UserSettings(path=settings_path, filename="settings.ini", use_config_file=True, convert_bools_and_none=True) # Create the settings object
	theme = settings["GUI"]["default_theme"]
	font_family = settings["GUI"]["font_family"]
	font_size = settings["GUI"]["font_size"]
	sg.theme(theme)
	sg.set_options(font=(font_family, int(font_size)))
	mainwindow()