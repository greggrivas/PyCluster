from astroquery.gaia import Gaia
from astropy import units as u
from astropy.coordinates import SkyCoord

import pandas as pd
import numpy as np

def one(ra,dec):
	'''
	SEARCH FOR A MAGNITUDE USING A SINGLE SOURCE-STAR (RA, DEC)
	'''
	dfGaia = pd.DataFrame()
	coord = SkyCoord(ra=ra, dec=dec,unit=(u.hourangle, u.deg))
	print(coord.dec.value)
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

	print('-----------------')
	# if len(array)>1:
	for i in array:
		value = round(i[3],2)
	return value

# one(ra="17:53:54.741",dec="-34:45:09.72")
# coord_init = ["17:53:54.741 -34:45:09.72"]
# coord = SkyCoord(coord_init,unit=(u.hourangle, u.deg))
# print(coord)

def GaiaFileSearch(filepath):
	'''
	USES A CSV FILE CONTAINING 2 COLUMNS (RA,DEC) AND SEARCHES FOR THE MAGNITUDES. RESULT IS SAVED IN A NEW CSV FILE.
	'''
	# filepath = 'C:/Users/PC-CP/Documents/Projects/Cluster application/Gaia_mags.csv'
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
		
	np.savetxt("test2.csv",result,fmt='%1.2f')
	# pd.DataFrame(result[]).to_csv("C:/Users/PC-CP/Documents/Projects/Cluster application/test.csv")

filepath = 'C:/Users/PC-CP/Documents/Projects/Cluster application/Gaia-mags.csv'
GaiaFileSearch(filepath)






'''
c = SkyCoord('17 53 54.741 -34 45 09.72 ', unit=(u.hourangle, u.deg)) TO 8ELW
print(c.ra.deg)
dump_to_file=False, output_format='csv'
'''