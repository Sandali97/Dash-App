import pandas as pd
import numpy as np
import folium
import geopandas as gpd
from shapely.geometry import Point, box
from IPython.display import clear_output
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import branca.colormap as cm
import branca
import calendar

data = pd.read_csv('company_data.csv')
drought_data = pd.read_csv('drought_data.csv')
chl=pd.read_csv('CSRD perccentage of pixels with chlorophyl bloom - 2023.csv')


def sub_categories():
    # # Define subcategories for each ESRS component
    subcategories = {
        'ESRS E1 - Climate Change': [
            {'label': 'GHG Emissions', 'value': 'GHGEmissions'},
            {'label': 'NonGHGAirPollutants', 'value': 'NonGHGAirPollutants'},
            {'label': 'Coastal Inundation', 'value': 'Coastal Inundation'},
            {'label': 'Riverine Inundation', 'value': 'Riverine Inundation'},
            {'label': 'Drought Risk', 'value': 'category'},
            {'label': 'Landslide Risk', 'value': 'AnnualLandslideOccurance25Km'},
            {'label': 'Hurricane Risk', 'value': 'AnnualHurricaneOccurance250Km'},
            {'label': 'Temperature', 'value': 'MonthlyTemperature'},
            {'label': 'Heatwave Risk', 'value': 'Heatwave Risk'},
            {'label': 'Coldwave Risk', 'value': 'Coldwave Risk'},
            {'label': 'Annual Rainfall', 'value': 'Annual Rainfall'}
        ],
        'ESRS E2 - Pollution': [
            {'label': 'Solid Waste', 'value': 'SolidWaste'},
            {'label': 'Water Pollutants', 'value': 'WaterPollutants'},
            {'label': 'Chlorophyll Percentage in 100m', 'value': 'ChlorophyllPercentage_100m'},
            {'label': 'Chlorophyll Percentage in 1000m', 'value': 'ChlorophyllPercentage_1000m'}
        ],
        'ESRS E3 - Water and Marine Resources': [
            {'label': 'Water Stress Score', 'value': 'waterStressScore'},
            {'label': 'Water Use', 'value': 'WaterUse'},
            {'label': 'Water Quality', 'value': 'WaterQuality'}
        ],
        'ESRS E4 - Biodiversity and Ecosystems': [
            {'label': 'Land Usage', 'value': 'landUsage'},
            {'label': 'Land Cover Types', 'value': 'landCover'},
            {'label': 'Distance to Closest KBA','value':'distance_Kms_to_closest_KBA'},
            {'label': 'Distance to Closest WPA','value':'distance_Kms_to_closest_WPA'},
            {'label': 'Located within a KBA','value':'located_within_KBA_or_Not'},
            {'label': 'Located within a KBA','value':'located_within_WPA_or_Not'},
            {'label': 'Total Species Count within 1km', 'value': 'TotalSpeciesCount1km'},
            {'label': 'Tree Cover Loss within 500m', 'value': 'tree_cover_loss'}
        ]
    }
    return subcategories

def app_layout():
    a = html.Div([
        # Add a link to the Google Fonts CSS
        html.Link(
            href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap",
            rel="stylesheet"
        ),

        # Title at the top
        html.Div([
            html.H1(
                'RS Metrics Alignment with the CSRD',
                style={'fontFamily': 'Roboto', 'fontSize': '24px', 'textAlign': 'center', 'color': 'white'}
            )
        ], style={'width': '100%', 'padding': '10px', 'backgroundColor': '#003366'}),  # Top row for title

        html.Div([
            # Left column with dropdown and company info
            html.Div([
                dcc.Dropdown(
                    id='company-dropdown',
                    options=[{'label': company, 'value': company} for company in company_data['Company'].unique()],
                    value='TotalEnergies SE'
                ),
                # Company information displayed here
                html.Div(id='company-info', style={'margin-top': '10px'}),

                html.Div(style={'height': '5px'}),

                # html.Label("Select a Location:", style={'margin-top': '5px', 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='location-dropdown',  # New dropdown for locations
                    options=[],
                    value='GAPCO Tanzania Oil Refinery',
                    placeholder="Select a location"
                ),
                # Year and Month Filter Row
                # html.Label("Select Year and Month:", style={'margin-top': '0px', 'fontWeight': 'bold'}),
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center', 'margin': '10px 0'},
                    
                    children=[
                        dcc.Dropdown(
                            id='year-dropdown',
                            options=[{'label': str(year), 'value': year} for year in years],
                            placeholder='Year',
                            value = '2024',
                            style={'width': '128px', 'marginRight': '10px'}
                        ),
                        dcc.Dropdown(
                            id='month-dropdown',
                            options=[{'label': month, 'value': month} for month in months],
                            placeholder='Month',
                            value = 'January',
                            style={'width': '128px'}
                        ),
                    ]
                ),

                # Main component selection
                dcc.Dropdown(
                    id='component-dropdown',
                    options=[{'label': key, 'value': key} for key in subcategories.keys()],
                    value='ESRS E1 - Climate Change',
                    style={'margin-top': '10px'}
                ),

                # Subcategory selection
                dcc.RadioItems(
                    id='subcategory-options',
                    options=[],
                    value='category',  # Default selection for Climate Change
                    style={'fontFamily': 'Roboto', 'margin-top': '10px','fontSize': '14px'},
                    labelStyle={'display': 'block'},  # Stack options vertically
                ),
                
                # Coastal options dropdown
                dcc.Dropdown(
                    id='coastal-options-container',  # Use Dropdown here
                    options=[],  # Initially empty options
                    style={'display': 'none', 'position': 'absolute', 'bottom': '20px', 'right': '20px','fontSize': '12px'}
                ),
                
                # riverine options dropdown
                dcc.Dropdown(
                    id='riverine-options-container',  # Use Dropdown here
                    options=[],  # Initially empty options
                    style={'display': 'none', 'position': 'absolute', 'bottom': '20px', 'right': '20px','fontSize': '12px'}
                ),

                # heatwave options dropdown
                dcc.Dropdown(
                    id='heatwave-options-container',  # Use Dropdown here
                    options=[],  # Initially empty options
                    style={'display': 'none', 'position': 'absolute', 'bottom': '20px', 'right': '20px','fontSize': '12px'}
                ),
                # coldwave options dropdown
                dcc.Dropdown(
                    id='coldwave-options-container',  # Use Dropdown here
                    options=[],  # Initially empty options
                    style={'display': 'none', 'position': 'absolute', 'bottom': '20px', 'right': '20px','fontSize': '12px'}
                ),
                # coldwave options dropdown
                dcc.Dropdown(
                    id='rainfall-options-container',  # Use Dropdown here
                    options=[],  # Initially empty options
                    style={'display': 'none', 'position': 'absolute', 'bottom': '20px', 'right': '20px','fontSize': '12px'}
                )
                
            ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 'fontFamily': 'Roboto',
                      'backgroundColor': '#88cad1', 'height': '77.5vh'}),  # Left column with company data

         # Div for the map
        html.Div(id='map-container', style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top',
                                                'fontFamily': 'Roboto', 'height': '77.5vh', 'backgroundColor': '#dee5e7',
                                                'position': 'relative'}),  
        
        ])
    ])
    return a

