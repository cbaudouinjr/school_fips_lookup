# school_fips_lookup
Looks up and stores school FIPS codes. FIPS codes are stored in a csv that can be fed into web applications such as [hackathon_manager](https://github.com/codeRIT/hackathon-manager).

## Running fips.py

### APIs
fips.py utilizes two API's to identify the FIPS code for a particular school. [Google Cloud's Geocoding API](https://developers.google.com/maps/documentation/geocoding/start) is used to calculate the longitiude and latitude for a school while the FCC Census is used to identify the county FIPS code with the supplied longitude and latitude.

`GC_API_KEY` The [Google Cloud Geocoding API](https://developers.google.com/maps/documentation/geocoding/start) requires an authenication key, this must be supplied as an environment variable. 

### CSV Input File
The import .csv file must contain the following column headers: `school, address, city, state`

### CSV Output File
The output .csv file will contain the following column headers: `school, address, city, state, fips`
> **Note:** If the script fails to find any data for a school or an error occurs, the fips will be `NONE`
