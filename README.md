# SimMobility_Viz - Visualizing SimMobility Data with Plotly Dash

SimMobility_Viz is a Plotly Dash web application designed to visualize SimMobility data, providing an interactive and user-friendly way to explore and analyze transportation and mobility-related information. This repository contains the code necessary to run the web app and visualize SimMobility data for various cities.

## Features

- Interactive data visualization using Plotly Dash.
- Support for multiple cities' SimMobility data.
- Easily expandable structure for adding data and visualizations for additional cities.

## Getting Started

Follow these instructions to set up and run the SimMobility_Viz web application on your local machine.

### Prerequisites

Make sure you have the following software installed:

- Python (>=3.6)
- Pip (Python package installer)

### Installation

1. Clone this repository to your local machine:
2. Navigate to the project directory (cd SImMobility_Viz)
3. install required Python packages using pip (pip install -r requirements.txt)

### Running the Web  App
1. Once the required packages are installed, run the web app using the following command: (python app.py)
2. Open a web browser and go to http://127.0.0.1:8051 to access the SimMobility_Viz web application.

### Adding data for a New City
To expand the application by adding data and visualizations for a new city, follow these steps:
1. Create a new folder inside the pages directory with the name of the city (e.g., pages/NewCity).
2. Place the relevant data files for the new city inside the newly created folder.
3. Copy and modify the existing visualization code to create visualizations for the new city. You can find the visualization code in the pages directory.
4. Update the navigation bar or sidebar to include a link to the newly added city's visualization.

### Contributing
Contributions are welcome! If you'd like to contribute to this project, please fork the repository, create a new branch, and submit a pull request with your changes.