def legends(subcategory_option,m):
    
    landcover_color_mapping,drought_color_mapping,emissions_color_mapping,NonGHG_emissions_color_mapping,encore_color_mapping= color_mapping()

    if subcategory_option == 'category':

        # Create a legend only for drought categories
        legend_html = '''
                <div style="position: fixed; top: 8px; right: 8px; z-index: 1000; background-color: white; padding: 
                6px; border: 1px solid grey; max-height: 800px; overflow-y: auto; font-size: 12px;">
            '''
        for class_name, color in drought_color_mapping.items():
            legend_html += f'<p><span style="color: {color};">■</span> {class_name}</p>'
        
        legend_html += '</div>'
        

    elif subcategory_option == 'GHGEmissions':

        # Create a legend only for drought categories
        legend_html = '''
                <div style="position: fixed; top: 6px; right: 8px; z-index: 1000; background-color: white; padding: 
                6px; border: 1px solid grey; max-height: 500px; overflow-y: auto; font-size: 12px;">
            '''
        for emission_name, emission_color in emissions_color_mapping.items():
            legend_html += f'<p><span style="color: {emission_color};">■</span> {emission_name}</p>'
        
        legend_html += '</div>'
        
    elif subcategory_option == 'NonGHGAirPollutants':

        # Create a legend only for drought categories
        legend_html = '''
                <div style="position: fixed; top: 6px; right: 8px; z-index: 1000; background-color: white; padding: 
                6px; border: 1px solid grey; max-height: 500px; overflow-y: auto; font-size: 12px;">
            '''
        for emission_name, emission_color in NonGHG_emissions_color_mapping.items():
            legend_html += f'<p><span style="color: {emission_color};">■</span> {emission_name}</p>'
        
        legend_html += '</div>'
        
    elif subcategory_option in ['AnnualLandslideOccurance25Km','AnnualHurricaneOccurance250Km']:
        legend_html = '''
                <div style="position: fixed; top: 6px; right: 8px; z-index: 1000; background-color: white; padding: 
                6px; border: 1px solid grey; max-height: 500px; overflow-y: auto; font-size: 12px;">
            '''
        landslide_hurricane_colors= {
            "Occurance" : "orange",
            "Data Not Available":"lightblue"
        }
        for landslide_name, landslide_color in landslide_hurricane_colors.items():
            legend_html += f'<p><span style="color: {landslide_color};">■</span> {landslide_name}</p>'
        
        legend_html += '</div>'
    elif subcategory_option in ['SolidWaste','WaterPollutants','waterStressScore','WaterUse','WaterQuality']:

        # Create a legend only for drought categories
        legend_html = '''
                <div style="position: fixed; top: 6px; right: 8px; z-index: 1000; background-color: white; padding: 
                6px; border: 1px solid grey; max-height: 500px; overflow-y: auto; font-size: 12px;">
            '''
        for solidwaste_name, solidwaste_color in encore_color_mapping.items():
            legend_html += f'<p><span style="color: {solidwaste_color};">■</span> {solidwaste_name}</p>'
        
        legend_html += '</div>'
        
        
    else:
        legend_html = '''
            <div style="position: fixed; top: 6px; right: 8px; z-index: 1000; background-color: white; padding: 
            6px; border: 1px solid grey; max-height: 500px; overflow-y: auto; font-size: 12px;">
            <p>No legend available for the selected option.</p>
        </div>
        '''
        
    return m.get_root().html.add_child(folium.Element(legend_html))
