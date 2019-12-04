from flask import Flask, request, render_template, jsonify
from mapcreation import *

alt.data_transformers.disable_max_rows()
alt.themes.enable('opaque')
school_level_map('elementary')
school_level_map('middle')
school_level_map('high')

# initialize the flask app
app = Flask('WhoServinWho', template_folder='html')



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/explore')
def map_explore():


    return(render_template('explore.html')
                            )

@app.route('/map')
def my_map():
    #get user input
    raw_data = request.args
    if bool(raw_data) == False:
        my_map = ''
    else:
        school_level = raw_data['school_level']
        school_level = [school_level]
        identity = dict(raw_data)
        del identity['school_level']
        print(identity)

        my_map = display(identity, school_level=school_level)


    rendered = render_template('map.html',
                                my_map = my_map
                                )

    return(rendered)

    



# run the app

if __name__ == "__main__":
    #do it
    # app.debug = True
    app.run()
