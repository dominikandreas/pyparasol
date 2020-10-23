# Parasol
Parasol is a JavaScript library for visualization of multi-objective optimization problems 
such as hyper-parameter tuning and is based on parallel coordinates.

Parallel coordinates make it easy to visualize different parameter configurations

For an interactive example, check out the original authors site for the javascript library:

https://parasoljs.github.io/demo/lrgv.html
 
# PyParasol

PyParasol is a Command line interface and API written in python that makes it easy to use Parasol 
without the need to write javascript code. It creates all HTML and javascript automatically and 
includes a HTTP server to let you view your data with ease.


# Quickstart:

PyParasol requires a python version of at least 3.6. Download python at https://www.python.org/downloads/ 

Install pyparasol
`pip install --user pyparasol`

Use command line interface to view a csv file
```shell script
$ pyparasol data\lrgv.csv  # replace with path to your csv file(s)

 * Serving Flask app "lrgv" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://localhost:5000/ (Press CTRL+C to quit)
```
Now navigate to http://localhost:5000/

# API usage example:
For an example how to use the API, have a look at the [example.py](https://github.com/dominikandreas/pyparasol/blob/master/example.py) script.

## Acknowledgements
The original implementation PyParasol which this fork based on and Parasol itself were created by the
 Kasprzyk Research Group at the University of Colorado Boulder.
 
For more information about parasol, refer to https://github.com/ParasolJS/parasol-es