def color_mapping():
    landcover_color_mapping = {
        "Water": 'mediumblue',
        "Trees": 'limegreen',
        "Grass": 'seagreen',
        "FloodedVegetation": 'lightseagreen',
        "Crops": 'yellowgreen',
        "ShrubAndScrub": 'olive',
        "Built": 'grey',
        "Bare": 'brown',
        "SnowAndIce": 'aqua',
        "Unknown": 'gainsboro'
        }
    drought_color_mapping = {
        "Abnormally Dry": 'beige',
        "Moderate Drought": 'lightred',
        "Severe Drought": 'orange',
        "Extreme Drought": 'red',
        "Exceptional Drought": 'darkred',
        "Normal": 'gray',
        "Abnormally Wet": 'lightgray',
        "Moderate Wet": 'lightblue',
        "Severe Wet": 'cadetblue',
        "Extreme Wet": 'blue',
        "Exceptional Wet": 'darkblue'
        }
    emissions_color_mapping = {
        "H": 'red',
        "M": 'beige',
        "Not Available" : 'lightblue'
        }
    NonGHG_emissions_color_mapping = {
        "H": 'red',
        "M": 'beige',
        "Not Available" : 'lightblue'
        }
    
    encore_color_mapping = {
        'VH':'red',
        'H':'orange',
        'M':'beige',
        'L':'green',
        'Not Available':'lightblue'
    }
    return landcover_color_mapping,drought_color_mapping,emissions_color_mapping,NonGHG_emissions_color_mapping,encore_color_mapping

def futuristic_color_mapping():
    from branca.colormap import StepColormap
    coastal_color_scale_2030 = branca.colormap.LinearColormap(
        colors=['green', 'beige', 'red'],
        vmin=0.0, 
        vmax=8.59
    )

    coastal_color_scale_2050 = branca.colormap.LinearColormap(
        colors=['green', 'beige', 'red'],
        vmin=0.0, 
        vmax=10.14
    )

    coastal_color_scale_2080 = branca.colormap.LinearColormap(
        colors=['green', 'beige', 'red'],
        vmin=0.0, 
        vmax=12.41
    )

    riverine_color_scale = branca.colormap.LinearColormap(
       colors=['green', 'orange', 'red'],
        vmin=0.0, 
        vmax=32.0
    ) 
    heatcoldwave_color_scale = branca.colormap.LinearColormap(
       colors=['green', 'orange', 'red'],
        vmin=0.0, 
        vmax=100.0,
        index=[0, 50, 100]
    ) 

    rainfall_color_scale = StepColormap(
        colors=['green', 'orange', 'red'],
        index=[0, 500, 1000],  # Define the breakpoints for color transition
        vmin=0.0, 
        vmax=1000.0 )
    return coastal_color_scale_2030,coastal_color_scale_2050,coastal_color_scale_2080,riverine_color_scale,heatcoldwave_color_scale,rainfall_color_scale

# GHG Emissions Handler
def handle_ghg_emissions(location, popup_text, m, emissions_color_mapping):
    emission_category = location['GHGEmissions']
    marker_color = emissions_color_mapping.get(emission_category, 'blue')
    icon_color = 'white' if marker_color != 'gainsboro' else 'black'
    popup_text += f"GHG Emission Impact: {emission_category}"
    legends('GHGEmissions', m)
    return marker_color, icon_color, popup_text

# Non-GHG Air Pollutants Handler
def handle_non_ghg_emissions(location, popup_text, m, NonGHG_emissions_color_mapping):
    nonGHG_emission_category = location['NonGHGAirPollutants']
    marker_color = NonGHG_emissions_color_mapping.get(nonGHG_emission_category, 'blue')
    icon_color = 'white' if marker_color != 'gainsboro' else 'black'
    popup_text += f"Non GHG Emission Impact: {nonGHG_emission_category}"
    legends('NonGHGAirPollutants', m)
    return marker_color, icon_color, popup_text

# Annual Landslide Occurrence Handler
def handle_landslide(location, popup_text, m):
    landslide_data = location['AnnualLandslideOccurance25Km']
    popup_text += f"Annual Landslide Occurrence 25km: {landslide_data}"
    legends('AnnualLandslideOccurance25Km', m)
    marker_color = 'blue' if pd.isna(landslide_data) else 'orange'
    return marker_color, popup_text

# Annual Hurricane Occurrence Handler
def handle_hurricane(location, popup_text, m):
    hurricane_data = location['AnnualHurricaneOccurance250Km']
    popup_text += f"Annual Hurricane Occurrence 25km: {hurricane_data}"
    legends('AnnualHurricaneOccurance250Km', m)
    marker_color = 'blue' if pd.isna(hurricane_data) else 'orange'
    return marker_color, popup_text

# Drought Category Handler
def handle_drought(location, popup_text, m, drought_info, drought_color_mapping):
    spi_info = drought_info[drought_info['locationName'] == location['locationName']]
    legends('category', m)
    if not spi_info.empty:
        drought_value = spi_info.iloc[0]['spi']
        drought_category = spi_info.iloc[0]['category']
        popup_text += f"Drought SPI: {drought_value}<br> Drought Category :{drought_category}<br>"
        marker_color = drought_color_mapping.get(drought_category, 'blue')
    else:
        popup_text += "Drought Data: No data available<br>"
        marker_color = 'blue'
    return marker_color, popup_text

# Coastal Inundation Handler
def handle_coastal_inundation(location, popup_text, m, coastal_scenario, coastal_color_scale_2030, coastal_color_scale_2050, coastal_color_scale_2080):
    inundation_value = location[coastal_scenario]
    popup_text += f"Coastal Inundation Value: {inundation_value}<br>"
    
    # Determine color and scale based on the scenario
    marker_color = 'blue' if pd.isna(inundation_value) else 'green'
    if coastal_scenario.startswith('CoastalInundation2030'):
        marker_color = coastal_color_scale_2030(inundation_value)
        coastal_color_scale_2030.add_to(m)
    elif coastal_scenario.startswith('CoastalInundation2050'):
        marker_color = coastal_color_scale_2050(inundation_value)
        coastal_color_scale_2050.add_to(m)
    elif coastal_scenario.startswith('CoastalInundation2080'):
        marker_color = coastal_color_scale_2080(inundation_value)
        coastal_color_scale_2080.add_to(m)
        
    return marker_color, popup_text

