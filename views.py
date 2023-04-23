import pandas as pd
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.response import Response
from waitress import serve
import json

@view_config(route_name='home', renderer='templates/home.jinja2')
def home_view(request):
    return {}

@view_config(route_name='benford', renderer='json')
def benford_view(request):

    # To obtain the uploaded CSV file
    file = request.POST['file'].file

    # To check if the 'file' parameter exists in the request
    if 'file' not in request.POST:
        return Response(json.dumps({'error': 'No file uploaded'}))
    
    # To check if the file is in CSV format
    if file.type != 'text/csv':
        return Response(json.dumps({'error': 'Only CSV files are supported'}))

    # To check if the file is empty
    if file.file is None:
        return Response(json.dumps({'error': 'Empty file uploaded'}))
        
     # Read the file as a DataFrame using pandas
    df = pd.read_csv(file, header=None, names=['number'], dtype={'number': str})

    # Check if the DataFrame has only one column
    if df.shape[1] != 1:
        result = {"error": "Input CSV must have only one column"}
        return Response(json.dumps(result))
    
    # Calculate the first-digit and it's distribution
    first_digits = df['number'].str[0].astype(int)
    distribution = first_digits.value_counts(normalize=True).sort_index()
    
    # expected distribution according to Benford's Law
    expected = pd.Series([0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046])
    
    # Compare the observed distribution to the expected distribution
    error = (distribution - expected).abs().sum() / 9
    
    # Return a JSON response indicating whether or not the data conforms to Benford's Law
    if error < 0.1:
        result = {"conforms_to_benfords_law": True}
    else:
        result = {"conforms_to_benfords_law": False}

    # Return the result as JSON
    return Response(json.dumps(result))


if __name__ == '__main__':
    config = Configurator()
    config.include('pyramid_jinja2')
    config.add_static_view(name='static', path='static')
    config.add_route('home', '/home')
    config.add_route('benford', '/home/benford')
    config.scan()
    app = config.make_wsgi_app()
    from waitress import serve
    serve(app, host='0.0.0.0', port=6543)