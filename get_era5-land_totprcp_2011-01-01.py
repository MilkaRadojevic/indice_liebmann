import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-land',
    {
        'format': 'netcdf',
        'variable': 'total_precipitation',
        'year': [
            '2011'
        ],
        'month': [
            '01'
        ],
        'day': [
            '01'
        ],
        'time': [
            '00:00',
        ],
        'area': [
            -9, 15, -13,
            17,
        ],
    },
    'tp_era5-land_reg_hour00_2011-01-01.nc')