# Riverine Inundation Handler
def handle_riverine_inundation(location, popup_text, m, riverine_scenario, riverine_color_scale):
    riv_inundation_value = location[riverine_scenario]
    popup_text += f"Riverine Inundation Value: {riv_inundation_value}<br>"
    marker_color = 'blue' if pd.isna(riv_inundation_value) else riverine_color_scale(riv_inundation_value)
    if riverine_scenario.startswith('RiverineInundation'):
        riverine_color_scale.add_to(m)
    return marker_color, popup_text

# Heatwave Risk Handler
def handle_heatwave(location, popup_text, m, heatwave_scenario, heatcoldwave_color_scale):
    heatwave_value = location[heatwave_scenario]
    popup_text += f"Heatwave Risk Value: {heatwave_value}<br>"
    marker_color = 'blue' if pd.isna(heatwave_value) else heatcoldwave_color_scale(heatwave_value)
    if heatwave_scenario.startswith('heatwaveRiskScore'):
        heatcoldwave_color_scale.add_to(m)
    return marker_color, popup_text

# Coldwave Risk Handler
def handle_coldwave(location, popup_text, m, coldwave_scenario, heatcoldwave_color_scale):
    coldwave_value = location[coldwave_scenario]
    popup_text += f"Coldwave Risk Value: {coldwave_value}<br>"
    marker_color = 'blue' if pd.isna(coldwave_value) else heatcoldwave_color_scale(coldwave_value)
    if coldwave_scenario.startswith('coldwaveRiskScore'):
        heatcoldwave_color_scale.add_to(m)
    return marker_color, popup_text

# Annual Rainfall Handler
def handle_rainfall(location, popup_text, m, rainfall_scenario, rainfall_color_scale):
    rainfall_value = location[rainfall_scenario]
    popup_text += f"Annual Accumulated Rainfall Value: {rainfall_value}<br>"
    marker_color = 'blue' if pd.isna(rainfall_value) else rainfall_color_scale(rainfall_value)
    if rainfall_scenario.startswith('annualAccumilatedRainfall'):
        rainfall_color_scale.add_to(m)
    return marker_color, popup_text

def solidwaste(m, subcategory_option, location, encore_color_mapping):
    # Initialize popup_text
    popup_text = ""

    if subcategory_option == 'SolidWaste':
        solidwaste = location['SolidWaste']
        marker_color = encore_color_mapping.get(solidwaste, 'blue') 
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Impact of Solid Waste: {solidwaste}"
        legends(subcategory_option, m)
        
    
    # Return the marker color, icon color, and popup text
    return marker_color, icon_color, popup_text

def waterpollutants(m, subcategory_option, location, encore_color_mapping):

    popup_text = ""
    if subcategory_option == 'WaterPollutants':
        waterpollutant = location['WaterPollutants']
        marker_color = encore_color_mapping.get(waterpollutant, 'blue') 
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Impact of Water Pollutants: {waterpollutant}"
        legends(subcategory_option, m)
    return marker_color, icon_color, popup_text

def chl_100m(m, subcategory_option, location):

    popup_text = ""
    if subcategory_option == 'ChlorophyllPercentage_100m':
        chl_100m = location['ChlorophyllPercentage_100m']
        marker_color = 'blue'
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Chlorophyll Percentage in 100m: {chl_100m}"
    return marker_color, icon_color, popup_text
    
def chl_1000m(m, subcategory_option, location):

    popup_text = ""
    if subcategory_option == 'ChlorophyllPercentage_1000m':
        chl_1000m = location['ChlorophyllPercentage_1000m']
        marker_color = 'blue'
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Chlorophyll Percentage in 1000m: {chl_1000m}"
    return marker_color, icon_color, popup_text

def waterStressScore(m, subcategory_option, location):

    popup_text = ""
    if subcategory_option == 'waterStressScore':
        waterstress = location['waterStressScore']
        if waterstress==0.0:
            marker_color = 'green',
        elif (waterstress>0 and waterstress<=50):
            marker_color = 'orange',
        elif (waterstress<=100 and waterstress>50):
            marker_color = 'red'
        else:
             marker_color = 'blue'
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Water Stress Score: {waterstress}"
        legends(subcategory_option, m)
    return marker_color, icon_color, popup_text

def wateruse(m, subcategory_option, location, encore_color_mapping):

    popup_text = ""
    if subcategory_option == 'WaterUse':
        wateruse = location['WaterUse']
        marker_color = encore_color_mapping.get(wateruse, 'blue') 
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Impact on Water Use: {wateruse}"
        legends(subcategory_option, m)
    return marker_color, icon_color, popup_text
    
def waterquality(m, subcategory_option, location, encore_color_mapping):

    popup_text = ""
    if subcategory_option == 'WaterQuality':
        waterquality = location['WaterQuality']
        marker_color = encore_color_mapping.get(waterquality, 'blue') 
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Impact on Water Quality: {waterquality}"
        legends(subcategory_option, m)
    return marker_color, icon_color, popup_text


def landusage(m, subcategory_option, location):

    popup_text = ""
    if subcategory_option == 'landUsage':
        landusage = location['landUsage']
        print(landusage)
        marker_color = 'blue'
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Land Usage in SqKm: {landusage}"

    return marker_color, icon_color, popup_text
    
def IUCN_1km(m, subcategory_option, location):
    popup_text = ""
    if subcategory_option == 'TotalSpeciesCount1km':
        iucn = location['TotalSpeciesCount1km']
        marker_color = 'blue'
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Total Species Count in 1km: {iucn}"
    return marker_color, icon_color, popup_text
    
def Dist_KBA_1km(m, subcategory_option, location):

    popup_text = ""
    if subcategory_option == 'distance_Kms_to_closest_KBA':
        dist_kba = location['distance_Kms_to_closest_KBA']
        marker_color = 'blue'
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Distance to Closest KBA: {dist_kba}"
    return marker_color, icon_color, popup_text

def Dist_WPA_1km(m, subcategory_option, location):

    popup_text = ""
    if subcategory_option == 'distance_Kms_to_closest_WPA':
        dist_wpa = location['distance_Kms_to_closest_WPA']
        marker_color = 'blue'
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Distance to Closest WPA: {dist_wpa}"
    return marker_color, icon_color, popup_text

def within_kba(m, subcategory_option, location):

    popup_text = ""
    if subcategory_option == 'located_within_KBA_or_Not':
        within_kba = location['located_within_KBA_or_Not']
        marker_color = 'blue'
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Located within KBA: {within_kba}"
    return marker_color, icon_color, popup_text

def within_wpa(m, subcategory_option, location):

    popup_text = ""
    if subcategory_option == 'located_within_WPA_or_Not':
        within_wpa = location['located_within_WPA_or_Not']
        marker_color = 'blue'
        icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
        popup_text += f"Location Name: {location['locationName']}<br>Located within WPA: {within_wpa}"
    return marker_color, icon_color, popup_text
company_data = data
app = dash.Dash(__name__)
server = app.server
app.title = 'CSRD' 

# Extract unique years from dynamic_data
years = drought_data['Year'].unique()  
months = list(calendar.month_name[1:]) 

# Define subcategories for each ESRS component
subcategories = sub_categories()

# Define the layout of the Dash app
app.layout = app_layout()

# Callback to update location options based on selected company
@app.callback(
    Output('location-dropdown', 'options'),
    [Input('company-dropdown', 'value')]
)
def set_location_options(selected_company):
    filtered_locations = company_data[company_data['Company'] == selected_company]
    return [{'label': loc, 'value': loc} for loc in filtered_locations['locationName'].unique()]

# Callback to update company information based on selected company
@app.callback(
    Output('company-info', 'children'),
    [Input('company-dropdown', 'value')]
)
def display_company_info(selected_company):
    company_rows = company_data[company_data['Company'] == selected_company]
    company_info = company_rows.iloc[0] 
    return html.Div([html.P(f"Number of Assets: {len(company_rows)}")])

# Callback to update subcategory options based on selected component
@app.callback(
    [Output('subcategory-options', 'options'),
     Output('coastal-options-container', 'options'),
     Output('coastal-options-container', 'style'),
     Output('riverine-options-container', 'options'),
     Output('riverine-options-container', 'style'),
     Output('heatwave-options-container', 'options'),
     Output('heatwave-options-container', 'style'),
     Output('coldwave-options-container', 'options'),
     Output('coldwave-options-container', 'style'),
     Output('rainfall-options-container', 'options'),
     Output('rainfall-options-container', 'style')],
    [Input('component-dropdown', 'value'),
     Input('subcategory-options', 'value')]
)


def update_subcategory_options(selected_component, selected_subcategory):
    if selected_component is None:
        # Ensure you return all 7 outputs even when no component is selected
        return [], [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}

    # Get the options for the selected component
    if selected_component in subcategories:
        options = [{'label': sub['label'], 'value': sub['value']} for sub in subcategories[selected_component]]

        # Check if the selected subcategory is for coastal inundation
        if selected_subcategory == 'Coastal Inundation':
            coastal_options = [
                {'label': '2030 RCP 4.5', 'value': 'CoastalInundation2030RCP45ReturnPeriod100Percentile95'},
                {'label': '2030 RCP 8.5', 'value': 'CoastalInundation2030RCP85ReturnPeriod100Percentile95'},
                {'label': '2050 RCP 4.5', 'value': 'CoastalInundation2050RCP45ReturnPeriod100Percentile95'},
                {'label': '2050 RCP 8.5', 'value': 'CoastalInundation2050RCP85ReturnPeriod100Percentile95'},
                {'label': '2080 RCP 4.5', 'value': 'CoastalInundation2080RCP45ReturnPeriod100Percentile95'},
                {'label': '2080 RCP 8.5', 'value': 'CoastalInundation2080RCP85ReturnPeriod100Percentile95'}
            ]
            # Return all 7 outputs, including hidden styles and empty options for riverine and heatwave
            return options, coastal_options, {'display': 'block'}, [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}

        if selected_subcategory == 'Riverine Inundation':
            riverine_options = [
                {'label': '2030 RCP 4.5', 'value': 'RiverineInundation2030RCP45ReturnPeriod100'},
                {'label': '2030 RCP 8.5', 'value': 'RiverineInundation2030RCP85ReturnPeriod100'},
                {'label': '2050 RCP 4.5', 'value': 'RiverineInundation2050RCP45ReturnPeriod100'},
                {'label': '2050 RCP 8.5', 'value': 'RiverineInundation2050RCP85ReturnPeriod100'},
                {'label': '2080 RCP 4.5', 'value': 'RiverineInundation2080RCP45ReturnPeriod100'},
                {'label': '2080 RCP 8.5', 'value': 'RiverineInundation2080RCP85ReturnPeriod100'}
            ]
            # Return all 7 outputs, including hidden styles and empty options for coastal and heatwave
            return options, [], {'display': 'none'}, riverine_options, {'display': 'block'}, [], {'display': 'none'}, [], {'display': 'none'}

        if selected_subcategory == 'Heatwave Risk':
            heatwave_options = [
                {'label': '2025 RCP 4.5', 'value': 'heatwaveRiskScore_2025_RCP45'},
                {'label': '2025 RCP 8.5', 'value': 'heatwaveRiskScore_2025_RCP85'},
                {'label': '2050 RCP 4.5', 'value': 'heatwaveRiskScore_2050_RCP45'},
                {'label': '2050 RCP 8.5', 'value': 'heatwaveRiskScore_2050_RCP85'},
                {'label': '2075 RCP 4.5', 'value': 'heatwaveRiskScore_2075_RCP45'},
                {'label': '2075 RCP 8.5', 'value': 'heatwaveRiskScore_2075_RCP85'},
                {'label': '2100 RCP 4.5', 'value': 'heatwaveRiskScore_2100_RCP45'},
                {'label': '2100 RCP 8.5', 'value': 'heatwaveRiskScore_2100_RCP85'}
            ]
            # Return all 7 outputs, including hidden styles and empty options for coastal and riverine
            return options, [], {'display': 'none'}, [], {'display': 'none'}, heatwave_options, {'display': 'block'}, [], {'display': 'none'}
            
        if selected_subcategory == 'Coldwave Risk':
            coldwave_options = [
                {'label': '2025 RCP 4.5', 'value': 'coldwaveRiskScore_2025_RCP45'},
                {'label': '2025 RCP 8.5', 'value': 'coldwaveRiskScore_2025_RCP85'},
                {'label': '2050 RCP 4.5', 'value': 'coldwaveRiskScore_2050_RCP45'},
                {'label': '2050 RCP 8.5', 'value': 'coldwaveRiskScore_2050_RCP85'},
                {'label': '2075 RCP 4.5', 'value': 'coldwaveRiskScore_2075_RCP45'},
                {'label': '2075 RCP 8.5', 'value': 'coldwaveRiskScore_2075_RCP85'},
                {'label': '2100 RCP 4.5', 'value': 'coldwaveRiskScore_2100_RCP45'},
                {'label': '2100 RCP 8.5', 'value': 'coldwaveRiskScore_2100_RCP85'}
            ]
            # Return all 7 outputs, including hidden styles and empty options for coastal and riverine
            return options, [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}, coldwave_options, {'display': 'block'}

        if selected_subcategory == 'Annual Rainfall':
            rainfall_options = [
                {'label': '2030 RCP 4.5', 'value': 'annualAccumilatedRainfall2030RCP45'},
                {'label': '2030 RCP 8.5', 'value': 'annualAccumilatedRainfall2030RCP85'},
                {'label': '2050 RCP 4.5', 'value': 'annualAccumilatedRainfall2050RCP45'},
                {'label': '2050 RCP 8.5', 'value': 'annualAccumilatedRainfall2050RCP85'},
                {'label': '2075 RCP 4.5', 'value': 'annualAccumilatedRainfall2080RCP45'},
                {'label': '2075 RCP 8.5', 'value': 'annualAccumilatedRainfall2080RCP85'}
            ]
            # Return all 7 outputs, including hidden styles and empty options for coastal and riverine
            return options, [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}, rainfall_options, {'display': 'block'}
        # If no coastal, riverine, or heatwave options are selected, hide all specific containers
        return options, [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}

    # If the selected component is not in subcategories, return empty outputs
    return [], [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}, [], {'display': 'none'}

    
# Callback to update the map based on the selected inputs
@app.callback(
    Output('map-container', 'children'),
    [Input('company-dropdown', 'value'),
     Input('location-dropdown', 'value'),
     Input('component-dropdown', 'value'),
     Input('subcategory-options', 'value'), 
     Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value'),
     Input('coastal-options-container','value'),
     Input('riverine-options-container','value'),
     Input('heatwave-options-container','value'),
     Input('coldwave-options-container','value'),
     Input('rainfall-options-container','value')]
)


def update_map(selected_company, selected_location, selected_component, subcategory_option, year, month,coastal_scenario,riverine_scenario,heatwave_scenario,coldwave_scenario,rainfall_scenario):

    company_locations = company_data[company_data['Company'] == selected_company]

    if selected_location:
        company_locations = company_locations[company_locations['locationName'] == selected_location]

    if company_locations.empty:
        return html.Div("No locations available for this company.")

    drought_info = drought_data[
        (drought_data['Company'] == selected_company) &
        (drought_data['Year'] == year) & 
        (drought_data['Month'] == month)]   

    map_html = create_map(company_locations,year, month,drought_info, selected_component, subcategory_option,coastal_scenario,riverine_scenario,heatwave_scenario,coldwave_scenario,rainfall_scenario)

    return html.Iframe(srcDoc=map_html, width='100%', height='500')



def create_map(company_locations,year, month,drought_info, selected_component=None, subcategory_option=None,coastal_scenario=None,riverine_scenario=None,heatwave_scenario=None,coldwave_scenario=None,rainfall_scenario=None):

    m = folium.Map(location=[19.085436759954092, -23.796692977181433], zoom_start=3, maptype="satellite")
 
    folium.TileLayer(
        tiles='http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
        attr='Google', 
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    
    # #color mapping
    coastal_color_scale_2030,coastal_color_scale_2050,coastal_color_scale_2080,riverine_color_scale,heatcoldwave_color_scale,rainfall_color_scale = futuristic_color_mapping()
    landcover_color_mapping, drought_color_mapping, emissions_color_mapping,NonGHG_emissions_color_mapping,encore_color_mapping= color_mapping()

    marker_color = 'blue'

    # Iterate over company locations and add markers
    for _, location in company_locations.iterrows():
        popup_text = f"Location: {location['locationName']}<br>"
        
        # Customize markers based on the selected component and subcategory
        if selected_component == 'ESRS E1 - Climate Change':
            # climatechange_options(subcategory_option,location,m,drought_info, coastal_scenario=None, riverine_scenario=None, heatwave_scenario=None, coldwave_scenario=None, rainfall_scenario=None)
            if subcategory_option == 'GHGEmissions':
                emission_category = location['GHGEmissions']
                marker_color = emissions_color_mapping.get(emission_category, 'blue')
                icon_color = 'white' if marker_color != 'gainsboro' else 'black'
                popup_text += f"GHG Emission Impact: {emission_category}"
                legends(subcategory_option, m)
                
            if subcategory_option == 'NonGHGAirPollutants':
                nonGHG_emission_category = location['NonGHGAirPollutants']
                marker_color = NonGHG_emissions_color_mapping.get(nonGHG_emission_category, 'blue') 
                icon_color = 'white' if marker_color != 'gainsboro' else 'black'  
                popup_text += f"Non GHG Emissin Impact: {nonGHG_emission_category}"
                legends(subcategory_option,m) 
                
            if subcategory_option == 'AnnualLandslideOccurance25Km':
                landslide_data = location['AnnualLandslideOccurance25Km']
                popup_text += f"Annual Landslide Occurance 25km: {landslide_data}"
                legends(subcategory_option,m)
                if pd.isna(landslide_data):
                    marker_color = 'blue'  
                else: 
                    marker_color = 'orange'
    
            if subcategory_option == 'AnnualHurricaneOccurance250Km':
                hurricane_data = location['AnnualHurricaneOccurance250Km']
                popup_text += f"Annual Hurricane Occurance 25km: {hurricane_data}"
                legends(subcategory_option,m) 
                if pd.isna(hurricane_data):
                    marker_color = 'blue'  
                else: 
                    marker_color = 'orange'
                    
            if subcategory_option =='category':
                spi_info = drought_info[drought_info['locationName'] == location['locationName']]
                legends(subcategory_option,m)
                if not drought_info.empty:
                    drought_value = spi_info.iloc[0]['spi']
                    drought_category = spi_info.iloc[0]['category']
                    popup_text += f"Drought SPI: {drought_value}<br> Drought Category :{drought_category}<br>"
                    marker_color = drought_color_mapping.get(drought_category, 'blue') 
                else:
                    popup_text += "Drought Data: No data available<br>"
                    
            if subcategory_option =='MonthlyTemperature':
                temp_info = drought_info[drought_info['locationName'] == location['locationName']]
                legends(subcategory_option,m)
                if not temp_info.empty:
                    tempt_value = temp_info.iloc[0]['MonthlyTemperature']
                    popup_text += f"Monthly Temperature Value: {tempt_value}"
                else:
                    popup_text += "No data available for this location<br>"
                    
            if subcategory_option == 'Coastal Inundation':
                if coastal_scenario:
                    inundation_value = location[coastal_scenario]
                    popup_text += f"Coastal Inundation Value: {inundation_value}<br>"
                    if coastal_scenario in ['CoastalInundation2030RCP45ReturnPeriod100Percentile95','CoastalInundation2030RCP85ReturnPeriod100Percentile95']: 
                        if pd.isna(inundation_value):
                            marker_color = 'blue'  
                        elif inundation_value == 0.0:
                            marker_color = 'green'  
                            marker_color = coastal_color_scale_2030(inundation_value)
                            
                    elif coastal_scenario in ['CoastalInundation2050RCP45ReturnPeriod100Percentile95','CoastalInundation2050RCP85ReturnPeriod100Percentile95']: 
                        if pd.isna(inundation_value):
                            marker_color = 'blue'  
                        elif inundation_value == 0.0:
                            marker_color = 'green'  
                        else:
                            marker_color = coastal_color_scale_2050(inundation_value)
                    elif coastal_scenario in['CoastalInundation2080RCP45ReturnPeriod100Percentile95','CoastalInundation2080RCP85ReturnPeriod100Percentile95']: 
                        if pd.isna(inundation_value):
                            marker_color = 'blue'  
                        elif inundation_value == 0.0:
                            marker_color = 'green'  
                        else:
                            marker_color = coastal_color_scale_2080(inundation_value)
        
                    if coastal_scenario in ['CoastalInundation2030RCP45ReturnPeriod100Percentile95', 
                                         'CoastalInundation2030RCP85ReturnPeriod100Percentile95',
                                         'CoastalInundation2050RCP45ReturnPeriod100Percentile95', 
                                         'CoastalInundation2050RCP85ReturnPeriod100Percentile95',
                                         'CoastalInundation2080RCP45ReturnPeriod100Percentile95', 
                                         'CoastalInundation2080RCP85ReturnPeriod100Percentile95']:
                        # Choose the appropriate color scale based on the scenario
                        if coastal_scenario.startswith('CoastalInundation2030'):
                            coastal_color_scale_2030.add_to(m)
                        elif coastal_scenario.startswith('CoastalInundation2050'):
                            coastal_color_scale_2050.add_to(m)
                        elif coastal_scenario.startswith('CoastalInundation2080'):
                            coastal_color_scale_2080.add_to(m)
            
            if subcategory_option == 'Riverine Inundation':
                if riverine_scenario:
                    riv_inundation_value = location[riverine_scenario]
                    popup_text += f"Riverine Inundation Value: {riv_inundation_value}<br>"
                    if pd.isna(riv_inundation_value):
                            marker_color = 'blue'  
                    elif riv_inundation_value == 0.0:
                        marker_color = 'green'  
                    else:
                        marker_color = riverine_color_scale(riv_inundation_value)
                    if riverine_scenario.startswith('RiverineInundation'):
                            riverine_color_scale.add_to(m)
                        
            if subcategory_option == 'Heatwave Risk':
                if heatwave_scenario:
                    heatwave_value = location[heatwave_scenario]
                    popup_text += f"Heatwave Risk Value: {heatwave_value}<br>"
                    if pd.isna(heatwave_value):
                            marker_color = 'blue'  
                    elif heatwave_value == 0.0:
                        marker_color = 'green'  
                    else:
                        marker_color = heatcoldwave_color_scale(heatwave_value)
                    if heatwave_scenario.startswith('heatwaveRiskScore'):
                            heatcoldwave_color_scale.add_to(m)
            
            if subcategory_option == 'Coldwave Risk':
                if coldwave_scenario:
                    coldwave_value = location[coldwave_scenario]
                    popup_text += f"Coldwave Risk Value: {coldwave_value}<br>"
                    if pd.isna(coldwave_value):
                        marker_color = 'blue'  
                    elif coldwave_value == 0.0:
                        marker_color = 'green'  
                    else:
                        marker_color = heatcoldwave_color_scale(coldwave_value)
                    if coldwave_scenario.startswith('coldwaveRiskScore'):
                            heatcoldwave_color_scale.add_to(m)
            
                        
            if subcategory_option == 'Annual Rainfall':
                if rainfall_scenario:
                    rainfall_value = location[rainfall_scenario]
                    popup_text += f"Annual Accumilated Rainfall Value: {rainfall_value}<br>"
                    if pd.isna(rainfall_value):
                        marker_color = 'blue'  
                    elif rainfall_value == 0.0:
                        marker_color = 'green'  
                    else:
                        marker_color = rainfall_color_scale(rainfall_value)
                    if rainfall_scenario.startswith('annualAccumilatedRainfall'):
                            rainfall_color_scale.add_to(m)
        if selected_component == 'ESRS E2 - Pollution': 
            if subcategory_option =='SolidWaste':
                marker_color,icon_color,popup_text= solidwaste(m,'SolidWaste',location,encore_color_mapping)
            if subcategory_option == 'WaterPollutants':
                marker_color,icon_color,popup_text= waterpollutants(m, 'WaterPollutants', location, encore_color_mapping)
            if subcategory_option == 'ChlorophyllPercentage_100m':
                marker_color,icon_color,popup_text = chl_100m(m, 'ChlorophyllPercentage_100m', location)
            if subcategory_option == 'ChlorophyllPercentage_1000m':
                marker_color,icon_color,popup_text = chl_1000m(m, 'ChlorophyllPercentage_1000m', location)
                
        if selected_component == 'ESRS E3 - Water and Marine Resources':
            if subcategory_option =='waterStressScore':
                marker_color,icon_color,popup_text= waterStressScore(m, 'waterStressScore', location)
            if subcategory_option =='WaterUse':
                marker_color,icon_color,popup_text= wateruse(m, 'WaterUse', location, encore_color_mapping)
            if subcategory_option =='WaterQuality':
                marker_color,icon_color,popup_text= waterquality(m, 'WaterQuality', location, encore_color_mapping)
                
        if selected_component =='ESRS E4 - Biodiversity and Ecosystem':
            if subcategory_option=='landUsage':
                marker_color,icon_color,popup_text = landusage(m, 'landUsage', location)
            if subcategory_option=='TotalSpeciesCount1km':
                marker_color,icon_color,popup_text = IUCN_1km(m, 'TotalSpeciesCount1km', location)
            if subcategory_option=='distance_Kms_to_closest_KBA':
                marker_color,icon_color,popup_text = Dist_KBA_1km(m, 'distance_Kms_to_closest_KBA', location)
            if subcategory_option=='distance_Kms_to_closest_WPA':
                marker_color,icon_color,popup_text = Dist_WPA_1km(m, 'distance_Kms_to_closest_WPA', location)
            if subcategory_option=='located_within_KBA_or_Not':
                marker_color,icon_color,popup_text = within_kba(m, 'located_within_KBA_or_Not', location)
            if subcategory_option=='located_within_WPA_or_Not':
                marker_color,icon_color,popup_text = within_wpa(m, 'located_within_WPA_or_Not', location)
            
        
        
        # else:
            #     popup_text += f"{subcategory_option.replace('_', ' ').title()} Data: No data available"
        
        # Add marker to the map
        folium.Marker(
            location=[location['latitude'], location['longitude']],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color=marker_color, icon='info-sign', icon_color='white')
        ).add_to(m)
        
    
    # Return the map's HTML representation
    return m._repr_html_()

# Run the Dash app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))  # Default to 8050 if PORT is not set
    app.run_server(host="0.0.0.0", port=port)
    

